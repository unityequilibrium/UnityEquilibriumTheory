"""
UET Muon g-2 Experiment
=======================
Validates Muon g-2 predictions against Fermilab 2023 data.

Tests:
1.  **Anomaly Match:** Does UET correction fill the gap?

Standard: Glass Box (metrics logged).
"""

import os
import sys
import csv
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Import UET Muon Solver from Engine folder
TOPIC_DIR = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly"
ENGINE_DIR = TOPIC_DIR / "Code" / "01_Engine"
sys.path.insert(0, str(ENGINE_DIR))

from Engine_Muon_G2 import UETMuonG2Solver


# Simple wrapper class to match old muon_solver interface


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


class UETMuonSolver:
    def __init__(self):
        self.solver = UETMuonG2Solver()
        self.a_exp = 1.16592061e-3
        self.a_sm = 1.16591810e-3

    def predict_anomaly(self):
        result = self.solver.solve()
        return result.a_mu_uet


def run_experiment():
    print("=" * 70)
    print("🧲 UET MUON g-2 EXPERIMENT (Standardized)")
    print("   Target: Fermilab E989 (2023)")
    print("=" * 70)

    solver = UETMuonSolver()

    # Values
    a_exp = solver.a_exp
    a_sm = solver.a_sm
    a_uet_pred = solver.predict_anomaly()

    # Discrepancy
    gap_obs = a_exp - a_sm
    gap_uet = a_uet_pred - a_sm  # Should match gap_obs

    print(f"{'Metric':<20} | {'Value (10^-9)':<15} | {'Notes'}")
    print("-" * 70)
    print(f"{'Experiment':<20} | {a_exp*1e9:<15.5f} | {'Fermilab 2023'}")
    print(f"{'Standard Model':<20} | {a_sm*1e9:<15.5f} | {'Theory Initiative 2020'}")
    print(f"{'Gap (Anomaly)':<20} | {gap_obs*1e9:<15.5f} | {'~5 sigma discrepancy'}")
    print("-" * 70)
    print(f"{'UET Correction':<20} | {gap_uet*1e9:<15.5f} | {'[CALIBRATED]'}")
    print(f"{'UET Prediction':<20} | {a_uet_pred*1e9:<15.5f} | {'SM + Correction'}")

    # Validation
    error = abs(a_uet_pred - a_exp)
    error_rel_gap = abs(gap_uet - gap_obs) / gap_obs * 100

    print("-" * 70)
    print(f"RESIDUAL ERROR: {error:.2e}")
    print(f"GAP MATCH ERROR: {error_rel_gap:.2f}%")

    status = "PASS" if error_rel_gap < 5.0 else "FAIL"
    print(f"STATUS: {status}")

    # Save Results
    result_dir = Path(__file__).resolve().parent.parent.parent / "Result"
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / "muon_results.csv"

    with open(result_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Metric", "UET", "Observed", "Error_Pct", "Status"])
        writer.writeheader()
        writer.writerow(
            {
                "Metric": "a_mu_anomaly",
                "UET": f"{gap_uet:.3e}",
                "Observed": f"{gap_obs:.3e}",
                "Error_Pct": f"{error_rel_gap:.2f}",
                "Status": status,
            }
        )

    print(f"✅ Results saved to '{result_path}'")

    if status == "PASS":
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


if __name__ == "__main__":
    run_experiment()
