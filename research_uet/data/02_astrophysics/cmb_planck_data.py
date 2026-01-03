"""
Cosmic Microwave Background (CMB) Data
========================================
Planck 2018 Observations

The CMB is the oldest light in the universe - a snapshot at z=1100.
It provides the most precise constraints on cosmological parameters.

Source: Planck Collaboration 2018
DOI: 10.1051/0004-6361/201833910

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# PLANCK 2018 COSMOLOGICAL PARAMETERS
# ============================================================

PLANCK_2018 = {
    # Hubble constant
    "H0": {
        "value": 67.4,
        "error": 0.5,
        "unit": "km/s/Mpc",
    },
    # Matter density
    "Omega_m": {
        "value": 0.315,
        "error": 0.007,
    },
    # Dark energy density
    "Omega_Lambda": {
        "value": 0.685,
        "error": 0.007,
    },
    # Baryon density
    "Omega_b_h2": {
        "value": 0.0224,
        "error": 0.0001,
    },
    # Cold dark matter density
    "Omega_c_h2": {
        "value": 0.120,
        "error": 0.001,
    },
    # Curvature
    "Omega_k": {
        "value": 0.001,
        "error": 0.002,
        "note": "Consistent with flat universe!",
    },
    # Spectral index
    "n_s": {
        "value": 0.965,
        "error": 0.004,
        "note": "Slight red tilt (not scale-invariant)",
    },
    # Amplitude of fluctuations
    "A_s": {
        "value": 2.1e-9,
        "error": 0.03e-9,
    },
    # Optical depth to reionization
    "tau": {
        "value": 0.054,
        "error": 0.007,
    },
    # Age of universe
    "age_Gyr": {
        "value": 13.797,
        "error": 0.023,
    },
    # Derived: sigma_8
    "sigma_8": {
        "value": 0.811,
        "error": 0.006,
        "note": "RMS fluctuation in 8 Mpc spheres",
    },
    # Source
    "source": "Planck Collaboration 2018",
    "doi": "10.1051/0004-6361/201833910",
}

# ============================================================
# CMB POWER SPECTRUM
# ============================================================

CMB_SPECTRUM = {
    "first_peak": {
        "l": 220,
        "meaning": "Angular scale = 1°",
        "physics": "Sound horizon at recombination",
        "constrains": "Flat geometry (Ω_k = 0)",
    },
    "second_peak": {
        "l": 537,
        "meaning": "Baryon loading",
        "physics": "Odd vs even peaks ratio",
        "constrains": "Ω_b",
    },
    "third_peak": {
        "l": 813,
        "meaning": "Dark matter",
        "physics": "Gravitational driving",
        "constrains": "Ω_c",
    },
    "damping_tail": {
        "l_range": [1000, 3000],
        "physics": "Silk damping (photon diffusion)",
        "constrains": "n_s, recombination history",
    },
}

# ============================================================
# BAO (BARYON ACOUSTIC OSCILLATIONS)
# ============================================================

BAO_DATA = {
    "sound_horizon": {
        "r_d": 147.09,  # Mpc
        "error": 0.26,
        "source": "Planck 2018",
        "note": "Standard ruler",
    },
    # BAO measurements at different redshifts
    "measurements": {
        "BOSS_z0.38": {
            "D_M/r_d": 10.23,
            "error": 0.17,
            "source": "BOSS DR12",
        },
        "BOSS_z0.51": {
            "D_M/r_d": 13.36,
            "error": 0.21,
        },
        "BOSS_z0.61": {
            "D_M/r_d": 15.72,
            "error": 0.23,
        },
        "eBOSS_Lya_z2.33": {
            "D_M/r_d": 37.6,
            "error": 1.1,
            "source": "eBOSS Lyα",
        },
    },
}

# ============================================================
# COSMIC TENSIONS
# ============================================================

COSMIC_TENSIONS = {
    "H0_tension": {
        "CMB": 67.4,
        "local": 73.04,
        "sigma": 4.9,
        "status": "Major crisis!",
    },
    "S8_tension": {
        "CMB": 0.832,  # Planck + ΛCDM
        "weak_lensing": 0.76,  # DES, KiDS
        "sigma": 2.5,
        "status": "Moderate tension",
        "S8_definition": "σ_8 × (Ω_m/0.3)^0.5",
    },
    "A_lens_anomaly": {
        "expected": 1.0,
        "observed": 1.18,
        "sigma": 2.8,
        "note": "More lensing than expected",
    },
}

# ============================================================
# UET PREDICTIONS
# ============================================================


def uet_cmb_interpretation():
    """
    UET interpretation of CMB physics.

    The CMB should be consistent with UET if:
    - C-I field was established by recombination
    - Acoustic oscillations are C-I mode oscillations
    """
    return {
        "acoustic_peaks": "C-I field compression modes",
        "damping": "C-I field dissipation",
        "polarization": "C-I tensor perturbations",
        "consistency": "UET should match ΛCDM at CMB epoch",
        "predictions": {
            "flat_geometry": "Yes (C-I symmetry)",
            "n_s < 1": "May explain (C-I field inflation?)",
            "r (tensor/scalar)": "Need calculation",
        },
    }


def uet_structure_formation():
    """
    UET interpretation of structure formation.

    Galaxy clusters, LSS should emerge from UET dynamics.
    """
    return {
        "interpretation": "Structures = C-I field density peaks",
        "dark_matter_role": "C-I field replaces particle DM",
        "prediction": "Same power spectrum as ΛCDM on large scales",
        "difference": "May differ on small scales (galaxies)",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("COSMIC MICROWAVE BACKGROUND (Planck 2018)")
    print("=" * 60)

    print(f"\nKey Parameters:")
    for key in ["H0", "Omega_m", "Omega_Lambda", "age_Gyr"]:
        p = PLANCK_2018[key]
        print(f"  {key} = {p['value']} ± {p['error']}")

    print(f"\nCMB Peaks:")
    for peak, data in CMB_SPECTRUM.items():
        if "l" in data:
            print(f"  {peak}: l = {data['l']} ({data['meaning']})")

    print(f"\nCosmic Tensions:")
    for name, t in COSMIC_TENSIONS.items():
        print(f"  {name}: {t['sigma']}σ - {t['status']}")
