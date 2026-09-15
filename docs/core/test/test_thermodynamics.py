"""
UET Thermodynamics Proof
========================
Demonstrates that the UET Master Equation strictly obeys the Second Law of Thermodynamics.

Theory:
The UET equation: dC/dt = kappa*Lap(C) + beta*(C - C^3)
is actually a GRADIENT FLOW of the Free Energy Functional F[C]:
    F[C] = Integral [ (kappa/2)|Grad C|^2 + V(C) ] dV
    where V(C) = -beta*C^2/2 + beta*C^4/4

Proof:
    dF/dt = Integral [ dF/dC * dC/dt ]
          = Integral [ - (dC/dt) * (dC/dt) ]  <-- since dC/dt = -dF/dC
          = - Integral [ (dC/dt)^2 ]
          <= 0

We will verify numerically that F[C] strictly decreases over time, proving the system seeks Equilibrium (Maximum Entropy).
"""
from docs.core.core_paths import repo_root

import sys
import numpy as np
import matplotlib.pyplot as plt
import os

repo_root = str(repo_root())
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from docs.core.uet_master_equation import UETParameters
from docs.core.uet_base_solver import UETBaseSolver


class ThermoTest(UETBaseSolver):
    def __init__(self, nx=64, ny=64, dt=0.01, params=None):
        super().__init__(
            nx=nx, ny=ny, dt=dt, params=params, name="Thermo_Test", log_dir="Result"
        )

        # Initialize random state (High Free Energy)
        np.random.seed(42)
        self.C = np.random.uniform(-1.5, 1.5, (ny, nx))

    def get_free_energy(self):
        """Calculate Ginzburg-Landau Free Energy."""
        # 1. Gradient Energy (Kinetic / Spatial Complexity)
        # Term: (kappa/2) * |Grad C|^2
        grad_x = np.gradient(self.C, axis=1)
        grad_y = np.gradient(self.C, axis=0)
        grad_term = (self.params.kappa / 2.0) * (grad_x**2 + grad_y**2)

        # 2. Potential Energy (Local Reaction)
        # Force f(C) = beta*(C - C^3)
        # Potential V(C) such that f = -V'
        # V'(C) = -beta*C + beta*C^3
        # V(C) = -beta*C^2/2 + beta*C^4/4
        # We assume equilibrium at C = +/- 1 (if beta=kappa balance?)
        # Let's use the exact integral of the force term.
        pot_term = self.params.beta * (-0.5 * self.C**2 + 0.25 * self.C**4)

        total_F = np.sum(grad_term + pot_term)
        return total_F

    def step(self, step_idx=0):
        # Explicit Euler Step

        # Diff
        lap = (
            np.roll(self.C, 1, axis=0)
            + np.roll(self.C, -1, axis=0)
            + np.roll(self.C, 1, axis=1)
            + np.roll(self.C, -1, axis=1)
            - 4 * self.C
        )
        diffusion = self.params.kappa * lap

        # Reaction
        reaction = self.params.beta * (self.C - self.C**3)

        dC = (diffusion + reaction) * self.dt
        self.C += dC

        if self.logger:
            self._log_current_state(step_idx)


def run_thermo_proof():
    print("=" * 70)
    print("🔥 UET THERMODYNAMICS PROOF (2nd Law Check)")
    print("=" * 70)

    params = UETParameters(kappa=0.1, beta=1.0)
    sim = ThermoTest(nx=64, ny=64, dt=0.01, params=params)

    F_history = []

    print("Simulating Gradient Flow...")
    for i in range(500):
        F = sim.get_free_energy()
        F_history.append(F)
        sim.step(i)

    # Validation
    F = np.array(F_history)
    dF = np.diff(F)

    # Check strict monotonicity (allow tiny numerical noise)
    violations = np.sum(dF > 1e-6)

    print(f"Initial Free Energy: {F[0]:.4f}")
    print(f"Final Free Energy:   {F[-1]:.4f}")
    print(f"Energy Violations:   {violations} (Should be 0)")

    if violations == 0:
        print("\n✅ PASS: Free Energy decreases monotonically.")
        print("   -> dF/dt <= 0 Checked.")
        print("   -> The Equation obeys the Second Law of Thermodynamics.")
        print("   -> System evolves towards Equilibrium (Minimum F).")
    else:
        print("\n❌ FAIL: Second Law Violation detected.")

    print("=" * 70)


if __name__ == "__main__":
    run_thermo_proof()
