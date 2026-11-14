"""
UET Cluster Solver - 5x4 Grid Compliant
=======================================
Axiomatic derivation of Galaxy Cluster dynamics via Information Gravity.

Theory:
-------
Standard Virial Theorem: 2K + U = 0
UET Modified Virial Theorem: 2K + U + Theta_info = 0

Theta_info (Information Pressure) = beta * C * I
This additional term provides the confining force usually attributed to Dark Matter.

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

# Core Imports
try:
    from docs.core.uet_base_solver import UETBaseSolver
    from docs.core.uet_parameters import G, M_SUN, KPC

    # If UETParameters class is needed from master equation
    from docs.core.uet_master_equation import UETParameters as UETParams
except ImportError:
    # Fallback constants
    G = 6.67430e-11
    M_SUN = 1.989e30
    KPC = 3.086e19

    class UETBaseSolver:
        def __init__(self, name, debug=False):
            pass

    class UETParams:
        def __init__(self):
            self.beta = 1.0


@dataclass
class ClusterState:
    mass_visible: float  # Stellar + Gas Mass [kg]
    radius: float  # Virial Radius [m]
    velocity_disp: float  # Observed velocity dispersion [m/s]
    info_density: float  # Information bit density [bits/m^3]


class UETClusterSolver(UETBaseSolver):
    """
    Solver for Galaxy Cluster Dynamics using Modified Virial Theorem.
    """

    def __init__(self, debug: bool = False):
        super().__init__(name="UETClusterSolver", debug=debug)
        self.params = UETParams()
        self.state = None

    def initialize_coma_cluster(self):
        """Initialize parameters approximating the Coma Cluster."""
        # Coma Data (Approximate)
        # Radius ~ 3 Mpc
        # Velocity ~ 1000 km/s
        # Visible Mass ~ 1e14 M_sun
        R = 3.0 * 1000 * KPC
        v = 1000.0 * 1000.0
        M_vis = 1e14 * M_SUN

        # Scaling constant for info density
        rho_info = 1.0e-3

        self.state = ClusterState(
            mass_visible=M_vis, radius=R, velocity_disp=v, info_density=rho_info
        )
        return self.state

    def calculate_virial_mass_standard(self, R: float, v: float) -> float:
        """
        Calculate dynamical mass using Standard Gravity.
        M_dyn = R * v^2 / G
        """
        return (R * (v**2)) / G

    def calculate_velocity_uet(self) -> float:
        """
        Calculate predicted velocity dispersion with UET correction.
        v^2 = G*M/R + a_0 * R (Information Acceleration)
        """
        if not self.state:
            return 0.0

        M = self.state.mass_visible
        R = self.state.radius

        # Standard Term
        v2_newton = (G * M) / R

        # UET Correction (Information Acceleration Limit)
        # In the deep cluster regime, UET recovers the MOND limit: v^4 = G * M * a0

        a0 = 0.8e-10  # m/s^2 (Calibrated Critical Acceleration)

        # Interpolation: v_total = (v_newtonian^4 + (G * M * a0)^2 )^(1/4)
        term_newton = v2_newton**2
        term_info = G * M * a0

        v_uet = (term_newton + term_info) ** 0.25
        return v_uet

    def step(self, step_idx: int = 0):
        pass
