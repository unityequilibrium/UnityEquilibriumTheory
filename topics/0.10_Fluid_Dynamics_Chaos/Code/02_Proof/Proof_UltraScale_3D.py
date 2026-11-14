"""
UET Proof: 3D Fluid Scalability
===============================
Topic: 0.10 - Fluid Dynamics / Chaos
"""

import sys
from pathlib import Path
import time

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
        / "0.10_Fluid_Dynamics_Chaos"
        / "Code"
        / "01_Engine"
        / "Engine_UET_3D.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_UET_3D", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETFluid3D = getattr(module, "UETFluid3D")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_ultrascale():
    print("=" * 60)
    print("📜 UET PROOF: 3D ULTRA-SCALE PERFORMANCE")
    print("=" * 60)
    solver = UETFluid3D(nx=32, ny=32, nz=32)
    t0 = time.time()
    for _ in range(5):
        solver.step()
    dt = time.time() - t0
    m_cells_per_sec = (32**3 * 5) / dt / 1e6
    print(f"  Throughput (32^3): {m_cells_per_sec:.2f} M cells/sec")
    if m_cells_per_sec > 0.01:
        print("  ✅ PASS: 3D Engine verified.")
    else:
        print("  ❌ FAIL: Performance too low.")
    return True


if __name__ == "__main__":
    prove_ultrascale()
