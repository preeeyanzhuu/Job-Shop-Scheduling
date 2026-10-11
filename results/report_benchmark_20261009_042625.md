# Benchmark report (benchmark_20261009_042625.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR    RL  CPSAT@10s
size                               
10x10   24.3  17.0  12.4        0.0
12x12   24.4  17.6  12.9        0.0
15x15   25.7  20.4  14.3        0.0
20x15   27.6  18.6  13.7        0.0
6x6     16.3  12.7   8.9        0.0
```
(instances per size: 10x10=10, 12x12=10, 15x15=10, 20x15=10, 6x6=10)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@10s
size                                  
10x10   0.001  0.000  0.078      0.252
12x12   0.001  0.001  0.113      1.632
15x15   0.001  0.001  0.218      9.724
20x15   0.002  0.002  0.262     10.053
6x6     0.000  0.000  0.028      0.024
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@10s
size                            
10x10     0     0   0         10
12x12     0     0   0         10
15x15     0     0   0         10
20x15     0     0   0         10
6x6       0     0   0         10
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
         SPT    MWKR CPSAT@10s
size                          
10x10  8/0/2   7/0/3    0/0/10
12x12  8/0/2   8/0/2    0/0/10
15x15  9/0/1  10/0/0    0/0/10
20x15  9/0/1   8/0/2    0/0/10
6x6    9/0/1   7/1/2    0/0/10
```

## Equal-budget reading guide
- RL average time: 0.140s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@10s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.