param(
  [string]$Dir = ".\results\smoke",
  [string]$Out = ".\CLAUDE_SmokeTest_Report.txt"
)

# مسارات
$metricsPath = Join-Path $Dir "metrics.json"

# شغّل أداة التحقق من السكيمة
$validateOut = & .\tools\validate_metrics.ps1 -Path $metricsPath 2>&1
# شغّل أداة فحص المخرجات
$artifactsOut = & .\tools\check_artifacts.ps1 -Dir $Dir 2>&1

# حمّل JSON (كما هو) لطباعته خامًا
if (Test-Path $metricsPath) {
  $metricsRaw = Get-Content -Raw -Path $metricsPath
} else {
  $metricsRaw = "<metrics.json NOT FOUND>"
}

# ابنِ التقرير النهائي
$NL = [Environment]::NewLine
$report = @()
$report += "CARE — Smoke Test — Report to Claude"
$report += "Directory: $Dir"
$report += ""
$report += "=== metrics.json (full content) ==="
$report += $metricsRaw
$report += ""
$report += "=== File List & Sizes ==="
$report += ($artifactsOut -join $NL)
$report += ""
$report += "=== Validation Messages ==="
$report += ($validateOut -join $NL)
$report += ""
$report += "=== Notes ==="
$report += "- Schema check above should show ✅ if all fields match exactly."
$report += "- Figures must start with CARE_ and be .png"
$report += "- Zip file must exist and be named CARE-v1.0.0-smoketest.zip"

$reportText = $report -join $NL
$reportText | Set-Content -Path $Out -Encoding UTF8

Write-Host "✅ Report generated:" (Resolve-Path $Out)
