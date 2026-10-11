# Benchmark report (benchmark_20261009_034339.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR  FIFO    RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                           
10x10   15.5  19.1  27.3  23.0        11.6       0.8        0.0
20x5     8.8  28.8  41.2  15.7        14.4       0.0        0.0
6x6     60.0  10.9  18.2  10.9         0.0       0.0        0.0
```
(instances per size: 10x10=1, 20x5=1, 6x6=1)

## Average solve time (seconds)
```
method    SPT   MWKR   FIFO     RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                               
10x10   0.001  0.001  0.001  0.070       0.118     1.019      4.565
20x5    0.001  0.001  0.001  0.103       0.111     0.705      0.734
6x6     0.000  0.000  0.000  0.025       0.025     0.019      0.024
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  FIFO  RL  CPSAT@0.1s  CPSAT@1s  CPSAT@10s
size                                                        
10x10     0     0     0   0           0         0          1
20x5      0     0     0   0           0         1          1
6x6       0     0     0   0           1         1          1
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
         SPT   MWKR   FIFO CPSAT@0.1s CPSAT@1s CPSAT@10s
size                                                    
10x10  0/0/1  0/0/1  1/0/0      0/0/1    0/0/1     0/0/1
20x5   0/0/1  1/0/0  1/0/0      0/0/1    0/0/1     0/0/1
6x6    1/0/0  0/1/0  1/0/0      0/0/1    0/0/1     0/0/1
```

## Equal-budget reading guide
- RL average time: 0.066s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.1s, CPSAT@1s, CPSAT@10s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.