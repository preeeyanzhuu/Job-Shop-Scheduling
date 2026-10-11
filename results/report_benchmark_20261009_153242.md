# Benchmark report (benchmark_20261009_153242.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR  FIFO    RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                                 
20x20   25.6  19.7  25.7  13.9       10.9      11.4       3.0        2.0        0.1        9.7        3.2         2.3
30x20   26.0  16.9  22.9  13.0        9.9      12.4       5.9        4.0        0.0       10.5        5.3         4.0
30x30   26.3  14.9  23.2  11.0        9.0      14.1       7.8        5.4        0.0        9.8        7.0         5.4
```
(instances per size: 20x20=5, 30x20=5, 30x30=5)

## Average solve time (seconds)
```
method    SPT   MWKR   FIFO     RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                                     
20x20   0.003  0.003  0.003  0.343      6.298     1.028     5.054     10.041     60.071      1.488      5.400      10.385
30x20   0.005  0.006  0.005  0.597      9.723     1.050     5.042     10.138     60.089      1.698      5.501      10.630
30x30   0.008  0.009  0.009  0.816     14.486     1.053     5.072     10.073     60.106      2.105      5.775      10.818
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  FIFO  RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                              
20x20     0     0     0   0          0         0         0          1          4          0          0           0
30x20     0     0     0   0          0         0         0          0          5          0          0           0
30x30     0     0     0   0          0         0         0          0          5          0          0           0
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
         SPT   MWKR   FIFO RL-best20 CPSAT@1s CPSAT@5s CPSAT@10s CPSAT@60s HYBRID@1s HYBRID@5s HYBRID@10s
size                                                                                                     
20x20  5/0/0  5/0/0  5/0/0     0/0/5    1/0/4    0/0/5     0/0/5     0/0/5     0/0/5     0/0/5      0/0/5
30x20  5/0/0  5/0/0  5/0/0     0/1/4    1/1/3    0/0/5     0/0/5     0/0/5     0/0/5     0/0/5      0/0/5
30x30  5/0/0  5/0/0  5/0/0     0/2/3    4/0/1    0/0/5     0/0/5     0/0/5     0/0/5     0/0/5      0/0/5
```

## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)
```
           hybrid  avg time  vs CP-SAT  its time  W/T/L  mean diff % vs RL alone W/T/L
size                                                                                  
20x20   HYBRID@1s     1.488   CPSAT@1s     1.028  4/0/1        -1.54             5/0/0
20x20   HYBRID@5s     5.400   CPSAT@5s     5.054  2/1/2         0.16             5/0/0
20x20  HYBRID@10s    10.385  CPSAT@10s    10.041  1/0/4         0.30             5/0/0
30x20   HYBRID@1s     1.698   CPSAT@1s     1.050  5/0/0        -1.62             5/0/0
30x20   HYBRID@5s     5.501   CPSAT@5s     5.042  4/0/1        -0.53             5/0/0
30x20  HYBRID@10s    10.630  CPSAT@10s    10.138  3/0/2         0.02             5/0/0
30x30   HYBRID@1s     2.105   CPSAT@1s     1.053  5/0/0        -3.71             5/0/0
30x30   HYBRID@5s     5.775   CPSAT@5s     5.072  3/0/2        -0.73             5/0/0
30x30  HYBRID@10s    10.818  CPSAT@10s    10.073  2/0/3        -0.04             5/0/0
```
(mean diff % < 0 means the hybrid has the shorter makespan)

## Equal-budget reading guide
- RL average time: 0.586s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@1s, CPSAT@5s, CPSAT@10s, CPSAT@60s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.