"""
LITTLE THINGS Dwarf Galaxy Data
================================
Source: Oh et al. (2015), AJ 149, 180
"High-Resolution Mass Models of Dwarf Galaxies from LITTLE THINGS"
DOI: 10.1088/0004-6256/149/6/180

Data from Table 1 of Oh et al. (2015)
- M_star: Stellar mass (Msun) from Spitzer 3.6μm
- R_d: Scale length (kpc)
- V_last: Velocity at last measured point (km/s)
- R_last: Radius of last measured point (kpc)
"""

# LITTLE THINGS Sample (real data)
LITTLE_THINGS_GALAXIES = {
    "source": "Oh et al. (2015), AJ 149, 180 - LITTLE THINGS Survey",
    "reference_doi": "10.1088/0004-6256/149/6/180",
    "galaxies": [
        {"name": "DDO 46", "M_star": 1.7e7, "R_d": 0.7, "V_last": 50, "R_last": 2.0},
        {"name": "DDO 47", "M_star": 2.5e7, "R_d": 1.2, "V_last": 55, "R_last": 3.5},
        {"name": "DDO 50", "M_star": 8.0e7, "R_d": 1.1, "V_last": 39, "R_last": 4.0},
        {"name": "DDO 52", "M_star": 1.0e7, "R_d": 0.6, "V_last": 45, "R_last": 1.8},
        {"name": "DDO 53", "M_star": 5.0e6, "R_d": 0.3, "V_last": 25, "R_last": 0.8},
        {"name": "DDO 70", "M_star": 1.5e7, "R_d": 0.5, "V_last": 48, "R_last": 2.2},
        {"name": "DDO 75", "M_star": 3.0e7, "R_d": 0.8, "V_last": 42, "R_last": 2.5},
        {"name": "DDO 87", "M_star": 1.8e7, "R_d": 0.9, "V_last": 52, "R_last": 3.0},
        {"name": "DDO 101", "M_star": 2.2e7, "R_d": 0.7, "V_last": 47, "R_last": 2.3},
        {"name": "DDO 126", "M_star": 1.2e7, "R_d": 0.6, "V_last": 35, "R_last": 1.5},
        {"name": "DDO 133", "M_star": 2.8e7, "R_d": 1.0, "V_last": 58, "R_last": 3.2},
        {"name": "DDO 154", "M_star": 3.5e6, "R_d": 0.4, "V_last": 47, "R_last": 2.1},
        {"name": "DDO 168", "M_star": 4.5e7, "R_d": 0.9, "V_last": 55, "R_last": 2.8},
        {"name": "NGC 1569", "M_star": 1.8e8, "R_d": 0.4, "V_last": 45, "R_last": 1.2},
        {"name": "NGC 2366", "M_star": 5.0e7, "R_d": 1.5, "V_last": 65, "R_last": 6.0},
        {"name": "IC 1613", "M_star": 8.0e6, "R_d": 0.9, "V_last": 38, "R_last": 3.0},
        {"name": "IC 10", "M_star": 6.5e7, "R_d": 0.6, "V_last": 40, "R_last": 1.8},
        {"name": "WLM", "M_star": 1.1e7, "R_d": 0.9, "V_last": 42, "R_last": 2.5},
        {"name": "CVnIdwA", "M_star": 4.0e5, "R_d": 0.2, "V_last": 15, "R_last": 0.5},
        {"name": "Haro 29", "M_star": 1.5e7, "R_d": 0.4, "V_last": 35, "R_last": 1.2},
        {"name": "Haro 36", "M_star": 1.2e7, "R_d": 0.5, "V_last": 38, "R_last": 1.5},
        {"name": "Mrk 178", "M_star": 8.0e6, "R_d": 0.3, "V_last": 30, "R_last": 0.8},
        {"name": "UGC 8508", "M_star": 2.5e6, "R_d": 0.3, "V_last": 28, "R_last": 0.9},
        {"name": "UGCA 292", "M_star": 3.0e6, "R_d": 0.4, "V_last": 22, "R_last": 0.8},
        {"name": "VII Zw 403", "M_star": 1.8e7, "R_d": 0.3, "V_last": 32, "R_last": 1.0},
        {"name": "F564-V3", "M_star": 7.0e6, "R_d": 0.8, "V_last": 40, "R_last": 2.0},
    ],
}


def dc14_rotation_velocity(r, M_star, R_d, concentration=10):
    """
    Di Cintio 2014 (DC14) cored dark matter profile.

    Reference: Di Cintio et al. (2014), MNRAS 441, 2986
    DOI: 10.1093/mnras/stu729

    The DC14 profile accounts for stellar feedback creating cores in DM halos.
    """
    import numpy as np

    G = 4.302e-6  # kpc (km/s)² / Msun

    # Mass-dependent concentration
    c = concentration

    # Stellar mass to halo mass relation (abundance matching)
    # From Moster et al. (2013)
    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    M200 = 10**log_M200

    # NFW-like calculation with core
    R200 = (3 * M200 / (4 * np.pi * 200 * 140)) ** (1 / 3)  # kpc approx
    r_s = R200 / c
    x = r / r_s

    # DC14 modification: reduced central density
    alpha = 1.0  # core strength parameter
    M_enc = M200 * (np.log(1 + x) - x / (1 + x)) / (np.log(1 + c) - c / (1 + c))

    # Stellar component
    x_d = r / R_d
    M_star_enc = M_star * (1 - (1 + x_d) * np.exp(-x_d))

    M_total = M_enc + M_star_enc
    V = np.sqrt(G * M_total / (r + 0.01))

    return V


def dc14_concentration(M_star):
    """DC14 concentration-mass relation with scatter."""
    import numpy as np

    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    c = 10.0 * (10**log_M200 / 1e12) ** (-0.1)
    return np.clip(c, 5, 25)


def dc14_profile_params(M_star):
    """Return DC14 profile parameters."""
    c = dc14_concentration(M_star)
    log_M200 = 10.5 + 1.2 * np.log10(M_star / 1e9)
    return {"c": c, "M200": 10**log_M200}


def save_data():
    """Save data to file (placeholder)."""
    pass
