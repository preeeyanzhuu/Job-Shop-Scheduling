# Instant Factory Scheduling with Reinforcement Learning

**Replacing a slow search loop with a learned policy for job-shop scheduling.**

A reinforcement-learning agent (MaskablePPO) learns to build job-shop schedules in a fraction of a second. It is benchmarked head-to-head against classical dispatching rules and Google OR-Tools CP-SAT, and combined with CP-SAT in a hybrid that warm-starts the solver with the learned schedule.

Built for the IEEE hackathon, **Track 03.2: The Learned Loop, From Search to Learning**.


---

## Table of contents

1. [The problem](#the-problem)
2. [Our approach](#our-approach)
3. [Key results](#key-results)
4. [How it works](#how-it-works)
5. [Project structure](#project-structure)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Models](#models)
9. [Tests](#tests)
10. [Honest limitations](#honest-limitations)
11. [Future work](#future-work)
12. [Team](#team)
13. [References and credits](#references-and-credits)

---

## The problem

In the **job-shop scheduling problem (JSP)**, a set of jobs must be processed on a set of machines. Each job is a fixed sequence of operations, each needing a particular machine for a given time. A machine handles one operation at a time, and a job's operations must run in order. The goal is to minimise the **makespan**, the time at which the last operation finishes.

JSP is NP-hard. Exact solvers such as CP-SAT find excellent schedules but search from scratch for every new problem, so they become slow as factories grow. Simple dispatching rules (SPT, MWKR, FIFO) are instant but leave a lot of quality on the table.

The track asks for exactly this trade-off to be attacked: take a slow, search-heavy problem, replace or speed up the loop with a learned model, and prove the result against a classical baseline.

## Our approach

| Component | What it does |
|---|---|
| **Simulator** | Builds a schedule one decision at a time. Each decision picks a job, and its next operation is placed as early as possible. |
| **Giffler-Thompson mask** | At each step, only jobs that genuinely compete for the earliest-finishing machine can be chosen. Every schedule built this way is *active*, and the set of active schedules always contains an optimal one. |
| **RL policy (MaskablePPO)** | A small shared network scores every allowed job; PPO trains it from simulated rewards on millions of random instances. |
| **Fast inference** | A batched numpy simulator and a numpy copy of the network, verified against the torch model. No GPU, no API, no torch needed at solve time. |
| **RL-best20** | Builds 20 schedules at once (1 greedy and 19 sampled) and keeps the best. |
| **Hybrid** | The RL schedule is given to CP-SAT as a warm-start hint, and CP-SAT refines it. The better of the two is returned, so the hybrid is never worse than RL alone. |
| **Baselines** | SPT, MWKR, FIFO rules, and CP-SAT with time limits from 0.25 s to 60 s. |

## Key results

Evaluated on **60 random instances**: 20 each of 20x20, 30x20 and 30x30 (jobs x machines), durations uniform in 1 to 99. All 15 methods solve the same instances, and every schedule is validated before it counts.

The gap is measured against the **best makespan found by any method on that instance**. On these instances that reference is CP-SAT at 60 s, so CP-SAT@60s is about 0% by construction. It is not a proven optimum (only 1 of 60 instances was proven optimal).

| Method | Avg gap | Avg time per instance |
|---|---:|---:|
| CP-SAT, 60 s (reference) | 0.05% | 59.7 s |
| Hybrid, 10 s | 3.35% | 10.2 s |
| CP-SAT, 10 s | 4.14% | 10.1 s |
| Hybrid, 5 s | 5.20% | 5.2 s |
| CP-SAT, 5 s | 6.13% | 5.1 s |
| **RL-best20** | **9.91%** | **0.50 s** |
| Hybrid, 1 s | 10.34% | 1.2 s |
| Hybrid, 0.5 s | 11.27% | 0.7 s |
| CP-SAT, 1 s | 12.11% | 1.04 s |
| **RL (greedy)** | **12.65%** | **0.12 s** |
| CP-SAT, 0.5 s | 14.20% | 0.56 s |
| CP-SAT, 0.25 s | 15.78% | 0.30 s |
| MWKR | 17.57% | 0.01 s |
| SPT | 25.33% | 0.01 s |
| FIFO | 26.36% | 0.01 s |


### What the results show

- **RL beats every dispatching rule.** 12.6% gap against 17.6% (MWKR), 25.3% (SPT) and 26.4% (FIFO), in about a tenth of a second.
- **RL wins at small time budgets.** RL-best20 (0.5 s) beats CP-SAT at 1 s on 47 of 60 instances and CP-SAT at 0.5 s on 55 of 60. Greedy RL (0.12 s) beats CP-SAT at 0.25 s on 49 of 60.
- **RL's advantage grows with problem size.** Greedy RL against CP-SAT at 1 s wins 3, 12 and 17 of 20 instances on 20x20, 30x20 and 30x30 respectively. CP-SAT slows as problems grow; the learned policy barely does.
- **The hybrid gives a modest extra gain.** At equal total time it beats plain CP-SAT on about 38 to 39 of 60 instances at 5 s and 10 s (3.35% against 4.14% at 10 s). It is never worse than RL alone.
- **Beyond about 5 seconds, search wins.** CP-SAT and the hybrid are better, and CP-SAT at 60 s beats everything. RL is a speed and quality trade-off, not a replacement for long solver runs.

Per-size gap (%) for the main methods:

| Size | RL | RL-best20 | CP-SAT 1 s | CP-SAT 5 s | CP-SAT 10 s | Hybrid 10 s |
|---|---:|---:|---:|---:|---:|---:|
| 20x20 | 14.2 | 10.3 | 10.1 | 3.6 | 2.3 | 1.7 |
| 30x20 | 13.5 | 11.0 | 13.0 | 7.5 | 5.0 | 4.2 |
| 30x30 | 10.3 | 8.5 | 13.2 | 7.3 | 5.1 | 4.2 |

Full tables (wins, head-to-head, hybrid versus CP-SAT at similar time) are in `results/report_benchmark_20261009_214428.md`.

## How it works

### Training flow

```
random instance generator (new instance every episode)
        |
        v
+------------------ ENVIRONMENT (env/) ------------------+
|  1. build 10 features per job                           |
|  2. Giffler-Thompson mask: allowed jobs only            |
|  3. place the chosen job's next operation, as early     |
|     as possible                                         |
|  4. reward = minus the rise in the lower bound          |
+----------+----------------------------------^-----------+
           | features + mask                  | job + reward
           v                                  |
+------------------ POLICY NETWORK (rl/policy.py) --------+
|  scores every job; masked jobs become -infinity         |
|  one allowed job is sampled; a critic estimates value   |
+----------+----------------------------------------------+
           v
+------------------ PPO (MaskablePPO) --------------------+
|  512 steps x 4 environments, then 10 update epochs,     |
|  batch size 256, clipped updates                        |
+----------+----------------------------------------------+
           v
   validation every 50,000 steps -> save "_best" checkpoint
```

### Solving a new instance

```
new instance -> fast batched simulator (rl/fast_sim.py)
                  features + Giffler-Thompson mask
                          |
                          v
                numpy copy of the trained network scores allowed jobs
                          |
                          v
            greedy (RL)  or  20 rollouts, keep best (RL-best20)
                          |
                          v
                   finished schedule  --> validate
                          |
                          v  (optional)
              CP-SAT refines it, using it as a hint (Hybrid)
```

PPO is only used for training. At solve time only the trained network runs.

### Features

Each job with work left is described by 10 numbers, all normalised by the current lower bound so that instances of different sizes look alike:

1. remaining work / lower bound
2. remaining operations / number of machines
3. next operation duration / lower bound
4. (earliest start - now) / lower bound
5. (machine busy-until - now) / lower bound
6. (job ready - now) / lower bound
7. remaining load of the next machine / lower bound
8. next duration / largest next duration among candidates
9. remaining work / largest remaining work among candidates
10. is the job a candidate to start right now (0 or 1)

### Policy network

- A shared row network (10 -> 64 -> 64) embeds every job.
- A context vector is the mean of the embeddings of the allowed jobs.
- A scoring network takes each job's embedding together with the context and outputs one score per job.
- A separate critic network estimates the state value from the context.
- Because the same network scores every job, **one model handles any instance size up to 32 jobs**.

### Reward

The reward at each step is the negative increase in the schedule's lower bound, divided by the starting lower bound. Summed over an episode, it measures how far the final makespan ends above the initial bound, so maximising it minimises makespan.

### Giffler-Thompson action restriction

At each step:

1. Find the pending operation that could **finish earliest**, and note its machine.
2. Keep only the jobs whose next operation is on that machine and **could start before that earliest finish**.

Choosing among only these jobs always produces an active schedule. The restriction is applied in `env/simulator.py` (`gt_jobs`), in `env/gym_env.py` (`action_masks`) and in `rl/fast_sim.py` (`BatchSim.observe`). Each model records its mask mode in a small `.json` file next to it (for example `models/ppo_gt_best.json`), and the solver reads it automatically. A model must be run with the same mask it was trained with.

### Training curriculum

Models are trained in stages, each fine-tuning the previous one with a lower learning rate:

| Stage | Config | Instance sizes |
|---|---|---|
| 1 | `ppo.yaml` | 5 to 12 jobs, 4 to 12 machines |
| 2 | `ppo_stage3.yaml`, `ppo_stage4.yaml`, `ppo_stage5.yaml` | weighted mixes of 6x6 up to 20x15 |
| GT | `ppo_gt.yaml` | as stage 1, with the Giffler-Thompson mask |
| Large | `ppo_large_gt.yaml` | mix of 10x10 up to 30x30, Giffler-Thompson mask |

Shared settings: 4 parallel environments, 512 steps per update, batch size 256, 10 epochs, gamma 1.0, GAE lambda 0.95, hidden size 64, padding to 32 jobs.

## Project structure

```
JOB_SCHEDULE/
├── common/              shared foundation
│   ├── types.py         Instance, Schedule, ScheduledOp, Solver base class
│   ├── generator.py     random instance generator
│   ├── validate.py      checks a schedule is legal and returns its makespan
│   └── io.py            JSON save / load
├── env/                 the scheduling world
│   ├── simulator.py     event-driven simulator, lower bound, Giffler-Thompson
│   ├── features.py      10 per-job features
│   └── gym_env.py       gymnasium wrapper with action masks and reward
├── rl/                  learning
│   ├── policy.py        job-scoring network and MaskablePPO policy
│   ├── train.py         training loop with validation and best-checkpoint saving
│   ├── agent.py         torch-based solver (reference implementation)
│   ├── fast_sim.py      batched numpy simulator
│   ├── fast_agent.py    numpy network + best-of-N solver
│   ├── speed_check.py   timing comparison
│   └── configs/         one yaml file per training stage
├── baselines/
│   ├── rules.py         SPT, MWKR, FIFO
│   ├── cpsat.py         OR-Tools CP-SAT with time limit and optional hint
│   └── hybrid.py        RL schedule -> CP-SAT warm start
├── evaluation/
│   ├── benchmark.py     runs every method, validates, writes CSV
│   ├── metrics.py       gap, idle time, utilisation
│   ├── report.py        markdown report with wins and head-to-head tables
│   ├── plots.py         quality-vs-time and bar charts
│   └── stubs.py         random placeholder when no model is found
├── demo/
│   ├── app.py           Streamlit app, two methods side by side
│   └── gantt.py         Gantt chart drawing
├── data/benchmarks/     ft06, ft10, ft20 (OR-Library) and the converter
├── models/              trained .zip models and their .json mask settings
├── results/             benchmark CSVs, reports and graphs
└── tests/               pytest suite
```

Every method (rules, RL, CP-SAT, hybrid) implements the same `Solver.solve(instance) -> Schedule` interface, so the benchmark and the demo treat them identically.

## Installation

Python 3.10 or newer is recommended.

```bash
git clone <your-repo-url>
cd JOB_SCHEDULE

python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

Main dependencies: `numpy`, `pandas`, `pyyaml`, `ortools`, `gymnasium`, `torch`, `stable-baselines3`, `sb3-contrib`, `matplotlib`, `streamlit`, `plotly`, `pytest`.

The saved models were trained with specific library versions. If a model fails to load, install the versions listed in your pinned `requirements.txt`.

All commands below are run from the project root.

## Usage

### 1. Run the demo

```bash
streamlit run demo/app.py
```

Pick a benchmark or random instance, choose two methods (for example `SPT` against `HYBRID@10`), and press **Schedule**. The app shows both Gantt charts, makespan, solve time and idle time.

### 2. Solve an instance from Python

```python
import numpy as np
from common.generator import random_instance
from common.validate import validate_schedule
from rl.fast_agent import FastRLScheduler

inst = random_instance(20, 20, np.random.default_rng(0))

greedy = FastRLScheduler("models/ppo_large_gt_best.zip")
best20 = FastRLScheduler("models/ppo_large_gt_best.zip", n_samples=20)

for solver in (greedy, best20):
    sch = solver.solve(inst)
    print(sch.method, validate_schedule(inst, sch), f"{sch.solve_time:.3f}s")
```

### 3. Benchmark

On random instances (to produce a run like the results above; the 60 s CP-SAT runs make this take over an hour):

```bash
python -m evaluation.benchmark --set random --size 20x20,30x20,30x30 --n-random 20 \
  --methods SPT,MWKR,FIFO,RL,RLBEST@20,CPSAT,HYBRID \
  --cpsat-limits 0.25,0.5,1,5,10,60 --hybrid-limits 0.5,1,5,10 \
  --model models/ppo_large_gt_best.zip
```

On the classic Fisher-Thompson instances (known optima: ft06 = 55, ft10 = 930, ft20 = 1165):

```bash
python -m evaluation.benchmark --set ft \
  --methods SPT,MWKR,FIFO,RL,RLBEST@20,CPSAT,HYBRID \
  --cpsat-limits 1,10 --hybrid-limits 1,5 \
  --model models/ppo_large_gt_best.zip
```

Method names: `SPT`, `MWKR`, `FIFO`, `RL`, `RLBEST@N`, `CPSAT@seconds`, `HYBRID@seconds` (the hybrid time is the CP-SAT time after the RL schedule). Results are written to `results/benchmark_<timestamp>.csv`.

### 4. Report and graphs

```bash
python -m evaluation.report      # markdown report from the latest CSV
python -m evaluation.plots       # results/bar_gap.png and results/gap_vs_time.png
```

Pass a CSV path as the last argument to use a specific run.

### 5. Train a model

```bash
python -m rl.train --config rl/configs/ppo_gt.yaml
python -m rl.train --config rl/configs/ppo_large_gt.yaml    # fine-tune on large instances
```

Training prints validation progress, saves the best checkpoint as `<name>_best.zip`, and writes the mask mode to a `.json` file next to each model. Use `--timesteps N` to override the length. Check the `save_path` in each config before running, so you do not overwrite a model you want to keep.

### 6. Convert more OR-Library instances

```bash
python -m data.benchmarks.convert_orlib data/benchmarks/jobshop1.txt
```

Add `--all` to convert every instance in the file.

## Models

| File | Description |
|---|---|
| `ppo_large_gt_best.zip` | Default model for the demo, tests and benchmarks. Giffler-Thompson mask, fine-tuned on 10x10 to 30x30. |
| `ppo_gt*.zip`, `ppo_large_gt*.zip` | Giffler-Thompson models at earlier or later checkpoints |
| `ppo_v1.zip` to `ppo_v5.zip`, `ppo_6x6.zip` | Earlier curriculum stages, unrestricted ("any") action mask |

Each `.zip` has a matching `.json` (for gt models) holding `{"mask_mode": "gt"}`; models without one default to `any`.

## Tests

```bash
pytest
```

To skip the two slow CP-SAT tests on ft10 and ft20 (up to 180 s each):

```bash
pytest -k "not ft10 and not ft20"
```

The suite covers:

- the schedule validator, including deliberately broken schedules
- generator reproducibility and JSON round trips
- simulator behaviour and agreement with the rule-based dispatcher
- the gymnasium environment and action masks
- CP-SAT reaching the known optima on ft06, ft10 and ft20
- the numpy simulator and agent matching the torch reference
- best-of-N never being worse than greedy, and being repeatable

## Honest limitations

We would rather state these ourselves than have them found:

- **The gap reference is not an optimum.** "Best found" is the best makespan any method achieved, which is CP-SAT at 60 s here. Only 1 of 60 instances was proven optimal.
- **Synthetic data only.** Training and benchmark instances come from the same generator (random machine order, durations 1 to 99). Results on real factories or on other benchmark families (for example Taillard) are untested.
- **Hardware is not equal.** CP-SAT runs with 8 workers; the RL solver is a single numpy process. Compare times with that in mind.
- **RL does not beat long solver runs.** Beyond roughly 5 seconds, CP-SAT and the hybrid are better. The benefit of RL is in the sub-second regime and on larger instances.
- **Small instances favour CP-SAT.** On 20x20, CP-SAT at 1 s is about as good as RL-best20 and better than greedy RL.
- **Simplified problem.** No machine breakdowns, setup times, due dates or jobs that revisit a machine.
- **One-way hybrid.** RL warm-starts CP-SAT, but CP-SAT solutions are not fed back into training.
- **Iteration counts are not measured**, only time and solution quality.

## Future work

- Benchmark on Taillard and other standard instance families.
- Re-scheduling experiments: machine breakdowns and rush orders, where fast decisions matter most.
- Close the loop: train the policy on CP-SAT's best schedules (imitation or self-improvement).
- Report training cost and the break-even number of instances.
- Extend the generator to setup times, due dates and flexible machines.

## References and credits

- B. Giffler and G. L. Thompson, "Algorithms for Solving Production-Scheduling Problems", *Operations Research*, 1960.
- H. Fisher and G. L. Thompson, "Probabilistic learning combinations of local job-shop scheduling rules", 1963 (ft06, ft10, ft20).
- J. E. Beasley, OR-Library (`jobshop1.txt`), the source of the classic instances.
- J. Schulman et al., "Proximal Policy Optimization Algorithms", 2017.
- Google OR-Tools CP-SAT solver.
- Stable-Baselines3 and SB3-Contrib (MaskablePPO), Gymnasium, PyTorch, Streamlit, Plotly.

## License

No license has been chosen yet. Add a `LICENSE` file (for example MIT) before publishing.
