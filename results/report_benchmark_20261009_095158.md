# Benchmark report (benchmark_20261009_095158.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR    RL  CPSAT@0.1s  CPSAT@1s
size                                          
10x10   22.9  16.8  10.1         4.0       0.0
15x15   19.1  13.0   8.1        10.3       0.0
```
(instances per size: 10x10=20, 15x15=20)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@0.1s  CPSAT@1s
size                                             
10x10   0.000  0.000  0.089       0.112     0.338
15x15   0.001  0.001  0.245       0.125     1.033
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@0.1s  CPSAT@1s
size                                       
10x10     0     0   0           3        20
15x15     0     0   0           0        20
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT    MWKR CPSAT@0.1s CPSAT@1s
size                                     
10x10  18/0/2  19/0/1     2/0/18   0/0/20
15x15  19/0/1  17/0/3     13/1/6   0/0/20
```

## Equal-budget reading guide
- RL average time: 0.167s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.1s, CPSAT@1s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.