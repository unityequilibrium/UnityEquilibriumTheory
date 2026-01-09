# run_all_cross_sweep.ps1
# One-command runner for UET Cross Sweep reproducibility
# Usage:
#   .\run_all_cross_sweep.ps1                    # Full run: matrix -> simulate -> aggregate -> plot
#   .\run_all_cross_sweep.ps1 -Mode aggregate_only  # Re-aggregate + plot only (skip simulation)

param(
  [ValidateSet("full", "aggregate_only")]
  [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"
$startTime = Get-Date

# Paths
$repoRoot = $PSScriptRoot
$scriptsDir = Join-Path $repoRoot "scripts"
$matricesDir = Join-Path $repoRoot "matrices"
$logsDir = Join-Path $repoRoot "logs"

# Ensure logs directory exists
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

# Start transcript
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$transcriptPath = Join-Path $logsDir "cross_sweep_$timestamp.log"
Start-Transcript -Path $transcriptPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " UET Cross Sweep Runner - Mode: $Mode"
Write-Host " Start Time: $startTime"
Write-Host "========================================" -ForegroundColor Cyan

# Cross sweep definitions
$sweeps = @(
  @{Name = "beta_k_ratio"; Matrix = "UET_Cross_CI_beta_k_ratio_seed10.csv"; RunDir = "runs_cross_beta_k_ratio_seed10" },
  @{Name = "beta_delta"; Matrix = "UET_Cross_CI_beta_delta_seed10.csv"; RunDir = "runs_cross_beta_delta_seed10" },
  @{Name = "s_delta"; Matrix = "UET_Cross_CI_s_delta_seed10.csv"; RunDir = "runs_cross_s_delta_seed10" }
)

function Run-Sweep {
  param($sweep)
  $matrixPath = Join-Path $matricesDir $sweep.Matrix
  $runDir = Join-Path $repoRoot $sweep.RunDir
    
  Write-Host "`n--- Processing: $($sweep.Name) ---" -ForegroundColor Yellow
    
  if ($Mode -eq "full") {
    # Check if matrix exists
    if (-not (Test-Path $matrixPath)) {
      Write-Host "  [SKIP] Matrix not found: $matrixPath" -ForegroundColor Red
      return
    }
        
    # Run simulation
    Write-Host "  [RUN] Running suite..."
    py (Join-Path $scriptsDir "run_suite.py") --matrix $matrixPath --out $runDir
  }
    
  # Aggregate
  if (Test-Path $runDir) {
    Write-Host "  [AGG] Aggregating results..."
    $summaryPath = Join-Path $runDir "UET_final_summary_v2.csv"
    py (Join-Path $scriptsDir "aggregate_final_summary.py") --runs $runDir --out $summaryPath
    Write-Host "  [OK] Summary: $summaryPath" -ForegroundColor Green
    
    # Plot phase maps
    if (Test-Path $summaryPath) {
      Write-Host "  [PLOT] Generating phase maps..."
      $plotDir = Join-Path $runDir "plots"
      py (Join-Path $scriptsDir "plot_phase_maps.py") --csv $summaryPath --outdir $plotDir --model C_I
      Write-Host "  [OK] Plots: $plotDir" -ForegroundColor Green
    }
  }
  else {
    Write-Host "  [SKIP] Run directory not found: $runDir" -ForegroundColor Red
  }
}

# Execute all sweeps
foreach ($sweep in $sweeps) {
  Run-Sweep -sweep $sweep
}

# Summary
$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Completed in: $($duration.TotalMinutes.ToString('F1')) minutes"
Write-Host " Log: $transcriptPath"
Write-Host "========================================" -ForegroundColor Cyan

Stop-Transcript
