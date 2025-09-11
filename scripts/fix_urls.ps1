param(
  [string]$Old = "https://github.com/mohammedsupoh/CARE-5G",
  [string]$New = "https://github.com/mohammedsupoh/CARE-5G"
)

Write-Host "Replacing:`n  $Old`n→ $New" -ForegroundColor Cyan

# استهدف ملفات نصية شائعة فقط (تجنب الثنائية)
$patterns = "*.md","*.tex","*.yml","*.yaml","*.ps1","*.py"
$files = Get-ChildItem -Recurse -Include $patterns -File | Where-Object { $_.FullName -notmatch "\\\.git\\" }

$changed = @()
foreach ($f in $files) {
  $raw = Get-Content $f.FullName -Raw -ErrorAction Stop
  $newRaw = $raw -replace [regex]::Escape($Old), $New `
                  -replace "mohammedsupoh", "mohammedsupoh"  # احتياط إن ذُكر الاسم فقط
  if ($newRaw -ne $raw) {
    $newRaw | Set-Content $f.FullName -Encoding UTF8
    $changed += $f.FullName
    Write-Host "Updated: $($f.FullName)" -ForegroundColor Green
  }
}

if ($changed.Count -gt 0) {
  git add $changed
  git commit -m "Update links to new username (supoh)"
  git push
  Write-Host "`nDone. Updated $($changed.Count) file(s) and pushed." -ForegroundColor Green
} else {
  Write-Host "No files needed updates." -ForegroundColor Yellow
}

