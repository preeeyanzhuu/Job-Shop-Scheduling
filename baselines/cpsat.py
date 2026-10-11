import time
from ortools.sat.python import cp_model
from common.types import Instance, Schedule, ScheduledOp, Solver


class CPSATScheduler(Solver):
    def __init__(self, time_limit_seconds=10.0, hint: Schedule = None, workers=8):
        self.time_limit = time_limit_seconds
        self.hint = hint
        self.workers = workers

    def solve(self, instance: Instance) -> Schedule:
        t0 = time.perf_counter()
        model = cp_model.CpModel()
        horizon = sum(sum(d) for d in instance.durations)

        starts, ends = {}, {}
        by_machine = {m: [] for m in range(instance.n_machines)}
        for j in range(instance.n_jobs):
            for k, (m, d) in enumerate(zip(instance.machines[j], instance.durations[j])):
                s = model.new_int_var(0, horizon, f"s_{j}_{k}")
                e = model.new_int_var(0, horizon, f"e_{j}_{k}")
                iv = model.new_interval_var(s, d, e, f"iv_{j}_{k}")
                starts[j, k], ends[j, k] = s, e
                by_machine[m].append(iv)
                if k > 0:                   
                    model.add(s >= ends[j, k - 1])

        for ivs in by_machine.values():            
            model.add_no_overlap(ivs)

        makespan = model.new_int_var(0, horizon, "makespan")
        model.add_max_equality(
            makespan, [ends[j, len(instance.machines[j]) - 1] for j in range(instance.n_jobs)])
        model.minimize(makespan)

        if self.hint is not None:           
            for o in self.hint.ops:
                model.add_hint(starts[o.job, o.op], o.start)
                model.add_hint(ends[o.job, o.op], o.end)
            model.add_hint(makespan, self.hint.makespan)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = float(self.time_limit)
        solver.parameters.num_workers = self.workers
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):

            from baselines.rules import RuleScheduler
            print(f"[warn] CP-SAT found no solution in {self.time_limit}s on {instance.name}; "
                  f"using best rule schedule")
            fb = min((RuleScheduler(n).solve(instance) for n in ("SPT", "MWKR", "FIFO")),
                     key=lambda sc: sc.makespan)
            return Schedule(fb.ops, "CPSAT(fallback)", time.perf_counter() - t0, False)

        ops = []
        for j in range(instance.n_jobs):
            for k in range(len(instance.machines[j])):
                s = solver.value(starts[j, k])
                ops.append(ScheduledOp(j, k, instance.machines[j][k], s,
                                       s + instance.durations[j][k]))
        return Schedule(ops, "CPSAT", time.perf_counter() - t0, status == cp_model.OPTIMAL)