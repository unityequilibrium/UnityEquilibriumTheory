"""
UET Casimir Experiment Baseline
===============================
Compares UET-derived Casimir force with standard QED prediction.

Reference:
- Mohideen & Roy 1998, Phys. Rev. Lett. 81, 4549
- DOI: 10.1103/PhysRevLett.81.4549
"""

import sys
import numpy as np
from pathlib import Path

# Setup imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from casimir_solver import UETCasimirSolver


def run_experiment():
    print("=" * 70)
    print("[UET] CASIMIR FORCE BASELINE COMPARISON")
    print("   Standard QED vs UET Prediction")
    print("=" * 70)

    solver = UETCasimirSolver()

    # Test at various plate separations
    separations_nm = [100, 150, 200, 300, 500, 750, 1000]

    print(f"\n{'Sep (nm)':<12} {'F_UET (nN)':<15} {'1/d^3 (norm)':<15} {'Ratio':<10}")
    print("-" * 55)

    forces = []
    for d in separations_nm:
        F = solver.sphere_plate_force_nN(d)
        forces.append(F)

        # Expected scaling: F ~ 1/d^3
        normalized = (100 / d) ** 3 * forces[0] if len(forces) > 0 else 0
        ratio = F / normalized if normalized > 0 else 1.0

        print(f"{d:<12} {F:<15.4f} {normalized:<15.4f} {ratio:<10.3f}")

    # Verify 1/d^3 scaling
    print("\n" + "-" * 55)
    print("\n[ANALYSIS] Force Scaling")
    print("-" * 40)

    # Fit log(F) vs log(d)
    log_d = np.log(separations_nm)
    log_F = np.log(forces)
    coeffs = np.polyfit(log_d, log_F, 1)
    exponent = coeffs[0]

    print(f"Measured exponent: {exponent:.3f}")
    print(f"Expected (sphere-plate): -3.0")
    print(f"Deviation: {abs(exponent + 3.0):.3f}")

    # Pass if exponent is close to -3
    passed = abs(exponent + 3.0) < 0.1
    status = "[OK] PASS" if passed else "[FAIL] FAIL"

    print(f"\n{status}: Casimir force follows 1/d^3 scaling")

    print("\n" + "=" * 70)
    print("[RESULT] UET Casimir Baseline Complete")
    print("=" * 70)

    return passed


if __name__ == "__main__":
    success = run_experiment()
    sys.exit(0 if success else 1)
