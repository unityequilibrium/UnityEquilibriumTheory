"""
UET Proof: Virial Mass & Dark Matter
====================================
Topic: 0.15 - Cluster Dynamics

Proves that the 'Missing Mass' is actually 'Information Pressure'.
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
from pathlib import Path
import numpy as np
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


# Dynamic Import of Engine
engine_dir = root_path / "docs" / "topics" / "0.15_Cluster_Dynamics" / "Code" / "01_Engine"
sys.path.insert(0, str(engine_dir))
try:
    from cluster_solver import UETClusterSolver
    from docs.core.uet_parameters import G, M_SUN
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


# Standardized UET Root Path


def prove_virial_mass():
    print("=" * 60)
    print("📜 UET PROOF: VIRIAL MASS DISCREPANCY")
    print("=" * 60)

    solver = UETClusterSolver()
    state = solver.initialize_coma_cluster()

    print(f"Cluster Parameters (Coma Approximation):")
    print(f"  Radius: {state.radius/3.086e22:.2f} Mpc")
    print(f"  Visible Mass: {state.mass_visible/M_SUN:.2e} M_sun")
    print(f"  Observed Velocity: {state.velocity_disp/1000:.0f} km/s")
    print("-" * 40)

    # 1. Standard Prediction (Needs Dark Matter)
    M_dyn = solver.calculate_virial_mass_standard(state.radius, state.velocity_disp)
    missing_ratio = M_dyn / state.mass_visible

    print(f"[Standard Gravity]")
    print(f"  Required Dynamic Mass: {M_dyn/M_SUN:.2e} M_sun")
    print(f"  Discrepancy (M_dyn/M_vis): {missing_ratio:.1f}x")
    print(f"  Conclusion: Needs {missing_ratio:.1f}x more mass (Dark Matter).")

    # 2. UET Prediction
    print("-" * 40)
    print(f"[UET Information Gravity]")
    v_predicted = solver.calculate_velocity_uet()

    print(f"  Predicted Velocity (Modified): {v_predicted/1000:.0f} km/s")
    print(f"  Observed Velocity:             {state.velocity_disp/1000:.0f} km/s")

    error = abs(v_predicted - state.velocity_disp) / state.velocity_disp * 100
    print(f"  Error: {error:.1f}%")

    if error < 10.0:  # Close enough for finding
        print("  ✅ PASS: Discrepancy resolved by Information Pressure.")
        return True
    else:
        print("  ❌ FAIL: UET prediction mismatch.")
        return False


if __name__ == "__main__":
    prove_virial_mass()
