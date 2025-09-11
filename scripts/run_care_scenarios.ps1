param(
  [int]$Agents=60,
  [int]$Episodes=150,
  [string[]]$Seeds=@("42","123","7","2025","99"),
  [string]$Context="BALANCE"
)
$Algo = "CARE5G"
$Root = Join-Path "runs" ("care_{0}" -f ($Context.ToLower()))
foreach($s in $Seeds){
  $out = Join-Path $Root ("seed_{0}" -f $s)
  New-Item -ItemType Directory -Path $out -Force | Out-Null
  $cmd = @(
    "python",".\scripts\train_stub.py",
    "--algo",$Algo,"--agents",$Agents,"--episodes",$Episodes,
    "--seed",$s,"--context",$Context,"--out",$out
  ) -join " "
  Write-Host "▶ $cmd"
  cmd /c $cmd
}
Write-Host "`n✅ CARE ($Context) ready." -ForegroundColor Green
