"""
Neutrino Mixing (PMNS) Data
============================
Source: PDG 2024, T2K, NOvA, NuFIT 2024
Reference: Phys. Rev. D 110, 030001 (2024)

PMNS Matrix describes neutrino flavor ↔ mass mixing
Similar to CKM for quarks, but MUCH larger angles!

POLICY: NO PARAMETER FIXING - All comparisons are honest
"""

import numpy as np

# ============================================================
# PMNS MATRIX PARAMETERS (PDG 2024 / NuFIT 2024)
# ============================================================

PMNS_MIXING_ANGLES = {
    # θ₁₂ - Solar mixing angle
    "theta12": {
        "value_deg": 33.44,
        "uncertainty_deg": 0.77,
        "sin_squared": 0.304,
        "sin_squared_uncertainty": 0.012,
        "source": "Solar + KamLAND",
        "note": "Well-determined",
    },
    # θ₂₃ - Atmospheric mixing angle
    "theta23": {
        "value_deg": 49.2,
        "uncertainty_deg": 1.0,
        "sin_squared": 0.573,  # Normal ordering
        "sin_squared_uncertainty": 0.020,
        "octant": "Upper (>45°)",
        "source": "T2K + NOvA + SK",
        "note": "Near maximal, octant undetermined",
    },
    # θ₁₃ - Reactor mixing angle (smallest)
    "theta13": {
        "value_deg": 8.57,
        "uncertainty_deg": 0.12,
        "sin_squared": 0.02219,
        "sin_squared_uncertainty": 0.00062,
        "source": "Daya Bay + RENO + Double Chooz",
        "note": "Most precisely measured",
    },
}

# CP Violation Phase
CP_PHASE = {
    "delta_CP_deg": 195,  # Best fit (Normal Ordering)
    "delta_CP_rad": 195 * np.pi / 180,
    "delta_CP_over_pi": 1.08,
    "uncertainty_deg": 40,
    "status": "~2σ from CP conservation (0 or π)",
    "T2K_value": 264,  # δCP ≈ -96° = 264°
    "NOvA_value": 156,  # δCP ≈ 0.87π
    "source": "PDG 2024 / NuFIT 5.3",
}

# ============================================================
# MASS SQUARED DIFFERENCES
# ============================================================

MASS_SPLITTINGS = {
    # Solar mass splitting
    "delta_m21_squared": {
        "value_eV2": 7.42e-5,
        "uncertainty_eV2": 0.21e-5,
        "source": "Solar + KamLAND",
        "determines": "Solar oscillations",
    },
    # Atmospheric mass splitting (|Δm²₃₁| or |Δm²₃₂|)
    "delta_m32_squared_NO": {  # Normal Ordering
        "value_eV2": 2.514e-3,
        "uncertainty_eV2": 0.028e-3,
        "source": "Atmospheric + LBL",
        "determines": "Atmospheric oscillations",
    },
    "delta_m32_squared_IO": {  # Inverted Ordering
        "value_eV2": -2.497e-3,
        "uncertainty_eV2": 0.028e-3,
        "source": "Atmospheric + LBL",
    },
}

# Mass ordering preference (2024)
MASS_ORDERING = {
    "preferred": "Normal (m₁ < m₂ < m₃)",
    "significance": "~2.5σ over Inverted",
    "source": "Global fit 2024",
}

# ============================================================
# PMNS MATRIX (Numerical form, Normal Ordering)
# ============================================================


def calculate_pmns_matrix(theta12_deg, theta23_deg, theta13_deg, delta_deg):
    """
    Calculate PMNS matrix from mixing angles.

    U = R₂₃ × Δ_CP × R₁₃ × Δ_CP† × R₁₂

    where R_ij are rotation matrices.
    """
    # Convert to radians
    t12 = np.radians(theta12_deg)
    t23 = np.radians(theta23_deg)
    t13 = np.radians(theta13_deg)
    d = np.radians(delta_deg)

    # Shortcuts
    c12, s12 = np.cos(t12), np.sin(t12)
    c23, s23 = np.cos(t23), np.sin(t23)
    c13, s13 = np.cos(t13), np.sin(t13)

    # PMNS matrix elements
    U = np.array(
        [
            [c12 * c13, s12 * c13, s13 * np.exp(-1j * d)],
            [
                -s12 * c23 - c12 * s23 * s13 * np.exp(1j * d),
                c12 * c23 - s12 * s23 * s13 * np.exp(1j * d),
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * np.exp(1j * d),
                -c12 * s23 - s12 * c23 * s13 * np.exp(1j * d),
                c23 * c13,
            ],
        ]
    )

    return U


