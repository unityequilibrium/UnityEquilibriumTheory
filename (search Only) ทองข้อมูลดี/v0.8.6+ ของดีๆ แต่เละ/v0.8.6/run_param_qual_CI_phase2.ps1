# Run UET C_I parameter qualification (phase 2: ratios + asymmetries)
$env:PYTHONPATH="."

Write-Host "=== 1) kC/kI ratio sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_k_ratio_sweep.csv --out runs_param_CI_k_ratio --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_k_ratio --out_csv runs_param_CI_k_ratio/validation.csv --json

Write-Host "=== 2) MC/MI ratio sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_M_ratio_sweep.csv --out runs_param_CI_M_ratio --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_M_ratio --out_csv runs_param_CI_M_ratio/validation.csv --json

Write-Host "=== 3) delta asymmetry sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_delta_asym_sweep.csv --out runs_param_CI_delta_asym --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_delta_asym --out_csv runs_param_CI_delta_asym/validation.csv --json

Write-Host "=== 4) s (tilt) sweep ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_s_sweep.csv --out runs_param_CI_s --progress_every_s 10 --wall_timeout_s 900
python scripts/validate_suite.py --runs runs_param_CI_s --out_csv runs_param_CI_s/validation.csv --json

Write-Host "DONE."
