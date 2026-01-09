Set-ExecutionPolicy -Scope Process Bypass | Out-Null
if (Test-Path .\.venv\Scripts\Activate.ps1) { . .\.venv\Scripts\Activate.ps1 }

Write-Host "== Atlas B: generate matrix ==" -ForegroundColor Cyan
python .\scripts\make_atlas_B.py --out .\matrices\atlas_B.csv
if ($LASTEXITCODE -ne 0) { throw "make_atlas_B failed" }

Write-Host "== Atlas B: run suite ==" -ForegroundColor Cyan
python .\scripts\run_suite.py --matrix .\matrices\atlas_B.csv --out .\runs\atlas_B
if ($LASTEXITCODE -ne 0) { throw "run_suite failed" }

Write-Host "== Atlas B: plot/report ==" -ForegroundColor Cyan
python .\scripts\plot_atlas_BC.py --runs .\runs\atlas_B --out .\reports\atlas_B
if ($LASTEXITCODE -ne 0) { throw "plot_atlas_BC failed" }

Write-Host "Atlas B complete -> reports\atlas_B" -ForegroundColor Green
