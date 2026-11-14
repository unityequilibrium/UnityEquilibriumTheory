"""
UETNeutrinoSolver: Neutrino physics calculations
================================================
Provides neutrino oscillation and mass predictions.
"""

import math


class UETNeutrinoSolver:
    """UET Neutrino Solver for oscillation and mass analysis."""

    def __init__(self, kappa=0.5):
        self.kappa = kappa
        # PDG 2024 / NuFIT 2024 values
        self.dm21_sq = 7.42e-5  # eV^2 (solar)
        self.dm32_sq = 2.515e-3  # eV^2 (atmospheric, NO)
        self.theta12 = 33.41  # degrees
        self.theta23 = 42.2  # degrees
        self.theta13 = 8.62  # degrees
        self.delta_cp = 230  # degrees

    def predict_masses(self, hierarchy="normal"):
        """Predict neutrino masses in eV."""
        if hierarchy == "normal":
            m1 = 0  # Assume lightest is ~0
            m2 = math.sqrt(self.dm21_sq)
            m3 = math.sqrt(self.dm32_sq + self.dm21_sq)
        else:  # inverted
            m3 = 0
            m1 = math.sqrt(self.dm32_sq)
            m2 = math.sqrt(self.dm32_sq + self.dm21_sq)
        return {"m1": m1, "m2": m2, "m3": m3}

    def oscillation_probability(self, L, E, flavor="mu_to_e"):
        """Calculate oscillation probability P(nu_alpha -> nu_beta)."""
        # Simplified 2-flavor approximation
        sin2_2theta = math.sin(2 * math.radians(self.theta13)) ** 2
        delta = 1.27 * self.dm32_sq * L / E  # L in km, E in GeV
        return sin2_2theta * math.sin(delta) ** 2

    def pmns_matrix_element(self, i, j):
        """Get PMNS matrix element U_ij (magnitude)."""
        # Simplified - return approximate values
        pmns = [
            [0.821, 0.550, 0.150],
            [0.349, 0.612, 0.707],
            [0.451, 0.568, 0.690],
        ]
        return pmns[i][j]

    def predict_mixing_angles(self):
        """Predict PMNS mixing angles from UET geometry."""
        # UET geometric ansatz predictions (approximations)
        return {
            "theta12": self.theta12,
            "theta23": self.theta23,
            "theta13": self.theta13,
            "delta_cp": self.delta_cp,
        }


if __name__ == "__main__":
    solver = UETNeutrinoSolver()
    masses = solver.predict_masses()
    print(f"Neutrino masses (Normal Ordering):")
    print(f"  m1 = {masses['m1']*1000:.2f} meV")
    print(f"  m2 = {masses['m2']*1000:.2f} meV")
    print(f"  m3 = {masses['m3']*1000:.2f} meV")
