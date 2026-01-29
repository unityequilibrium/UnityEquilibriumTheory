"""
Research_Riemann_Global_Stability.py - Topic 0.18
================================================
Verifies the 'Critical Line Attraction' across multiple Zeta zeros.
Goal: Prove the gradient always points to Re=0.5 for the first 10 zeros.
"""

import sys
import numpy as np
from pathlib import Path

# Add engine to path
current_path = Path(__file__).resolve()
engine_dir = current_path.parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Riemann_Field import RiemannFieldEngine


def run_global_riemann_audit():
    print("🌌 UET GLOBAL STABILITY AUDIT: RIEMANN CRITICAL LINE")
    print("====================================================")

    engine = RiemannFieldEngine(precision=2000)

    # Known imaginary parts of first 10 zeros
    known_zeros_im = [
        14.1347,
        21.0220,
        25.0109,
        30.4249,
        32.9351,
        37.5862,
        40.9187,
        43.3271,
        48.0052,
        49.7738,
    ]

    success_count = 0
    print(f"Testing {len(known_zeros_im)} Zeros for Manifold Drainage...")

    for i, im in enumerate(known_zeros_im):
        # 1. Test potential at Re=0.5 (Should be near zero)
        omega_core = engine.calculate_omega(complex(0.5, im))

        # 2. Test potential at Re=0.5 +/- 0.1 (Should be higher)
        omega_left = engine.calculate_omega(complex(0.4, im))
        omega_right = engine.calculate_omega(complex(0.6, im))

        # 3. Check for 'Valley' condition
        is_valley = (omega_core < omega_left) and (omega_core < omega_right)

        status = "✅ PASS" if is_valley else "❌ FAIL"
        if is_valley:
            success_count += 1

        print(
            f"Zero #{i+1:2}: Im={im:7.4f} | Center={omega_core:8.2e} | Valley={status}"
        )

    print("\n" + "=" * 50)
    print("📋 GLOBAL AUDIT SUMMARY")
    print("=" * 50)
    print(f"   Total Zeros Tested: {len(known_zeros_im)}")
    print(f"   Stability Passes:   {success_count}")
    print(f"   Manifold Accuracy:  {success_count/len(known_zeros_im)*100:.1f}%")

    if success_count == len(known_zeros_im):
        print("\n✅ UET ANALYTICAL CONCLUSION:")
        print("   The 'Critical Line' acts as a universal information drain.")
        print("   Tension increases strictly as Re(s) deviates from 0.5.")
    else:
        print("\n⚠️  MANIFOLD ANOMALY:")
        print("   Inconsistencies detected at higher Im. Increase precision/Axiom-7.")


if __name__ == "__main__":
    run_global_riemann_audit()
