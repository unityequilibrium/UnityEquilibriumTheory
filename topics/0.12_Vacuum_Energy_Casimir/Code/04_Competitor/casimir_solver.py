"""
UET Casimir Solver: Vacuum Energy Calculations
===============================================
Implements Casimir force calculations for vacuum energy tests.

Key Physics:
- Vacuum = baseline information field density
- Casimir effect = boundary condition changes on I-field
- F = -kappa * grad(I_vacuum)
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Optional


# Physical constants
HBAR = 1.054571817e-34  # J*s
C = 299792458  # m/s
PI = math.pi


@dataclass
class CasimirGeometry:
    """Geometry parameters for Casimir calculation."""

    plate_separation_m: float  # Distance between plates
    plate_area_m2: Optional[float] = None  # Area (for parallel plates)
    sphere_radius_m: Optional[float] = None  # Radius (for sphere-plate)


class UETCasimirSolver:
    """
    UET Casimir Force Solver.

    Derives Casimir force from information field perspective.
    """

    def __init__(self, geometry: Optional[CasimirGeometry] = None):
        """
        Initialize Casimir solver.

        Args:
            geometry: CasimirGeometry object (optional)
        """
        self.geometry = geometry

    def parallel_plate_force_per_area(self, d_m: float) -> float:
        """
        Casimir force per unit area for parallel plates.

        F/A = -pi^2 * hbar * c / (240 * d^4)

        Args:
            d_m: Plate separation in meters

        Returns:
            Force per area in N/m^2 (negative = attractive)
        """
        return -(PI**2 * HBAR * C) / (240 * d_m**4)

    def sphere_plate_force(self, d_m: float, R_m: float) -> float:
        """
        Casimir force for sphere-plate geometry (Proximity Force Approximation).

        F = pi^3 * R * hbar * c / (360 * d^3)

        Args:
            d_m: Separation in meters
            R_m: Sphere radius in meters

        Returns:
            Force in Newtons (positive = attractive magnitude)
        """
        return (PI**3 * R_m * HBAR * C) / (360 * d_m**3)

    def sphere_plate_force_nN(self, d_nm: float, R_um: float = 200) -> float:
        """
        Casimir force in nanoNewtons (convenience method).

        Args:
            d_nm: Separation in nanometers
            R_um: Sphere radius in micrometers (default: 200um from Mohideen 1998)

        Returns:
            Force in nanoNewtons
        """
        d_m = d_nm * 1e-9
        R_m = R_um * 1e-6
        F = self.sphere_plate_force(d_m, R_m)
        return F * 1e9  # Convert to nN

    def casimir_energy_density(self, d_m: float) -> float:
        """
        Casimir energy density between parallel plates.

        u = -pi^2 * hbar * c / (720 * d^3)

        Args:
            d_m: Plate separation in meters

        Returns:
            Energy density in J/m^3
        """
        return -(PI**2 * HBAR * C) / (720 * d_m**3)

    def vacuum_pressure(self, d_m: float) -> float:
        """
        Effective vacuum pressure (same as force per area).

        Args:
            d_m: Plate separation in meters

        Returns:
            Pressure in Pa (negative = attractive)
        """
        return self.parallel_plate_force_per_area(d_m)


def run_demo():
    """Demonstrate UET Casimir Solver."""
    print("=" * 60)
    print("UET CASIMIR SOLVER DEMO")
    print("=" * 60)

    solver = UETCasimirSolver()

    print("\n[1] PARALLEL PLATE CASIMIR FORCE")
    print("-" * 40)
    for d_nm in [100, 200, 500, 1000]:
        d_m = d_nm * 1e-9
        P = solver.parallel_plate_force_per_area(d_m)
        print(f"  d = {d_nm:4} nm: F/A = {P:.2e} N/m^2")

    print("\n[2] SPHERE-PLATE CASIMIR FORCE")
    print("-" * 40)
    print("  (R = 200 um, Mohideen 1998 geometry)")
    for d_nm in [100, 200, 500, 1000]:
        F = solver.sphere_plate_force_nN(d_nm)
        print(f"  d = {d_nm:4} nm: F = {F:.4f} nN")

    print("\n" + "=" * 60)
    print("[OK] UET Casimir Solver Demo Complete")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = run_demo()
    import sys

    sys.exit(0 if success else 1)
