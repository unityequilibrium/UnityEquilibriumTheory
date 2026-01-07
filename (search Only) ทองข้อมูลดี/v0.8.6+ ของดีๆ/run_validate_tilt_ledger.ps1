# Ledger-only tilt validation (no timeseries needed)
# Run from repo root (uet_harness_v0_1)
$env:PYTHONPATH="."
python scripts/validate_CI_s_tilt_ledger.py --ledger runs_param_CI_s_longT/ledger.csv --out_csv runs_param_CI_s_longT/validation_tilt_ledger.csv --rel_tol 0.01 --abs_tol 1e-3
