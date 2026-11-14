"""
UET Proof: Mass Generation & Hierarchy (PDG Data)
=================================================
Topic: 0.17 - Mass Generation

Validates correct loading of PDG Lepton Data and Koide Formula.
"""

import sys
from pathlib import Path

# Path setup
curr = Path(__file__).resolve()
while curr.name != "docs" and curr.parent != curr:
    curr = curr.parent
root_path = curr.parent

# Engine Import (Dynamic)
try:
    import importlib.util

    engine_file = (
        curr
        / "topics"
        / "0.17_Mass_Generation"
        / "Code"
        / "01_Engine"
        / "Engine_Mass_Higgs.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Mass_Higgs", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    run_mass_engine = getattr(module, "run_mass_engine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_mass():
    print("=" * 60)
    print("📜 UET PROOF: LEPTON MASSES (PDG Verfiied)")
    print("=" * 60)

    # Executes the full engine check (loading CSV, calculating Koide, etc.)
    success = run_mass_engine()

    if success:
        print("  ✅ PASS: Engine loaded PDG data and validated Koide.")
    else:
        print("  ❌ FAIL: Engine check failed.")
    return success


if __name__ == "__main__":
    prove_mass()
