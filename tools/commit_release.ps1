param(
  [switch]$UpdateReleasePack = $false,
  [switch]$IncludePosts      = $true,
  [switch]$IncludePaper      = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Update-ReleasePack {
  $zip = "release\CARE-5G_validation_pack_v1.zip"
  if (-not (Test-Path "release\pack")) { Write-Host "[SKIP] release\pack not found." -ForegroundColor Yellow; return }
  Write-Host "[ZIP] Rebuilding $zip ..." -ForegroundColor Cyan
  Compress-Archive -Path "release\pack\*" -DestinationPath $zip -Force
  Write-Host "[SHA256] Refreshing SHA256SUMS.txt ..." -ForegroundColor Cyan
  Get-ChildItem release -Filter *.zip | %{
    $h=(Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLower()
    "$h *$($_.Name)"
  } | Set-Content release\SHA256SUMS.txt
  git add $zip release\SHA256SUMS.txt
}

function Add-IfExists([string[]]$paths) {
  $toAdd = @()
  foreach($p in $paths){ if (Test-Path $p){ $toAdd += $p } }
  if ($toAdd.Count) { git add $toAdd }
}

# اختياري: تجاهل PDFs في posts مرة واحدة
$gi = ".gitignore"
if (Test-Path $gi) {
  $giText = Get-Content $gi -Raw
  if ($giText -notmatch "(?m)^posts/\*\.pdf$") {
    Add-Content $gi "`nposts/*.pdf"
    git add $gi
  }
}

# 1) تحديث الحزمة إن طلبت
if ($UpdateReleasePack) {
  # ضمّن أي صورة pack محدثة
  Add-IfExists @("release\pack\figs\pareto.png")
  Update-ReleasePack
}

# 2) إضافة ملفات المحتوى (اختياري)
if ($IncludePosts) {
  Add-IfExists @(
    "posts\linkedin_final_*.md",
    "posts\linkedin_first_comment_*.txt",
    "posts\table_*.png"
  )
}
if ($IncludePaper) {
  if (Test-Path "paper") { git add paper }
}

# 3) دائمًا: ضمّن مستندات النتائج إن وُجدت
Add-IfExists @(
  "README.md","stats.csv","stats.md",
  "reports\agg_ci.md","reports\ablation_results.md",
  "figs\fairness_ci.png","figs\fairness_ci.pdf",
  "figs\hyperparam_heatmap.png","figs\hyperparam_heatmap.pdf",
  "tables\*.tex"
)

# 4) الكوميّت (إن وُجد staged)
git diff --staged --quiet
if ($LASTEXITCODE -eq 1) {
  $parts = @()
  if ($UpdateReleasePack) { $parts += "release pack" }
  if ($IncludePosts)      { $parts += "posts" }
  if ($IncludePaper)      { $parts += "paper" }
  if (-not $parts.Count)  { $parts += "docs" }
  $msg = "chore: update " + ($parts -join ", ")
  git commit -m $msg
} else {
  Write-Host "[INFO] Nothing to commit (staging empty)." -ForegroundColor Yellow
}

# 5) الدفع
git push
