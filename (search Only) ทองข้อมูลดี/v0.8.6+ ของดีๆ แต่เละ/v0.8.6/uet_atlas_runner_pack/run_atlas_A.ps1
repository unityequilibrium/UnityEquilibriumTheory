Set-ExecutionPolicy -Scope Process Bypass | Out-Null
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
if (Test-Path "$repoRoot\.venv\Scripts\Activate.ps1") { . "$repoRoot\.venv\Scripts\Activate.ps1" }

Write-Host "== Atlas A: generate matrix ==" -ForegroundColor Cyan
python "$repoRoot\scripts\gen_atlas_matrix.py" --preset stage1 --out "$repoRoot\matrices\atlas_A.csv"
if ($LASTEXITCODE -ne 0) { throw "gen_atlas_matrix failed" }

Write-Host "== Atlas A: run suite ==" -ForegroundColor Cyan
python "$repoRoot\scripts\run_suite.py" --matrix "$repoRoot\matrices\atlas_A.csv" --out "$repoRoot\runs\atlas_A"
if ($LASTEXITCODE -ne 0) { throw "run_suite failed" }

Write-Host "== Atlas A: plot ==" -ForegroundColor Cyan
python "$repoRoot\scripts\summarize_atlas.py" --runs_root "$repoRoot\runs\atlas_A"
if ($LASTEXITCODE -ne 0) { throw "summarize_atlas failed" }

Write-Host "Atlas A complete -> reports\atlas_A" -ForegroundColor Green
