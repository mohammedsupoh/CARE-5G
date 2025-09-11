param(
  [int]$Agents=60,
  [int]$Episodes=150,
  [int[]]$Seeds=@(42,123,7,2025,99),
  [string]$Context="BALANCE",
  [string[]]$Variants=@("no_fairness_term","no_admission","two_stage")
)

Write-Host "Starting Ablation Study..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path .\runs\ablation -Force | Out-Null

foreach($v in $Variants){
  Write-Host "`nRunning variant: $v" -ForegroundColor Yellow
  foreach($s in $Seeds){
    $out = "runs\ablation\$v\seed_$s"
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    $log = Join-Path $out "train_log.txt"

    $cmd = "python .\scripts\ablation_train.py --variant $v --agents $Agents --episodes $Episodes --seed $s --context $Context --out $out"
    Write-Host ("  Seed {0}..." -f $s) -NoNewline
    cmd /c $cmd 2>&1 | Tee-Object -FilePath $log | Out-Null

    if(Test-Path "$out\aggregate.json"){
      Write-Host " OK" -ForegroundColor Green
    } else {
      Write-Host " FAILED" -ForegroundColor Red
      Write-Host "  See: $log" -ForegroundColor DarkYellow
    }
  }
}

Write-Host "`n✅ Ablations complete!" -ForegroundColor Green

Write-Host "`nAggregating ablation results..." -ForegroundColor Cyan
python .\scripts\aggregate_ablation.py
