import numpy as np
import pytest

from common.generator import random_instance
from common.validate import validate_schedule
from env.features import build_job_features
from env.simulator import JobShopSimulator
from rl.fast_sim import BatchSim


def _instances(seed, count=25):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        yield random_instance(int(rng.integers(2, 14)), int(rng.integers(2, 10)), rng), rng


@pytest.mark.parametrize("mode", ["gt", "any"])
def test_features_and_masks_match_reference_every_step(mode):
    for inst, rng in _instances(1):
        ref = JobShopSimulator().reset(inst)
        fast = BatchSim(inst, 1, mode)
        while not ref.done():
            feats, ready, mask = fast.observe()
            np.testing.assert_array_equal(feats[0], np.clip(build_job_features(ref), -10, 10))
            want_ready = np.zeros(inst.n_jobs, bool)
            want_ready[ref.ready_jobs()] = True
            np.testing.assert_array_equal(ready[0], want_ready)
            want_mask = np.zeros(inst.n_jobs, bool)
            want_mask[ref.gt_jobs() if mode == "gt" else ref.ready_jobs()] = True
            np.testing.assert_array_equal(mask[0], want_mask)
            j = int(rng.choice(np.flatnonzero(want_mask)))
            ref.step(j)
            fast.step(np.array([j]))
        assert fast.done()
        assert fast.makespans()[0] == ref.makespan()
        a = validate_schedule(inst, fast.to_schedule(0))
        b = validate_schedule(inst, ref.to_schedule())
        assert a == b


def test_batch_rollouts_are_independent():
    for inst, rng in _instances(2, count=10):
        B = 4
        batch = BatchSim(inst, B, "gt")
        singles = [BatchSim(inst, 1, "gt") for _ in range(B)]
        while not batch.done():
            _, _, mask = batch.observe()
            acts = np.array([int(rng.choice(np.flatnonzero(mask[b]))) for b in range(B)])
            batch.step(acts)
            for b in range(B):
                _, _, m1 = singles[b].observe()
                assert m1[0, acts[b]]                      
                singles[b].step(acts[b:b + 1])
        for b in range(B):
            assert batch.makespans()[b] == singles[b].makespans()[0]
            validate_schedule(inst, batch.to_schedule(b))
