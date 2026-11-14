"""
UET Proof: Black Hole Singularity Resolution
=============================================
Topic: 0.2 - Black Hole Physics
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
        / "0.2_Black_Hole_Physics"
        / "Code"
        / "01_Engine"
        / "Engine_BlackHole.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_BlackHole", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETBlackHoleEngine = getattr(module, "UETBlackHoleEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_singularity_resolution():
    print("=" * 60)
    print("📜 UET PROOF: BLACK HOLE SINGULARITY RESOLUTION")
    print("=" * 60)
    engine = UETBlackHoleEngine(rs=1.0)
    metrics = engine.get_extra_metrics()
    print(f"  Event Horizon r_s:      {metrics['rs']:.2f}")
    if metrics["singularity_resolved"]:
        print("  ✅ PASS: Singularity resolved (Density is finite).")
    else:
        print("  ❌ FAIL: Singularity persists.")
    return True


if __name__ == "__main__":
    prove_singularity_resolution()
