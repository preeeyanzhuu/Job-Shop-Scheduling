import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from baselines.cpsat import CPSATScheduler
from baselines.rules import RuleScheduler
from baselines.hybrid import HybridScheduler
from common.generator import random_instance
from common.io import load_instance
from common.validate import validate_schedule
from evaluation.metrics import machine_idle_time
from evaluation.stubs import RandomScheduler

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "data" / "benchmarks"
RESULTS = ROOT / "results"

_RL_CACHE = {}


def get_solver(name, model_path=None):
    if name in ("SPT", "MWKR", "FIFO"):
        return RuleScheduler(name), name
    if name in ("RL", "RLSLOW"):
        if model_path and Path(model_path).exists():
            try:
                key = (str(model_path), name, 1)
                if key not in _RL_CACHE:                 
                    if name == "RL":                  
                        from rl.fast_agent import FastRLScheduler
                        _RL_CACHE[key] = FastRLScheduler(str(model_path))
                    else:                          
                        from rl.agent import RLScheduler
                        _RL_CACHE[key] = RLScheduler(str(model_path))
                return _RL_CACHE[key], ("RL" if name == "RL" else "RL(slow)")
            except ImportError as e:
                print(f"[warn] RL agent not available ({e}); using stub")
        return RandomScheduler(), "RL(stub)"  
    if name.startswith("CPSAT@"):
        limit = float(name.split("@")[1])
        return CPSATScheduler(limit), f"CPSAT@{limit:g}s"
    if name.startswith("HYBRID@"):
        limit = float(name.split("@")[1])
        rl_solver, rl_label = get_solver("RL", model_path)
        suffix = "(stub)" if rl_label != "RL" else ""
        return HybridScheduler(rl_solver, limit), f"HYBRID@{limit:g}s{suffix}"
    

    if name.startswith("RLBEST@"):
        n = int(name.split("@")[1])
        if model_path and Path(model_path).exists():
            key = (str(model_path), "RLBEST", n)
            if key not in _RL_CACHE:
                from rl.fast_agent import FastRLScheduler 
                _RL_CACHE[key] = FastRLScheduler(str(model_path), n_samples=n)
            return _RL_CACHE[key], f"RL-best{n}"
        return RandomScheduler(), "RL(stub)"
    raise ValueError(f"unknown method {name}")
    
def load_benchmarks(names=None):
    out = []
    for p in sorted(BENCH.glob("*.json")):
        if p.name == "best_known.json":
            continue
        inst = load_instance(p)
        if names is None or inst.name in names:
            out.append(inst)
    return out


def load_best_known():
    p = BENCH / "best_known.json"
    return json.loads(p.read_text()) if p.exists() else {}


def make_random(n, sizes, seed):
    rng = np.random.default_rng(seed)
    out = []
    for size in sizes.lower().split(","):
        J, M = map(int, size.split("x"))
        for i in range(n):
            inst = random_instance(J, M, rng)
            inst.name = f"rand{i}_{J}x{M}"
            out.append(inst)
    return out


def run(instances, methods, model_path=None, cpsat_limits=(1, 10, 60), hybrid_limits=(0.25,)):
    expanded = []
    for m in methods:
        if m == "CPSAT":
            expanded += [f"CPSAT@{l}" for l in cpsat_limits]
        elif m == "HYBRID":
            expanded += [f"HYBRID@{l}" for l in hybrid_limits]
        else:
            expanded.append(m)

    rows = []
    for inst in instances:
        for name in expanded:
            solver, label = get_solver(name, model_path)
            sch = solver.solve(inst)
            mk = validate_schedule(inst, sch)   
            rows.append(dict(instance=inst.name, n_jobs=inst.n_jobs, n_machines=inst.n_machines,
                             method=label, makespan=mk, solve_time=sch.solve_time,
                             optimal=sch.optimal, idle_time=machine_idle_time(inst, sch)))
            print(f"{inst.name:>14} {label:>10} makespan={mk:<6} time={sch.solve_time:.3f}s")

    df = pd.DataFrame(rows)
    known = load_best_known()
    ref = df.groupby("instance")["makespan"].transform("min")  
    df["best_known"] = [min(known.get(i, r), r) if i in known else r
                        for i, r in zip(df["instance"], ref)]
    df["gap"] = 100.0 * (df["makespan"] - df["best_known"]) / df["best_known"]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["ft", "random", "all"], default="ft")
    ap.add_argument("--names", default=None, help="comma list, e.g. ft06,ft10")
    ap.add_argument("--methods", default="SPT,MWKR,FIFO,RL,CPSAT")
    ap.add_argument("--cpsat-limits", default="1,10,60")
    ap.add_argument("--hybrid-limits", default="0.1,0.25,0.5", help="CP-SAT seconds AFTER the RL schedule")
    ap.add_argument("--n-random", type=int, default=10)
    ap.add_argument("--size", default="8x8", help="e.g. 10x10 or 10x10,15x15,20x15")
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--model", default=None, help="path to trained model (RL)")
    a = ap.parse_args()

    insts = []
    if a.set in ("ft", "all"):
        insts += load_benchmarks(a.names.split(",") if a.names else None)
    if a.set in ("random", "all"):
        insts += make_random(a.n_random, a.size, a.seed)

    df = run(insts, a.methods.split(","), a.model, [float(x) for x in a.cpsat_limits.split(",")],
         [float(x) for x in a.hybrid_limits.split(",")])
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"benchmark_{datetime.now():%Y%m%d_%H%M%S}.csv"
    df.to_csv(out, index=False)
    print("\nAverages per method:")
    print(df.groupby("method")[["gap", "solve_time", "idle_time"]].mean().round(2))
    print("\nSaved", out)


if __name__ == "__main__":
    main()