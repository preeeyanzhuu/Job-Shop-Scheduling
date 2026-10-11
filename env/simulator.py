"""Event-driven job shop simulator. Plain Python, no RL in here.

Action meaning: "pick a job; its next operation is placed as early as possible",
i.e. start = max(job_ready[j], machine_free[machine of that op]).
"""
from common.types import Instance, Schedule, ScheduledOp


class JobShopSimulator:
    def reset(self, instance: Instance):
        self.inst = instance
        n, m = instance.n_jobs, instance.n_machines
        self.next_op = [0] * n         
        self.job_ready = [0] * n           
        self.machine_free = [0] * m         
        self.remaining_work = [sum(d) for d in instance.durations]  
        self.remaining_load = [0] * m                     
        for j in range(n):
            for mach, d in zip(instance.machines[j], instance.durations[j]):
                self.remaining_load[mach] += d
        self.ops = []
        self.total_ops = sum(len(r) for r in instance.machines)
        return self
    def ready_jobs(self):
        return [j for j in range(self.inst.n_jobs)
                if self.next_op[j] < len(self.inst.machines[j])]

    def next_machine(self, j):
        return self.inst.machines[j][self.next_op[j]]

    def next_duration(self, j):
        return self.inst.durations[j][self.next_op[j]]

    def earliest_start(self, j):
        return max(self.job_ready[j], self.machine_free[self.next_machine(j)])

    def candidates(self):
        jobs = self.ready_jobs()
        t = min(self.earliest_start(j) for j in jobs)
        return [j for j in jobs if self.earliest_start(j) == t]

    def gt_jobs(self):
        jobs = self.ready_jobs()
        best = min(jobs, key=lambda j: (self.earliest_start(j) + self.next_duration(j), j))
        m = self.next_machine(best)
        ec = self.earliest_start(best) + self.next_duration(best)
        return [j for j in jobs
                if j == best or (self.next_machine(j) == m and self.earliest_start(j) < ec)]

    def done(self):
        return len(self.ops) == self.total_ops

    def makespan(self):
        return max((o.end for o in self.ops), default=0)

    def lower_bound(self):
        lb_jobs = max(self.job_ready[j] + self.remaining_work[j]
                      for j in range(self.inst.n_jobs))
        lb_mach = max(self.machine_free[m] + self.remaining_load[m]
                      for m in range(self.inst.n_machines))
        return max(lb_jobs, lb_mach)
    def step(self, job: int) -> bool:
        if not (0 <= job < self.inst.n_jobs) or self.next_op[job] >= len(self.inst.machines[job]):
            raise ValueError(f"job {job} has no operation left")
        k = self.next_op[job]
        m = self.inst.machines[job][k]
        d = self.inst.durations[job][k]
        start = max(self.job_ready[job], self.machine_free[m])
        end = start + d
        self.ops.append(ScheduledOp(job, k, m, start, end))
        self.job_ready[job] = end
        self.machine_free[m] = end
        self.remaining_work[job] -= d
        self.remaining_load[m] -= d
        self.next_op[job] += 1
        return self.done()

    def to_schedule(self, method="SIM", solve_time=0.0) -> Schedule:
        return Schedule(list(self.ops), method, solve_time, False)