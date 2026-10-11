# Benchmark report (benchmark_20261009_100357.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR  FIFO    RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                           
10x10   24.3  17.0  26.3  13.2         3.5       0.0        0.0
12x12   24.4  17.6  24.1  13.3        10.3       0.7        0.0
15x15   25.2  19.9  26.1  12.8        16.3       6.0        0.0
20x15   27.0  18.0  25.9  13.7        16.4       7.8        0.0
6x6     16.3  12.7  14.8   9.7         0.0       0.0        0.0
```
(instances per size: 10x10=10, 12x12=10, 15x15=10, 20x15=10, 6x6=10)

## Average solve time (seconds)
```
method    SPT   MWKR   FIFO     RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                               
10x10   0.001  0.000  0.000  0.080       0.116     0.298      0.272
12x12   0.001  0.001  0.001  0.163       0.117     0.931      2.268
15x15   0.002  0.001  0.002  0.256       0.123     1.032      9.848
20x15   0.002  0.002  0.003  0.299       0.120     1.027     10.046
6x6     0.000  0.000  0.000  0.027       0.023     0.021      0.023
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  FIFO  RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                        
10x10     0     0     0   0           1        10         10
12x12     0     0     0   0           0         4         10
15x15     0     0     0   0           0         0         10
20x15     0     0     0   0           0         0         10
6x6       0     0     0   0          10        10         10
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT   MWKR    FIFO CPSAT@0.1s CPSAT@1s CPSAT@10s
size                                                      
10x10   9/0/1  7/0/3  10/0/0     0/0/10   0/0/10    0/0/10
12x12   9/0/1  7/0/3  10/0/0      2/0/8   0/0/10    0/0/10
15x15  10/0/0  9/0/1   9/1/0      7/0/3   0/0/10    0/0/10
20x15   9/0/1  8/0/2   8/0/2      8/0/2    1/0/9    0/0/10
6x6     8/0/2  6/1/3   6/0/4     0/0/10   0/0/10    0/0/10
```

## Equal-budget reading guide
- RL average time: 0.165s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.1s, CPSAT@1s, CPSAT@10s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.