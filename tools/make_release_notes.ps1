param([string]$Dir = ".\results\CARE_v1.0.0_full")

$metrics = Join-Path $Dir "metrics.json"
if(-not (Test-Path $metrics)){ Write-Error "metrics.json not found in $Dir"; exit 2 }
$j = Get-Content $metrics -Raw | ConvertFrom-Json

$passE = [double]$j.final.efficiency -ge 0.80
$passF = [double]$j.final.fairness   -ge 0.70
$passC = [bool]$j.convergence.achieved -and ([int]$j.convergence.episode -lt 50)
$passAll = $passE -and $passF -and $passC
$result = if($passAll){"Met"} else {"Not Met"}

$lines = @()
$lines += "# Release Notes — v1.0.0"
$lines += "- Context: SCARCITY"
$lines += ("- Episodes: {0}" -f [int]$j.episodes_trained)
$lines += "- Targets: Efficiency ≥ 0.80 & Fairness ≥ 0.70"
$lines += ("- Result: {0} (E={1:N3}, F={2:N3})" -f $result, [double]$j.final.efficiency, [double]$j.final.fairness)

$lines | Set-Content -Path .\RELEASE_NOTES.md -Encoding UTF8
Write-Host "✅ RELEASE_NOTES.md created"
