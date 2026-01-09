# Run UET Parameter Qualification (C_I)
# From repo root (uet_harness_v0_1):
#   powershell -ExecutionPolicy Bypass -File .\run_param_qual_CI.ps1
$env:PYTHONPATH="."

Write-Host "=== 1) C_I beta sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_beta_sweep.csv --out runs_param_CI_beta --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_beta --out_csv runs_param_CI_beta/validation.csv --json

Write-Host "=== 2) C_I kC / kI sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_k_sweep.csv --out runs_param_CI_k --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_k --out_csv runs_param_CI_k/validation.csv --json

Write-Host "=== 3) C_I MC / MI sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_M_sweep.csv --out runs_param_CI_M --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_M --out_csv runs_param_CI_M/validation.csv --json

Write-Host "=== 4) C_I deltaC / deltaI sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_delta_sweep.csv --out runs_param_CI_delta --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_delta --out_csv runs_param_CI_delta/validation.csv --json

Write-Host "DONE."
