param(
  [string]$Tag       = "v0.3",
  [string]$Title     = "CARE-5G v0.3 — 5-seed CI + Ablations + Heatmaps",
  [string]$NotesPath = "release\\notes_v0.9-validation.md",
  [string[]]$Assets  = @("release\\CARE-5G_validation_pack_v1.zip","release\\SHA256SUMS.txt")
)

$ErrorActionPreference = "Stop"

if (-not $env:GITHUB_TOKEN) {
  throw "Set `$env:GITHUB_TOKEN (token with 'repo' scope) before running this script."
}

# Extract owner/repo from origin URL (supports HTTPS & SSH)
$remote = git config --get remote.origin.url
if ($remote -match "github\.com[:/](.+?)/(.+?)(?:\.git)?$") {
  $owner = $Matches[1]
  $repo  = $Matches[2]
} else {
  throw "Cannot parse 'origin' remote for owner/repo."
}

$headers = @{
  Authorization = "token $env:GITHUB_TOKEN"
  "User-Agent"  = "ps-release-script"
  Accept        = "application/vnd.github+json"
}

# Read release notes (PS5-friendly)
$bodyText = ""
if (Test-Path $NotesPath) {
  $bodyText = Get-Content $NotesPath -Raw
}

# Try get existing release by tag
$release = $null
try {
  $release = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$owner/$repo/releases/tags/$Tag" -Method Get
} catch {
  # not found => will create
}

if (-not $release) {
  # Create release
  $payload = @{
    tag_name   = $Tag
    name       = $Title
    body       = $bodyText
    draft      = $false
    prerelease = $false
  } | ConvertTo-Json
  $release = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$owner/$repo/releases" -Method Post -Body $payload
} else {
  # Update name/body if needed
  $patch = @{ name = $Title; body = $bodyText } | ConvertTo-Json
  $release = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$owner/$repo/releases/$($release.id)" -Method Patch -Body $patch
}

# Upload assets (delete old asset with same name if exists)
$uploadUrl = $release.upload_url -replace "{\?name,label}",""
# Fetch current assets list
$currentAssets = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$owner/$repo/releases/$($release.id)/assets" -Method Get

foreach ($f in $Assets) {
  if (-not (Test-Path $f)) { Write-Warning "Missing asset: $f"; continue }

  $name = [IO.Path]::GetFileName($f)
  # If asset with same name exists, delete it
  $existing = $null
  foreach ($a in $currentAssets) {
    if ($a.name -eq $name) { $existing = $a; break }
  }
  if ($existing) {
    Write-Host "Deleting existing asset: $name" -ForegroundColor Yellow
    Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/repos/$owner/$repo/releases/assets/$($existing.id)" -Method Delete
  }

  $ctype = "application/octet-stream"
  if ($name -match "\.zip$") { $ctype = "application/zip" }
  elseif ($name -match "\.txt$") { $ctype = "text/plain" }

  Write-Host "Uploading $name ..." -ForegroundColor Cyan
  Invoke-RestMethod `
    -Headers @{ Authorization = $headers.Authorization; "User-Agent" = $headers."User-Agent"; "Content-Type" = $ctype } `
    -Uri "$uploadUrl?name=$([Uri]::EscapeDataString($name))" -Method Post -InFile $f | Out-Null
}

Write-Host "✅ Release URL: $($release.html_url)" -ForegroundColor Green
