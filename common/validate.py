from .types import Instance, Schedule


def validate_schedule(instance: Instance, schedule: Schedule) -> int:
    seen = {}
    for o in schedule.ops:
        key = (o.job, o.op)
        if key in seen:
            raise ValueError(f"operation {key} appears more than once")
        seen[key] = o

    for j in range(instance.n_jobs):
        for k in range(len(instance.machines[j])):
            if (j, k) not in seen:
                raise ValueError(f"operation (job {j}, op {k}) is missing")
    expected = sum(len(m) for m in instance.machines)
    if len(seen) != expected:
        raise ValueError(f"expected {expected} operations, got {len(seen)} (unknown ops present)")

    for (j, k), o in seen.items():
        if o.machine != instance.machines[j][k]:
            raise ValueError(f"(job {j}, op {k}) on machine {o.machine}, "
                             f"expected {instance.machines[j][k]}")

        if o.end - o.start != instance.durations[j][k]:
            raise ValueError(f"(job {j}, op {k}) has length {o.end - o.start}, "
                             f"expected {instance.durations[j][k]}")
        if o.start < 0:
            raise ValueError(f"(job {j}, op {k}) starts before time 0")
        if k > 0 and o.start < seen[(j, k - 1)].end:
            raise ValueError(f"job {j}: op {k} starts at {o.start} before op {k-1} "
                             f"ends at {seen[(j, k - 1)].end}")

    by_machine = {}
    for o in seen.values():
        by_machine.setdefault(o.machine, []).append(o)
    for m, lst in by_machine.items():
        lst.sort(key=lambda x: (x.start, x.end))
        for a, b in zip(lst, lst[1:]):
            if b.start < a.end:
                raise ValueError(f"machine {m}: (job {a.job}, op {a.op}) and "
                                 f"(job {b.job}, op {b.op}) overlap")
    return schedule.makespan


def makespan(schedule: Schedule) -> int:
    return schedule.makespan