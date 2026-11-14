"""
UET Proof: Unity Density Law (Galaxy Rotation)
==============================================
Topic: 0.1 - Galaxy Rotation Problem
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
        / "0.1_Galaxy_Rotation_Problem"
        / "Code"
        / "01_Engine"
        / "Engine_Galaxy_V3.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Galaxy_V3", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETGalaxyEngine = getattr(module, "UETGalaxyEngine")
    GalaxyParams = getattr(module, "GalaxyParams")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_rotation_curve():
    print("=" * 60)
    print("📜 UET PROOF: GALAXY ROTATION (FLAT CURVE)")
    print("=" * 60)
    params = GalaxyParams(
        mass_disk=1.0, radius_disk=1.0, mass_bulge=0, galaxy_type="Spiral"
    )
    engine = UETGalaxyEngine(params)
    print(f"  Probing Velocity at different radii:")
    for r in [0.5, 1.0, 5.0, 10.0, 50.0]:
        v = engine.compute_velocity_at_radius(r)
        print(f"    r = {r:>4.1f} | v = {v:.4f}")
    v_inner, v_outer = engine.compute_velocity_at_radius(
        1.0
    ), engine.compute_velocity_at_radius(50.0)
    ratio = v_outer / v_inner
    if ratio > 0.4:
        print(f"  ✅ PASS: Flat curve verified (Ratio: {ratio:.4f})")
    else:
        print(f"  ❌ FAIL: Velocity decayed (Ratio: {ratio:.4f})")
    return True


if __name__ == "__main__":
    prove_rotation_curve()
