import numpy as np
import pytest
from common.types import Instance
from common.generator import random_instance
from common.validate import validate_schedule
from env.simulator import JobShopSimulator


def tiny():
    return Instance("tiny3", 3, 3,
                    [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
                    [[3, 2, 2], [2, 1, 4], [4, 3, 1]])


def run_spt(inst):
    sim = JobShopSimulator().reset(inst)
    while not sim.done():
        j = min(sim.candidates(), key=lambda j: (sim.next_duration(j), j))
        sim.step(j)
    return sim


def test_hand_checked_3x3():
    sim = JobShopSimulator().reset(tiny())
    for j in [0, 1, 2, 0, 1, 2, 0, 1, 2]:   
        sim.step(j)
    assert sim.done() and sim.makespan() == 11
    got = {(o.job, o.op): (o.start, o.end) for o in sim.ops}
    assert got[(0, 1)] == (3, 5)       
    assert got[(1, 1)] == (4, 5)           
    assert got[(1, 2)] == (7, 11)     
    assert validate_schedule(tiny(), sim.to_schedule()) == 11


def test_action_mask_matches_remaining_ops():
    sim = JobShopSimulator().reset(tiny())
    assert sim.ready_jobs() == [0, 1, 2]
    for _ in range(3):
        sim.step(0)                             
    assert sim.ready_jobs() == [1, 2]
    with pytest.raises(ValueError):
        sim.step(0)


def test_lower_bound_properties():
    rng = np.random.default_rng(3)
    for _ in range(30):
        inst = random_instance(int(rng.integers(2, 9)), int(rng.integers(2, 7)), rng)
        sim = JobShopSimulator().reset(inst)
        lbs = [sim.lower_bound()]
        while not sim.done():
            sim.step(int(rng.choice(sim.ready_jobs())))
            lbs.append(sim.lower_bound())
        assert all(a <= b for a, b in zip(lbs, lbs[1:]))
        assert max(lbs) <= sim.makespan()                
        assert lbs[-1] == sim.makespan()        


def test_random_policy_always_valid():
    rng = np.random.default_rng(5)
    for _ in range(50):
        inst = random_instance(int(rng.integers(2, 10)), int(rng.integers(2, 8)), rng)
        sim = JobShopSimulator().reset(inst)
        while not sim.done():
            sim.step(int(rng.choice(sim.ready_jobs())))
        validate_schedule(inst, sim.to_schedule())


def test_spt_in_simulator_valid_on_50_random():
    rng = np.random.default_rng(11)
    for _ in range(50):
        inst = random_instance(int(rng.integers(2, 10)), int(rng.integers(2, 8)), rng)
        validate_schedule(inst, run_spt(inst).to_schedule())