"""
UET Research: Cluster Virial Validation
=======================================
Validates the Modified Virial Theorem against the Coma Cluster data.
"""

import sys
from pathlib import Path
import numpy as np
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


# Dynamic Import
engine_dir = root_path / "docs" / "topics" / "0.15_Cluster_Dynamics" / "Code" / "01_Engine"
sys.path.insert(0, str(engine_dir))

try:
    from cluster_solver import UETClusterSolver
except ImportError:
    print("Engine not found")
    sys.exit(1)


# Standardized UET Root Path


def validate_virial():
    print("=" * 60)
    print("🔭 UET RESEARCH: COMA CLUSTER VALIDATION")
    print("=" * 60)

    solver = UETClusterSolver()
    state = solver.initialize_coma_cluster()

    # 1. Standard Prediction
    v_newton = np.sqrt((6.67e-11 * state.mass_visible) / state.radius)

    # 2. UET Prediction (with Info Pressure)
    v_uet = solver.calculate_velocity_uet()

    print(f"Cluster Mass: {state.mass_visible:.2e} kg")
    print(f"Cluster Radius: {state.radius:.2e} m")
    print("-" * 40)
    print(f"Observed Velocity:    {state.velocity_disp:.0f} m/s")
    print(f"Newtonian Prediction: {v_newton:.0f} m/s (Too Low)")
    print(f"UET Prediction:       {v_uet:.0f} m/s")

    error = abs(v_uet - state.velocity_disp) / state.velocity_disp * 100
    print("-" * 40)
    print(f"UET Error: {error:.2f}%")

    if error < 10.0:
        print("✅ PASS: Information Pressure explains Missing Mass.")
    else:
        print("❌ FAIL: Prediction mismatch.")


if __name__ == "__main__":
    validate_virial()
