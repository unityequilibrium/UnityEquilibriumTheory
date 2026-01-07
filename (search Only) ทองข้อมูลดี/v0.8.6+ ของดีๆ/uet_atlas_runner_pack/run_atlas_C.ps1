Set-ExecutionPolicy -Scope Process Bypass | Out-Null
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
if (Test-Path "$repoRoot\.venv\Scripts\Activate.ps1") { . "$repoRoot\.venv\Scripts\Activate.ps1" }

Write-Host "== Atlas C: generate matrix ==" -ForegroundColor Cyan
python "$repoRoot\scripts\gen_atlas_matrix.py" --preset stage1 --out "$repoRoot\matrices\atlas_C.csv"
if ($LASTEXITCODE -ne 0) { throw "gen_atlas_matrix failed" }

Write-Host "== Atlas C: run suite ==" -ForegroundColor Cyan
python "$repoRoot\scripts\run_suite.py" --matrix "$repoRoot\matrices\atlas_C.csv" --out "$repoRoot\runs\atlas_C"
if ($LASTEXITCODE -ne 0) { throw "run_suite failed" }

Write-Host "== Atlas C: plot ==" -ForegroundColor Cyan
python "$repoRoot\scripts\summarize_atlas.py" --runs_root "$repoRoot\runs\atlas_C"
if ($LASTEXITCODE -ne 0) { throw "summarize_atlas failed" }

Write-Host "Atlas C complete -> reports\atlas_C" -ForegroundColor Green
