param(
  [int]$Agents=60,
  [int]$Episodes=5,
  [int]$Seed=42,
  [string]$Context="SCARCITY"
)

# 1) ابحث عن ملف التدريب تلقائياً داخل المشروع
$names = @('train.py','main.py','run.py','runner.py','baseline_train.py')
$files = @()
foreach($n in $names){
  $files += Get-ChildItem -Path . -Recurse -File -Filter $n -ErrorAction SilentlyContinue
}
# استبعد مجلدات غير مفيدة
$rx = '\\(\.git|venv|env|site-packages|__pycache__|build|dist)\\'
$files = $files | Where-Object { $_.FullName -notmatch $rx }

if(-not $files -or $files.Count -eq 0){
  Write-Host "[ERR] لم أجد ملف تدريب. جرّب للتشخيص:" -ForegroundColor Yellow
  Write-Host 'Get-ChildItem -Recurse -File -Include *train*.py | Select-Object FullName' -ForegroundColor Yellow
  exit 1
}

$trainer = $files[0].FullName
Write-Host ">>> Using trainer: $trainer"

# 2) اكتشف علم الخوارزمية من --help
$help = & python "$trainer" -h 2>&1
if     ($help -match '--algo')       { $AF='--algo' }
elseif ($help -match '--method')     { $AF='--method' }
elseif ($help -match '--baseline')   { $AF='--baseline' }
else   { $AF='--algo' }  # افتراضي

# 3) أنشئ مجلد الإخراج واحفظ اللوج
$out = "baselines\qmix\seed_$Seed"
New-Item -ItemType Directory -Path $out -Force | Out-Null

$cmd = 'python "{0}" {1} qmix --agents {2} --episodes {3} --seed {4} --context {5} --out "{6}"' -f $trainer, $AF, $Agents, $Episodes, $Seed, $Context, (Resolve-Path $out)
Write-Host ">>> $cmd"
cmd /c $cmd 2>&1 | Tee-Object -FilePath "$out\train_log.txt"

if (Test-Path "$out\aggregate.json") {
  Write-Host "[OK] aggregate.json -> $out\aggregate.json" -ForegroundColor Green
} else {
  Write-Host "[WARN] No aggregate.json in $out (راجع آخر سطور اللوج أدناه)" -ForegroundColor Yellow
  if (Test-Path "$out\train_log.txt") { Get-Content "$out\train_log.txt" -Tail 40 }
}
