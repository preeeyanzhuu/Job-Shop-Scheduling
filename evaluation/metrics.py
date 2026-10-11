from common.types import Instance, Schedule


def makespan_gap(makespan, best_known) -> float:
    return 100.0 * (makespan - best_known) / best_known


def _per_machine(instance, schedule):
    spans = {m: [] for m in range(instance.n_machines)}
    for o in schedule.ops:
        spans[o.machine].append((o.start, o.end))
    return spans


def machine_idle_time(instance: Instance, schedule: Schedule) -> int:
    total = 0
    for spans in _per_machine(instance, schedule).values():
        if spans:
            busy = sum(e - s for s, e in spans)
            total += max(e for _, e in spans) - min(s for s, _ in spans) - busy
    return total


def machine_utilisation(instance: Instance, schedule: Schedule) -> list:
    ms = schedule.makespan
    return [sum(e - s for s, e in spans) / ms if ms else 0.0
            for spans in _per_machine(instance, schedule).values()]