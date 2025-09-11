## CARE-5G v1.0.3

**DOI:** https://doi.org/10.5281/zenodo.17102480

### Highlights
- 5 independent seeds with 95% CI checks in CI
- Full baselines (QMIX/VDN/IQL/PF) under uniform configs
- Ablations (no-fairness / no-admission / 2-stage)
- Sensitivity (lr × ε-decay) + heatmaps
- Pareto (fairness vs efficiency), convergence, CI bands

### Artifacts
- \CARE-5G_validation_pack_v1.zip\ — validation pack (ENV/BUILD/WORKLOAD/RESULTS/QC)
- \SHA256SUMS.txt\ — integrity checksums

### Repro Quickstart
1) Prepare env (CPU freq lock, NUMA/core isolation)
2) Build (exact flags + commits)
3) Run multi-seed baselines (60 agents, 150 episodes)
4) Stats & effects (Cliff’s δ, Hedges’ g, Holm–Bonferroni)
5) Plots (Pareto + convergence + heatmaps)

### Notes
- Additional scenarios beyond SCARCITY will be expanded in the next release
