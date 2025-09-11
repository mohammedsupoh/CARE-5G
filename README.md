# CARE: Context-Aware Resource Evaluation Framework for 5G Network Slicing
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17102480.svg)](https://doi.org/10.5281/zenodo.17102480)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)

## 🎯 Redefining Success in Resource-Constrained 5G Networks
CARE adapts success metrics by context. In **SCARCITY** (60 agents), it delivers:
- **Efficiency:** 85.8% (≥80% target)
- **Fairness:** 73.8% (≥70% target)
- **Satisfaction:** 79.8%
- **Converged:** TRUE

## 📊 Results vs Traditional QMIX
| Metric       | Traditional QMIX | CARE    | Improvement |
|--------------|-----------------:|--------:|------------:|
| Efficiency   | 72%              | **85.8%** | +13.8%     |
| Fairness     | 58%              | **73.8%** | +15.8%     |
| Satisfaction | 65%              | **79.8%** | +14.8%     |

## 📁 Repository Structure

## Citation
See **BibTeX**: [docs/citation.bib](docs/citation.bib)

<!-- Badges -->
[![CI](https://github.com/mohammedsupoh/CARE-5G/actions/workflows/validate_artifacts.yml/badge.svg)](https://github.com/mohammedsupoh/CARE-5G/actions/workflows/validate_artifacts.yml)
[![Release](https://img.shields.io/github/v/release/mohammedsupoh/CARE-5G?label=Release)](https://github.com/mohammedsupoh/CARE-5G/releases)

## Quick Links
- **Overview:** https://github.com/mohammedsupoh/CARE-5G/blob/main/reports/overview.md
- **Pareto (95% CI):** https://github.com/mohammedsupoh/CARE-5G/blob/main/figs/pareto.png?raw=1
- **Stats:** https://github.com/mohammedsupoh/CARE-5G/blob/main/stats.csv
## Statistical significance (n=5 seeds)
We report two-sided Mann–Whitney U (MWU) and Welch’s t-tests. For fairness, Welch’s test is skipped under zero variance (reported as “n/a”). Results show statistically significant differences for CARE vs. all baselines:

- **QMIX:** eff (MWU p=0.00398; Welch p<1e-50), fair (MWU p=0.00398; Welch n/a)
- **VDN:**  eff (MWU p=0.00398; Welch p<1e-50), fair (MWU p=0.00398; Welch n/a)
- **IQL:**  eff (MWU p=0.00398; Welch p<1e-50), fair (MWU p=0.00398; Welch n/a)
- **PF:**   eff (MWU p=0.00398; Welch p<1e-50), fair (MWU p=0.00398; Welch n/a)

**Conclusion.** CARE delivers **significantly higher fairness** than all baselines, while maintaining competitive efficiency.

