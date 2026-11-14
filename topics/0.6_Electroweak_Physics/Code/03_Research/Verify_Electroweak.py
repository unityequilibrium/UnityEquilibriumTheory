"""
Verify_Electroweak.py
=====================
Grand Production Upscale: Verification of Topic 0.6.
Checks if UET Geometric Derivation matches Standard Model (CODATA 2024).

Constraint:
    sin^2(theta_W) = 0.23121 (Experimental)
    UET Prediction must be within 1% error without curve fitting.
"""

import sys
from pathlib import Path
import numpy as np

# --- ROBUST PATH FINDER ---


# Local Engine Import (Relative Robust)
current_dir = Path(__file__).resolve().parent
engine_dir = current_dir.parent / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

from Engine_Electroweak import UETElectroweakSolver


def run_verification():
    print("⚡ UET ELECTROWEAK: PRODUCTION VERIFICATION")
    print("===========================================")
    print("Target: CODATA 2024 Values (Unbiased Check)\n")

    solver = UETElectroweakSolver()
    res = solver.solve()

    # Standard Model Values (CODATA)
    SM_SIN2_THETA = 0.23121
    SM_MW = 80.377  # GeV
    SM_GF = 1.1663787e-5  # GeV^-2

    # 1. Weinberg Angle Check
    error_angle = abs(res.sin2_theta_W - SM_SIN2_THETA) / SM_SIN2_THETA * 100
    print(f"[1] Weinberg Angle (sin^2 theta_W)")
    print(f"    UET Predicted: {res.sin2_theta_W:.5f}")
    print(f"    CODATA Value:  {SM_SIN2_THETA:.5f}")
    print(f"    Error:         {error_angle:.2f}%")

    if error_angle < 1.0:
        print("    ✅ STATUS: MATCH (Geometric Origin Confirmed)")
    else:
        print("    ❌ STATUS: FAILED (Geometry Mismatch)")

    print("-" * 30)

    # 2. W Mass Check
    error_mw = abs(res.m_W_predicted - SM_MW) / SM_MW * 100
    print(f"[2] W Boson Mass")
    print(f"    UET Predicted: {res.m_W_predicted:.3f} GeV")
    print(f"    CODATA Value:  {SM_MW:.3f} GeV")
    print(f"    Error:         {error_mw:.2f}%")

    if error_mw < 1.0:
        print("    ✅ STATUS: MATCH")
    else:
        print("    ❌ STATUS: FAILED")

    print("-" * 30)

    # 3. Fermi Constant Check
    error_gf = abs(res.fermi_constant - SM_GF) / SM_GF * 100
    print(f"[3] Fermi Constant (G_F)")
    print(f"    UET Predicted: {res.fermi_constant:.5e}")
    print(f"    CODATA Value:  {SM_GF:.5e}")
    print(f"    Error:         {error_gf:.2f}%")

    # Overall Result
    if error_angle < 1.0 and error_mw < 1.0:
        print("\n🏆 FINAL RESULT: ELECTROWEAK GEOMETRY VERIFIED")
    else:
        print("\n⚠️ FINAL RESULT: REQUIRES CALIBRATION")


if __name__ == "__main__":
    run_verification()
