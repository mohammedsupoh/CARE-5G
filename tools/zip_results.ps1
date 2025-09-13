param([string]$Dir = ".\results\CARE_v1.0.0_full")
$zip = Join-Path $Dir "CARE-v1.0.0-results.zip"
$items = @(
  (Join-Path $Dir "metrics.json"),
  (Join-Path $Dir "CARE_figure1_convergence.png"),
  (Join-Path $Dir "CARE_figure2_satisfaction.png"),
  (Join-Path $Dir "CARE_figure3_combined_metrics.png"),
  (Join-Path $Dir "CARE_figure4_success_zones.png"),
  (Join-Path $Dir "CARE_table1_final_results.png")
)
if(Test-Path $zip){ Remove-Item $zip -Force }
Compress-Archive -Path $items -DestinationPath $zip -Force
Write-Host "✅ Created:" (Resolve-Path $zip)
