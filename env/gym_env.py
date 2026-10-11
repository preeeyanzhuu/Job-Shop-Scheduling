import gymnasium as gym
import numpy as np
from gymnasium import spaces

from common.generator import random_instance, sample_size_range
from env.features import N_FEATURES, build_job_features
from env.simulator import JobShopSimulator

def sample_from_mix(rng, size_mix):
    w = np.array([m[2] for m in size_mix], dtype=float)
    k = int(rng.choice(len(size_mix), p=w / w.sum()))
    return random_instance(int(size_mix[k][0]), int(size_mix[k][1]), rng)

class JobShopEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, min_jobs=5, max_jobs=12, min_machines=4, max_machines=12,
                 pad_jobs=32, seed=None, size_mix=None, mask_mode="any"):
        super().__init__()
        self.size_range = (min_jobs, max_jobs, min_machines, max_machines)
        self.size_mix = size_mix       
        if mask_mode not in ("any", "gt"):
            raise ValueError("mask_mode must be 'any' or 'gt'")
        self.mask_mode = mask_mode           
        self.pad_jobs = pad_jobs
        self.sim = JobShopSimulator()
        self.action_space = spaces.Discrete(pad_jobs)
        self.observation_space = spaces.Dict({
            "jobs": spaces.Box(-10.0, 10.0, (pad_jobs, N_FEATURES), np.float32),
            "mask": spaces.Box(0.0, 1.0, (pad_jobs,), np.float32),
        })
        self._seed = seed
        self.lb0 = 1

    def _obs(self):
        jobs = np.zeros((self.pad_jobs, N_FEATURES), np.float32)
        n = self.sim.inst.n_jobs
        jobs[:n] = np.clip(build_job_features(self.sim), -10, 10)
        ready = np.zeros(self.pad_jobs, dtype=np.float32)
        ready[self.sim.ready_jobs()] = 1.0
        return {"jobs": jobs, "mask": ready}

    def action_masks(self) -> np.ndarray:
        mask = np.zeros(self.pad_jobs, dtype=bool)
        mask[self.sim.gt_jobs() if self.mask_mode == "gt" else self.sim.ready_jobs()] = True
        return mask

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed if seed is not None else self._seed)
        self._seed = None                         
        if options and "instance" in options:
            inst = options["instance"]  
        else:
            inst = (sample_from_mix(self.np_random, self.size_mix) if self.size_mix
            else sample_size_range(self.np_random, *self.size_range))
        if inst.n_jobs > self.pad_jobs:
            raise ValueError(f"instance has {inst.n_jobs} jobs but pad_jobs={self.pad_jobs}")
        self.sim.reset(inst)
        self.lb0 = max(self.sim.lower_bound(), 1)
        return self._obs(), {"n_jobs": inst.n_jobs, "n_machines": inst.n_machines}

    def step(self, action):
        action = int(action)
        if not self.action_masks()[action]:
            raise ValueError(f"invalid action {action} (job has no operation left)")
        before = self.sim.lower_bound()
        done = self.sim.step(action)
        reward = -(self.sim.lower_bound() - before) / self.lb0
        info = {}
        if done:
            info = {"makespan": self.sim.makespan(), "n_jobs": self.sim.inst.n_jobs,
                    "n_machines": self.sim.inst.n_machines, "lb0": self.lb0}
        return self._obs(), reward, done, False, info