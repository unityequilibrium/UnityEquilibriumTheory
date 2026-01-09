# run_all.ps1
# One-click: build canonical summaries + phase maps for all official runs.
# Usage (PowerShell, repo root):
#   powershell -ExecutionPolicy Bypass -File .\run_all.ps1
#
# Requirements:
#   - python available in PATH
#   - scripts/make_final_summary.py exists
#   - scripts/plot_phase_maps.py exists

$ErrorActionPreference = "Stop"

function Ensure-Dir($p) {
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
}

function Safe-Name($s) {
  # make a filename-safe tag
  return ($s -replace '[\\\/:\*\?"<>\| ]', '_')
}

# -----------------------------
# Official runs list (from user)
# -----------------------------
$RUNS = @(
  # Phase Map / Cross-Sweep
  "runs_betaXs_tiltCOnly",
  "runs_betaXs_tiltOpp",

  # Single-Parameter Sweeps
  "runs_param_CI_s_v2",
  "runs_param_CI_beta",
  "runs_param_CI_k_ratio",
  "runs_param_CI_kappa",
  "runs_param_CI_delta",
  "runs_param_CI_asym",
  "runs_param_CI_Mscale",
  "runs_param_CI_Meq",

  # Optional (aNeg1 variants)
  "runs_cross_CI_beta_s_aNeg1_seed10",
  "runs_param_CI_delta_aNeg1"
)

Ensure-Dir "reports"

# -----------------------------
# Build per-run summary + plots
# -----------------------------
$summaryCsvs = @()

foreach ($r in $RUNS) {
  if (-not (Test-Path $r)) {
    Write-Host "[SKIP] $r (folder not found)" -ForegroundColor Yellow
    continue
  }

  $tag = Safe-Name $r
  $outCsv = Join-Path "reports" ("{0}_UET_final_summary.csv" -f $tag)
  $phaseOut = Join-Path "reports" ("phase_maps_{0}" -f $tag)
  Ensure-Dir $phaseOut

  Write-Host "==================================================" -ForegroundColor Cyan
  Write-Host "[RUN] $r" -ForegroundColor Cyan
  Write-Host "  -> summary: $outCsv"
  Write-Host "  -> phase  : $phaseOut"

  # Try cleaner interface (--runs). If not supported, fallback to --runs_glob.
  $ok = $false
  try {
    python scripts/make_final_summary.py --runs $r --out $outCsv
    $ok = $true
  }
  catch {
    Write-Host "  [INFO] make_final_summary.py does not accept --runs; trying --runs_glob fallback..." -ForegroundColor DarkYellow
  }

  if (-not $ok) {
    python scripts/make_final_summary.py --runs_glob $r --out $outCsv
  }

  # Plot phase maps (expects columns beta + s_tilt + grade_bias)
  try {
    python scripts/plot_phase_maps.py --csv $outCsv --outdir $phaseOut
  }
  catch {
    Write-Host "  [WARN] plot_phase_maps failed for $r (likely missing beta/s_tilt/grade_bias). Skipping plots." -ForegroundColor Yellow
  }

  if (Test-Path $outCsv) {
    $summaryCsvs += $outCsv
  }
}

# -----------------------------
# Combine all summaries (optional but useful)
# -----------------------------
if ($summaryCsvs.Count -gt 0) {
  $allCsv = Join-Path "reports" "UET_final_summary_ALL.csv"
  Write-Host "==================================================" -ForegroundColor Green
  Write-Host "[MERGE] -> $allCsv" -ForegroundColor Green

  # Merge via python inline: concat with a run_set column
  python scripts/merge_summaries.py --inputs $summaryCsvs --out $allCsv

  # Build an aggregated phase map for beta×s (only when those runs exist)
  $betaXsCsvs = @()
  foreach ($r in @("runs_betaXs_tiltCOnly", "runs_betaXs_tiltOpp")) {
    $tag = Safe-Name $r
    $p = Join-Path "reports" ("{0}_UET_final_summary.csv" -f $tag)
    if (Test-Path $p) { $betaXsCsvs += $p }
  }

  if ($betaXsCsvs.Count -gt 0) {
    $betaXsOut = Join-Path "reports" "UET_final_summary_betaXs.csv"
    $betaXsPhase = Join-Path "reports" "phase_maps_betaXs"
    Ensure-Dir $betaXsPhase

    Write-Host "[MERGE betaXs] -> $betaXsOut" -ForegroundColor Green

    python scripts/merge_summaries.py --inputs $betaXsCsvs --out $betaXsOut

    try {
      python scripts/plot_phase_maps.py --csv $betaXsOut --outdir $betaXsPhase
    }
    catch {
      Write-Host "  [WARN] aggregated betaXs phase map failed. (Check columns beta/s_tilt/grade_bias)." -ForegroundColor Yellow
    }
  }

}
else {
  Write-Host "[WARN] No per-run summaries were created. Nothing to merge." -ForegroundColor Yellow
}

Write-Host "=================================================="
Write-Host "DONE ✅  Check ./reports/" -ForegroundColor Cyan
