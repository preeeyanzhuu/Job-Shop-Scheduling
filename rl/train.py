import argparse
import json
import time
from pathlib import Path

import numpy as np
import yaml
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv

from common.generator import sample_size_range
from env.gym_env import JobShopEnv, sample_from_mix
from env.simulator import JobShopSimulator
from rl.agent import greedy_schedule
from rl.policy import JobScorerPolicy, JobScoringExtractor

ROOT = Path(__file__).resolve().parent.parent


def rule_makespan(inst, rule):
    sim = JobShopSimulator().reset(inst)
    keys = {"SPT": lambda j: (sim.next_duration(j), j),
            "MWKR": lambda j: (-sim.remaining_work[j], j)}
    while not sim.done():
        sim.step(min(sim.candidates(), key=keys[rule]))
    return sim.makespan()


def sample_val_instance(rng, cfg):
    if cfg.get("size_mix"):
        return sample_from_mix(rng, cfg["size_mix"])
    return sample_size_range(rng, cfg["min_jobs"], cfg["max_jobs"],
                             cfg["min_machines"], cfg["max_machines"])


class ValidationCallback(BaseCallback):

    def __init__(self, val, spt_avg, mwkr_avg, pad_jobs, eval_freq, best_path,
                 best_rule_each=None, mask_mode="any"):
        super().__init__()
        self.val, self.spt, self.mwkr, self.eval_freq = val, spt_avg, mwkr_avg, eval_freq
        self.rule_each = np.asarray(best_rule_each, dtype=float) 
        self.env = JobShopEnv(pad_jobs=pad_jobs, mask_mode=mask_mode)
        self.best, self.best_ratio = float("inf"), float("inf")
        self.best_path, self.last, self.t0 = best_path, 0, time.time()

    def _on_step(self) -> bool:
        if self.num_timesteps - self.last >= self.eval_freq:
            self.last = self.num_timesteps
            self.report()
        return True

    def report(self):
        mk = np.array([greedy_schedule(self.model, self.env, i).makespan for i in self.val], float)
        avg = float(mk.mean())
        ratio = float((mk / self.rule_each).mean())   
        tag = ""
        if ratio < self.best_ratio:           
            self.best, self.best_ratio = avg, ratio
            self.model.save(self.best_path)
            tag = "  (new best saved)"
        print(f"steps {self.num_timesteps:>9} | agent {avg:8.1f} | SPT {self.spt:8.1f} | "
              f"MWKR {self.mwkr:8.1f} | agent/best-rule {avg / min(self.spt, self.mwkr):5.3f} | "
              f"ratio {ratio:5.3f} | "
              f"{(time.time() - self.t0) / 60:5.1f} min{tag}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="rl/configs/ppo.yaml")
    ap.add_argument("--timesteps", type=int, default=None, help="override total_timesteps")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / a.config))
    if a.timesteps:
        cfg["total_timesteps"] = a.timesteps

    sizes = (cfg.get("min_jobs", 5), cfg.get("max_jobs", 12),
             cfg.get("min_machines", 4), cfg.get("max_machines", 12))
    mix = cfg.get("size_mix")
    mask_mode = cfg.get("mask_mode", "any")           
    make = lambda k: (lambda: JobShopEnv(*sizes, pad_jobs=cfg["pad_jobs"], seed=cfg["seed"] + k,
                                         size_mix=mix, mask_mode=mask_mode))
    env = DummyVecEnv([make(k) for k in range(cfg["n_envs"])])

    rng = np.random.default_rng(cfg["val_seed"])    
    val = [sample_val_instance(rng, cfg) for _ in range(cfg["n_val"])]
    spt = float(np.mean([rule_makespan(i, "SPT") for i in val]))
    mwkr = float(np.mean([rule_makespan(i, "MWKR") for i in val]))
    rule_each = [min(rule_makespan(i, "SPT"), rule_makespan(i, "MWKR")) for i in val]
    print(f"validation: {len(val)} instances | SPT avg {spt:.1f} | MWKR avg {mwkr:.1f} | "
          f"action rule: {mask_mode}")

    if cfg.get("init_from"):                            
        print("fine-tuning from", cfg["init_from"])
        model = MaskablePPO.load(str(ROOT / cfg["init_from"]), env=env, device="cpu",
                                 learning_rate=cfg["learning_rate"], ent_coef=cfg["ent_coef"])
    else:
        model = MaskablePPO(
            JobScorerPolicy, env, seed=cfg["seed"], verbose=0, device="cpu",
            learning_rate=cfg["learning_rate"], n_steps=cfg["n_steps"], batch_size=cfg["batch_size"],
            n_epochs=cfg["n_epochs"], gamma=cfg["gamma"], gae_lambda=cfg["gae_lambda"],
            ent_coef=cfg["ent_coef"],
            policy_kwargs=dict(features_extractor_class=JobScoringExtractor,
                               features_extractor_kwargs=dict(hidden=cfg["hidden"])))

    save = ROOT / cfg["save_path"]
    save.parent.mkdir(parents=True, exist_ok=True)
    best_zip = save.with_name(save.stem + "_best.zip")
    for z in (save, best_zip):               
        z.with_suffix(".json").write_text(json.dumps({"mask_mode": mask_mode}))
    cb = ValidationCallback(val, spt, mwkr, cfg["pad_jobs"], cfg["eval_freq"], str(best_zip),
                            best_rule_each=rule_each, mask_mode=mask_mode)
    t0 = time.time()
    model.learn(total_timesteps=cfg["total_timesteps"], callback=cb, reset_num_timesteps=False)
    minutes = (time.time() - t0) / 60
    cb.report()
    model.save(save)
    print(f"\nTraining time: {minutes:.1f} min for {cfg['total_timesteps']} steps "
          f"({cfg['total_timesteps'] / (minutes * 60):.0f} steps/s). Saved {save}")
    print(f"Best validation average: agent {cb.best:.1f} vs SPT {spt:.1f}, MWKR {mwkr:.1f}")
    print("Beats SPT:", cb.best < spt, "| Beats best rule:", cb.best < min(spt, mwkr))
    print("Note the training time for the deck. Best checkpoint:", cb.best_path)


if __name__ == "__main__":
    main()