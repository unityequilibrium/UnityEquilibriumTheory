param(
  [string]$PythonExe = "python"
)

Write-Host "== Ensure venv =="
if (!(Test-Path ".\.venv")) {
  & $PythonExe -m venv .venv
}
# Activate
. .\.venv\Scripts\Activate.ps1

python -m pip install -U pip | Out-Host

# Minimal deps for dashboards/plots (adjust if your repo has requirements.txt)
$req = @("numpy","pandas","matplotlib")
foreach ($p in $req) {
  pip install $p | Out-Host
}

Write-Host "== Python used: ==" -ForegroundColor Green
python -c "import sys; print(sys.executable)"
