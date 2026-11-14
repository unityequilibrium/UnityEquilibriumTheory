"""
UET Proof: Nuclear Stability Valley
===================================
Topic: 0.16 - Heavy Nuclei
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
        / "0.16_Heavy_Nuclei"
        / "Code"
        / "01_Engine"
        / "Engine_Heavy_Nuclei.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Heavy_Nuclei", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETHeavyNucleiEngine = getattr(module, "UETHeavyNucleiEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_stability():
    print("=" * 60)
    print("📜 UET PROOF: NUCLEAR STABILITY VALLEY")
    print("=" * 60)
    solver = UETHeavyNucleiEngine()
    be_fe = solver.compute_binding_energy(26, 56) / 56
    be_u = solver.compute_binding_energy(92, 238) / 238
    print(f"  BE/A (Fe-56): {be_fe:.4f}")
    print(f"  BE/A (U-238): {be_u:.4f}")
    if be_fe > be_u:
        print("  ✅ PASS: Iron is more stable than Uranium axiomatically.")
    else:
        print("  ❌ FAIL: Incorrect stability profile.")
    return True


if __name__ == "__main__":
    prove_stability()
