"""
UET Proof: Hydrogen Spectrum (Atomic Physics)
============================================
Topic: 0.20 - Atomic Physics

Validates correct loading of NIST Data and comparison logic.
"""

import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# Path setup
# --- ROBUST PATH FINDER ---


# Setup local imports for Topic 0.20
topic_path = root_path / "docs" / "topics" / "0.20_Atomic_Physics"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    # Use the new Class logic
    from Engine_Atomic_Hydrogen import UETAtomicEngine
except ImportError as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


# Standardized UET Root Path


def prove_hydrogen():
    print("=" * 60)
    print("📜 UET PROOF: HYDROGEN SPECTRUM (Real Data Verified)")
    print("=" * 60)

    # Instantiate the Engine
    engine = UETAtomicEngine()
    success = engine.run_atomic_verification()

    if success:
        print("  ✅ PASS: Engine correctly loaded NIST Data and matched Theory.")
    else:
        print("  ❌ FAIL: Engine integrity check failed.")

    return success


if __name__ == "__main__":
    prove_hydrogen()
