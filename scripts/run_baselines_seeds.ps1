param(
  [int]$Agents=60,
  [int]$Episodes=150,
  [string[]]$Seeds=@("42","123","7","2025","99"),
  [string]$Context="SCARCITY",
  [string[]]$Algos=@("qmix","vdn","iql","pf")
)

# يشغّل لكل خوارزمية ولكل seed ويضمن out فريد: baselines\<algo>\seed_<seed>
foreach($algo in $Algos){
  foreach($s in $Seeds){
    $out = "baselines\${algo}\seed_${s}"
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    # ✳️ عدّل السطر التالي إذا كان اسم سكربت التدريب مختلفًا عندك
    python .\scripts\run_multiseed.py --algo $algo --agents $Agents --episodes $Episodes --seeds $s --context $Context --out $out
  }
}

# تجميع سريع بعد الانتهاء
if (Test-Path .\scripts\aggregate.py) {
  python .\scripts\aggregate.py --root baselines
}
