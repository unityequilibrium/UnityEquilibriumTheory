"""
UET Cluster Dynamics Engine - 5x4 Grid Compliant
================================================
Axiomatic derivation of Cluster Virial Mass and Dynamics.

Theory:
-------
Galaxy Clusters exhibit "Missing Mass" (Dark Matter).
UET explains this as an **Information Halo** effect, identical to Galaxies
but at a larger scale.

The Halo Density rho_h is derived from the Vacuum Coupling:
rho_h(r) = rho_b(r) * (rho_vac / rho_local)

Axioms:
- No Fitted Dark Matter.
- No "Cluster Temperature" fitting.
- Virial Equilibrium emerges from Information Pressure.

Topic: 0.15 Cluster Dynamics
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

# --- ROBUST PATH FINDER ---


# Core Imports
from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_master_equation import UETParameters


class UETClusterSolver(UETBaseSolver):
    """
    Cluster Dynamics Solver.
    Uses Information Halo to predict Virial Velocity without Dark Matter.
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        dt: float = 0.001,
        initial_mass: float = 100.0,
        temp_dispersion: float = 0.05,
        params: Optional[UETParameters] = None,
        name: str = "UET_Cluster_Stability",
    ):
        # Default Parameters if not provided
        if params is None:
            # Kappa (Pressure) vs Beta (Gravity)
            params = UETParameters(kappa=0.1, alpha=0.0, beta=0.0005)

        super().__init__(
            nx=nx,
            ny=ny,
            dt=dt,
            params=params,
            name=name,
            topic="0.15_Cluster_Dynamics",
            pillar="01_Engine",
            stable_path=True,
        )

        self.M_baryon = initial_mass
        self.temp_dispersion = temp_dispersion
        self.topic = "0.15_Cluster_Dynamics"
        self.pillar = "01_Engine"

        # Stability Constraints (Axiom 6: NEA)
        self.constraints = {"C_min": 1e-12}

        # Initialize Cluster Baryonic Distribution (King Profile or Gaussian)
        # King Profile ~ (1 + (r/rc)^2)^-1.5
        x = np.linspace(-10, 10, nx)
        y = np.linspace(-10, 10, ny)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        rc = 2.0  # Core radius

        # Baryonic Density (strictly positive)
        self.C = self.M_baryon * (1 + (R / rc) ** 2) ** (-1.5)
        self.C = np.clip(self.C, 1e-12, None)
        # Normalize to Mass
        norm = np.sum(self.C)
        if norm > 0:
            self.C *= self.M_baryon / norm

        self.I_halo = np.zeros_like(self.C)
        self.V_virial = 0.0

    def compute_halo(self):
        """
        Derive Information Halo using Fisher Information Density.
        Halo Density = kappa * |grad C|^2 / (C + epsilon)
        Regularization applied to prevent vacuum explosion.
        """
        # Handle coupled fields (tuple) from UETMasterEquation
        C_field = self.C[0] if isinstance(self.C, tuple) else self.C

        # 2D Gradient (ny, nx)
        grads = np.gradient(C_field, self.dy, self.dx)
        dy, dx = grads

        grad_sq = dy**2 + dx**2
        # Use soft min to prevent division by zero-ish
        return self.params.kappa * grad_sq / (C_field + 1e-6)

    def step(self, step_idx: int = 0):
        """
        Execute one DYNAMIC UET time step.
        Balance Attraction (Beta) and Dispersion (Kappa).
        """
        # 1. Physics Step via Base Solver (UET Master Equation)
        super().step(step_idx)

        # 2. Update Halo based on new C-field
        self.I_halo = self.compute_halo()
        self.I = self.I_halo  # SYNC: Ensure the Master Equation sees the Halo

        # 3. Update Virial Velocity based on total effective mass
        M_b = np.sum(self.C)
        M_h = np.sum(self.I_halo)
        M_tot = M_b + M_h
        self.V_virial = np.sqrt(M_tot)

    def get_kinetic_energy(self) -> float:
        """Estimate Kinetic Energy from Virial Velocity."""
        return 0.5 * self.M_baryon * (self.V_virial**2)

    def get_extra_metrics(self) -> Dict[str, Any]:
        M_b = np.sum(self.C)
        M_h = np.sum(self.I_halo)
        return {
            "M_baryon": M_b,
            "M_halo": M_h,
            "M_total": M_b + M_h,
            "Halo_Ratio": M_h / (M_b + 1e-9),
            "V_virial": self.V_virial,
            "kinetic": self.get_kinetic_energy(),
        }


def run_demo():
    print("🚀 Verifying Cluster Solver (0.15) - Dynamic Mode...")
    solver = UETClusterSolver(nx=40, ny=40, initial_mass=500.0)

    print("Computing Halo...")
    solver.step(0)

    m = solver.get_extra_metrics()
    print(f"  M_baryon: {m['M_baryon']:.2f}")
    print(f"  M_halo  : {m['M_halo']:.2f} (Derived from Fisher Info)")
    print(f"  M_total : {m['M_total']:.2f}")
    print(f"  Ratio   : {m['Halo_Ratio']:.2f}")

    path = solver.save_results()
    print(f"✅ Cluster Result: {path}")


if __name__ == "__main__":
    run_demo()
