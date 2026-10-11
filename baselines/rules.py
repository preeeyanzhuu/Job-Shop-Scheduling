import time
from common.types import Instance, Schedule, ScheduledOp, Solver

def dispatch(instance: Instance, choose, method: str) -> Schedule:
    t0 = time.perf_counter()
    n = instance.n_jobs
    nxt = [0] * n
    job_ready = [0] * n
    mach_free = [0] * instance.n_machines
    remaining = [sum(d) for d in instance.durations]
    total = sum(len(m) for m in instance.machines)
    ops = []
    info = dict(instance=instance, nxt=nxt, job_ready=job_ready, remaining=remaining)

    while len(ops) < total:
        est = {}
        for j in range(n):
            if nxt[j] < len(instance.machines[j]):
                m = instance.machines[j][nxt[j]]
                est[j] = max(job_ready[j], mach_free[m])
        t = min(est.values())
        cands = [j for j in sorted(est) if est[j] == t]
        j = choose(cands, info)
        k = nxt[j]
        m = instance.machines[j][k]
        d = instance.durations[j][k]
        ops.append(ScheduledOp(j, k, m, t, t + d))
        mach_free[m] = t + d
        job_ready[j] = t + d
        remaining[j] -= d
        nxt[j] += 1

    return Schedule(ops, method, time.perf_counter() - t0, False)


def _spt(cands, info):
    inst, nxt = info["instance"], info["nxt"]
    return min(cands, key=lambda j: (inst.durations[j][nxt[j]], j))


def _mwkr(cands, info):
    return min(cands, key=lambda j: (-info["remaining"][j], j))


def _fifo(cands, info):
    return min(cands, key=lambda j: (info["job_ready"][j], j))


RULES = {"SPT": _spt, "MWKR": _mwkr, "FIFO": _fifo}


class RuleScheduler(Solver):
    def __init__(self, rule_name: str):
        if rule_name not in RULES:
            raise ValueError(f"unknown rule {rule_name}; choose from {list(RULES)}")
        self.rule_name = rule_name

    def solve(self, instance: Instance) -> Schedule:
        return dispatch(instance, RULES[self.rule_name], self.rule_name)