import time
from pathlib import Path

import numpy as np

from common.types import Instance, Schedule, Solver
from rl.fast_sim import BatchSim, N_FEATURES


def _read_mask_mode(model_path) -> str:
    import json
    side = Path(model_path).with_suffix(".json")
    return json.loads(side.read_text()).get("mask_mode", "any") if side.exists() else "any"


class NumpyScorer:

    def __init__(self, w1, b1, w2, b2, w3, b3, w4, b4):
        f32 = lambda a: np.ascontiguousarray(a, dtype=np.float32)
        H = w2.shape[0]
        self.w1t, self.b1 = f32(w1.T), f32(b1)
        self.w2t, self.b2 = f32(w2.T), f32(b2)
        self.w3ht, self.w3ct = f32(w3[:, :H].T), f32(w3[:, H:].T)
        self.b3 = f32(b3)
        self.w4, self.b4 = f32(w4.reshape(-1)), np.float32(np.asarray(b4).reshape(-1)[0])
        self.H = H

    @classmethod
    def from_model(cls, model):
        fe = model.policy.features_extractor
        g = lambda layer: (layer.weight.detach().cpu().numpy(), layer.bias.detach().cpu().numpy())
        (w1, b1), (w2, b2) = g(fe.row_net[0]), g(fe.row_net[2])
        (w3, b3), (w4, b4) = g(fe.score_net[0]), g(fe.score_net[2])
        return cls(w1, b1, w2, b2, w3, b3, w4, b4)

    def scores(self, feats, ready, mask=None):
        B, n, F = feats.shape
        h = np.maximum(feats.reshape(B * n, F) @ self.w1t + self.b1, 0.0)
        h = np.maximum(h @ self.w2t + self.b2, 0.0).reshape(B, n, self.H)
        m = ready[..., None].astype(np.float32)
        ctx = (h * m).sum(1) / np.maximum(m.sum(1), 1.0)                    
        cterm = ctx @ self.w3ct + self.b3                               
        if mask is None:
            z = (h.reshape(B * n, self.H) @ self.w3ht).reshape(B, n, self.H) + cterm[:, None, :]
            return np.maximum(z, 0.0) @ self.w4 + self.b4
        bi, ji = np.nonzero(mask)                                         
        z = np.maximum(h[bi, ji] @ self.w3ht + cterm[bi], 0.0)
        out = np.full((B, n), -np.inf, dtype=np.float32)
        out[bi, ji] = z @ self.w4 + self.b4
        return out


class FastRLScheduler(Solver):
    def __init__(self, model_path, n_samples=1, mask_mode=None, seed=0, temperature=0.5,
                 verify=True):
        from sb3_contrib import MaskablePPO
        import rl.policy
        model = MaskablePPO.load(str(model_path), device="cpu")
        self.scorer = NumpyScorer.from_model(model)
        self.mask_mode = mask_mode or _read_mask_mode(model_path)
        self.n_samples, self.seed, self.temperature = max(int(n_samples), 1), seed, float(temperature)
        if verify:
            self._verify(model)

    def _verify(self, model, tol=1e-3):
        import torch as th
        rng = np.random.default_rng(0)
        P = model.observation_space["mask"].shape[0]
        jobs = rng.random((4, P, N_FEATURES)).astype(np.float32)
        ready = rng.random((4, P)) > 0.3
        ready[:, 0] = True
        with th.no_grad():
            ref = model.policy.features_extractor(
                {"jobs": th.as_tensor(jobs), "mask": th.as_tensor(ready.astype(np.float32))})[:, :P]
        mine = self.scorer.scores(jobs, ready)
        err = float(np.abs(ref.numpy()[ready] - mine[ready]).max())
        if err > tol:
            raise RuntimeError(f"numpy scorer disagrees with the torch model (max error {err:.2e})")

    def solve(self, instance: Instance) -> Schedule:
        t0 = time.perf_counter()
        B = self.n_samples
        sim = BatchSim(instance, B, self.mask_mode)
        rng = np.random.default_rng(self.seed)
        inv_t = 1.0 / max(self.temperature, 1e-6)
        while not sim.done():
            feats, ready, mask = sim.observe()
            logits = self.scorer.scores(feats, ready, mask)
            if B > 1:                                         
                u = rng.random((B - 1, instance.n_jobs))
                gumbel = -np.log(-np.log(np.clip(u, 1e-12, 1 - 1e-12)))
                logits = logits.astype(np.float64)
                logits[1:] = logits[1:] * inv_t + gumbel
            sim.step(np.where(mask, logits, -np.inf).argmax(1))
        best = int(sim.makespans().argmin())              
        name = "RL" if B == 1 else f"RL-best{B}"
        return sim.to_schedule(best, name, time.perf_counter() - t0)
