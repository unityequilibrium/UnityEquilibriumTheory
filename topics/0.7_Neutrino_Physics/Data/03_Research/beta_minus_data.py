"""
Beta-Minus Decay Data
======================
Source: PDG 2024, NNDC
Reference: https://www.nndc.bnl.gov/

Decay: n → p + e⁻ + ν̄_e (or in nucleus: A_Z → A_{Z+1} + e⁻ + ν̄_e)

POLICY: NO PARAMETER FIXING - All comparisons are honest
"""

import numpy as np

# ============================================================
# BETA-MINUS DECAY MECHANISM
# ============================================================

BETA_MINUS_MECHANISM = {
    "process": "n → p + e⁻ + ν̄_e",
    "quark_level": "d → u + W⁻ → u + e⁻ + ν̄_e",
    "occurs_in": "Neutron-rich nuclei, free neutron",
    "Z_change": "+1",
    "A_change": 0,  # Mass number unchanged
    "energy_released": True,  # Always exothermic for neutron-rich
}

# ============================================================
# FREE NEUTRON DECAY (Most fundamental!)
# ============================================================

FREE_NEUTRON = {
    "lifetime_s": 878.4,
    "uncertainty_s": 0.5,
    "Q_value_keV": 782.3,  # m_n - m_p - m_e
    "max_electron_energy_keV": 1293.3,  # Q + m_e
    "branching_ratio": 1.0,  # 100% to this channel
    "source": "PDG 2024",
}

# ============================================================
# IMPORTANT β⁻ ISOTOPES
# ============================================================

BETA_MINUS_ISOTOPES = {
    # Tritium - used in fusion, watches, exit signs
    "H3": {
        "parent": "³H (Tritium)",
        "daughter": "³He",
        "half_life_years": 12.32,
        "Q_value_keV": 18.591,
        "max_electron_E_keV": 18.591,
        "use": "Fusion fuel, luminescent signs, neutrino mass (KATRIN)",
        "source": "PDG 2024",
    },
    # Carbon-14 - radiocarbon dating
    "C14": {
        "parent": "¹⁴C",
        "daughter": "¹⁴N",
        "half_life_years": 5700,
        "Q_value_keV": 156.5,
        "max_electron_E_keV": 156.5,
        "use": "Radiocarbon dating",
        "source": "NNDC",
    },
    # Phosphorus-32 - medical, research
    "P32": {
        "parent": "³²P",
        "daughter": "³²S",
        "half_life_days": 14.29,
        "Q_value_keV": 1710.7,
        "max_electron_E_keV": 1710.7,
        "use": "Medical treatment, DNA labeling",
        "source": "NNDC",
    },
    # Strontium-90 - nuclear fallout
    "Sr90": {
        "parent": "⁹⁰Sr",
        "daughter": "⁹⁰Y",
        "half_life_years": 28.79,
        "Q_value_keV": 546.0,
        "max_electron_E_keV": 546.0,
        "use": "RTG power, bone cancer treatment",
        "note": "Fission product, bone-seeker",
        "source": "NNDC",
    },
    # Cesium-137 - nuclear fallout
    "Cs137": {
        "parent": "¹³⁷Cs",
        "daughter": "¹³⁷Ba",
        "half_life_years": 30.17,
        "Q_value_keV": 1175.6,
        "max_electron_E_keV": 514.0,  # To ground state
        "gamma_keV": 661.6,  # Daughter gamma
        "use": "Calibration, industrial radiography",
        "note": "Fission product",
        "source": "NNDC",
    },
    # Iodine-131 - medical, fallout
    "I131": {
        "parent": "¹³¹I",
        "daughter": "¹³¹Xe",
        "half_life_days": 8.02,
        "Q_value_keV": 970.8,
        "max_electron_E_keV": 606.3,
        "use": "Thyroid treatment, imaging",
        "note": "Fission product, thyroid-seeker",
        "source": "NNDC",
    },
    # Cobalt-60 - radiotherapy
    "Co60": {
        "parent": "⁶⁰Co",
        "daughter": "⁶⁰Ni",
        "half_life_years": 5.27,
        "Q_value_keV": 2823.1,
        "max_electron_E_keV": 317.9,
        "gamma_1_keV": 1173.2,
        "gamma_2_keV": 1332.5,
        "use": "Radiotherapy, food sterilization",
        "source": "NNDC",
    },
    # Technetium-99 - nuclear medicine
    "Tc99": {
        "parent": "⁹⁹Tc",
        "daughter": "⁹⁹Ru",
        "half_life_years": 211100,
        "Q_value_keV": 293.5,
        "max_electron_E_keV": 293.5,
        "use": "⁹⁹ᵐTc daughter for SPECT imaging",
        "source": "NNDC",
    },
}

