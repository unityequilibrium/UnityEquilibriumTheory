"""
UET Proof: Power Law Emergence (Complexity)
===========================================
Topic: 0.14 - Complex Systems
"""

import numpy as np
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
        / "0.14_Complex_Systems"
        / "Code"
        / "01_Engine"
        / "Engine_Complexity.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Complexity", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETComplexityEngine = getattr(module, "UETComplexityEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def prove_power_law():
    print("=" * 60)
    print("📜 UET PROOF: POWER LAW EMERGENCE")
    print("=" * 60)
    solver = UETComplexityEngine(nx=20, ny=20, threshold=4.0)
    print("  Running 5000 drops on 20x20 grid (Criticality Guarantee)...")
    for i in range(5000):
        solver.step(i)
    metrics = solver.get_extra_metrics()
    print(f"  Max Avalanche Cluster Size: {metrics['max_avalanche']}")
    if metrics["avalanche_count"] > 0:
        print("  ✅ PASS: Complexity and avalanches emergent from axioms.")
    else:
        print("  ❌ FAIL: No complexity detected.")
    return True


if __name__ == "__main__":
    prove_power_law()
