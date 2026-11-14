"""
Quark Mass Data - PDG 2024
===========================
Real experimental data for all 6 quarks.

Source: Particle Data Group 2024
DOI: 10.1093/ptep/ptac097

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# PDG 2024 QUARK MASSES
# MS-bar scheme at μ = 2 GeV for light quarks
# ============================================================

QUARK_MASSES = {
    # First Generation
    "up": {
        "mass_MeV": 2.16,
        "error_up": 0.49,
        "error_down": 0.26,
        "scheme": "MS-bar at 2 GeV",
        "source": "PDG 2024",
    },
    "down": {
        "mass_MeV": 4.67,
        "error_up": 0.48,
        "error_down": 0.17,
        "scheme": "MS-bar at 2 GeV",
        "source": "PDG 2024",
    },
    # Second Generation
    "strange": {
        "mass_MeV": 93.4,
        "error_up": 8.6,
        "error_down": 3.4,
        "scheme": "MS-bar at 2 GeV",
        "source": "PDG 2024",
    },
    "charm": {
        "mass_GeV": 1.27,
        "error": 0.02,
        "scheme": "MS-bar at m_c",
        "source": "PDG 2024",
    },
    # Third Generation
    "bottom": {
        "mass_GeV": 4.18,
        "error_up": 0.03,
        "error_down": 0.02,
        "scheme": "MS-bar at m_b",
        "source": "PDG 2024",
    },
    "top": {
        "mass_GeV": 172.57,
        "error": 0.29,
        "scheme": "Pole mass (direct)",
        "source": "PDG 2024 (LHC average)",
    },
}

# Mass ratios (more fundamental than absolute masses)
QUARK_MASS_RATIOS = {
    "m_u/m_d": 2.16 / 4.67,  # ~0.46
    "m_s/m_d": 93.4 / 4.67,  # ~20.0
    "m_c/m_s": 1270 / 93.4,  # ~13.6
    "m_b/m_c": 4180 / 1270,  # ~3.3
    "m_t/m_b": 172570 / 4180,  # ~41.3
    "m_t/m_u": 172570 / 2.16,  # ~80,000
}

# Quark charges
QUARK_CHARGES = {
    "up": +2 / 3,
    "down": -1 / 3,
    "strange": -1 / 3,
    "charm": +2 / 3,
    "bottom": -1 / 3,
    "top": +2 / 3,
}

# ============================================================
# UET PREDICTIONS (NO FITTING!)
# ============================================================


def uet_quark_mass_prediction(kappa=0.5, beta=1.0):
    """
    UET predicts quark masses from C-I field topology.

    Each generation = different winding level
    Masses scale exponentially with winding number

    m_q ~ m_0 * exp(n * π * κ)

    where n = generation × (charge factor)
    """

    # Base scale (electron mass as reference)
    m_0 = 0.511  # MeV (electron)

    # Winding numbers for each quark (hypothesis)
    # Up-type: u=1, c=2, t=3
    # Down-type: d=1.5, s=2.5, b=3.5 (heavier due to +1/2 winding)

    windings = {
        "up": 1.0,
        "down": 1.5,
        "strange": 2.5,
        "charm": 3.0,
        "bottom": 4.0,
        "top": 5.5,
    }

    predictions = {}
    for quark, n in windings.items():
        # UET formula: m = m_0 * exp(n * π * κ)
        mass = m_0 * np.exp(n * np.pi * kappa)
        predictions[quark] = mass

    return predictions


def uet_generation_mass_ratio():
    """
    UET predicts mass ratios between generations.

    For adjacent generations with same charge:
    m_{n+1} / m_n ~ exp(π * κ)

    With κ = 0.5: ratio ~ exp(π/2) ~ 4.81
    """
    kappa = 0.5

    # Adjacent generation ratio
    basic_ratio = np.exp(np.pi * kappa)  # ~4.81

    return {
        "up_type_ratio": basic_ratio,  # c/u, t/c
        "down_type_ratio": basic_ratio,  # s/d, b/s
        "note": "Adjacent generations should have ~4.81× mass ratio",
    }


# ============================================================
# EXPERIMENTAL CONSTANTS
# ============================================================

# Proton mass (for reference)
PROTON_MASS_MEV = 938.27208816

# Note: Proton mass >> sum of quark masses!
# m_p = 938 MeV, but m_u + m_u + m_d = 9 MeV
# => 99% of proton mass is QCD binding energy!

PROTON_QUARK_CONTENT = {
    "valence": "uud",
    "sum_quark_mass_MeV": 2.16 + 2.16 + 4.67,  # ~9 MeV
    "binding_energy_MeV": 938.27 - 9,  # ~929 MeV
    "binding_fraction": 929 / 938.27,  # ~99%!
}


if __name__ == "__main__":
    print("=" * 60)
    print("QUARK MASSES - PDG 2024")
    print("=" * 60)

    print("\nQuark Masses:")
    print(f"{'Quark':<10} {'Mass':<15} {'Charge':<8}")
    print("-" * 33)
    for name, data in QUARK_MASSES.items():
        if "mass_MeV" in data:
            mass_str = f"{data['mass_MeV']:.2f} MeV"
        else:
            mass_str = f"{data['mass_GeV']:.2f} GeV"
        charge = QUARK_CHARGES[name]
        print(f"{name:<10} {mass_str:<15} {charge:+.2f}")

    print("\nMass Range:")
    print(f"  m_t/m_u = {QUARK_MASS_RATIOS['m_t/m_u']:.0f}")
    print(f"  This is 8×10⁴ - the hierarchy problem!")

    print("\nProton Binding:")
    print(f"  Quark masses: {PROTON_QUARK_CONTENT['sum_quark_mass_MeV']:.1f} MeV")
    print(f"  Binding energy: {PROTON_QUARK_CONTENT['binding_energy_MeV']:.1f} MeV")
    print(f"  QCD fraction: {PROTON_QUARK_CONTENT['binding_fraction']*100:.1f}%")
