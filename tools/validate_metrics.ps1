param(
  [Parameter(Mandatory=$true)][string]$Path
)
function Is-Number($v){ return ($v -is [double]) -or ($v -is [int]) -or ($v -is [decimal]) }
if(!(Test-Path $Path)){ Write-Error "metrics.json not found: $Path"; exit 2 }
$json = Get-Content -Raw -Path $Path | ConvertFrom-Json

$fail = @()
function Add-Fail($m){ $script:fail += $m }

# وجود الحقول الأساسية
if(-not $json.experiment){ Add-Fail "missing: experiment" }
if(-not $json.timestamp){ Add-Fail "missing: timestamp" }
if(-not $json.context){ Add-Fail "missing: context" }
if(-not $json.agents){ Add-Fail "missing: agents" }
if(-not $json.episodes_trained){ Add-Fail "missing: episodes_trained" }
if(-not $json.final){ Add-Fail "missing: final{...}" }
if(-not $json.convergence){ Add-Fail "missing: convergence{...}" }
if(-not $json.recent_10_episodes){ Add-Fail "missing: recent_10_episodes{...}" }
if(-not $json.best_achieved){ Add-Fail "missing: best_achieved{...}" }

# تحقق من القيم الأساسية
if($json.experiment -ne "CARE_v1.0.0"){ Add-Fail "experiment must be CARE_v1.0.0" }
if($json.context -ne "SCARCITY"){ Add-Fail "context must be SCARCITY" }
if($json.agents -ne 60){ Add-Fail "agents must be 60" }

# final
if($json.final){
  if(-not (Is-Number $json.final.efficiency)){ Add-Fail "final.efficiency must be number" }
  if(-not (Is-Number $json.final.fairness)){ Add-Fail "final.fairness must be number" }
  if(-not (Is-Number $json.final.satisfaction)){ Add-Fail "final.satisfaction must be number" }
}

# convergence
if($json.convergence){
  if(-not ($json.convergence.achieved -is [bool])){ Add-Fail "convergence.achieved must be boolean" }
  if(($null -ne $json.convergence.episode) -and (-not (Is-Number $json.convergence.episode))){
    Add-Fail "convergence.episode must be number or null"
  }
}

# recent_10_episodes
if($json.recent_10_episodes){
  if(-not (Is-Number $json.recent_10_episodes.efficiency_mean)){ Add-Fail "recent_10_episodes.efficiency_mean must be number" }
  if(-not (Is-Number $json.recent_10_episodes.fairness_mean)){ Add-Fail "recent_10_episodes.fairness_mean must be number" }
  if(-not (Is-Number $json.recent_10_episodes.satisfaction_mean)){ Add-Fail "recent_10_episodes.satisfaction_mean must be number" }
}

# best_achieved
if($json.best_achieved){
  if(-not (Is-Number $json.best_achieved.efficiency)){ Add-Fail "best_achieved.efficiency must be number" }
  if(-not (Is-Number $json.best_achieved.fairness)){ Add-Fail "best_achieved.fairness must be number" }
  if(-not (Is-Number $json.best_achieved.at_episode)){ Add-Fail "best_achieved.at_episode must be number" }
}

if($fail.Count -eq 0){
  Write-Host "✅ metrics.json schema OK"
  "{0,-18} {1}" -f "efficiency:", $json.final.efficiency
  "{0,-18} {1}" -f "fairness:",   $json.final.fairness
  "{0,-18} {1}" -f "satisfaction:",$json.final.satisfaction
  "{0,-18} {1}" -f "converged?:", $json.convergence.achieved
  if($json.convergence.episode){ "{0,-18} {1}" -f "at episode:", $json.convergence.episode }
  exit 0
}else{
  Write-Host "❌ metrics.json schema issues:"
  $fail | ForEach-Object { Write-Host " - $_" }
  exit 1
}
