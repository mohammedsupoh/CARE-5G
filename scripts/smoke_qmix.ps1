param(
  [int]$Agents=60,
  [int]$Episodes=5,
  [int]$Seed=42,
  [string]$Context="SCARCITY"
)

# === 1) ابحث عن ملف التدريب تلقائياً ===
$names = @('train.py','baseline_train.py','main.py','run.py','runner.py')
$files = @()
foreach($n in $names){
  $files += Get-ChildItem -Path . -Recurse -File -Filter $n -ErrorAction SilentlyContinue
}
# استبعد مجلدات غير مفيدة
$rx = '\\(\.git|venv|env|site-packages|__pycache__|build|dist)\\'
$files = $files | Where-Object { $_.FullName -notmatch $rx }

if(-not $files -or $files.Count -eq 0){
  Write-Host "[ERR] لم أجد ملف تدريب. نفّذ للتحقق:" -ForegroundColor Yellow
  Write-Host "Get-ChildItem -Recurse -File -Filter train*.py | Select-Object FullName" -ForegroundColor Yellow
  exit 1
}

$trainer = $files[0].FullName
Write-Host ">>> Using trainer: $trainer"

# === 2) اكتشف علم الخوارزمية من --help ===
$help = & python "$trainer" -h 2>&1
if     ($help -match '--algo')       { $AF='--algo' }
elseif ($help -match '--method')     { $AF='--method' }
elseif ($help -match '--baseline')   { $AF='--baseline' }
else   { $AF='--algo' }  # افتراضي

# === 3) نفّذ تجربة دخانية لِـ QMIX وبحفظ لوج ===
$out = "baselines\qmix\seed_$Seed"
New-Item -ItemType Directory -Path $out -Force | Out-Null

$cmd = "python `"$trainer`" $AF qmix --agents $Agents --episodes $Episodes --seed $Seed --context $Context --out `"$out`""
Write-Host ">>> $cmd"
cmd /c $cmd 2>&1 | Tee-Object -FilePath "$out\train_log.txt"

if (Test-Path "$out\aggregate.json") {
  Write-Host "[OK] aggregate.json -> $out\aggregate.json" -ForegroundColor Green
} else {
  Write-Host "[WARN] No aggregate.json in $out (راجع $out\train_log.txt)" -ForegroundColor Yellow
}
