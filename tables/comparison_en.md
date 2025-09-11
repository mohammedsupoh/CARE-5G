# Comparison Table (CARE vs Baselines)

| Algorithm | Efficiency (mean) | Fairness (mean) | Note |
|---|---:|---:|---|
| CARE | **0.86** | **0.74** | Reference |
| QMIX | 0.87 | 0.52 | Slightly higher eff, low fairness |
| VDN  | 0.83 | 0.60 | Lower than CARE on both |
| IQL  | 0.80 | 0.58 | Lower than CARE on both |
| PF   | 0.78 | 0.70 | Borderline fairness, lower eff |

> Stats (n=5): MWU p≈0.00398 across comparisons; Welch eff p<1e-50; fairness Welch n/a under zero variance.
