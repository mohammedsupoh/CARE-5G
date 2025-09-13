param([string]$Dir = ".")
$required = @(
  "metrics.json",
  "CARE_figure1_convergence.png",
  "CARE_figure2_satisfaction.png",
  "CARE_figure3_combined_metrics.png",
  "CARE_figure4_success_zones.png",
  "CARE_table1_final_results.png",
  "CARE-v1.0.0-smoketest.zip"
)
$missing = @()
foreach($name in $required){
  $p = Join-Path $Dir $name
  if(Test-Path $p){
    $item = Get-Item $p
    $kb = [math]::Round($item.Length/1KB,0)
    Write-Host ("{0} — {1}KB" -f $name, $kb)
  }else{
    Write-Host ("MISSING — {0}" -f $name)
    $missing += $name
  }
}
if($missing.Count -eq 0){
  Write-Host "✅ All required artifacts present."
  exit 0
}else{
  Write-Host "❌ Missing: $($missing -join ', ')"
  exit 1
}
