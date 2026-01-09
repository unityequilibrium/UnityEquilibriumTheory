
# Run UET Parameter Qualification (C_only)
# Usage: from repo root (uet_harness_v0_1):  powershell -ExecutionPolicy Bypass -File .\run_param_qual.ps1

$env:PYTHONPATH="."

Write-Host "=== 1) delta (=lambda) sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_delta_ext.csv --out runs_param_delta_ext --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_delta_ext --out_csv runs_param_delta_ext/validation.csv --json

Write-Host "=== 2) kappa sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_kappa_sweep.csv --out runs_param_kappa --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_kappa --out_csv runs_param_kappa/validation.csv --json

Write-Host "=== 3) M sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_M_sweep.csv --out runs_param_M --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_M --out_csv runs_param_M/validation.csv --json

Write-Host "DONE."
