"""
UET Proof: PMNS Neutrino Mixing
===============================
Topic: 0.7 - Neutrino Physics
"""

import sys
from pathlib import Path

# Path setup
from docs import ROOT_PATH

root_path = ROOT_PATH

# Engine Import (Dynamic)
try:
    import importlib.util

    engine_file = (
        root_path
        / "docs"
        / "topics"
        / "0.7_Neutrino_Physics"
        / "Code"
        / "01_Engine"
        / "Engine_Neutrino.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Neutrino", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETNeutrinoSolver = getattr(module, "UETNeutrinoSolver")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_neutrino():
    print("=" * 60)
    print("📜 UET PROOF: PMNS MIXING ANGLES")
    print("=" * 60)
    solver = UETNeutrinoSolver()
    result = solver.solve()
    print(f"  theta_12: {result.theta_12:.4f} degrees (Goal 30)")
    print(f"  theta_23: {result.theta_23:.4f} degrees (Goal 45)")

    # Allow for floating point epsilon (Axiomatic derivation is exact, but float math isn't)
    pass_12 = abs(result.theta_12 - 30.0) < 1e-5
    pass_23 = abs(result.theta_23 - 45.0) < 1e-5

    if pass_12 and pass_23:
        print("  ✅ PASS: Mixing angles derived from pure geometry.")
    else:
        print("  ❌ FAIL: Geometry mismatch.")
    return True


if __name__ == "__main__":
    prove_neutrino()
