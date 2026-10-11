import numpy as np
from baselines.rules import dispatch
from common.types import Instance, Schedule, Solver


class RandomScheduler(Solver):
    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)

    def solve(self, instance: Instance) -> Schedule:
        choose = lambda cands, info: int(self.rng.choice(cands))
        return dispatch(instance, choose, "RL")