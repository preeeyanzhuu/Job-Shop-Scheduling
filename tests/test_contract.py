import copy
import numpy as np
import pytest
from common.types import Instance, Schedule, ScheduledOp as S
from common.validate import validate_schedule
from common.generator import random_instance, sample_size_range
from common.io import save_instance, load_instance, save_schedule, load_schedule


def tiny():
    inst = Instance("tiny3", 3, 3,
                    [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
                    [[3, 2, 2], [2, 1, 4], [4, 3, 1]])
    ops = [S(0, 0, 0, 0, 3), S(0, 1, 1, 3, 5), S(0, 2, 2, 5, 7),
           S(1, 0, 1, 0, 2), S(1, 1, 2, 4, 5), S(1, 2, 0, 7, 11),
           S(2, 0, 2, 0, 4), S(2, 1, 0, 4, 7), S(2, 2, 1, 7, 8)]
    return inst, Schedule(ops, "hand")


def test_valid_schedule():
    inst, sch = tiny()
    assert validate_schedule(inst, sch) == 11


def _mutate(sch, job, op, **kw):
    sch = copy.deepcopy(sch)
    for o in sch.ops:
        if (o.job, o.op) == (job, op):
            for k, v in kw.items():
                setattr(o, k, v)
    return sch


def test_broken_schedules():
    inst, sch = tiny()
    with pytest.raises(ValueError):           
        validate_schedule(inst, _mutate(sch, 2, 1, start=2, end=5))
    with pytest.raises(ValueError):               
        validate_schedule(inst, _mutate(sch, 0, 1, start=1, end=3))
    with pytest.raises(ValueError):                
        validate_schedule(inst, Schedule(sch.ops[:-1]))
    with pytest.raises(ValueError):          
        validate_schedule(inst, _mutate(sch, 0, 0, end=4))
    with pytest.raises(ValueError):               
        validate_schedule(inst, _mutate(sch, 0, 0, machine=1))
    with pytest.raises(ValueError):                       
        validate_schedule(inst, Schedule(sch.ops + [sch.ops[0]]))


def test_generator_reproducible():
    a = random_instance(5, 4, np.random.default_rng(7))
    b = random_instance(5, 4, np.random.default_rng(7))
    assert a == b
    for row in a.machines:
        assert sorted(row) == list(range(4))
    assert all(1 <= d <= 99 for r in a.durations for d in r)


def test_sample_size_range():
    inst = sample_size_range(np.random.default_rng(0), 4, 8, 3, 5)
    assert 4 <= inst.n_jobs <= 8 and 3 <= inst.n_machines <= 5


def test_io_roundtrip(tmp_path):
    inst, sch = tiny()
    save_instance(inst, tmp_path / "i.json")
    assert load_instance(tmp_path / "i.json") == inst
    save_schedule(sch, tmp_path / "s.json")
    assert load_schedule(tmp_path / "s.json") == sch


    

def test_spt_cross_check_simulator_vs_rules():
    from baselines.rules import RuleScheduler
    from tests.test_env import run_spt
    rng = np.random.default_rng(2024)
    for _ in range(50):
        inst = random_instance(int(rng.integers(2, 11)), int(rng.integers(2, 8)), rng)
        a = validate_schedule(inst, run_spt(inst).to_schedule())
        b = validate_schedule(inst, RuleScheduler("SPT").solve(inst))
        assert a == b