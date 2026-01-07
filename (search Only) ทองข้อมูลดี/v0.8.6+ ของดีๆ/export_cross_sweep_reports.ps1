# export_cross_sweep_reports.ps1
# Copies light-weight artifacts from runs_* into reports/ for sharing/review.
# Run from repo root (where runs_cross_* folders exist).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\export_cross_sweep_reports.ps1
#
# Output:
#   reports\cross_sweeps\seed10\...

$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$Path) {
  if (!(Test-Path $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }
}

$DestRoot = "reports/cross_sweeps/seed10"
Ensure-Dir $DestRoot

$Runs = @(
  "runs_cross_beta_k_ratio_seed10",
  "runs_cross_beta_delta_seed10",
  "runs_cross_s_delta_seed10"
)

foreach ($r in $Runs) {
  if (!(Test-Path $r)) {
    Write-Host "Missing $r (skip)"
    continue
  }
  $dst = Join-Path $DestRoot $r
  Ensure-Dir $dst

  # Copy summaries + validations if present
  $files = @(
    "UET_final_summary_v2.csv",
    "validation_transient_v3.json",
    "validation_bias_v2.json",
    "ledger.csv"
  )
  foreach ($f in $files) {
    $src = Join-Path $r $f
    if (Test-Path $src) {
      Copy-Item $src $dst -Force
      Write-Host "Copied $src -> $dst"
    }
  }

  # Copy plots folder (light artifacts)
  $plots = Join-Path $r "plots"
  if (Test-Path $plots) {
    $dstPlots = Join-Path $dst "plots"
    Ensure-Dir $dstPlots
    Copy-Item (Join-Path $plots "*") $dstPlots -Recurse -Force
    Write-Host "Copied $plots -> $dstPlots"
  }
}

Write-Host ""
Write-Host "DONE ✅"
Write-Host "See: reports/cross_sweeps/seed10/"
