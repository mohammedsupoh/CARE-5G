param(
  [string]$Py = "python",
  [string]$SitePkgs = "C:\Python310\Lib\site-packages"
)

Write-Host ">> Cleaning bogus entries in $SitePkgs ..."
$bad = @('-', '-p', '-ip')
foreach($name in $bad){
  $p = Join-Path $SitePkgs $name
  if(Test-Path $p){
    Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
  }
}
# أي مجلدات .dist-info تبدأ بشرطة "-"
Get-ChildItem $SitePkgs -Directory -Force |
  Where-Object { $_.Name -match '^\-.*\.dist-info$' } |
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ">> Purging pip cache ..."
& $Py -m pip cache purge | Out-Null

Write-Host ">> Reinstalling pip cleanly ..."
& $Py -m pip install --upgrade --force-reinstall pip
