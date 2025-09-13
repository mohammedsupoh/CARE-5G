param(
  [string]$OutDir = ".\results\smoke"
)

# اكتشاف بايثون (python أو py -3)
$python = $null
$pyArgs = @()
try { & python --version *> $null; $python = "python" } catch {}
if(-not $python){
  try { & py -3 --version *> $null; $python = "py"; $pyArgs = @("-3") } catch {}
}
if(-not $python){
  Write-Error "Python not found. Install Python 3.9+ and ensure it's in PATH."
  exit 2
}

# التحقق من التبعيات (numpy, matplotlib)
& $python @pyArgs "-c" "import numpy, matplotlib" *> $null
if($LASTEXITCODE -ne 0){
  Write-Host "Installing required packages (numpy, matplotlib) ..."
  & $python @pyArgs "-m" "pip" "install" "--upgrade" "pip"
  & $python @pyArgs "-m" "pip" "install" "numpy" "matplotlib"
}

# تشغيل مولّد الـ Smoke Test
& $python @pyArgs ".\tools\smoketest_generate.py" $OutDir

# التحقق وإعداد التقرير إن توفرت الأدوات
if(Test-Path ".\tools\validate_metrics.ps1"){ .\tools\validate_metrics.ps1 -Path (Join-Path $OutDir "metrics.json") }
if(Test-Path ".\tools\check_artifacts.ps1"){  .\tools\check_artifacts.ps1 -Dir  $OutDir }
if(Test-Path ".\tools\make_claude_report.ps1"){ .\tools\make_claude_report.ps1 -Dir $OutDir -Out ".\CLAUDE_SmokeTest_Report.txt" }
