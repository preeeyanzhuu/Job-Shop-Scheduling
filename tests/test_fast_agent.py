from pathlib import Path

import numpy as np
import pytest

from common.generator import random_instance
from common.validate import validate_schedule

pytest.importorskip("torch")
pytest.importorskip("sb3_contrib")
MODEL = Path(__file__).resolve().parent.parent / "models" / "ppo_large_gt_best.zip"
pytestmark = pytest.mark.skipif(not MODEL.exists(), reason="trained model missing")


@pytest.fixture(scope="module")
def agents():
    from rl.agent import RLScheduler
    from rl.fast_agent import FastRLScheduler
    return RLScheduler(MODEL), FastRLScheduler(MODEL), FastRLScheduler(MODEL, n_samples=20)


def test_greedy_matches_original_agent(agents):
    slow, fast, _ = agents
    rng = np.random.default_rng(7)
    same = 0
    for _ in range(30):
        inst = random_instance(int(rng.integers(3, 20)), int(rng.integers(3, 15)), rng)
        a, b = slow.solve(inst), fast.solve(inst)
        validate_schedule(inst, b)
        same += validate_schedule(inst, a) == b.makespan
    assert same >= 29


def test_best_of_n_valid_never_worse_and_repeatable(agents):
    _, fast, best = agents
    rng = np.random.default_rng(8)
    for _ in range(10):
        inst = random_instance(int(rng.integers(4, 18)), int(rng.integers(4, 12)), rng)
        g, b1, b2 = fast.solve(inst), best.solve(inst), best.solve(inst)
        validate_schedule(inst, b1)
        assert b1.makespan <= g.makespan      
        assert b1.makespan == b2.makespan        
