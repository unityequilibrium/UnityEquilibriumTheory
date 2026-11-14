"""
Dark Energy & Hubble Tension Data
=================================
Data source for UET Cosmology validation.
"""

# ==============================================================================
# HUBBLE TENSION DATA
# ==============================================================================

HUBBLE_MEASUREMENTS = {
    "Planck_2018": {
        "H0": 67.4,
        "error": 0.5,
        "source": "Planck 2018 (CMB)",
        "redshift": 1100,
    },
    "SH0ES_2022": {
        "H0": 73.04,
        "error": 1.04,
        "source": "SH0ES (Riess et al. 2022)",
        "redshift": 0.05,
    },
}

HUBBLE_TENSION = {
    "difference": 73.04 - 67.4,
    "tension_sigma": (73.04 - 67.4) / ((0.5**2 + 1.04**2) ** 0.5),  # approx 4.9
}

# ==============================================================================
# PANTHEON+ SUPERNOVAE
# ==============================================================================

PANTHEON_PLUS = {
    "n_sne": 1701,
    "n_sne_unique": 1550,
    "redshift_range": (0.001, 2.26),
    "source": "Brout et al. 2022",
    "doi": "10.3847/1538-4357/ac8e04",
    "Omega_M": {
        "value": 0.334,
        "error": 0.018,
    },
    "w": {
        "value": -1.03,  # Approx
        "error": 0.04,  # Approx
    },
    "H0_combined": {
        "value": 73.04,
        "error": 1.04,
    },
}

# ==============================================================================
# DARK ENERGY PARAMETERS
# ==============================================================================

DARK_ENERGY = {
    "current_constraints": {
        "w": -1.03,
        "w_error": 0.03,
        "source": "Pantheon+ & Planck",
    },
    "the_problem": {
        "discrepancy": "10^122",
        "rho_vac_theory": 1e74,  # GeV^4
        "rho_vac_obs": 1e-47,  # GeV^4
    },
}

COSMOLOGY_PARAMS = {
    "Omega_Lambda": 0.685,
    "Omega_M": 0.315,
}

# ==============================================================================
# UET LOGIC
# ==============================================================================


def uet_hubble_prediction(z):
    """Placeholder for H(z) prediction."""
    pass


def uet_dark_energy_interpretation():
    return {
        "hypothesis": "Vacuum pressure from C-I field gradient",
        "prediction": "w varies effectively with info density",
        "status": "Qualitative only",
    }


def uet_hubble_tension_hypothesis():
    return {
        "hypothesis_1": "Scale-dependent H0",
        "hypothesis_2": "Information Horizon",
        "hypothesis_3": "Running Constants",
    }
