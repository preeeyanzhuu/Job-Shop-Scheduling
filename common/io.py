import json
from pathlib import Path
from .types import Instance, Schedule, ScheduledOp


def save_instance(instance: Instance, path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"name": instance.name, "n_jobs": instance.n_jobs,
                   "n_machines": instance.n_machines,
                   "machines": instance.machines, "durations": instance.durations}, f)


def load_instance(path) -> Instance:
    with open(path) as f:
        d = json.load(f)
    return Instance(d["name"], d["n_jobs"], d["n_machines"], d["machines"], d["durations"])


def save_schedule(schedule: Schedule, path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"method": schedule.method, "solve_time": schedule.solve_time,
                   "optimal": schedule.optimal,
                   "ops": [vars(o) for o in schedule.ops]}, f)


def load_schedule(path) -> Schedule:
    with open(path) as f:
        d = json.load(f)
    return Schedule([ScheduledOp(**o) for o in d["ops"]], d["method"],
                    d["solve_time"], d["optimal"])