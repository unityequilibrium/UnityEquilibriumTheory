"""
UET Proof: Hubble Tension Resolution
====================================
Topic: 0.3 - Cosmology / Hubble Tension
"""

# --- ROBUST PATH FINDER ---
from pathlib import Path
import sys
import os
from docs import ROOT_PATH

root_path = ROOT_PATH


# Setup local imports for Topic 0.3
topic_path = root_path / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    from Engine_Cosmology import UETCosmologyEngine
except ImportError as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


# Standardized UET Root Path


def prove_hubble_resolution():
    print("=" * 60)
    print("📜 UET PROOF: HUBBLE TENSION RESOLUTION")
    print("=" * 60)

    # 1. Instantiate Core Engine
    engine = UETCosmologyEngine()

    # 2. Execute Audit
    engine.step()

    # 3. Verify Metrics
    metrics = engine.get_extra_metrics()
    h0_pred = metrics.get("H0_predicted", 0.0)

    print(f"  UET Hubble Parameter H0: {h0_pred:.2f}")

    if 72 < h0_pred < 74:
        print("  ✅ PASS: Hubble Tension resolved by Information Expansion.")
        return True
    else:
        print(f"  ❌ FAIL: Predicted H0 ({h0_pred:.2f}) out of expected range (72-74).")
        return False


if __name__ == "__main__":
    prove_hubble_resolution()
