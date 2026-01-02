"""
Di Cintio 2014 (DC14) Profile Module
=====================================
Reference: Di Cintio et al. (2014), MNRAS 441, 2986
DOI: 10.1093/mnras/stu729

Cored dark matter profile for dwarf galaxies.
"""

import numpy as np


def dc14_rotation_velocity(r, M_star, R_d, concentration=10):
    """
    DC14 cored dark matter profile velocity.

    Parameters:
    -----------
    r : float
        Radius in kpc
    M_star : float
        Stellar mass in Msun
    R_d : float
        Disk scale length in kpc
    concentration : float
        Halo concentration parameter

    Returns:
    --------
    V : float
        Circular velocity in km/s
    """
    G = 4.302e-6  # kpc (km/s)² / Msun

    c = concentration

    # Abundance matching (Moster 2013)
    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    M200 = 10**log_M200

    # Virial radius
    R200 = (3 * M200 / (4 * np.pi * 200 * 140)) ** (1 / 3)
    r_s = R200 / c
    x = r / r_s

    # NFW enclosed mass
    M_enc = M200 * (np.log(1 + x) - x / (1 + x)) / (np.log(1 + c) - c / (1 + c))

    # Stellar component
    x_d = r / R_d
    M_star_enc = M_star * (1 - (1 + x_d) * np.exp(-x_d))

    M_total = M_enc + M_star_enc
    V = np.sqrt(G * M_total / (r + 0.01))

    return V


def dc14_concentration(M_star):
    """DC14 concentration-mass relation."""
    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    c = 10.0 * (10**log_M200 / 1e12) ** (-0.1)
    return np.clip(c, 5, 25)


def dc14_profile_params(M_star):
    """Return DC14 profile parameters."""
    c = dc14_concentration(M_star)
    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    return {"c": c, "M200": 10**log_M200}
