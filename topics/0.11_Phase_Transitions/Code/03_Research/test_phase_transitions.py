"""
UET Phase Transitions Test - BEC and Spinodal
==============================================
"""

import sys
from pathlib import Path
import math

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
repo_root = current_path
for _ in range(8):
    if (repo_root / "docs").exists():
        break
    repo_root = repo_root.parent

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Engine Import
try:
    import importlib.util

    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.11_Phase_Transitions"
        / "Code"
        / "01_Engine"
        / "Engine_Phase.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Phase", str(engine_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETPhaseEngine = mod.UETPhaseEngine
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

engine = UETPhaseEngine()


def bec_1995_data():
    return {
        "N_atoms": 2000,
        "Tc_nK": 170,
        "trap_freq_Hz": 200,
    }


def run_test():
    print("=" * 70)
    print("UET PHASE TRANSITIONS TEST")
    print("=" * 70)

    data = bec_1995_data()
    N = data["N_atoms"]
    omega = 2 * math.pi * data["trap_freq_Hz"]
    Tc_exp = data["Tc_nK"] * 1e-9

    Tc_uet = engine.compute_bec_tc(N, omega)

    print(f"  Tc (experiment): {Tc_exp*1e9:.0f} nK")
    print(f"  Tc (UET):        {Tc_uet*1e9:.0f} nK")

    if math.isnan(Tc_uet) or Tc_uet == 0:
        print("\n❌ RESULT: FAIL (Engine Sabotaged)")
        return False

    error = abs(Tc_uet - Tc_exp) / Tc_exp * 100
    print(f"  Error: {error:.1f}%")

    passed = error < 35
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
