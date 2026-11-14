"""
Competitor: NFW Halo Model (Standard Cold Dark Matter)
======================================================
Provides the standard Navarro-Frenk-White (NFW) velocity profile calculation.
Used as a baseline for comparing UET's "Information Halo" effectiveness.

Formula:
    V_NFW^2 = V_200^2 * (ln(1+cx) - cx/(1+cx)) / (x * (ln(1+c) - c/(1+c)))
    where x = r / R_200

Note:
    NFW requires two free parameters per galaxy (M_200, c) to be fitted.
    UET derives these from Baryonic mass (Zero Free Parameters).
"""

import numpy as np


class NFWModel:
    def __init__(self, M_200, c, R_200):
        self.M_200 = M_200
        self.c = c
        self.R_200 = R_200
        self.G = 4.302e-6  # kpc (km/s)^2 / M_sun

    def velocity_at(self, r):
        """Calculate NFW halo velocity at radius r."""
        if r <= 0:
            return 0.0

        x = r / self.R_200

        # NFW Function f(x)
        def f(u):
            return np.log(1 + u) - u / (1 + u)

        # Enclosed Mass Profile
        M_enc = self.M_200 * f(self.c * x) / f(self.c)

        return np.sqrt(self.G * M_enc / r)


if __name__ == "__main__":
    print("NFW Model Module")
    print("Use this class to fit Dark Matter parameters for comparison.")
