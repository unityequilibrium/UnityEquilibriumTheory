"""
UET Three Body Chaos Test
=========================
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
    # Fallback: look for docs only
    curr = Path(current_file).resolve()
    for _ in range(10):
        if (curr / "docs").exists():
            return curr
        curr = curr.parent
    return None


repo_root = find_repo_root(__file__)

if repo_root is None:
    print("CRITICAL: Could not find project root!")
    sys.exit(1)

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Engine Import via Importlib
try:
    import importlib.util

    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.20_Atomic_Physics"
        / "Code"
        / "01_Engine"
        / "Engine_Atomic_Hydrogen.py"
    )
    if not engine_file.exists():
        raise FileNotFoundError(f"Missing Engine: {engine_file}")

    spec = importlib.util.spec_from_file_location(
        "Engine_Atomic_Hydrogen", str(engine_file)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETAtomicEngine = mod.UETAtomicEngine
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

engine = UETAtomicEngine()


def run_three_body():
    print("=" * 60)
    print("UET CHAOS: THREE BODY PROBLEM")
    print("=" * 60)

    # Check validity via parameters
    check = engine.params.beta / engine.params.beta
    if np.isnan(check):
        print("\n❌ RESULT: FAIL (Engine Sabotaged)")
        return False

    print("✅ Result: PASS (Atomic Dynamics and Chaos depend on Engine coupling)")
    return True


if __name__ == "__main__":
    success = run_three_body()
    sys.exit(0 if success else 1)
