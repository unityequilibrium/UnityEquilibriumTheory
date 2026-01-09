# Long-T tilt sweep + custom validation (curve-fit)
$env:PYTHONPATH="."

Write-Host "=== Run s (tilt) sweep with longer T ==="
python scripts/run_suite.py --matrix matrices/UET_Param_CI_s_sweep_longT.csv --out runs_param_CI_s_longT --progress_every_s 10 --wall_timeout_s 900

Write-Host "=== Custom validate: plateau + OmegaT ~ -alpha s^2 ==="
python scripts/validate_CI_s_tilt.py --runs runs_param_CI_s_longT --out_csv runs_param_CI_s_longT/validation_tilt.csv --window 400 --plateau_tol 1e-5 --rel_tol 0.05 --abs_tol 0.02
