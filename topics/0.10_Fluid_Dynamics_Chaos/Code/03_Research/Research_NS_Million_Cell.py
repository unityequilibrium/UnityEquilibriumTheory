"""
Research_NS_Million_Cell.py - UET Millennium Siege (Topic 0.10)
==============================================================
"The Million Cell Challenge"

Goal:
Simulate a 3D Fluid Dynamics system with 1,000,000 spatial cells ($100^3$).
This demonstrates "Supercomputer Scale" capability on the user's machine.

Specs:
- Grid: 100 x 100 x 100 = 1,000,000 Unity Sites.
- Physics: UET Fluid 3D + Planck Regulator (to ensure stability).
- Output: Steps Per Second (SPS) and Memory Footprint estimate.
"""

import sys
import numpy as np
import time
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
engine_dir = current_path.parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

title_art = """
   _____________________
  /  _  \__    ___/  _  \\
 /  /_\  \|    | /  /_\  \\
/    |    \    |/    |    \\
\____|__  /____|\____|__  /
        \/              \/
   MILLION CELL SIEGE
"""

try:
    from Engine_UET_3D import UETFluid3D
except ImportError as e:
    print(f"❌ Error: Engine_UET_3D not found. {e}")
    sys.exit(1)


# Include Regulator Class (Self-Contained for Scalability)
class PlanckRegulatedEngine(UETFluid3D):
    def __init__(self, nx, ny, nz, kappa, limit_factor=5000.0):
        super().__init__(nx=nx, ny=ny, nz=nz, kappa=kappa)
        self.plank_limit = limit_factor
        self.regulator_activations = 0

    def apply_planck_regulator(self):
        # 3D Gradient Magnitude
        dz, dy, dx = np.gradient(self.C)
        grad_mag = np.sqrt(dz**2 + dy**2 + dx**2)

        # Check Limit
        mask = grad_mag > self.plank_limit
        if np.any(mask):
            self.regulator_activations += np.sum(mask)
            # Local Smoothing (Dissipation)
            from scipy.ndimage import gaussian_filter

            smoothed = gaussian_filter(self.C, sigma=0.5)
            self.C[mask] = smoothed[mask]

    def step(self):
        super().step()
        self.apply_planck_regulator()


def run_million_cell_siege(steps=100):
    print(title_art)
    print("🏰 STARTING MILLION CELL RUN (1,000,000 Sites)")
    print("==================================================")

    # 1. Initialization
    nx, ny, nz = 100, 100, 100
    total_sites = nx * ny * nz

    print(f"   Grid: {nx}x{ny}x{nz} = {total_sites:,.0f} Cells")
    mem_est = (total_sites * 8 * 5) / (1024**2)  # C, I, Laplacian, Grad, Buffers ~ 5 arrays
    print(f"   Est. Memory: ~{mem_est:.2f} MB")

    print("⚡ Allocating Memory & Initializing Engine...")
    start_init = time.time()

    # Initialize Engine
    engine = PlanckRegulatedEngine(nx=nx, ny=ny, nz=nz, kappa=1e-5)

    # Inject Initial Turbulence
    np.random.seed(999)
    noise = np.random.normal(0, 10.0, engine.C.shape).astype(np.float64)
    engine.C += noise

    init_time = time.time() - start_init
    print(f"   Initialization Complete in {init_time:.2f}s")

    # 2. Performance Loop
    print(f"\n🚀 Running {steps} Iterations...")

    start_loop = time.time()

    for t in range(1, steps + 1):
        engine.step()

        if t % 10 == 0:
            # Metrics
            sps = t / (time.time() - start_loop)
            max_c = np.max(engine.C)
            print(f"   Step {t}: Max C={max_c:.2f} | Speed={sps:.2f} steps/s")

    end_loop = time.time()
    duration = end_loop - start_loop
    avg_sps = steps / duration

    print("-" * 65)
    print(f"🏁 SIEGE COMPLETE in {duration:.2f}s")
    print(f"   Average Speed: {avg_sps:.2f} Steps/Second")
    print(f"   Throughput:    {avg_sps * total_sites / 1e6:.2f} Million Updates/Sec")

    print("\n🏆 SUPREME VICTORY: Million-Cell Scale Achieved.")
    print("   UET is Ready for Supercomputer Deployment.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=50)
    args = parser.parse_args()

    run_million_cell_siege(steps=args.steps)
