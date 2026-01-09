# setup_reports.ps1
# Copy cross-sweep artifacts to reports/ and lock environment

$repoRoot = $PSScriptRoot
$reportDir = Join-Path $repoRoot "reports\cross_sweeps\seed10"

# Create directories
$sweeps = @("beta_k_ratio", "beta_delta", "s_delta")
foreach ($s in $sweeps) {
    $dir = Join-Path $reportDir $s
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
}

# Copy summaries
Copy-Item "runs_cross_beta_k_ratio_seed10\UET_final_summary_v2.csv" (Join-Path $reportDir "beta_k_ratio\") -Force
Copy-Item "runs_cross_beta_delta_seed10\UET_final_summary_v2.csv" (Join-Path $reportDir "beta_delta\") -Force
Copy-Item "runs_cross_s_delta_seed10\UET_final_summary_v2.csv" (Join-Path $reportDir "s_delta\") -Force

# Copy plots if exist
if (Test-Path "runs_cross_beta_k_ratio_seed10\plots") { Copy-Item "runs_cross_beta_k_ratio_seed10\plots" (Join-Path $reportDir "beta_k_ratio\plots") -Recurse -Force }
if (Test-Path "runs_cross_beta_delta_seed10\plots") { Copy-Item "runs_cross_beta_delta_seed10\plots" (Join-Path $reportDir "beta_delta\plots") -Recurse -Force }
if (Test-Path "runs_cross_s_delta_seed10\plots") { Copy-Item "runs_cross_s_delta_seed10\plots" (Join-Path $reportDir "s_delta\plots") -Recurse -Force }

# Create ledger.csv
$ledger = @"
sweep,summary_file,run_count,timestamp
beta_k_ratio,UET_final_summary_v2.csv,250,$(Get-Date -Format "yyyy-MM-dd HH:mm")
beta_delta,UET_final_summary_v2.csv,300,$(Get-Date -Format "yyyy-MM-dd HH:mm")
s_delta,UET_final_summary_v2.csv,300,$(Get-Date -Format "yyyy-MM-dd HH:mm")
"@
$ledger | Out-File -FilePath (Join-Path $reportDir "ledger.csv") -Encoding UTF8

# Lock environment
py -m pip freeze | Out-File -FilePath (Join-Path $repoRoot "requirements_frozen.txt") -Encoding UTF8
py -V | Out-File -FilePath (Join-Path $repoRoot "PYTHON_VERSION.txt") -Encoding UTF8

Write-Host "Done! Artifacts copied to: $reportDir" -ForegroundColor Green
Write-Host "Environment locked: requirements_frozen.txt, PYTHON_VERSION.txt" -ForegroundColor Green
