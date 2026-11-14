"""
UET Proof: Spontaneous Symmetry Breaking
========================================
Topic: 0.11 - Phase Transitions
"""

import sys
from pathlib import Path
import numpy as np
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Engine Import (Dynamic)
try:
    import importlib.util

    engine_file = (
        root_path
        / "docs"
        / "topics"
        / "0.11_Phase_Transitions"
        / "Code"
        / "01_Engine"
        / "Engine_Phase.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Phase", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETPhaseEngine = getattr(module, "UETPhaseEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


# Standardized UET Root Path


def prove_symmetry_breaking():
    print("=" * 60)
    print("📜 UET PROOF: SPONTANEOUS SYMMETRY BREAKING")
    print("=" * 60)
    solver = UETPhaseEngine(temperature=0.05, nx=32, ny=32)
    for _ in range(200):
        solver.step()

    metrics = solver.get_extra_metrics()
    order_param = metrics["order_parameter"]

    # Kill Switch Detection (NaN Check)
    if np.isnan(order_param) or order_param == 0.0:
        print("  ❌ FAIL: Engine sabotaged or invalid coupling.")
        return False

    print(f"  Final Order Parameter (Low T): {order_param:.4f}")
    if order_param > 0.7:
        print("  ✅ PASS: Symmetry broke spontaneously.")
        return True
    else:
        print("  ❌ FAIL: Disordered state persisted.")
        return False


if __name__ == "__main__":
    success = prove_symmetry_breaking()
    sys.exit(0 if success else 1)
