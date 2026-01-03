"""
Dark Energy and Cosmological Data
==================================
Pantheon+ Type Ia Supernovae and Hubble Tension

This tests UET's ability to explain:
1. Accelerating universe expansion
2. Hubble tension (H₀ = 67 vs 73 km/s/Mpc)
3. Dark energy equation of state w

Sources:
- Pantheon+ (2022): 1701 SNe Ia, DOI: 10.3847/1538-4357/ac8e04
- Planck 2018: CMB, DOI: 10.1051/0004-6361/201833910
- SH0ES (2022): Local H₀, DOI: 10.3847/2041-8213/ac5c5b

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# HUBBLE TENSION
# ============================================================

HUBBLE_MEASUREMENTS = {
    # CMB (Early Universe) measurements
    "Planck_2018": {
        "H0": 67.4,
        "error": 0.5,
        "method": "CMB + ΛCDM",
        "source": "Planck Collaboration 2018",
        "doi": "10.1051/0004-6361/201833910",
        "redshift": "z = 1100",
    },
    "ACT_2020": {
        "H0": 67.9,
        "error": 1.5,
        "method": "CMB (ground)",
        "source": "Atacama Cosmology Telescope",
    },
    # Local (Late Universe) measurements
    "SH0ES_2022": {
        "H0": 73.04,
        "error": 1.04,
        "method": "Cepheid + SNe Ia",
        "source": "Riess et al. 2022",
        "doi": "10.3847/2041-8213/ac5c5b",
        "redshift": "z < 0.1",
    },
    "CCHP_2019": {
        "H0": 69.8,
        "error": 1.9,
        "method": "TRGB + SNe Ia",
        "source": "Chicago-Carnegie Hubble Program",
    },
    "H0LiCOW_2020": {
        "H0": 73.3,
        "error": 1.8,
        "method": "Strong lensing time delays",
        "source": "H0LiCOW Collaboration",
    },
}

# The Tension
HUBBLE_TENSION = {
    "early_universe": 67.4,  # Planck
    "late_universe": 73.04,  # SH0ES
    "difference": 73.04 - 67.4,  # 5.64 km/s/Mpc
    "combined_error": np.sqrt(0.5**2 + 1.04**2),  # ~1.15
    "tension_sigma": (73.04 - 67.4) / np.sqrt(0.5**2 + 1.04**2),  # ~4.9σ
    "status": "4-5σ tension - MAJOR PROBLEM!",
}

# ============================================================
# PANTHEON+ TYPE IA SUPERNOVAE
# ============================================================

PANTHEON_PLUS = {
    "name": "Pantheon+",
    "n_sne": 1701,
    "n_sne_unique": 1550,
    "redshift_range": [0.001, 2.26],
    "source": "Scolnic et al. 2022",
    "doi": "10.3847/1538-4357/ac8e04",
    # Cosmological results
    "Omega_M": {
        "value": 0.334,
        "error": 0.018,
        "note": "Flat ΛCDM",
    },
    "w": {
        "value": -1.03,
        "error": 0.04,
        "note": "wCDM (consistent with Λ)",
    },
    # Combined with SH0ES
    "H0_combined": {
        "value": 73.04,
        "error": 1.04,
    },
}

# ============================================================
# COSMOLOGICAL PARAMETERS
# ============================================================

COSMOLOGY_PARAMS = {
    # Planck 2018 ΛCDM
    "planck_2018": {
        "H0": 67.4,
        "Omega_M": 0.315,
        "Omega_Lambda": 0.685,
        "Omega_b": 0.0493,
        "Omega_k": 0.0,  # Flat
        "sigma_8": 0.811,
        "n_s": 0.965,
        "w": -1.0,  # Fixed (cosmological constant)
    },
    # Current observational constraints
    "current": {
        "age_Gyr": 13.797,
        "age_error": 0.023,
        "z_eq": 3387,  # Matter-radiation equality
        "z_rec": 1089,  # Recombination
    },
}

# ============================================================
# DARK ENERGY EQUATION OF STATE
# ============================================================

DARK_ENERGY = {
    "cosmological_constant": {
        "w": -1.0,
        "w_a": 0.0,
        "name": "ΛCDM",
        "status": "Consistent with data",
    },
    "current_constraints": {
        "w": -1.03,
        "w_error": 0.04,
        "w_a": 0.0,  # Time evolution
        "w_a_error": 0.2,
        "source": "Pantheon+ + Planck + BAO",
    },
    "the_problem": {
        "observed_Lambda": 2.89e-122,  # In Planck units
        "QFT_prediction": 1.0,  # In Planck units
        "discrepancy": "10^122 - WORST PREDICTION IN PHYSICS!",
        "note": "This is the cosmological constant problem",
    },
}

# ============================================================
# UET PREDICTION
# ============================================================


def uet_hubble_prediction(kappa=0.5, beta=1.0):
    """
    UET prediction for Hubble constant.

    In UET, H₀ emerges from C-I field balance.
    The Hubble tension might be explained by:
    - Different C-I configurations at different epochs
    - Scale-dependent κ
    """
    # Current crude estimate
    # H₀ ~ c/R_H where R_H ~ 1/(κ × Λ_cosmo)

    # UET doesn't have a specific H₀ prediction yet
    # This is a MAJOR GAP to fill

    return {
        "H0_uet": "NOT YET DERIVED",
        "status": "Gap in UET - needs theoretical work",
        "approach": [
            "1. Derive Λ from C-I field vacuum energy",
            "2. Connect κ to cosmological scales",
            "3. Explain early vs late difference",
        ],
    }


def uet_dark_energy_interpretation():
    """
    UET interpretation of dark energy.

    Λ could be the residual C-I field energy:
    ρ_Λ = κ × (some C-I vacuum structure)
    """
    return {
        "hypothesis": "Dark energy = C-I field vacuum energy",
        "prediction": "w should exactly equal -1 (cosmological constant)",
        "test": "If w ≠ -1, UET needs modification",
        "current_data": "w = -1.03 ± 0.04 (consistent with -1)",
        "status": "CONSISTENT but not predictive yet",
    }


def uet_hubble_tension_hypothesis():
    """
    Can UET explain the Hubble tension?

    Possible mechanisms:
    1. Scale-dependent κ (κ(z))
    2. Early vs late C-I field configurations
    3. Modified distance-redshift relation
    """
    return {
        "hypothesis_1": "κ evolves with cosmic time",
        "hypothesis_2": "C-I field wasn't in equilibrium at z=1100",
        "hypothesis_3": "Modified growth of structure",
        "status": "SPECULATIVE - needs calculation",
        "if_works": "Would solve 4.9σ tension!",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("DARK ENERGY & HUBBLE TENSION")
    print("=" * 60)

    print(f"\nHubble Tension:")
    print(f"  Planck (CMB): H₀ = {HUBBLE_TENSION['early_universe']} km/s/Mpc")
    print(f"  SH0ES (Local): H₀ = {HUBBLE_TENSION['late_universe']} km/s/Mpc")
    print(f"  Tension: {HUBBLE_TENSION['tension_sigma']:.1f}σ !!!!")

    print(f"\nDark Energy:")
    print(
        f"  w = {DARK_ENERGY['current_constraints']['w']} ± {DARK_ENERGY['current_constraints']['w_error']}"
    )
    print(f"  Status: Consistent with Λ (w = -1)")

    print(f"\nCosmological Constant Problem:")
    print(f"  {DARK_ENERGY['the_problem']['discrepancy']}")
