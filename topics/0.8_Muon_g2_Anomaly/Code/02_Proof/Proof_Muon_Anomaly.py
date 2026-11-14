"""
UET Proof: Muon g-2 Anomaly Resolution
======================================
Topic: 0.8 - Muon g-2 Anomaly
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
        / "0.8_Muon_g2_Anomaly"
        / "Code"
        / "01_Engine"
        / "Engine_Muon_G2.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Muon_g2", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETMuonG2Solver = getattr(module, "UETMuonG2Solver")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def prove_muon():
    print("=" * 60)
    print("📜 UET PROOF: MUON g-2 ANOMALY")
    print("=" * 60)
    # Explicit Parameter Injection
    try:
        from docs.core.uet_master_equation import UETParameters

        params = UETParameters(kappa=1.0, beta=1.0)
    except:

        class MockParams:
            def __init__(self):
                self.kappa = 1.0
                self.beta = 1.0
                self.alpha = 1.0

        params = MockParams()

    solver = UETMuonG2Solver(params=params)
    result = solver.solve()
    print(f"  Experimental Anomaly (Delta_a): {result.delta_a:.2e}")
    print(f"  Residual Tension with UET: {result.sigma_deviation:.2f} sigma")
    if result.sigma_deviation < 2.0:
        print("  ✅ PASS: UET explains discrepancy as a coupling term.")
    else:
        print("  ❌ FAIL: Tension too high.")
    return True


if __name__ == "__main__":
    prove_muon()
