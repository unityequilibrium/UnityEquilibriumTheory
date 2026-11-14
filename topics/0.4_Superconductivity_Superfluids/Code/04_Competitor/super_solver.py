"""
UETSuperSolver: Superconductivity calculations using BCS/McMillan theory
========================================================================
Provides Tc (critical temperature) predictions for superconductors.
"""

import math


class UETSuperSolver:
    """UET Superconductivity Solver with McMillan formula implementation."""

    def __init__(self, kappa=0.5):
        self.kappa = kappa
        self.theta_D = 300.0  # Debye temperature (K)
        self.lambda_ep = 0.5  # electron-phonon coupling
        self.mu_star = 0.13  # Coulomb pseudopotential

    def set_material(self, theta_D, lambda_ep, mu_star):
        """Set material parameters for Tc calculation."""
        self.theta_D = theta_D
        self.lambda_ep = lambda_ep
        self.mu_star = mu_star

    def find_critical_temperature(self):
        """
        Calculate critical temperature using McMillan formula:
        Tc = (theta_D / 1.45) * exp(-1.04 * (1 + lambda) / (lambda - mu* (1 + 0.62*lambda)))
        """
        lam = self.lambda_ep
        mu = self.mu_star
        theta = self.theta_D

        # McMillan formula (1968)
        if lam <= mu * (1 + 0.62 * lam):
            return 0.0  # No superconductivity

        numerator = -1.04 * (1 + lam)
        denominator = lam - mu * (1 + 0.62 * lam)

        Tc = (theta / 1.45) * math.exp(numerator / denominator)
        return Tc


if __name__ == "__main__":
    solver = UETSuperSolver()
    # Test with Niobium parameters
    solver.set_material(275, 0.82, 0.13)
    Tc = solver.find_critical_temperature()
    print(f"Nb Tc = {Tc:.2f} K (observed: 9.25 K)")
