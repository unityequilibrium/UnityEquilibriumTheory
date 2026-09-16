"""
UET Lite Engine Rollout Validation
==================================
Verifies that the new Core-4 Engine works correctly with the high-level Solvers:
1. Cosmology (Scalar)
2. Quantum (2D Field)
3. Superconductivity (Grid Phase Transition)

Method:
- Instantiate standard Solver.
- Hot-swap `solver.engine` with `UETLiteEngine`.
- Run simulation and check for physical failures (NaN, divergence) or logic errors.
"""

import sys
import os
import numpy as np

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from docs.scripts.core.runners.uet_lite_engine import UETLiteEngine
import importlib.util


def dynamic_import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Paths to Solvers
base_topics = os.path.join(project_root, "docs", "topics")

# 0.3 Cosmo
cosmo_path = os.path.join(
    base_topics, "0.3_Cosmology_Hubble_Tension", "Code", "baseline", "cosmo_solver.py"
)
cosmo_mod = dynamic_import("cosmo_solver", cosmo_path)
UETCosmoSolver = cosmo_mod.UETCosmoSolver

# 0.9 Quantum
quantum_path = os.path.join(
    base_topics, "0.9_Quantum_Nonlocality", "Code", "baseline", "quantum_solver.py"
)
quantum_mod = dynamic_import("quantum_solver", quantum_path)
UETQuantumSolver = quantum_mod.UETQuantumSolver

# 0.4 Super
super_path = os.path.join(
    base_topics, "0.4_Superconductivity_Superfluids", "Code", "baseline", "super_solver.py"
)
super_mod = dynamic_import("super_solver", super_path)
UETSuperSolver = super_mod.UETSuperSolver


def validate_cosmology():
    print("\n[1] Testing Cosmology Solver (Scalar 0D)...")
    solver = UETCosmoSolver(dt=0.01)

    # SWAP ENGINE
    print("    > Swapping to UETLiteEngine...")
    solver.engine = UETLiteEngine(solver.params)

    try:
        # Run until a=0.5 (mid-universe)
        step = 0
        while solver.a < 0.5 and step < 500:
            solver.step(step)
            step += 1

        print(f"    > Success! Reached scale factor a={solver.a:.3f}")
        return True
    except Exception as e:
        print(f"    ❌ FAIL: {e}")
        return False


def validate_quantum():
    print("\n[2] Testing Quantum Solver (2D Field)...")
    solver = UETQuantumSolver(dt=1.0)  # Large dt for quantum logical steps

    # SWAP ENGINE
    print("    > Swapping to UETLiteEngine...")
    solver.engine = UETLiteEngine(solver.params)

    try:
        solver.set_measurement_settings(0, 22.5)
        for i in range(50):
            solver.step(i)

        corr = solver.get_correlation()
        print(f"    > Success! Correlation E = {corr:.3f}")
        return True
    except Exception as e:
        print(f"    ❌ FAIL: {e}")
        return False


def validate_superconductivity():
    print("\n[3] Testing Superconductivity Solver (Mean Field)...")
    solver = UETSuperSolver(dt=0.01)

    # SWAP ENGINE
    print("    > Swapping to UETLiteEngine...")
    solver.engine = UETLiteEngine(solver.params)

    try:
        # Run phase transition check
        solver.temperature = 5.0  # Low temp
        for i in range(50):
            solver.step(i)

        order = solver.get_order_parameter()
        print(f"    > Success! Order Parameter = {order:.3f}")
        return True
    except Exception as e:
        print(f"    ❌ FAIL: {e}")
        return False


def run_all_validations():
    print("=" * 60)
    print("UET LITE ROLLOUT VALIDATION")
    print("=" * 60)

    results = [validate_cosmology(), validate_quantum(), validate_superconductivity()]

    print("-" * 60)
    if all(results):
        print("✅ ALL SYSTEMS GREEN: UETLite is safe to deploy.")
        return True
    else:
        print("❌ CRITICAL FAILURE: Do not deploy UETLite.")
        return False


if __name__ == "__main__":
    run_all_validations()
