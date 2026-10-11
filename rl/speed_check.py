import argparse
import time

import numpy as np

from common.generator import random_instance
from common.validate import validate_schedule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="models/ppo_large_gt_best.zip")
    ap.add_argument("--n", type=int, default=10, help="instances per size")
    ap.add_argument("--sizes", default="10x10,20x20,30x30")
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--skip-slow", action="store_true", help="do not run the old SB3 path")
    a = ap.parse_args()

    from rl.fast_agent import FastRLScheduler
    fast = FastRLScheduler(a.model)
    best = FastRLScheduler(a.model, n_samples=a.samples)
    slow = None
    if not a.skip_slow:
        from rl.agent import RLScheduler
        slow = RLScheduler(a.model)
    rng = np.random.default_rng(a.seed)
    warm = random_instance(8, 8, rng)
    fast.solve(warm); best.solve(warm)      
    print(f"model {a.model} | action rule: {fast.mask_mode} | best-of-N uses N={a.samples}")
    print(f"{'size':>6} | {'old ms':>8} {'fast ms':>8} {'speedup':>8} {'same mk':>8} | "
          f"{'greedy mk':>10} {'best-N mk':>10} {'gain %':>7} {'bestN ms':>9}")
    for size in a.sizes.split(","):
        J, M = map(int, size.split("x"))
        t_old, t_new, t_best, same, mk_g, mk_b = [], [], [], 0, [], []
        for _ in range(a.n):
            inst = random_instance(J, M, rng)
            g = fast.solve(inst)
            b = best.solve(inst)
            mg, mb = validate_schedule(inst, g), validate_schedule(inst, b)
            t_new.append(g.solve_time); t_best.append(b.solve_time); mk_g.append(mg); mk_b.append(mb)
            if slow:
                s = slow.solve(inst)
                t_old.append(s.solve_time)
                same += int(validate_schedule(inst, s) == mg)
        old = f"{np.mean(t_old) * 1000:8.0f}" if slow else f"{'-':>8}"
        spd = f"{np.mean(t_old) / np.mean(t_new):7.1f}x" if slow else f"{'-':>8}"
        sm = f"{same}/{a.n}" if slow else "-"
        gain = 100 * (np.mean(mk_g) - np.mean(mk_b)) / np.mean(mk_g)
        print(f"{size:>6} | {old} {np.mean(t_new) * 1000:8.0f} {spd:>8} {sm:>8} | "
              f"{np.mean(mk_g):10.1f} {np.mean(mk_b):10.1f} {gain:6.1f}% {np.mean(t_best) * 1000:9.0f}")


if __name__ == "__main__":
    main()
