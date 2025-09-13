# CARE v1.0.0 - SCARCITY (Full Run)
**Status:** PASS

## Final Metrics
- Efficiency: 0.912
- Fairness:   0.786
- Satisfaction: 0.306

## Convergence
- Achieved: True
- Episode:  46

## Files
- CARE_figure1_convergence.png
- CARE_figure2_satisfaction.png
- CARE_figure3_combined_metrics.png
- CARE_figure4_success_zones.png
- CARE_table1_final_results.png
- CARE-v1.0.0-results.zip

## Reproduce
    $env:EPISODES="100"
    $env:CALIBRATE="1"
    .\tools\run_smoketest.ps1 -OutDir .\results\CARE_v1.0.0_full
    .\tools\zip_results.ps1    -Dir      .\results\CARE_v1.0.0_full


