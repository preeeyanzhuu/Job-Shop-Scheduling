from pathlib import Path
import numpy as np
import pytest
from common.io import load_instance
from common.generator import random_instance
from common.validate import validate_schedule
from baselines.rules import RuleScheduler
from baselines.cpsat import CPSATScheduler

BENCH = Path(__file__).resolve().parent.parent / "data" / "benchmarks"


def need(name):
    p = BENCH / f"{name}.json"
    if not p.exists():
        pytest.skip(f"{p.name} missing - run convert_orlib.py")
    return load_instance(p)


def test_cpsat_ft06():
    inst = need("ft06")
    s = CPSATScheduler(10).solve(inst)
    assert validate_schedule(inst, s) == 55 and s.optimal


def test_cpsat_ft10():
    inst = need("ft10")
    s = CPSATScheduler(180).solve(inst)
    assert validate_schedule(inst, s) == 930


def test_cpsat_ft20():
    inst = need("ft20")
    s = CPSATScheduler(180).solve(inst)
    assert validate_schedule(inst, s) == 1165


@pytest.mark.parametrize("rule", ["SPT", "MWKR", "FIFO"])
def test_rules_valid_on_random(rule):
    rng = np.random.default_rng(1)
    for _ in range(50):
        inst = random_instance(int(rng.integers(3, 9)), int(rng.integers(3, 7)), rng)
        validate_schedule(inst, RuleScheduler(rule).solve(inst))


def test_hint_not_worse():
    inst = need("ft06")
    plain = CPSATScheduler(5).solve(inst)
    hinted = CPSATScheduler(5, hint=RuleScheduler("SPT").solve(inst)).solve(inst)
    assert validate_schedule(inst, hinted) <= validate_schedule(inst, plain)