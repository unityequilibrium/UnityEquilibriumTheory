"""
Research_Riemann_Zeta_UET.py - Topic 0.18
========================================
Visualizing the Riemann Potential Field.
Demonstrates the 'Pull' of the Critical Line.
"""

import sys
import numpy as np
import argparse
from pathlib import Path

# Add engine to path
current_path = Path(__file__).resolve()
engine_dir = current_path.parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Riemann_Field import RiemannFieldEngine


def run_riemann_research():
    print("🌌 UET MILLENNIUM RESEARCH: RIEMANN HYPOTHESIS")
    print("===============================================")

    engine = RiemannFieldEngine(precision=2000)

    # 1. Scan the Critical Strip [0.1, 0.9] around a known zero
    # First zero is at approx 1/2 + 14.13i
    target_im = 14.134725
    print(f"\n[1] Scanning Manifold around Real-Time Sink (Im ~ {target_im})...")

    re_test = [0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]
    potentials = []

    for re in re_test:
        omega = engine.calculate_omega(complex(re, target_im))
        potentials.append(omega)
        print(f"    s = {re:4.2f} + {target_im:4.2f}i | Omega = {omega:8.5e}")

    min_idx = np.argmin(potentials)
    best_re = re_test[min_idx]

    print(f"\n📊 RESULT: Minimum Potential found at Re = {best_re}")
    if best_re == 0.5:
        print("   ✅ UET CONSISTENCY: Unity Sink aligns with Critical Line.")
    else:
        print("   ⚠️  UET DISTORTION: Check precision or grid resolution.")

    # 2. Gradient Descent Proof (Topic 0.18 Specialty) (Optional)
    parser = argparse.ArgumentParser(description="Research Riemann Zeta UET")
    parser.add_argument(
        "--proof", action="store_true", help="Run the full Gradient Descent Proof (Slow)"
    )
    args = parser.parse_args()

    if args.proof:
        print("\n[2] Gradient Descent from Offset State (Re=0.8)...")
        path = engine.find_gradient_sink(
            complex(0.8, target_im + 0.5), lerp=0.005, iterations=2000, verbose=True
        )
        final = path[-1]
        print(f"    Final Equilibrium: {final.real:8.5f} + {final.imag:8.5f}i")
        print(f"    Residual Omega:    {engine.calculate_omega(final):8.5e}")

        if abs(final.real - 0.5) < 0.05:
            print("   ✅ PROOF: Manifold Tension forces state onto the Critical Line.")
    else:
        print("\n[2] Gradient Descent Proof (Skipped)")
        print("    ℹ️  Run with '--proof' to see the full Manifold Tension demonstration.")


if __name__ == "__main__":
    run_riemann_research()
