Set-ExecutionPolicy -Scope Process Bypass | Out-Null
if (Test-Path .\.venv\Scripts\Activate.ps1) { . .\.venv\Scripts\Activate.ps1 }

if (!(Test-Path .\scripts\grid_audit.py)) {
  Write-Host "scripts\grid_audit.py not found. Skip." -ForegroundColor Yellow
  exit 0
}

Write-Host "== Grid audit ==" -ForegroundColor Cyan
python .\scripts\grid_audit.py --out .\reports\grid_audit
if ($LASTEXITCODE -ne 0) { throw "grid_audit failed" }

Write-Host "Grid audit complete -> reports\grid_audit" -ForegroundColor Green
