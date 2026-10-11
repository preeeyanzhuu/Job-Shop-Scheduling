# Benchmark report (benchmark_20261009_103138.csv)

## Average gap to best known / best found (%)  (lower is better)
```
method   SPT  MWKR   RL  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                         
20x20   16.5  12.1  7.9         5.2       3.2       0.1           6.3          4.6        2.4
30x20   15.3   6.8  4.4         5.6       2.3       0.0           3.2          3.0        2.1
```
(instances per size: 20x20=10, 30x20=10)

## Average solve time (seconds)
```
method    SPT   MWKR     RL  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                             
20x20   0.003  0.003  0.310       0.552     1.028     2.034         0.666        0.858      1.352
30x20   0.005  0.005  0.458       0.562     1.048     2.045         0.830        1.008      1.506
```

## Wins per size (instances where the method matches the best makespan; ties count for all)
```
method  SPT  MWKR  RL  CPSAT@0.5s  CPSAT@1s  CPSAT@2s  HYBRID@0.25s  HYBRID@0.5s  HYBRID@1s
size                                                                                       
20x20     0     0   0           0         1         8             0            0          1
30x20     0     0   0           0         0         9             0            0          1
```

## Head-to-head: RL vs each method (wins / ties / losses for RL, by makespan)
```
          SPT   MWKR CPSAT@0.5s CPSAT@1s CPSAT@2s HYBRID@0.25s HYBRID@0.5s HYBRID@1s
size                                                                                
20x20   9/1/0  8/0/2      1/0/9   0/0/10   0/0/10       0/0/10      0/0/10    0/0/10
30x20  10/0/0  8/0/2      6/0/4    2/0/8   0/0/10        0/1/9      0/0/10    0/0/10
```

## Hybrid vs plain CP-SAT at SIMILAR TOTAL TIME (hybrid time = RL + CP-SAT)
```
             hybrid  avg time   vs CP-SAT  its time  W/T/L  mean diff % vs RL alone W/T/L
size                                                                                     
20x20  HYBRID@0.25s     0.666  CPSAT@0.5s     0.552  2/0/8         1.10            10/0/0
20x20   HYBRID@0.5s     0.858    CPSAT@1s     1.028  2/0/8         1.39            10/0/0
20x20     HYBRID@1s     1.352    CPSAT@1s     1.028  6/0/4        -0.67            10/0/0
30x20  HYBRID@0.25s     0.830    CPSAT@1s     1.048  3/0/7         0.91             9/1/0
30x20   HYBRID@0.5s     1.008    CPSAT@1s     1.048  3/0/7         0.73            10/0/0
30x20     HYBRID@1s     1.506    CPSAT@1s     1.048  6/0/4        -0.17            10/0/0
```
(mean diff % < 0 means the hybrid has the shorter makespan)

## Equal-budget reading guide
- RL average time: 0.384s. Compare it with the CP-SAT column whose limit is closest to that time (CP-SAT columns: CPSAT@0.5s, CPSAT@1s, CPSAT@2s).
- Report losses honestly: wherever CP-SAT wins at a similar or smaller budget, say so.