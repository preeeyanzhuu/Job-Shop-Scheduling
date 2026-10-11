# Benchmark report (benchmark_20261009_100655.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR   RL  CPSAT@0.1s  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s
size                                                                  
15x15   20.1  12.9  9.4         9.7          4.6         2.8       0.0
20x15   19.9   9.8  4.9         8.3          4.9         1.9       0.1
```
(instances per size: 15x15=20, 20x15=20)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@0.1s  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s
size                                                                      
15x15   0.001  0.001  0.169       0.120        0.272       0.524     1.031
20x15   0.002  0.002  0.223       0.121        0.283       0.526     1.027
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@0.1s  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s
size                                                                
15x15     0     0   0           0            0           1        19
20x15     0     0   1           0            0           1        18
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT    MWKR CPSAT@0.1s CPSAT@0.25s CPSAT@0.5s CPSAT@1s
size                                                            
15x15  18/0/2  17/0/3     11/0/9      2/0/18     1/0/19   0/0/20
20x15  18/1/1  18/0/2     15/0/5      8/0/12     4/0/16   1/0/19
```

## Equal-budget reading guide
- RL average time: 0.196s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.1s, CPSAT@0.25s, CPSAT@0.5s, CPSAT@1s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.