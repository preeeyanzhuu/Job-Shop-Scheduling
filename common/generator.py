import numpy as np
from .types import Instance


def random_instance(n_jobs, n_machines, rng, low=1, high=99) -> Instance:
    machines = [[int(m) for m in rng.permutation(n_machines)] for _ in range(n_jobs)]
    durations = [[int(d) for d in rng.integers(low, high + 1, size=n_machines)]
                 for _ in range(n_jobs)]
    return Instance(f"rand_{n_jobs}x{n_machines}", n_jobs, n_machines, machines, durations)


def sample_size_range(rng, min_jobs, max_jobs, min_machines, max_machines,
                      low=1, high=99) -> Instance:
    n_jobs = int(rng.integers(min_jobs, max_jobs + 1))
    n_machines = int(rng.integers(min_machines, max_machines + 1))
    return random_instance(n_jobs, n_machines, rng, low, high)