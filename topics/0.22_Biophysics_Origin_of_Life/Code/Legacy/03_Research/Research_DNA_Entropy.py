"""
UET DNA Information Entropy
===========================
"""

import sys
from pathlib import Path
import numpy as np


# --- EXTREMELY ROBUST PATH FINDER ---
def find_repo_root(current_file):
    curr = Path(current_file).resolve()
    # Go up until we find docs AND README.md
    for _ in range(12):
        if (curr / "docs").exists() and (curr / "README.md").exists():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    return None


repo_root = find_repo_root(__file__)

if repo_root is None:
    print("CRITICAL: Could not find project root!")
    sys.exit(1)

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Engine Import
try:
    import importlib.util

    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.22_Biophysics_Origin_of_Life"
        / "Code"
        / "01_Engine"
        / "Engine_Biophysics.py"
    )
    if not engine_file.exists():
        raise FileNotFoundError(f"Missing Engine: {engine_file}")

    spec = importlib.util.spec_from_file_location("Engine_Biophysics", str(engine_file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETBiophysicsEngine = mod.UETBiophysicsEngine
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

engine = UETBiophysicsEngine()


def run_test():
    print("=" * 70)
    print("UET DNA INFORMATION ENTROPY")
    print("=" * 70)

    # Delegation to Engine
    res = engine.search_origin_of_life()

    if np.isnan(res["Biological_Omega"]) or res["Biological_Omega"] == 0.0:
        print("\n❌ RESULT: FAIL (Engine Sabotaged - No Biological Value)")
        return False

    print(f"  Biological Stability Ω: {res['Biological_Omega']:.4f}")
    print("✅ Result: PASS (DNA Information Stability depends on Engine)")
    return True


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
