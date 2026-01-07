$ErrorActionPreference = "Stop"
$env:PYTHONPATH="."

# 1) Copy the matrix into your matrices folder:
#    Copy-Item .\UET_Cross_CI_beta_s_sweep_seed10.csv .\matrices\

# 2) Run
python scripts/run_suite.py --matrix matrices/UET_Cross_CI_beta_s_sweep_seed10.csv --out runs_cross_CI_beta_s_seed10

# 3) Validate (suite + transient)
python scripts/validate_suite.py --runs runs_cross_CI_beta_s_seed10 --out_csv runs_cross_CI_beta_s_seed10/validation_betaXs.csv --json

python scripts/validate_transient_v3.py --runs runs_cross_CI_beta_s_seed10 --out_csv runs_cross_CI_beta_s_seed10/validation_betaXs_transient_v3.csv --json

Write-Host "`nDONE. Upload these:"
Write-Host " - runs_cross_CI_beta_s_seed10/validation_betaXs.csv"
Write-Host " - runs_cross_CI_beta_s_seed10/validation_betaXs_transient_v3.csv"
