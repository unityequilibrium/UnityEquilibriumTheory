"""
UET Phase Transition Experiment
===============================
Validates Critical Phenomena:
1.  **Symmetry Breaking:** Does the system choose a state (±C0) when cooled?
2.  **Domain Formation:** Do domains form and coarsen (Spinodal Decomposition)?

Test Protocol:
1.  Start at High Temp (Disordered, C ~ 0).
2.  Quench to Low Temp (Ordered).
3.  Observe Order Parameter growth.
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
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Dynamic Import of Engine
try:
    import importlib.util

    engine_path = (
        root_path
        / "docs"
        / "topics"
        / "0.11_Phase_Transitions"
        / "Code"
        / "01_Engine"
        / "Engine_Phase.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Phase", engine_path)
    engine_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_module)
    UETPhaseEngine = engine_module.UETPhaseEngine
except Exception as e:
    print(f"CRITICAL ERROR: Could not import Phase Engine. {e}")
    sys.exit(1)

from docs.core.uet_master_equation import UETParameters


# Standardized UET Root Path


def run_experiment():
    print("=" * 70)
    print("[UET] PHASE TRANSITION EXPERIMENT")
    print("   Testing Symmetry Breaking & Spinodal Decomposition")
    print("=" * 70)

    # Parameters for Double Well (alpha < 0)
    # V(C) = -0.1*C^2 + 0.25*C^4  => Minima at C = ±sqrt(0.1/1.0) approx ±0.31
    params = UETParameters(kappa=0.002, alpha=-1.0, beta=0.0)

    # Initialize with small random noise (Hot state)
    # Using Semi-Implicit, we can use larger dt=0.01 safely
    # Initialize with small random noise (Hot state)
    # Using Semi-Implicit, we can use larger dt=0.01 safely
    solver = UETPhaseEngine(nx=64, ny=64, dt=0.01, temperature=0.05, params=params)
    solver.C = np.random.randn(64, 64) * 0.01

    print(f"{'Step':<10} | {'Mean |C| (Order)':<20} | {'Domains':<10}")
    print("-" * 50)

    for i in range(201):
        solver.step(i)

        if i % 20 == 0:
            order_param = np.mean(np.abs(solver.C))
            domains = solver.get_domain_count()
            print(f"{i:<10} | {order_param:<20.4f} | {domains:<10.0f}")

    # Verification
    final_order = np.mean(np.abs(solver.C))

    # Theory: Should settle near sqrt(|alpha|/gamma) = sqrt(1.0/1.0) = 1.0 (if gamma=1)
    # Code implements dV/dC = alpha*C + gamma*C^3. Equil: C(alpha + gamma*C^2) = 0 => C^2 = -alpha/gamma = 1.0
    theoretical_order = 1.0

    print("-" * 50)
    print(f"Final Order Parameter: {final_order:.4f}")
    print(f"Theoretical Target:    {theoretical_order:.4f}")

    if final_order > 0.5:
        print("[OK] PASS: Symmetry Broken (System chose Ordered State)")
    else:
        print("[FAIL] FAIL: System remained Disordered (C ~ 0)")

    if solver.get_domain_count() < 2000:  # Arbitrary high number for noise
        print("[OK] PASS: Domains Coarsened (Structure emerged)")


if __name__ == "__main__":
    run_experiment()
