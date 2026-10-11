from dataclasses import dataclass, field


@dataclass
class Instance:
    name: str
    n_jobs: int
    n_machines: int
    machines: list
    durations: list


@dataclass
class ScheduledOp:
    job: int
    op: int
    machine: int
    start: int
    end: int


@dataclass
class Schedule:
    ops: list = field(default_factory=list)
    method: str = ""
    solve_time: float = 0.0 
    optimal: bool = False

    @property
    def makespan(self) -> int:
        return max((o.end for o in self.ops), default=0)


class Solver:

    def solve(self, instance: Instance) -> Schedule:
        raise NotImplementedError