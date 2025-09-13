param([string]$Dir = ".\results\CARE_v1.0.0_full")

$metrics = Join-Path $Dir "metrics.json"
if(-not (Test-Path $metrics)){ Write-Error "metrics.json not found in $Dir"; exit 2 }

$j = Get-Content $metrics -Raw | ConvertFrom-Json

$passE = [double]$j.final.efficiency -ge 0.80
$passF = [double]$j.final.fairness   -ge 0.70
$passC = [bool]$j.convergence.achieved -and ([int]$j.convergence.episode -lt 50)
$passAll = $passE -and $passF -and $passC
$status = if($passAll){"PASS"} else {"FAIL"}
$episode = if($j.convergence.episode){ [string]$j.convergence.episode } else { "-" }

$lines = @()
$lines += "# CARE v1.0.0 - SCARCITY (Full Run)"
$lines += "**Status:** $status"
$lines += ""
$lines += "## Final Metrics"
$lines += ("- Efficiency: {0:N3}" -f [double]$j.final.efficiency)
$lines += ("- Fairness:   {0:N3}" -f [double]$j.final.fairness)
$lines += ("- Satisfaction: {0:N3}" -f [double]$j.final.satisfaction)
$lines += ""
$lines += "## Convergence"
$lines += "- Achieved: $($j.convergence.achieved)"
$lines += "- Episode:  $episode"
$lines += ""
$lines += "## Files"
$lines += "- CARE_figure1_convergence.png"
$lines += "- CARE_figure2_satisfaction.png"
$lines += "- CARE_figure3_combined_metrics.png"
$lines += "- CARE_figure4_success_zones.png"
$lines += "- CARE_table1_final_results.png"
$lines += "- CARE-v1.0.0-results.zip"
$lines += ""
$lines += "## Reproduce"
$lines += '    $env:EPISODES="100"'
$lines += '    $env:CALIBRATE="1"'
$lines += '    .\tools\run_smoketest.ps1 -OutDir .\results\CARE_v1.0.0_full'
$lines += '    .\tools\zip_results.ps1    -Dir      .\results\CARE_v1.0.0_full'

$lines | Set-Content -Path .\README.md -Encoding UTF8
