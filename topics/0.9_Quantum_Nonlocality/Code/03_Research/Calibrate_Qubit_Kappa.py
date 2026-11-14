"""
UET Qubit Calibration Script
============================
Sweeps 'kappa' (Information Diffusion Coefficient) to match Real T1.

Target:
- IBMQ Manila Q0 T1: 120.31 us (from arXiv:2306.09578v3)
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
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


try:
    import importlib.util

    engine_file = (
        root_path
        / "docs"
        / "topics"
        / "0.9_Quantum_Nonlocality"
        / "Code"
        / "01_Engine"
        / "Engine_UET_Qubit.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_UET_Qubit", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETQubitEngine = getattr(module, "UETQubitEngine")

    from docs.core.uet_parameters import UETParameters
except Exception as e:
    print(f"CRITICAL: Engine Import Failed: {e}")
    sys.exit(1)


# Standardized UET Root Path


def measure_t1(kappa_val):
    # 1. Setup Engine with Candidate Kappa
    params = UETParameters(kappa=kappa_val, beta=1.0, scale="calibration_sweep", origin="Sweep")
    engine = UETQubitEngine(uet_params=params)
    engine.set_excited_state()

    # 2. Run Short Sim
    steps = 150
    amps = []

    for _ in range(steps):
        amps.append(engine.step())

    # 3. Fit T1
    # A(t) = A0 * exp(-t/T1)
    # T1 = -t / ln(A/A0) at t=50
    idx = 50
    A0 = amps[0]
    At = amps[idx]
    t = float(idx)  # 1 step = 1 us

    if At < A0 and At > 0:
        return -t / np.log(At / A0)
    return 0.0


def run_calibration():
    # Target
    target_t1 = 120.31
    print(f"🎯 EXPERIMENTAL TARGET: T1 = {target_t1} us")
    print("-" * 50)

    # Sweep
    kappas = np.linspace(1.0, 2.0, 11)  # Sweep 1.0 to 2.0
    results = []

    best_k = None
    min_err = float("inf")

    print(f"{'Kappa':<10} | {'Sim T1 (us)':<12} | {'Error (%)':<10}")
    print("-" * 40)

    for k in kappas:
        t1 = measure_t1(k)
        err = abs(t1 - target_t1) / target_t1 * 100
        print(f"{k:<10.2f} | {t1:<12.2f} | {err:<10.1f}")

        if err < min_err:
            min_err = err
            best_k = k

    print("-" * 50)
    print(f"✅ OPTIMAL KAPPA: {best_k:.2f} (Error: {min_err:.1f}%)")

    return best_k


if __name__ == "__main__":
    run_calibration()
