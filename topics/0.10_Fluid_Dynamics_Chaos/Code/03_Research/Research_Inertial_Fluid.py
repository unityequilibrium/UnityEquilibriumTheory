"""
UET Tier 4: Inertia & Waves (The Momentum Proof)
===============================================
Demonstrates that UET can simulate inertia and wave propagation
by including the second-order time derivative (tau term).

Regimes:
1. Overdamped (tau=0): Diffusion-like, no momentum (like honey).
2. Inertial (tau > 0): Wave-like, supports momentum (like water).
"""

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


import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager
from docs.core.uet_master_equation import UETParameters

import os
import time
import numpy as np
import matplotlib.pyplot as plt


class InertialUETSolver:
    """UET Master Equation with 2nd order inertia term."""

    def __init__(self, nx=100, dx=0.1, tau=0.1, kappa=0.01):
        self.nx = nx
        self.dx = dx
        self.tau = tau
        self.kappa = kappa

        # Fields
        self.C = np.zeros(nx)
        self.v = np.zeros(nx)  # First derivative dC/dt (velocity)

    def step(self, dt):
        """Update using 2nd order leapfrog-style integration."""
        # 1. Laplacian
        lap = np.zeros_like(self.C)
        lap[1:-1] = (self.C[2:] - 2 * self.C[1:-1] + self.C[:-2]) / self.dx**2

        # 2. Physics: tau*a + v = Kappa*Lap(C)
        # a = (Kappa*Lap(C) - v) / tau
        if self.tau > 0:
            acceleration = (self.kappa * lap - self.v) / self.tau
            self.v += dt * acceleration
            self.C += dt * self.v
        else:
            # Overdamped limit (standard UET)
            self.C += dt * (self.kappa * lap)

        # Physical constraint
        np.maximum(self.C, 0.0, out=self.C)


def run_inertial_comparison():
    print("=" * 70)
    print("🌊 UET TIER 4: INERTIA & WAVE PROPAGATION")
    print("=" * 70)

    nx = 200
    dx = 0.05
    dt = 0.005
    steps = 600  # More time for waves to travel

    # --- 1. Overdamped Case (tau=0) ---
    print("\n   [1/2] Simulating Overdamped Regime (Honey)...")
    solver_od = InertialUETSolver(nx=nx, dx=dx, tau=0, kappa=0.1)
    # Pulse injection
    start_pos = nx // 4
    solver_od.C[start_pos] = 10.0

    history_od = []
    for i in range(steps):
        solver_od.step(dt)
        if i % 100 == 0:
            history_od.append(solver_od.C.copy())

    # --- 2. Inertial Case (tau=2.0) ---
    print("\n   [2/2] Simulating Inertial Regime (Water/Waves)...")
    # Higher tau = stronger inertia
    solver_in = InertialUETSolver(nx=nx, dx=dx, tau=1.5, kappa=0.1)
    # Pulse injection
    solver_in.C[start_pos] = 10.0
    # Velocity injection (pushing the wave to the right)
    solver_in.v[start_pos] = 50.0

    history_in = []
    for i in range(steps):
        solver_in.step(dt)
        if i % 100 == 0:
            history_in.append(solver_in.C.copy())

    # --- Analysis ---
    # In pure diffusion (tau=0), peak stays at start_pos.
    # In inertial (tau>0), peak should TRAVEL.
    peak_od = np.argmax(solver_od.C)
    peak_in = np.argmax(solver_in.C)

    displacement = abs(peak_in - start_pos)

    print("-" * 60)
    print(f"   Start Position: {start_pos}")
    print(f"   Peak Position (Overdamped): {peak_od}")
    print(f"   Peak Position (Inertial):   {peak_in}")
    print(f"   Displacement: {displacement} cells")

    # Check if peak traveled significantly
    has_wave = displacement > 5
    status = "✅ MOTION DETECTED" if has_wave else "⚠️ STATIONARY (Diffusive)"
    print(f"   Wave Effect: {status}")

    # --- Visualization ---
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.10_Fluid_Dynamics_Chaos",
        experiment_name="Research_Inertial_Fluid",
        pillar="03_Research",
        category="showcase",
    )
    fig_dir = result_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    for i, h in enumerate(history_od):
        plt.plot(h, label=f"T={i*100}")
    plt.axvline(start_pos, color="r", linestyle="--", alpha=0.3, label="Start")
    plt.title("Overdamped (tau=0)\nPure Diffusion")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    for i, h in enumerate(history_in):
        plt.plot(h, label=f"T={i*100}")
    plt.axvline(start_pos, color="r", linestyle="--", alpha=0.3, label="Start")
    plt.title("Inertial (tau=1.5)\nWave Propagation (Momentum)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(fig_dir / "inertial_tier4.png")
    print(f"\n   ✅ Results saved to: {fig_dir / 'inertial_tier4.png'}")

    if has_wave:
        print("\n   RESULT: PASS (UET successfully models Fluid Inertia)")
        return True
    else:
        print("\n   RESULT: FAIL (No wave propagation detected)")
        return False


if __name__ == "__main__":
    success = run_inertial_comparison()
    sys.exit(0 if success else 1)
