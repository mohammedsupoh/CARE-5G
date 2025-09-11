param(
  [int]$Agents=60,
  [int]$Episodes=150,
  [string[]]$Seeds=@("42","123","7","2025","99"),
  [string]$Context="SCARCITY",
  [string[]]$Algos=@("QMIX","VDN","IQL","PF")
)

# نضمن المجلد
New-Item -ItemType Directory -Path .\baselines -Force | Out-Null

foreach($algo in $Algos){
  foreach($s in $Seeds){
    $out = "baselines\${algo}\seed_${s}"
    New-Item -ItemType Directory -Path $out -Force | Out-Null

    $cmd = @(
      "python",".\scripts\train_stub.py",
      "--algo",$algo,"--agents",$Agents,"--episodes",$Episodes,
      "--seed",$s,"--context",$Context,"--out",$out
    ) -join " "
    Write-Host "▶ $cmd"
    cmd /c $cmd
  }
}
Write-Host "`n✅ Done generating baselines." -ForegroundColor Green
