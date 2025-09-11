# tools\fix_cite.ps1 — Add/Replace "Cite this work" in README.md
param(
  [string]$Version = "v1.0.3",
  [string]$DOI     = "10.5281/zenodo.17102480"
)

$DOIUrl  = "https://doi.org/$DOI"
$key     = ("CARE5G_Supoh_{0}" -f ($Version -replace '[^0-9A-Za-z_\.]','_')).ToString()
$year    = (Get-Date -Format yyyy)
$root    = (Get-Location).Path
$readme  = Join-Path $root "README.md"

if (-not (Test-Path $readme)) { Set-Content -Path $readme -Value "# CARE-5G`r`n" -Encoding UTF8 }

$nl = "`r`n"
$bibLines = @()
$bibLines += '<!-- CITATION-START -->'
$bibLines += '## Cite this work'
$bibLines += ''
$bibLines += 'If you use this repository, please cite:'
$bibLines += ''
$bibLines += "**DOI:** $DOIUrl"
$bibLines += ''
$bibLines += '```bibtex'
$bibLines += "@software{$key,"
$bibLines += "  author  = {Supoh, Mohammed Hifze},"
$bibLines += "  title   = {CARE-5G: Fairness-Aware Resource Allocation for 5G},"
$bibLines += "  version = {$Version},"
$bibLines += "  year    = {$year},"
$bibLines += "  doi     = {$DOI},"
$bibLines += "  url     = {$DOIUrl}"
$bibLines += "}"
$bibLines += '```'
$bibLines += '<!-- CITATION-END -->'
$bib = ($bibLines -join $nl)

try { $content = Get-Content -Path $readme -Raw -ErrorAction Stop } catch { $content = "" }
if ($null -eq $content) { $content = "" }

$reMarkers = '(?is)<!--\s*CITATION-START\s*-->.*?<!--\s*CITATION-END\s*-->'
$reHeading = '(?ims)^##\s*Cite\s*this\s*work.*?(?=^\s*##\s+|\z)'

if ([regex]::IsMatch([string]$content, $reMarkers)) {
  $new = [regex]::Replace([string]$content, $reMarkers, $bib)
} elseif ([regex]::IsMatch([string]$content, $reHeading)) {
  $new = [regex]::Replace([string]$content, $reHeading, $bib)
} else {
  $sep = if ($content -match '\S$') { $nl + $nl } else { "" }
  $new = $content + $sep + $bib + $nl
}

Set-Content -Path $readme -Value $new -Encoding UTF8
Write-Host "=== WROTE Cite section to README.md ==="
Select-String -Path $readme -Pattern "Cite this work","@software" -SimpleMatch | ForEach-Object { $_.Line }
