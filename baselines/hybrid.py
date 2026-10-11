from baselines.cpsat import CPSATScheduler
from common.types import Instance, Schedule, Solver


class HybridScheduler(Solver):
    def __init__(self, rl_solver: Solver, time_limit_seconds=0.25, workers=8):
        self.rl, self.limit, self.workers = rl_solver, time_limit_seconds, workers
        self.last_rl_makespan = None       

    def solve(self, instance: Instance) -> Schedule:
        start = self.rl.solve(instance)
        self.last_rl_makespan = start.makespan
        cp = CPSATScheduler(self.limit, hint=start, workers=self.workers).solve(instance)
        best = cp if cp.makespan <= start.makespan else start
        return Schedule(list(best.ops), "HYBRID", start.solve_time + cp.solve_time,
                        best is cp and cp.optimal)