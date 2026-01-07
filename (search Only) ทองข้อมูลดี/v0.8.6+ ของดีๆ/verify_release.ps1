# verify_release.ps1
# Quick verification script for release package

$repoRoot = $PSScriptRoot
$errors = @()

Write-Host "=== UET Release Verification ===" -ForegroundColor Cyan

# 1. Check essential files
Write-Host "`n[1] Checking essential files..." -ForegroundColor Yellow
$essentials = @(
  "scripts/run_suite.py",
  "scripts/aggregate_final_summary.py",
  "scripts/plot_phase_maps.py",
  "requirements.txt",
  "README.md",
  "run_all_cross_sweep.ps1"
)

foreach ($f in $essentials) {
  $path = Join-Path $repoRoot $f
  if (Test-Path $path) {
    Write-Host "  OK: $f" -ForegroundColor Green
  }
  else {
    Write-Host "  MISSING: $f" -ForegroundColor Red
    $errors += "Missing: $f"
  }
}

# 2. Check Python
Write-Host "`n[2] Checking Python..." -ForegroundColor Yellow
try {
  $pyVer = py -V 2>&1
  Write-Host "  OK: $pyVer" -ForegroundColor Green
}
catch {
  Write-Host "  ERROR: Python not found" -ForegroundColor Red
  $errors += "Python not found"
}

# 3. Check imports
Write-Host "`n[3] Checking Python imports..." -ForegroundColor Yellow
$testImport = py -c "import numpy, pandas, matplotlib; print('OK')" 2>&1
if ($testImport -eq "OK") {
  Write-Host "  OK: numpy, pandas, matplotlib" -ForegroundColor Green
}
else {
  Write-Host "  ERROR: Missing dependencies" -ForegroundColor Red
  $errors += "Missing Python dependencies"
}

# 4. Check matrices
Write-Host "`n[4] Checking matrices..." -ForegroundColor Yellow
$matrices = Get-ChildItem (Join-Path $repoRoot "matrices") -Filter "*.csv" -ErrorAction SilentlyContinue
if ($matrices.Count -gt 0) {
  Write-Host "  OK: $($matrices.Count) matrix files found" -ForegroundColor Green
}
else {
  Write-Host "  WARNING: No matrix files" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($errors.Count -eq 0) {
  Write-Host "All checks PASSED!" -ForegroundColor Green
}
else {
  Write-Host "Found $($errors.Count) error(s):" -ForegroundColor Red
  $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
