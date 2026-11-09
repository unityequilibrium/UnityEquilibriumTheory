import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

import unittest
import numpy as np
import sys
from docs.core.uet_glass_box import UETPathManager

from pathlib import Path

# Bulletproof Core Injection
core_dir = Path(__file__).resolve().parents[4] / "core"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

try:
    from uet_matrix_engine import UniverseState, MatrixEvolution
except ImportError:
    # Fallback to docs package if available
    repo_root = Path(__file__).resolve().parents[5]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from docs.core.uet_matrix_engine import UniverseState, MatrixEvolution

# Inline fluid data to avoid import path issues
# Source: CRC Handbook of Chemistry and Physics
FLUID_DATA = {
    "water_20c": {"density": 998.2, "viscosity": 1.002e-3},  # kg/m³, Pa·s
    "air_20c": {"density": 1.204, "viscosity": 1.825e-5},
}


def get_fluid(name):
    return FLUID_DATA.get(name, FLUID_DATA["air_20c"])


class TestMatrixVortex(unittest.TestCase):
    def setUp(self):
        # 1. Load Real Fluid Data (Air at 20C)
        # Using Air because low viscosity promotes wake formation slightly better than honey
        self.fluid = get_fluid("air_20c")
        self.rho = self.fluid["density"]
        self.mu = self.fluid["viscosity"]

        # 2. Setup 3D Container
        self.size = 30
        self.state = UniverseState(self.size)

        # 3. Create Cylinder Obstacle in Center
        # Cylinder axis along Z (Vertical), Flow along X
        center = self.size // 2
        radius = 4
        z, y, x = np.indices((self.size, self.size, self.size))

        # Mask: x^2 + y^2 < r^2 (Vertical Cylinder)
        r_sq = (x - center) ** 2 + (y - center) ** 2
        self.obstacle_mask = r_sq < radius**2

        # 4. Engine
        # Note: In real simulation, we need to inject 'mu' into the step function.
        # Currently step() has hardcoded viscosity=0.01.
        # For this Stress Test, pass/fail depends on topological correctness (Wake),
        # not exact Reynolds number matching (which requires huge grids).
        self.engine = MatrixEvolution()

    def test_wake_formation(self):
        """Verify that a Wake (Low Velocity Zone) forms behind the cylinder."""

        # Inflow Velocity
        v_in = 1.0
        dt = 0.1
        steps = 40

        current_state = self.state

        print(f"Simulating Flow Past Cylinder (Air, {steps} steps)...")

        for i in range(steps):
            # 1. Evolve Physics
            current_state = self.engine.step(current_state, dt=dt)

            # 2. Apply Boundary Conditions
            vx = current_state.tensor[2]
            vy = current_state.tensor[3]
            vz = current_state.tensor[4]

            # A. Inflow (Left Wall, X=0) => Constant Velocity
            vx[:, :, 0] = v_in
            vy[:, :, 0] = 0
            vz[:, :, 0] = 0

            # B. Outflow (Right Wall, X=MAX) => Zero Gradient (Neumann) usually,
            # but for simple test, let's just let it flow or clamp boundaries.
            # We'll leave X=MAX evolvable (Open Boundary)

            # C. Obstacle (No Slip) => Velocity = 0 inside/on cylinder
            vx[self.obstacle_mask] = 0.0
            vy[self.obstacle_mask] = 0.0
            vz[self.obstacle_mask] = 0.0

            current_state.tensor[2] = vx
            current_state.tensor[3] = vy
            current_state.tensor[4] = vz

        # Analysis: Measure Velocity "Upstream" vs "Downstream" (Wake)
        center = self.size // 2
        z_slice = center  # Mid-height

        # Upstream (Before Cylinder)
        v_upstream = np.mean(
            current_state.tensor[2, z_slice, center, 2]
        )  # Close to inlet

        # Downstream (Behind Cylinder) - The Wake
        # Cylinder is at 'center', radius 4. So wake is at center + radius + buffer
        wake_pos = center + 6
        v_wake = np.mean(current_state.tensor[2, z_slice, center, wake_pos])

        print(f"Inflow Velocity: {v_in:.2f}")
        print(f"Upstream Velocity (X=2): {v_upstream:.2f}")
        print(f"Wake Velocity (X={wake_pos}): {v_wake:.2f}")

        # Verification: Wake should be slower than Upstream due to shielding/drag
        # Ratio < 0.8 implies significant drag/separation
        wake_ratio = v_wake / v_upstream
        print(f"Wake Ratio: {wake_ratio:.2f}")

        if wake_ratio < 0.5:
            print("✅ PASS: Significant Wake Detected (Flow Separation)")
        elif wake_ratio < 0.9:
            print("⚠️ PASS: Slight Wake Detected")
        else:
            print("❌ FAIL: No Wake (Flow passed through ghost?)")

        self.assertLess(
            wake_ratio, 0.9, "Obstacle must create a velocity deficit (Wake)."
        )


if __name__ == "__main__":
    unittest.main()
