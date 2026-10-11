# Benchmark report (benchmark_20261009_102201.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR   RL  CPSAT@0.25s  CPSAT@0.35s  CPSAT@0.5s  CPSAT@0.75s  CPSAT@1s  HYBRID@0.1s  HYBRID@0.25s  HYBRID@0.5s
size                                                                                                                        
15x15   26.3  12.8  8.7          4.7          3.4         2.2          0.8       0.2          7.2           4.0          2.6
20x15   18.2  10.2  7.0          6.1          3.7         2.4          1.6       0.7          6.0           4.3          2.1
```
(instances per size: 15x15=20, 20x15=20)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@0.25s  CPSAT@0.35s  CPSAT@0.5s  CPSAT@0.75s  CPSAT@1s  HYBRID@0.1s  HYBRID@0.25s  HYBRID@0.5s
size                                                                                                                            
15x15   0.001  0.001  0.172        0.275        0.372       0.521        0.776     1.027        0.294         0.445        0.700
20x15   0.002  0.002  0.228        0.285        0.383       0.529        0.779     1.026        0.366         0.515        0.757
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@0.25s  CPSAT@0.35s  CPSAT@0.5s  CPSAT@0.75s  CPSAT@1s  HYBRID@0.1s  HYBRID@0.25s  HYBRID@0.5s
size                                                                                                                      
15x15     0     0   0            0            0           0            4        15            0             0            2
20x15     0     0   0            0            0           0            2        12            0             1            5
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT    MWKR CPSAT@0.25s CPSAT@0.35s CPSAT@0.5s CPSAT@0.75s CPSAT@1s HYBRID@0.1s HYBRID@0.25s HYBRID@0.5s
size                                                                                                              
15x15  20/0/0  18/0/2      2/0/18      1/0/19     0/0/20      0/0/20   0/0/20      0/0/20       0/0/20      0/0/20
20x15  20/0/0  16/0/4      8/0/12      4/0/16     2/0/18      0/0/20   0/0/20      0/2/18       0/0/20      0/0/20
```

## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)
```
             hybrid  avg time    vs CP-SAT  its time   W/T/L  mean diff % vs RL alone W/T/L
size                                                                                       
15x15   HYBRID@0.1s     0.294  CPSAT@0.25s     0.275  3/1/16         2.35            20/0/0
15x15  HYBRID@0.25s     0.445  CPSAT@0.35s     0.372  8/2/10         0.61            20/0/0
15x15   HYBRID@0.5s     0.700  CPSAT@0.75s     0.776  4/1/15         1.72            20/0/0
20x15   HYBRID@0.1s     0.366  CPSAT@0.35s     0.383  4/0/16         2.26            18/2/0
20x15  HYBRID@0.25s     0.515   CPSAT@0.5s     0.529  4/1/15         1.89            20/0/0
20x15   HYBRID@0.5s     0.757  CPSAT@0.75s     0.779  7/0/13         0.49            20/0/0
```
(mean diff % < 0 means the hybrid has the shorter makespan)

## Equal-budget reading guide
- RL average time: 0.200s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.25s, CPSAT@0.35s, CPSAT@0.5s, CPSAT@0.75s, CPSAT@1s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.