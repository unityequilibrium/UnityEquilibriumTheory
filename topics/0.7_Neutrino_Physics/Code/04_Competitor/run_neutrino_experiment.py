"""
UET Neutrino Experiment
=======================
Validates Neutrino Mixing Angle predictions against PDG 2024 data.

Tests:
1.  **Mixing Angles:** theta_12, theta_23, theta_13.
2.  **CP Violation:** delta_CP.

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

from neutrino_solver import UETNeutrinoSolver


def run_experiment():
    print("=" * 70)
    print("[SCOPE] UET NEUTRINO MIXING EXPERIMENT (Standardized)")
    print("   Hypothesis: Geometric I-Field Symmetry")
    print("=" * 70)

    solver = UETNeutrinoSolver()
    predictions = solver.predict_mixing_angles()

    # PDG 2024 Values
    obs = {
        "theta12": 33.44,  # Solar
        "theta23": 49.2,  # Atmospheric
        "theta13": 8.57,  # Reactor
        "delta_cp": 195.0,  # T2K fit
    }

    results = []

    print(
        f"{'Angle':<10} | {'UET (Deg)':<10} | {'Obs (Deg)':<10} | {'Error':<10} | {'Status'}"
    )
    print("-" * 70)

    total_error = 0.0
    pass_count = 0

    for key in obs:
        uet_val = predictions[key]
        obs_val = obs[key]

        error = abs(uet_val - obs_val) / obs_val * 100
        total_error += error

        # 15% tolerance for geometric ansatz (qualitative fit)
        status = "PASS" if error < 15.0 else "FAIL"
        if status == "PASS":
            pass_count += 1

        print(
            f"{key:<10} | {uet_val:<10.2f} | {obs_val:<10.2f} | {error:<9.2f}% | {status}"
        )

        results.append(
            {
                "Metric": key,
                "UET": f"{uet_val:.2f}",
                "Observed": f"{obs_val:.2f}",
                "Error_Pct": f"{error:.2f}",
                "Status": status,
            }
        )

    avg_error = total_error / len(obs)
    pass_pct = (pass_count / len(obs)) * 100

    print("-" * 70)
    print(f"[DATA] SUMMARY:")
    print(f"   Average Error: {avg_error:.2f}%")
    print(f"   Pass Rate:     {pass_pct:.1f}% ({pass_count}/{len(obs)})")
    print("-" * 70)

    # Save Results
    result_dir = Path(__file__).resolve().parent.parent.parent / "Result"
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / "neutrino_results.csv"

    with open(result_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Metric", "UET", "Observed", "Error_Pct", "Status"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"[OK] Results saved to '{result_path}'")

    if pass_pct >= 75.0:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


if __name__ == "__main__":
    run_experiment()
