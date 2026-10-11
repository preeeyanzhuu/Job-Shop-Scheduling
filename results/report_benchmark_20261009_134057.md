# Benchmark report (benchmark_20261009_134057.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR   RL  RL-best20  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                                    
20x20   15.9  11.5  7.3        5.6         5.9       3.6       0.5           5.7          4.0        2.1
30x20   15.7   7.1  4.7        3.1         5.3       2.6       0.2           3.5          3.3        2.4
```
(instances per size: 20x20=10, 30x20=10)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  RL-best20  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                                        
20x20   0.003  0.003  0.348      7.555       0.538     1.037     2.035         0.695        0.892      1.401
30x20   0.005  0.005  0.454      9.527       0.558     1.047     2.036         0.800        0.986      1.490
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  RL-best20  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                                  
20x20     0     0   0          0           0         0         7             0            0          3
30x20     0     0   0          1           0         0         8             0            0          1
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT   MWKR RL-best20 CPSAT@0.5s CPSAT@1s CPSAT@2s HYBRID@0.25s HYBRID@0.5s HYBRID@1s
size                                                                                          
20x20   9/1/0  8/0/2     0/1/9      4/0/6   0/0/10   0/0/10       0/0/10      0/0/10    0/0/10
30x20  10/0/0  8/0/2     0/2/8      6/0/4    2/0/8   0/0/10        0/1/9      0/0/10    0/0/10
```

## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)
```
             hybrid  avg time   vs CP-SAT  its time  W/T/L  mean diff % vs RL alone W/T/L
size                                                                                     
20x20  HYBRID@0.25s     0.695  CPSAT@0.5s     0.538  6/0/4        -0.15            10/0/0
20x20   HYBRID@0.5s     0.892    CPSAT@1s     1.037  2/0/8         0.41            10/0/0
20x20     HYBRID@1s     1.401    CPSAT@1s     1.037  8/0/2        -1.44            10/0/0
30x20  HYBRID@0.25s     0.800  CPSAT@0.5s     0.558  7/0/3        -1.65             9/1/0
30x20   HYBRID@0.5s     0.986    CPSAT@1s     1.047  2/0/8         0.77            10/0/0
30x20     HYBRID@1s     1.490    CPSAT@1s     1.047  6/0/4        -0.15            10/0/0
```
(mean diff % < 0 means the hybrid has the shorter makespan)

## Equal-budget reading guide
- RL average time: 0.401s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.5s, CPSAT@1s, CPSAT@2s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.