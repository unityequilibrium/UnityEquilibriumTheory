"""
Weak Nuclear Force Data - PDG/NuFIT 6.0 (2024)
===============================================
Real experimental data for validating UET weak force predictions.

Sources:
- NuFIT 6.0 (September 2024) - Global neutrino oscillation analysis
- Particle Data Group (PDG) 2024
- Fermi coupling measurements
"""

# NuFIT 6.0 (September 2024) - Neutrino Oscillation Parameters
# Normal Ordering (NO) best fit values

# Mixing angles (sin² theta)
NEUTRINO_MIXING = {
    "sin2_theta12": {"value": 0.303, "error_1sigma": 0.012, "precision_3sigma_pct": 13},
    "sin2_theta13": {"value": 0.02225, "error_1sigma": 0.00075, "precision_3sigma_pct": 8},
    "sin2_theta23": {
        "value": 0.451,
        "error_1sigma": 0.019,
        "precision_3sigma_pct": 10,
    },  # Lower octant
}

# Mass-squared differences (eV²)
MASS_SQUARED_DIFF = {
    "delta_m21_sq": {"value": 7.41e-5, "error_1sigma": 0.21e-5, "unit": "eV^2"},
    "delta_m31_sq_NO": {"value": 2.507e-3, "error_1sigma": 0.026e-3, "unit": "eV^2"},  # Normal
    "delta_m32_sq_IO": {"value": -2.486e-3, "error_1sigma": 0.025e-3, "unit": "eV^2"},  # Inverted
}

# CP-violating phase (degrees)
CP_PHASE = {
    "delta_CP_NO": {"value": 194, "error_1sigma": 25, "unit": "degrees"},
    "delta_CP_IO": {"value": 284, "error_1sigma": 27, "unit": "degrees"},
}

# Fermi coupling constant
GF_FERMI = {"value": 1.1663787e-5, "error": 0.0000006e-5, "source": "PDG 2024"}  # GeV^-2

# W and Z boson masses
WEAK_BOSON_MASSES = {
    "W_pm": {"mass_GeV": 80.3692, "error": 0.0133},
    "Z_0": {"mass_GeV": 91.1876, "error": 0.0021},
}

# Weinberg angle (weak mixing angle)
WEINBERG_ANGLE = {
    "sin2_theta_W": {"value": 0.23121, "error": 0.00004},
    "source": "PDG 2024 (on-shell scheme)",
}

# Beta decay rates for validation
BETA_DECAY_DATA = {
    "neutron": {"lifetime_s": 878.4, "error": 0.5, "Q_value_keV": 782.347, "source": "PDG 2024"},
    "tritium": {
        "half_life_years": 12.32,
        "error": 0.02,
        "Q_value_keV": 18.591,
    },
    "C14": {
        "half_life_years": 5700,
        "error": 30,
        "Q_value_keV": 156.476,
    },
}

# CKM matrix elements (for weak quark transitions)
CKM_MATRIX = {
    "Vud": {"value": 0.97373, "error": 0.00031},
    "Vus": {"value": 0.2243, "error": 0.0008},
    "Vub": {"value": 0.00382, "error": 0.00020},
    "Vcd": {"value": 0.221, "error": 0.004},
    "Vcs": {"value": 0.975, "error": 0.006},
    "Vcb": {"value": 0.0408, "error": 0.0014},
    "Vtd": {"value": 0.0080, "error": 0.0003},
    "Vts": {"value": 0.0388, "error": 0.0011},
    "Vtb": {"value": 1.013, "error": 0.030},
}


def oscillation_probability(L_km: float, E_GeV: float, dm2_eV2: float, sin2_2theta: float) -> float:
    """
    Two-flavor neutrino oscillation probability.

    P(να → νβ) = sin²(2θ) × sin²(1.27 × Δm² × L / E)

    Where:
    - L is baseline in km
    - E is neutrino energy in GeV
    - Δm² is mass-squared difference in eV²
    """
    import numpy as np

    phase = 1.27 * dm2_eV2 * L_km / E_GeV
    return sin2_2theta * np.sin(phase) ** 2


if __name__ == "__main__":
    print("=" * 60)
    print("Weak Nuclear Force Data - NuFIT 6.0 / PDG 2024")
    print("=" * 60)

    print("\nNeutrino Mixing Angles:")
    for name, data in NEUTRINO_MIXING.items():
        print(f"  {name}: {data['value']:.5f} +/- {data['error_1sigma']:.5f}")

    print("\nMass-squared Differences:")
    for name, data in MASS_SQUARED_DIFF.items():
        print(f"  {name}: {data['value']:.3e} +/- {data['error_1sigma']:.2e} {data['unit']}")

    print(f"\nFermi Constant: G_F = {GF_FERMI['value']:.7e} GeV^-2")
    print(f"Weinberg Angle: sin²θ_W = {WEINBERG_ANGLE['sin2_theta_W']['value']:.5f}")

    print(f"\nW boson: {WEAK_BOSON_MASSES['W_pm']['mass_GeV']:.4f} GeV")
    print(f"Z boson: {WEAK_BOSON_MASSES['Z_0']['mass_GeV']:.4f} GeV")
