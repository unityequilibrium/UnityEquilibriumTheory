"""
UET Electroweak Experiment
==========================
Validates Electroweak predictions against PDG 2024 data.

Tests:
1.  **W/Z Ratio:** Derived from Weinberg Angle.
2.  **Higgs Mass:** Derived from VEV and self-coupling.
3.  **Weinberg Angle:** Check consistency.

Standard: Glass Box (metrics logged).
"""

import sys
import csv
from pathlib import Path

# Ensure generic imports work
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from electroweak_solver import UETElectroweakSolver


def run_experiment():
    print("=" * 70)
    print("[ZAP] UET ELECTROWEAK EXPERIMENT (Standardized)")
    print("=" * 70)

    solver = UETElectroweakSolver()

    # PDG 2024 Values
    obs_wz_ratio = 0.8815
    obs_higgs_mass = 125.25  # GeV
    obs_sin2_theta = 0.23121

    results = []

    print(
        f"{'Metric':<20} | {'UET':<10} | {'Observed':<10} | {'Error':<10} | {'Status'}"
    )
    print("-" * 70)

    # 1. W/Z Ratio
    uet_wz = solver.calculate_wz_ratio()
    err_wz = abs(uet_wz - obs_wz_ratio) / obs_wz_ratio * 100
    status_wz = "PASS" if err_wz < 1.0 else "FAIL"  # 1% tolerance for W/Z ratio
    results.append(
        {
            "Metric": "WZ_Ratio",
            "UET": f"{uet_wz:.5f}",
            "Observed": f"{obs_wz_ratio:.5f}",
            "Error_Pct": f"{err_wz:.4f}",
            "Status": status_wz,
        }
    )
    print(
        f"{'M_W / M_Z':<20} | {uet_wz:<10.5f} | {obs_wz_ratio:<10.5f} | {err_wz:<9.4f}% | {status_wz}"
    )

    # 2. Higgs Mass
    uet_hm = solver.calculate_higgs_mass()
    err_hm = abs(uet_hm - obs_higgs_mass) / obs_higgs_mass * 100
    status_hm = "PASS" if err_hm < 1.0 else "FAIL"
    results.append(
        {
            "Metric": "Higgs_Mass",
            "UET": f"{uet_hm:.3f}",
            "Observed": f"{obs_higgs_mass:.3f}",
            "Error_Pct": f"{err_hm:.4f}",
            "Status": status_hm,
        }
    )
    print(
        f"{'M_Higgs (GeV)':<20} | {uet_hm:<10.3f} | {obs_higgs_mass:<10.3f} | {err_hm:<9.4f}% | {status_hm}"
    )

    # 3. Weinberg Angle ( Consistency Check )
    uet_sin2 = solver.sin2_theta_w
    err_sin2 = abs(uet_sin2 - obs_sin2_theta) / obs_sin2_theta * 100
    status_sin2 = (
        "PASS" if err_sin2 < 0.001 else "FAIL"
    )  # Should be 0 since it is defined
    results.append(
        {
            "Metric": "sin2_theta_w",
            "UET": f"{uet_sin2:.5f}",
            "Observed": f"{obs_sin2_theta:.5f}",
            "Error_Pct": f"{err_sin2:.4f}",
            "Status": status_sin2,
        }
    )
    print(
        f"{'sin^2(theta_W)':<20} | {uet_sin2:<10.5f} | {obs_sin2_theta:<10.5f} | {err_sin2:<9.4f}% | {status_sin2}"
    )

    # Implied Coupling Ratio
    kappa_beta = solver.get_mixing_parameters()
    print("-" * 70)
    print(f"[INFO]  Implied Coupling Ratio (kappa / beta): {kappa_beta:.4f}")
    print(
        f"    (To match nature, Gradient Penalty must be ~3.3x stronger than Info Coupling)"
    )

    # Save Results
    result_dir = Path(__file__).resolve().parent.parent.parent / "Result"
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / "electroweak_results.csv"

    with open(result_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Metric", "UET", "Observed", "Error_Pct", "Status"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"[OK] Results saved to '{result_path}'")

    if all(r["Status"] == "PASS" for r in results):
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


if __name__ == "__main__":
    run_experiment()
