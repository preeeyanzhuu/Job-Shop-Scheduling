# Benchmark report (benchmark_20261009_150337.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR  FIFO    RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s
size                                                                               
20x20   25.1  19.2  25.2  15.0       11.1      10.2       3.8        2.0        0.5
30x20   26.5  17.3  23.4  14.1       11.9      13.3       6.8        3.9        0.0
30x30   27.0  15.6  23.8  11.2       10.4      14.6       8.2        6.1        0.0
```
(instances per size: 20x20=5, 30x20=5, 30x30=5)

## Average solve time (seconds)
```
method    SPT   MWKR   FIFO     RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s
size                                                                                   
20x20   0.003  0.003  0.003  0.495      6.524     1.036     5.066     10.045     60.085
30x20   0.006  0.007  0.006  0.691      9.752     1.049     5.040     10.129     60.107
30x30   0.009  0.011  0.009  0.884     14.659     1.053     5.054     10.068     60.119
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  FIFO  RL  RL-best20  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s
size                                                                            
20x20     0     0     0   0          0         0         0          1          4
30x20     0     0     0   0          0         0         0          0          5
30x30     0     0     0   0          0         0         0          0          5
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
         SPT   MWKR   FIFO RL-best20 CPSAT@1s CPSAT@5s CPSAT@10s CPSAT@60s
size                                                                      
20x20  5/0/0  5/0/0  5/0/0     0/0/5    1/0/4    0/0/5     0/0/5     0/0/5
30x20  5/0/0  5/0/0  5/0/0     0/1/4    2/0/3    0/0/5     0/0/5     0/0/5
30x30  5/0/0  5/0/0  5/0/0     0/3/2    5/0/0    1/0/4     0/0/5     0/0/5
```

## Equal-budget reading guide
- RL average time: 0.690s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@1s, CPSAT@5s, CPSAT@10s, CPSAT@60s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.