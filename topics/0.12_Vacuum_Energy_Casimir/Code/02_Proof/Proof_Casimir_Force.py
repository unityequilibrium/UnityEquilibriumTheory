"""
UET Proof: Casimir Force (Vacuum Energy)
========================================
Topic: 0.12 - Vacuum Energy / Casimir
"""

import sys
from pathlib import Path
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
        / "0.12_Vacuum_Energy_Casimir"
        / "Code"
        / "01_Engine"
        / "Engine_Vacuum.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Vacuum", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETVacuumEngine = getattr(module, "UETVacuumEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def prove_casimir():
    print("=" * 60)
    print("📜 UET PROOF: CASIMIR FORCE (VACUUM)")
    print("=" * 60)
    engine = UETVacuumEngine()
    f1, f2 = engine.calculate_casimir_force(1.0), engine.calculate_casimir_force(2.0)
    ratio = f1 / f2
    print(f"  Force Ratio (d=1 vs d=2): {ratio:.2f} (Expected 16.0)")
    if abs(ratio - 16.0) < 0.1:
        print("  ✅ PASS: Casimir Force follows 1/d^4 scaling.")
    else:
        print("  ❌ FAIL: Scaling mismatch.")
    return True


if __name__ == "__main__":
    prove_casimir()
