## CARE — Scientific Validation PR

**Summary**
- [ ] Multi-seed aggregate (n=5): attach `aggregate.json`
- [ ] Baselines vs CARE: attach `stats.csv` + `stats.md`
- [ ] Plots: `figs/pareto.png`, `figs/conv_efficiency.png`, `figs/conv_fairness.png`, (`figs/conv_satisfaction.png` if available)
- [ ] Acceptance Criteria met? (CI lower bounds) ☐ Yes ☐ No

**Links**
- Issue: closes #<issue-number>
- Runbook: see Baselines/Multiseed issues

**Notes**
- Welch’s t-test is skipped automatically under zero variance to avoid numerical instability; MWU reported regardless.
