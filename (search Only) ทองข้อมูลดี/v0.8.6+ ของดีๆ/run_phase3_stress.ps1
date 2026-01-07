# Phase3: Combined stress + scaling checks (ledger-only validation)
# Place the CSV matrices into .\matrices\ and the validator into .\scripts\
$env:PYTHONPATH="."

Write-Host "=== 1) Stress C_only (random) ==="
python scripts/run_suite.py --matrix matrices/UET_Stress_C_only_v1.csv --out runs_stress_Conly --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_stress_ledger.py --runs runs_stress_Conly --out_csv runs_stress_Conly/validation_stress.csv --max_backtracks 0 --omega_nan_fail

Write-Host "=== 2) Stress C_I (random asymmetry) ==="
python scripts/run_suite.py --matrix matrices/UET_Stress_CI_v1.csv --out runs_stress_CI --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_stress_ledger.py --runs runs_stress_CI --out_csv runs_stress_CI/validation_stress.csv --max_backtracks 0 --omega_nan_fail

Write-Host "=== 3) Scaling check grid=128 subset ==="
python scripts/run_suite.py --matrix matrices/UET_Scale_grid128_v1.csv --out runs_scale_128 --progress_every_s 10 --wall_timeout_s 1200
python scripts/validate_stress_ledger.py --runs runs_scale_128 --out_csv runs_scale_128/validation_stress.csv --max_backtracks 0 --omega_nan_fail

Write-Host "DONE."
