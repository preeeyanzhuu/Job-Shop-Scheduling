# Benchmark report (benchmark_20261009_214428.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR  FIFO    RL  RL-best20  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@0.5s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                                                                       
20x20   25.4  19.3  29.2  14.2       10.3         15.4        12.9      10.1       3.6        2.3        0.2         11.3        9.8        3.3         1.7
30x20   27.5  18.2  26.0  13.5       11.0         16.9        15.6      13.0       7.5        5.0        0.0         13.0       12.0        6.5         4.2
30x30   23.1  15.3  23.9  10.3        8.5         15.1        14.0      13.2       7.3        5.1        0.0          9.5        9.2        5.8         4.2
```
(instances per size: 20x20=20, 30x20=20, 30x30=20)

## Average solve time (seconds)
```
method    SPT   MWKR   FIFO     RL  RL-best20  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@0.5s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                                                                           
20x20   0.003  0.003  0.003  0.080      0.256        0.303       0.541     1.032     5.083     10.043     60.069        0.620      1.123      5.173      10.118
30x20   0.006  0.006  0.006  0.118      0.519        0.287       0.582     1.043     5.051     10.158     58.889        0.736      1.213      5.158      10.271
30x30   0.009  0.010  0.009  0.173      0.713        0.309       0.551     1.049     5.063     10.088     60.116        0.815      1.339      5.237      10.264
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  FIFO  RL  RL-best20  CPSAT@0.25s  CPSAT@0.5s  CPSAT@1s  CPSAT@5s  CPSAT@10s  CPSAT@60s  HYBRID@0.5s  HYBRID@1s  HYBRID@5s  HYBRID@10s
size                                                                                                                                                    
20x20     0     0     0   0          0            0           0         0         0          2         16            0          0          0           2
30x20     0     0     0   0          0            0           0         0         0          0         19            0          0          1           0
30x30     0     0     0   0          0            0           0         0         0          0         20            0          0          0           0
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT    MWKR    FIFO RL-best20 CPSAT@0.25s CPSAT@0.5s CPSAT@1s CPSAT@5s CPSAT@10s CPSAT@60s HYBRID@0.5s HYBRID@1s HYBRID@5s HYBRID@10s
size                                                                                                                                           
20x20  19/0/1  18/0/2  20/0/0    0/1/19      13/0/7     5/0/15   3/0/17   0/0/20    0/0/20    0/0/20      0/0/20    0/0/20    0/0/20     0/0/20
30x20  19/0/1  20/0/0  20/0/0    0/2/18      18/0/2     16/0/4   12/0/8   0/0/20    0/0/20    0/0/20      0/3/17    0/0/20    0/0/20     0/0/20
30x30  19/0/1  19/0/1  20/0/0    0/4/16      18/0/2     16/0/4   17/0/3   4/0/16    0/0/20    0/0/20      0/5/15    0/0/20    0/0/20     0/0/20
```

## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)
```
            hybrid  avg time   vs CP-SAT  its time   W/T/L  mean diff % vs RL alone W/T/L
size                                                                                     
20x20  HYBRID@0.5s     0.620  CPSAT@0.5s     0.541  11/1/8        -1.43            20/0/0
20x20    HYBRID@1s     1.123    CPSAT@1s     1.032  9/0/11        -0.19            20/0/0
20x20    HYBRID@5s     5.173    CPSAT@5s     5.083  12/0/8        -0.29            20/0/0
20x20   HYBRID@10s    10.118   CPSAT@10s    10.043  13/0/7        -0.59            20/0/0
30x20  HYBRID@0.5s     0.736  CPSAT@0.5s     0.582  17/0/3        -2.25            17/3/0
30x20    HYBRID@1s     1.213    CPSAT@1s     1.043  12/1/7        -0.87            20/0/0
30x20    HYBRID@5s     5.158    CPSAT@5s     5.051  11/0/9        -0.87            20/0/0
30x20   HYBRID@10s    10.271   CPSAT@10s    10.158  13/0/7        -0.72            20/0/0
30x30  HYBRID@0.5s     0.815    CPSAT@1s     1.049  17/0/3        -3.22            15/5/0
30x30    HYBRID@1s     1.339    CPSAT@1s     1.049  17/1/2        -3.54            20/0/0
30x30    HYBRID@5s     5.237    CPSAT@5s     5.063  15/0/5        -1.42            20/0/0
30x30   HYBRID@10s    10.264   CPSAT@10s    10.088  13/0/7        -0.94            20/0/0
```
(mean diff % < 0 means the hybrid has the shorter makespan)

## Equal-budget reading guide
- RL average time: 0.124s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.25s, CPSAT@0.5s, CPSAT@1s, CPSAT@5s, CPSAT@10s, CPSAT@60s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.