param(
  [string]$OutDir = ".\results\CARE_v1.0.0_full",
  [int]$Episodes = 100
)
$env:EPISODES = $Episodes
.\tools\run_smoketest.ps1 -OutDir $OutDir
