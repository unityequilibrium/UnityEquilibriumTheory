"""
UET Engine Comparison Benchmark: Lite vs Master
===============================================
This script verifies the "Safety Bridge" hypothesis:
Can the Core-4 Lite Engine reproduce the physics of the 7-term Master Equation?

Test Case: 1D Reaction-Diffusion with Information Source.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Explicitly add the project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Use the Rich Parameter class confirmed to work with the engine
    from docs.core.uet_master_equation import UETMasterEquation, UETParameters
    from docs.scripts.core.runners.uet_lite_engine import UETLiteEngine
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Sys Path: {sys.path}")
    sys.exit(1)


def run_comparison():
    print("=" * 60)
    print("UET ENGINE BENCHMARK: Core-4 Lite vs Legacy Master")
    print("=" * 60)

    # 1. Setup Parameters
    params = UETParameters(
        alpha=1.0,
        gamma=0.1,
        kappa=0.1,
        beta=0.5,
        W_N=0.0,  # Turn OFF Natural Will in Master to test core parity first
        gamma_J=0.1,
    )

    # 2. Initialize Engines
    master_engine = UETMasterEquation(params)
    lite_engine = UETLiteEngine(params)

    # 3. Setup Initial Conditions (1D Gaussian)
    N = 100
    dx = 0.1
    x = np.linspace(-5, 5, N)
    C_init = np.exp(-(x**2))
    I_field = 0.1 * np.sin(x)  # Information field

    # Run separate simulations
    C_master = C_init.copy()
    C_lite = C_init.copy()

    dt = 0.005
    steps = 1000

    print(f"Running {steps} steps on both engines...")

    track_diff = []

    for i in range(steps):
        # Update Master
        C_master = master_engine.step(C_master, dt, dx, I=I_field)

        # Update Lite
        C_lite = lite_engine.step(C_lite, dt, dx, I=I_field)

        # Compare
        diff = np.mean(np.abs(C_master - C_lite))
        track_diff.append(diff)

        if i % 100 == 0:
            Ω_master = master_engine.compute_omega(C_master, dx, I=I_field)
            Ω_lite = lite_engine.compute_omega(C_lite, dx, I=I_field)
            print(f"Step {i:4d}: Diff={diff:.6f}, Ω_M={Ω_master:.4f}, Ω_L={Ω_lite:.4f}")

    final_diff = track_diff[-1]
    print("-" * 60)
    print(f"Final Average Difference: {final_diff:.6f}")

    if final_diff < 1e-5:
        print("✅ PASS: Lite Engine matches Master Engine (Core Terms)")
        return True
    else:
        print("❌ FAIL: Divergence detected.")
        return False


if __name__ == "__main__":
    run_comparison()