# Standard PMNS matrix (using best-fit values)
PMNS_MATRIX = calculate_pmns_matrix(33.44, 49.2, 8.57, 195)

# Magnitudes only (for easier comparison)
PMNS_MAGNITUDES = np.abs(PMNS_MATRIX)

# ============================================================
# CKM vs PMNS COMPARISON
# ============================================================

CKM_VS_PMNS = {
    "CKM_angles": {"theta12_Cabibbo": 13.0, "theta23_cb": 2.4, "theta13_ub": 0.2},  # degrees
    "PMNS_angles": {"theta12_solar": 33.44, "theta23_atm": 49.2, "theta13_reactor": 8.57},
    "key_difference": "PMNS angles are MUCH larger than CKM",
    "ratio_theta12": 33.44 / 13.0,  # ~2.6
    "ratio_theta23": 49.2 / 2.4,  # ~20
    "ratio_theta13": 8.57 / 0.2,  # ~43
}

# ============================================================
# UET PREDICTIONS (NO FITTING!)
# ============================================================


def uet_pmns_prediction(kappa=0.5, beta=1.0):
    """
    UET prediction for PMNS mixing angles.

    In UET framework:
    - Neutrinos = pure I-field excitations
    - Mixing = I-field mode interference
    - Large angles because neutrinos are nearly massless

    Key insight: PMNS angles scale inversely with mass!
    Quarks (heavy) → small CKM angles
    Neutrinos (light) → large PMNS angles

    UET predicts: θ ~ π/n where n is "winding number"
    """
    # Geometric predictions
    # θ₁₂ ~ π/6 = 30° (hexagonal symmetry?)
    theta12_uet = 30.0

    # θ₂₃ ~ π/4 = 45° (maximal mixing)
    theta23_uet = 45.0

    # θ₁₃ ~ κ × π/16 (small, suppressed by κ)
    theta13_uet = kappa * (180 / 16)  # = 5.6°

    # δ_CP ~ π (maximal CP violation?)
    delta_uet = 180.0

    return {
        "theta12": theta12_uet,
        "theta23": theta23_uet,
        "theta13": theta13_uet,
        "delta_CP": delta_uet,
    }


def uet_mass_ratio_from_mixing():
    """
    UET: Mass ratios related to mixing angles.

    For CKM: sin(θ_C) ~ √(m_d/m_s) (Gatto relation)
    For PMNS: Similar relation might hold?

    sin²(θ₁₂) ~ m₂/m₃ ?
    """
    sin2_12 = 0.304

    # If this is mass ratio...
    # m2/m3 ~ 0.304
    # sqrt(Δm²₂₁) / sqrt(Δm²₃₂) = sqrt(7.4e-5) / sqrt(2.5e-3)
    #                            = 0.0086 / 0.050 = 0.17

    # Not quite 0.304, but same order of magnitude

    ratio_from_masses = np.sqrt(7.42e-5) / np.sqrt(2.514e-3)

    return {
        "sin2_theta12": sin2_12,
        "mass_ratio_sqrt": ratio_from_masses,
        "ratio": sin2_12 / ratio_from_masses,
    }


# ============================================================
# OSCILLATION PROBABILITY FORMULAS
# ============================================================


def P_numu_to_nue(E_GeV, L_km, theta23, theta13, delta_m32_eV2, delta_CP=0):
    """
    Simplified ν_μ → ν_e appearance probability.

    P(ν_μ → ν_e) ≈ sin²(2θ₁₃) × sin²(θ₂₃) × sin²(Δ)

    where Δ = 1.27 × Δm²₃₂ × L / E
    """
    # Phase factor (in natural units)
    Delta = 1.27 * delta_m32_eV2 * L_km / E_GeV

    sin2_2theta13 = np.sin(2 * np.radians(theta13)) ** 2
    sin2_theta23 = np.sin(np.radians(theta23)) ** 2

    P = sin2_2theta13 * sin2_theta23 * np.sin(Delta) ** 2

    return P
