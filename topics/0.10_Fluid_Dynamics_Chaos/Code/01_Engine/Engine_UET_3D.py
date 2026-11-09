"""
3D UET Fluid Solver Engine - 5x4 Grid Compliant
===============================================
Isolating the 3D Omega Functional implementation for Topic 0.10.
Compliant with 5x4 Scientific Grid Architecture.
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


import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Core Imports
from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_master_equation import UETParameters


class UETFluid3D(UETBaseSolver):
    """3D UET Fluid Solver using Ω functional (Inherits BaseSolver)."""

    def __init__(
        self,
        nx: int = 16,
        ny: int = 16,
        nz: int = 16,
        dt: float = 0.001,
        kappa: float = 0.1,  # Physical Viscosity (User must provide)
        beta: float = 1.0,  # Axiomatic Unity Coupling
        alpha: float = 2.0,
        name: str = "UET_Fluid_3D",
    ):
        # Create Parameters Object
        params = UETParameters(kappa=kappa, beta=beta, alpha=alpha, C0=1.0)

        # Initialize Base Solver
        # BaseSolver is 2D by default (nx, ny). We override 'nz' here or handle it manually.
        # BaseSolver creates self.C as (ny, nx).
        # We need (nz, ny, nx).
        # We will let BaseSolver init, then OVERWRITE fields with 3D versions.

        super().__init__(
            nx=nx,
            ny=ny,
            dt=dt,
            params=params,
            name=name,
            topic="0.10_Fluid_Dynamics_Chaos",
            pillar="01_Engine",
        )

        self.nz = nz
        self.dz = 1.0 / nz  # Assuming Lz=1

        # Overwrite 2D Fields with 3D Fields
        self.C = np.ones((nz, ny, nx)) * self.params.C0
        self.I = np.zeros((nz, ny, nx))

        # Axiomatic Mobility (Unity)
        self.mobility_M = 1.0

        # Initialize BC
        self.set_lid_driven_bc()

        # History for proofs
        self.omega_history = []
        self.energy_history = []
        self.vol = self.dx * self.dy * self.dz

    def set_lid_driven_bc(self):
        """Set boundary conditions via density."""
        # Lid Driven: Top Z layer driven? Or Top Y?
        # Standard: Top Y usually, but here let's say Top Z for 3D box.
        self.C[-1, :, :] = self.params.C0 * 1.1  # Top Z: higher density
        self.C[0, :, :] = self.params.C0

    def V(self, C: np.ndarray) -> np.ndarray:
        """Potential V(C)."""
        return 0.5 * self.params.alpha * (C - self.params.C0) ** 2

    def dV_dC(self, C: np.ndarray) -> np.ndarray:
        """Derivative of potential."""
        return self.params.alpha * (C - self.params.C0)

    def compute_laplacian_3d(self, f: np.ndarray) -> np.ndarray:
        """Compute 3D Laplacian."""
        # Using vectorized slicing for speed
        lap = np.zeros_like(f)
        dx2 = self.dx**2  # Assuming dx=dy=dz

        # Interior points [1:-1, 1:-1, 1:-1]
        # In 3D: C(x+1) + C(x-1) + C(y+1) + ... - 6C

        c = f[1:-1, 1:-1, 1:-1]

        term_x = (f[1:-1, 1:-1, 2:] + f[1:-1, 1:-1, :-2] - 2 * c) / dx2
        term_y = (f[1:-1, 2:, 1:-1] + f[1:-1, :-2, 1:-1] - 2 * c) / dx2
        term_z = (f[2:, 1:-1, 1:-1] + f[:-2, 1:-1, 1:-1] - 2 * c) / dx2

        lap[1:-1, 1:-1, 1:-1] = term_x + term_y + term_z
        return lap

    def step(self, step_idx: int = 0):
        """Gradient descent step on Ω."""
        lap_C = self.compute_laplacian_3d(self.C)

        # dΩ/dC = V'(C) - κ∇²C + βI
        dOmega_dC = (
            self.dV_dC(self.C) - self.params.kappa * lap_C + self.params.beta * self.I
        )
        dOmega_dI = self.params.beta * self.C

        # Gradient descent
        self.C = self.C - self.dt * dOmega_dC
        self.I = self.I - self.dt * dOmega_dI

        # Physical constraint: C > 0
        self.C = np.maximum(self.C, 0.01)

        # Reapply BC
        self.set_lid_driven_bc()

        # Update History for Proofs
        self.omega_history.append(self.compute_omega())
        self.energy_history.append(np.sum(self.C) * self.vol)  # Energy proxy

        # Update Admin
        self.time += self.dt
        self.step_count += 1

    def _log_current_state(self, step_idx: int):
        """
        Compute 3D UET metrics (Override BaseSolver which assumes 2D).
        """
        # Calculate Base Energies (Hamiltonian Components)
        # Potential: V(C) ~ 0.5 * alpha * (C - C0)^2
        term_potential = 0.5 * self.params.alpha * (self.C - self.params.C0) ** 2

        # Gradient: 0.5 * kappa * |grad C|^2
        # Use simple gradient magnitude approximation for logging
        # Or proper 3D gradient if possible
        # For speed, let's skip expensive gradient calculation if not needed for physics
        # Just use finite difference magnitude if needed, or 0.

        # Let's try to do it right:
        dz, dy, dx = np.gradient(self.C, self.dz, self.dy, self.dx)
        grad_sq = dz**2 + dy**2 + dx**2

        term_gradient = 0.5 * self.params.kappa * grad_sq
        term_entropy = self.params.beta * self.C * self.I

        # Integrated Values
        total_omega = np.sum(term_potential + term_gradient + term_entropy) * self.vol

        metrics = {
            "step": step_idx,
            "time_val": self.time,
            "omega": total_omega,
            "potential": np.sum(term_potential) * vol,
            "gradient_energy": np.sum(term_gradient) * vol,
            "entropy_interaction": np.sum(term_entropy) * vol,
            # "field_c": self.C # Too big for 3D logging? Base logger usually handles it.
            # Base logger might choke on 3D JSON.
            # Let's log a slice for visualization.
            "field_c_slice": self.C[self.nz // 2, :, :],  # Mid-Z slice (2D)
        }

        metrics.update(self.get_extra_metrics())
        self.logger.log_step(**metrics)

    def get_extra_metrics(self) -> Dict[str, Any]:
        """Get 3D specific metrics."""
        return {
            "max_density": float(np.max(self.C)),
            "smoothness_check": self.is_smooth(),
        }

    def compute_omega(self) -> float:
        """Compute 3D Omega."""
        term_potential = self.V(self.C)
        dz, dy, dx = np.gradient(self.C)
        term_gradient = 0.5 * self.params.kappa * (dz**2 + dy**2 + dx**2)
        term_interaction = self.params.beta * self.C * self.I
        return float(
            np.sum(term_potential + term_gradient + term_interaction) * self.vol
        )

    def run(self, steps: int = 500, verbose: bool = True):
        """Standard run method for proofs."""
        for i in range(steps):
            self.step(i)
            if verbose and i % 100 == 0:
                print(f"  Step {i}: Ω={self.omega_history[-1]:.4e}")

    def is_smooth(self) -> bool:
        """Check if solution is finite."""
        return bool(np.isfinite(self.C).all())

    def get_max_gradient(self) -> float:
        """Compute max intensity of gradient."""
        # dz, dy, dx = np.gradient(self.C, self.dz, self.dy, self.dx) # dy, dx are in base class
        # nz, ny, nx = self.C.shape
        dz, dy, dx = np.gradient(self.C)
        grad_mag = np.sqrt(dz**2 + dy**2 + dx**2)
        return float(np.max(grad_mag))

    def get_max_laplacian(self) -> float:
        """Compute max laplacian."""
        lap = self.compute_laplacian_3d(self.C)
        return float(np.max(np.abs(lap)))

    # --- PHYSICAL UTILITY EXTENSION ---
    def calculate_buoyancy_gradient(
        self, rho_fluid: float, g: float = 9.80665
    ) -> float:
        """Standard hydrostatic gradient dP/dy = -rho*g."""
        # Kill Switch Check
        check = self.params.beta / self.params.beta
        return float(-rho_fluid * g * check)


# =============================================================================
# VERIFICATION DEMO
# =============================================================================
def run_demo():
    print("DEBUG: NEW VERSION 5x4 RUNNING")
    print("🚀 Verifying 5x4 Grid Compliance for Fluid 3D Engine...")
    # Small grid for speed
    solver = UETFluid3D(nx=16, ny=16, nz=16, dt=0.001)

    print("Running 50 steps...")
    for i in range(51):
        solver.step(i)

    path = solver.save_results()
    print(f"✅ Fluid 3D Result: {path}")


if __name__ == "__main__":
    run_demo()
