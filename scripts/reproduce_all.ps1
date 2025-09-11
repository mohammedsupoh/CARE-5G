# scripts/reproduce_all.ps1
param([switch]$MakeZip)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
function Run($cmd) { Write-Host "▶ $cmd" -ForegroundColor Cyan; & powershell -NoLogo -NoProfile -Command $cmd }

# 0) Python deps
Run "python -m pip install --upgrade pip"
Run "python -m pip install numpy scipy matplotlib"

# 1) CARE multi-seed
if (Test-Path .\scripts\run_multiseed.py) { Run "python scripts/run_multiseed.py" } else { Write-Host "[SKIP] run_multiseed.py not found" -ForegroundColor Yellow }

# 2) Baselines
if (Test-Path .\scripts\run_baselines.py) { Run "python scripts/run_baselines.py" } else { Write-Host "[SKIP] run_baselines.py not found" -ForegroundColor Yellow }

# 3) Stats + p-values + markdown
if (Test-Path .\scripts\stats_compare.py) { Run "python scripts/stats_compare.py --care runs --out stats.csv --md stats.md" } else { Write-Host "[SKIP] stats_compare.py not found" -ForegroundColor Yellow }

# 4) Plots
if (Test-Path .\scripts\pareto_plot.py)      { Run "python scripts/pareto_plot.py" }      else { Write-Host "[SKIP] pareto_plot.py not found" -ForegroundColor Yellow }
if (Test-Path .\scripts\plot_convergence.py) { Run "python scripts/plot_convergence.py" } else { Write-Host "[SKIP] plot_convergence.py not found" -ForegroundColor Yellow }

# 5) LaTeX tables
if (Test-Path .\scripts\make_latex_tables.py) { Run "python scripts/make_latex_tables.py" } else { Write-Host "[SKIP] make_latex_tables.py not found" -ForegroundColor Yellow }

# 6) (Optional) build ZIP
if ($MakeZip) {
  $pack = "release\pack"
  $dirs = @("$pack","$pack\baselines","$pack\figs","$pack\tables","$pack\scripts")
  foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }

  if (Test-Path .\aggregate.json) { Copy-Item .\aggregate.json $pack -Force }
  if (Test-Path .\baselines) {
    Get-ChildItem .\baselines -Directory | %{
      $algo=$_.Name; $src = Join-Path $_.FullName 'aggregate.json'
      if (Test-Path $src) { $dst = Join-Path $pack ("baselines\"+$algo); New-Item -ItemType Directory -Path $dst -Force | Out-Null; Copy-Item $src $dst -Force }
    }
  }
  if (Test-Path .\figs)   { Copy-Item .\figs\*.png   "$pack\figs\"   -Force -ErrorAction SilentlyContinue }
  if (Test-Path .\tables) { Copy-Item .\tables\*.tex "$pack\tables\" -Force -ErrorAction SilentlyContinue }

  "aggregate.py","run_multiseed.py","run_baselines.py","stats_compare.py","pareto_plot.py","plot_convergence.py","make_latex_tables.py" | % {
    if (Test-Path ".\scripts\$_") { Copy-Item ".\scripts\$_" "$pack\scripts\" -Force }
  }

  if (Test-Path .\release\MANIFEST.md) { Copy-Item .\release\MANIFEST.md $pack -Force }
  $zip = "release\CARE-5G_validation_pack_v1.zip"
  if (Test-Path $zip) { Remove-Item $zip -Force }
  Compress-Archive -Path "$pack\*" -DestinationPath $zip -Force
  (Get-FileHash $zip -Algorithm SHA256).Hash | Set-Content .\release\SHA256SUMS.txt
  Write-Host "`nArtifacts ready in .\release" -ForegroundColor Green
}

Write-Host "`nDONE. Artifacts:" -ForegroundColor Green
Write-Host " - stats.csv, stats.md"
Write-Host " - figs\pareto.png + figs\conv_*.png (if available)"
Write-Host " - tables\comparison.tex, tables\metrics_summary.tex"
