# Benchmark report (benchmark_20261009_094300.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR    RL  CPSAT@0.1s  CPSAT@1s
size                                          
10x10   22.9  16.8  10.8         3.6       0.0
15x15   20.4  14.3   9.0        11.0       0.0
```
(instances per size: 10x10=20, 15x15=20)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@0.1s  CPSAT@1s
size                                             
10x10   0.000  0.000  0.076       0.111     0.336
15x15   0.001  0.001  0.163       0.120     1.031
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@0.1s  CPSAT@1s
size                                       
10x10     0     0   0           4        20
15x15     0     0   0           0        20
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT    MWKR CPSAT@0.1s CPSAT@1s
size                                     
10x10  17/0/3  17/1/2     2/0/18   0/0/20
15x15  20/0/0  17/0/3     12/0/8   0/0/20
```

## Equal-budget reading guide
- RL average time: 0.120s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.1s, CPSAT@1s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.