$ErrorActionPreference = "Stop"
$env:PYTHONPATH="."

# Copy the matrix file into your matrices/ folder first:
#   Copy-Item .\UET_Param_CI_Mscale_equalconv_sweep.csv .\matrices\

python scripts/run_suite.py --matrix matrices/UET_Param_CI_Mscale_equalconv_sweep.csv --out runs_param_CI_Meq

python scripts/validate_suite.py --runs runs_param_CI_Meq --out_csv runs_param_CI_Meq/validation_Meq.csv --json

python scripts/validate_transient_v3.py --runs runs_param_CI_Meq --out_csv runs_param_CI_Meq/validation_Meq_transient_v3.csv --json

Write-Host "`nDONE. Upload these:"
Write-Host " - runs_param_CI_Meq/validation_Meq.csv"
Write-Host " - runs_param_CI_Meq/validation_Meq_transient_v3.csv"
