# Benchmark report (benchmark_20261009_132657.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR    RL  CPSAT@1s  CPSAT@10s
size                                         
10x10   22.3  16.5   9.9       0.0        0.0
15x15   28.8  18.2  13.9       4.1        0.0
20x15   22.8  18.2  14.4       7.4        0.0
```
(instances per size: 10x10=10, 15x15=10, 20x15=10)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@1s  CPSAT@10s
size                                            
10x10   0.001  0.000  0.075     0.222      0.218
15x15   0.002  0.002  0.232     1.029      8.764
20x15   0.003  0.002  0.372     1.033     10.058
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@1s  CPSAT@10s
size                                      
10x10     0     0   0        10         10
15x15     0     0   0         0         10
20x15     0     0   0         0         10
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
         SPT    MWKR CPSAT@1s CPSAT@10s
size                                   
10x10  8/0/2  10/0/0   0/0/10    0/0/10
15x15  8/0/2   9/0/1   0/0/10    0/0/10
20x15  7/0/3   9/0/1    1/0/9    0/0/10
```

## Equal-budget reading guide
- RL average time: 0.226s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@1s, CPSAT@10s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.