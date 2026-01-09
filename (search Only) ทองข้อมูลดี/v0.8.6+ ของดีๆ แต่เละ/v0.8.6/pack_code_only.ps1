# pack_code_only.ps1
# Create a code-only zip pack (no simulation data)
# Output: uet_code_only_pack.zip

$repoRoot = $PSScriptRoot
$zipName = "uet_code_only_pack.zip"
$zipPath = Join-Path $repoRoot $zipName
$tempDir = Join-Path $env:TEMP "uet_code_pack_$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "Creating code-only pack..." -ForegroundColor Cyan

# Clean __pycache__ first
Write-Host "  Cleaning __pycache__..." -ForegroundColor Yellow
Get-ChildItem -Path $repoRoot -Recurse -Force -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $repoRoot -Recurse -Force -File -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Create temp directory
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Check uet_core exists
$uetCore = Join-Path $repoRoot "uet_core"
if (-not (Test-Path $uetCore)) {
  Write-Host "ERROR: uet_core/ not found! Cannot create valid pack." -ForegroundColor Red
  exit 1
}

# Copy essential folders
Write-Host "  Copying scripts..." -ForegroundColor Yellow
Copy-Item (Join-Path $repoRoot "scripts") (Join-Path $tempDir "scripts") -Recurse -Force

Write-Host "  Copying uet_core..." -ForegroundColor Yellow
Copy-Item $uetCore (Join-Path $tempDir "uet_core") -Recurse -Force

Write-Host "  Copying matrices..." -ForegroundColor Yellow
if (Test-Path (Join-Path $repoRoot "matrices")) {
  Copy-Item (Join-Path $repoRoot "matrices") (Join-Path $tempDir "matrices") -Recurse -Force
}

Write-Host "  Copying docs..." -ForegroundColor Yellow
if (Test-Path (Join-Path $repoRoot "docs")) {
  Copy-Item (Join-Path $repoRoot "docs") (Join-Path $tempDir "docs") -Recurse -Force
}

Write-Host "  Copying schemas..." -ForegroundColor Yellow
if (Test-Path (Join-Path $repoRoot "schemas")) {
  Copy-Item (Join-Path $repoRoot "schemas") (Join-Path $tempDir "schemas") -Recurse -Force
}

# Copy root-level files (NO reports)
Write-Host "  Copying root files..." -ForegroundColor Yellow
Get-ChildItem $repoRoot -File | Where-Object { 
  $_.Extension -in @(".py", ".ps1", ".md", ".txt", ".json", ".toml", ".cfg") -or
  $_.Name -in @("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "requirements_frozen.txt")
} | ForEach-Object {
  Copy-Item $_.FullName $tempDir -Force
}

# Clean __pycache__ from temp (in case it was copied)
Get-ChildItem -Path $tempDir -Recurse -Force -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $tempDir -Recurse -Force -File -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Remove old zip if exists
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

# Create zip
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Cleanup temp
Remove-Item $tempDir -Recurse -Force

# Summary
$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "`nDone!" -ForegroundColor Green
Write-Host "Output: $zipPath"
Write-Host "Size: $([math]::Round($zipSize, 2)) MB"

# Quick verify
Write-Host "`nVerifying pack contents..." -ForegroundColor Yellow
$testExtract = Join-Path $env:TEMP "uet_verify_$(Get-Date -Format 'yyyyMMddHHmmss')"
Expand-Archive -Path $zipPath -DestinationPath $testExtract -Force
$hasUetCore = Test-Path (Join-Path $testExtract "uet_core")
$hasScripts = Test-Path (Join-Path $testExtract "scripts")
Remove-Item $testExtract -Recurse -Force

if ($hasUetCore -and $hasScripts) {
  Write-Host "  OK: uet_core/ present" -ForegroundColor Green
  Write-Host "  OK: scripts/ present" -ForegroundColor Green
}
else {
  Write-Host "  ERROR: Missing essential folders!" -ForegroundColor Red
}