# ============================================================
# KURIE PLOT ANALYSIS (For neutrino mass)
# ============================================================

KURIE_PLOT = {
    "purpose": "Determine neutrino mass from endpoint",
    "equation": "K(E) = √(N(E) / (p E F)) vs E",
    "straight_line_if": "m_ν = 0",
    "deviation_at_endpoint": "Indicates m_ν > 0",
    "best_isotope": "³H (Tritium) - lowest Q value",
    "KATRIN_limit_eV": 0.8,  # Upper limit on m_ν
    "source": "KATRIN 2022",
}

# ============================================================
# FERMI FUNCTION AND PHASE SPACE
# ============================================================


def fermi_function(Z, E_e, m_e=0.511):
    """
    Fermi function F(Z, E) for Coulomb correction.

    Accounts for attraction (β⁻) or repulsion (β⁺)
    between emitted electron/positron and daughter nucleus.
    """
    # Simplified non-relativistic approximation
    alpha = 1 / 137.036
    eta = Z * alpha * m_e / np.sqrt(E_e**2 - m_e**2) if E_e > m_e else 0

    if eta == 0:
        return 1.0

    # F ≈ 2πη / (1 - exp(-2πη)) for β⁻
    F = 2 * np.pi * eta / (1 - np.exp(-2 * np.pi * eta))

    return F


def phase_space_factor(Q_keV, Z_daughter):
    """
    Calculate phase space factor f for beta decay.

    f = ∫₀^Q p_e E_e (Q - E_e)² F(Z, E_e) dE_e

    This determines relative decay rates.
    """
    Q = Q_keV / 1000  # Convert to MeV
    m_e = 0.511  # MeV

    # Numerical integration (simplified)
    n_points = 100
    E_values = np.linspace(m_e + 0.001, Q + m_e - 0.001, n_points)

    f_sum = 0
    for E_e in E_values:
        p_e = np.sqrt(E_e**2 - m_e**2) if E_e > m_e else 0
        T_nu = Q + m_e - E_e  # Neutrino energy
        F = fermi_function(Z_daughter, E_e, m_e)

        integrand = p_e * E_e * T_nu**2 * F
        f_sum += integrand

    f = f_sum * (Q / n_points)  # dE spacing

    return f


# ============================================================
# UET PREDICTIONS (NO FITTING!)
# ============================================================


def uet_beta_minus_interpretation():
    """
    UET interpretation of beta-minus decay.

    In UET framework:
    - d quark has higher "winding number" than u quark
    - β⁻ = unwinding: d → u releases energy
    - Electron carries away negative C-field "twist"
    - Antineutrino carries away I-field information

    Key prediction: Decay rate ~ (mass difference)⁵
    """
    interpretation = {
        "d_quark": "Higher topological winding (heavier)",
        "u_quark": "Lower topological winding (lighter)",
        "decay": "Unwinding from d to u configuration",
        "electron": "Carries negative C-field twist",
        "antineutrino": "Carries I-field information flux",
        "W_boson": "Virtual I-field propagator",
        "rate_scaling": "Γ ∝ Q⁵ (phase space)",
    }

    return interpretation


def uet_lifetime_from_Q(Q_keV, ft_value_s=3600):
    """
    Estimate β⁻ lifetime from Q value using UET.

    Rough scaling: t ∝ 1/Q⁵ (phase space)
    """
    # Reference: neutron with Q = 782 keV, τ = 878 s
    Q_ref = 782.3  # keV
    tau_ref = 878.4  # s

    # Scale by (Q_ref/Q)⁵
    tau_estimate = tau_ref * (Q_ref / Q_keV) ** 5

    return tau_estimate
