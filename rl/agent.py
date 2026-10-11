import json
import time
from pathlib import Path

import numpy as np

from common.types import Instance, Schedule, Solver
from env.gym_env import JobShopEnv


def read_mask_mode(model_path) -> str:
    side = Path(model_path).with_suffix(".json")
    if side.exists():
        return json.loads(side.read_text()).get("mask_mode", "any")
    return "any"


def _run(model, env: JobShopEnv, instance: Instance, deterministic: bool):
    obs, _ = env.reset(options={"instance": instance})
    done = False
    while not done:
        action, _ = model.predict(obs, action_masks=env.action_masks(), deterministic=deterministic)
        obs, _, done, _, _ = env.step(int(np.asarray(action).reshape(-1)[0]))
    return env.sim.to_schedule()


def greedy_schedule(model, env: JobShopEnv, instance: Instance, method="RL") -> Schedule:
    t0 = time.perf_counter()
    sch = _run(model, env, instance, deterministic=True)
    sch.method, sch.solve_time = method, time.perf_counter() - t0
    return sch


def best_of_n_schedule(model, env: JobShopEnv, instance: Instance, n: int,
                       method="RL", seed=0) -> Schedule:
    import torch
    t0 = time.perf_counter()
    best = _run(model, env, instance, deterministic=True)
    torch.manual_seed(seed)                  
    for _ in range(max(n - 1, 0)):
        cand = _run(model, env, instance, deterministic=False)
        if cand.makespan < best.makespan:
            best = cand
    best.method, best.solve_time = method, time.perf_counter() - t0
    return best


class RLScheduler(Solver):
    def __init__(self, model_path, device="cpu", n_samples=1, mask_mode=None, seed=0):
        from sb3_contrib import MaskablePPO
        import rl.policy  
        self.model = MaskablePPO.load(str(model_path), device=device)
        self.mask_mode = mask_mode or read_mask_mode(model_path)
        self.n_samples, self.seed = int(n_samples), seed
        self.env = JobShopEnv(pad_jobs=self.model.observation_space["mask"].shape[0],
                              mask_mode=self.mask_mode)

    def solve(self, instance: Instance) -> Schedule:
        if self.n_samples <= 1:
            return greedy_schedule(self.model, self.env, instance, "RL")
        return best_of_n_schedule(self.model, self.env, instance, self.n_samples,
                                  f"RL-best{self.n_samples}", self.seed)