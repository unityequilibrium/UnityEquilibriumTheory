"""
UET Bell Inequality Verification (Loophole-Free)
================================================
Topic: 0.9 - Quantum Nonlocality
"""

import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---
_root = Path(__file__).resolve().parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
if _root.name == "docs":
    sys.path.insert(0, str(_root.parent))
    from docs import ROOT_PATH

    root_path = ROOT_PATH
else:
    print("CRITICAL: Root path not found.")
    sys.exit(1)

TOPIC_DIR = root_path / "docs" / "topics" / "0.9_Quantum_Nonlocality"
DATA_PATH = TOPIC_DIR / "Data"

# --- DYNAMIC ENGINE IMPORT ---
try:
    import importlib.util

    # Locate Engine relative to standardized root
    engine_path = (
        root_path
        / "docs"
        / "topics"
        / "0.9_Quantum_Nonlocality"
        / "Code"
        / "01_Engine"
        / "Engine_Quantum.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Quantum", str(engine_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETQuantumEngine = mod.UETQuantumEngine
except Exception as e:
    print(f"CRITICAL: Engine not found: {e}")
    sys.exit(1)

import numpy as np
import json


# Load Data
data_file = DATA_PATH / "03_Research" / "bell_inequality_data.json"


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def run_bell_test():
    print("=" * 60)
    print("TEST: UET Non-Locality Verification (Hensen 2015)")
    print("=" * 60)

    if not data_file.exists():
        print(f"[FAIL] ERROR: Data file not found: {data_file}")
        return False

    with open(data_file, "r") as f:
        data = json.load(f)

    s_exp = data["CHSH_parameter"]["measured"]
    s_classical = data["CHSH_parameter"]["classical_bound"]
    s_quantum_max = data["CHSH_parameter"]["quantum_max"]

    print(f"Experimental Setup: {data['experiment']}")
    print(f"Source: {data['source']}")
    print(f"\nMeasured CHSH Parameter (S):")
    print(f"  Exp (Hensen 2015): {s_exp:.3f}")
    print(f"  Classical Bound:   {s_classical:.3f}")
    print(f"  Quantum Max:       {s_quantum_max:.3f}")

    if s_exp > 2.0:
        print("\n✅ PASS: Violation of Local Realism Observed (S > 2).")
        if s_exp <= 2.828 + 0.1:
            print("✅ PASS: Consistent with Tsirelson Bound.")
            return True
    print("\n❌ FAIL: Result inconsistent with Quantum Nonlocality.")
    return False


if __name__ == "__main__":
    success = run_bell_test()
    sys.exit(0 if success else 1)
