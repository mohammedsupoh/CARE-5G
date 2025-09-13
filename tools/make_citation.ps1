# يولّد CITATION.cff بصيغة YAML صحيحة (بدون أي توسعة متغيّرات داخلية)
param(
  [string]$RepoUrl = "https://github.com/<your-user>/CARE-5G",
  [string]$Version = "v1.0.0"
)

$today = Get-Date -Format yyyy-MM-dd
$yaml = @()
$yaml += "cff-version: 1.2.0"
$yaml += "title: CARE: Redefining Success in 5G Network Slicing"
$yaml += ("version: {0}" -f $Version)
$yaml += "authors:"
$yaml += "  - family-names: Supoh"
$yaml += "    given-names: Mohammed Hifze"
$yaml += ("date-released: {0}" -f $today)
$yaml += ("repository-code: {0}" -f $RepoUrl)
$yaml += "preferred-citation:"
$yaml += "  type: software"
$yaml += "  title: CARE-5G"

$yaml | Set-Content -Path .\CITATION.cff -Encoding UTF8
Write-Host "✅ CITATION.cff created"
