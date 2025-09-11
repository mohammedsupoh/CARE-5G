# Results Documentation — CARE-5G (EN)

**Setup:** SCARCITY · 60 agents · 150 episodes · 5 seeds · 95% CI  
**Summary:** Efficiency ≈ **0.86**, Fairness ≈ **0.74**. Statistically significant vs QMIX/VDN/IQL/PF (MWU).  
> Full numbers in `stats.csv` and `stats.md`.

## Plots
![Pareto (95% CI)](../figs/pareto.png)
![Convergence — Efficiency](../figs/conv_efficiency.png)
![Convergence — Fairness](../figs/conv_fairness.png)
![Convergence — Satisfaction](../figs/conv_satisfaction.png)
![Radar](../figs/radar.png)

## Tables
- Comparison table (Markdown EN): `tables/comparison_en.md`
- LaTeX table: `tables/comparison.tex` and CARE summary: `tables/metrics_summary.tex`
- Statistics: `stats.csv` + `stats.md`

## Notes
- MWU reported; Welch skipped under zero variance (n/a).
- Fully reproducible (multi-seed runs + scripts).
