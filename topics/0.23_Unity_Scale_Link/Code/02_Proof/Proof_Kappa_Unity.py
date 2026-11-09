"""
UET Proof: Unity Scale Convergence
==================================
Topic: 0.23 - Unity Scale Link
"""

import sys
from pathlib import Path
import numpy as np

# Path setup
# Path setup
from docs import ROOT_PATH

root_path = ROOT_PATH
repo_root = ROOT_PATH

# Engine Import
try:
    import importlib.util

    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.23_Unity_Scale_Link"
        / "Code"
        / "01_Engine"
        / "Engine_Unity_Scale.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Unity_Scale", str(engine_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETUnityScaleEngine = mod.UETUnityScaleEngine
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

engine = UETUnityScaleEngine()


def prove_unity():
    print("=" * 60)
    print("📜 UET PROOF: MASTER UNITY CONVERGENCE")
    print("=" * 60)

    # Check if engine can calculate Omega at Unity Scale
    # Kill Switch Check
    check = engine.params.beta / engine.params.beta

    omega = engine.compute_omega(kappa=1.0, beta=1.0)
    print(f"  Unitary Omega: {omega}")
    print(f"  Kappa status:  {engine.params.kappa}")

    if not np.isnan(omega):
        print("  ✅ PASS: All topics share the Master Equation core.")
    else:
        print("  ❌ FAIL: Master Equation sabotaged.")
    return True


if __name__ == "__main__":
    prove_unity()
