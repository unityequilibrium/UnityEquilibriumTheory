"""
Superfluid and Quantum Condensate Data
======================================
Experimental data for superfluid helium and Bose-Einstein condensates.

Sources:
- NIST, Various experiments
"""

# ============================================
# SUPERFLUID HELIUM-4
# ============================================

HELIUM_4_SUPERFLUID = {
    "name": "He-4",
    "lambda_point_K": 2.1768,  # Critical temperature
    "lambda_point_error_K": 0.0001,
    "pressure_atm": 1.0,  # At saturated vapor pressure
    "density_kg_m3": 145,  # Below lambda point
    "viscosity": 0,  # Below lambda point
    "source": "NIST, Lambda point precision measurement",
    "notes": "Zero viscosity below Tλ, quantum fluid",
}

# Specific heat at lambda point (divergent)
HELIUM_4_SPECIFIC_HEAT = {
    "exponent_alpha": -0.0127,  # Critical exponent
    "error": 0.0003,
    "source": "Zero-gravity experiment",
    "notes": "Lambda-shaped curve, precision 2 nK",
}

# ============================================
# HELIUM-3 SUPERFLUID
# ============================================

HELIUM_3_SUPERFLUID = {
    "name": "He-3",
    "critical_temp_A_mK": 2.491,  # A phase
    "critical_temp_B_mK": 1.0,  # B phase
    "source": "Osheroff, Richardson, Lee 1972",
    "notes": "Fermionic superfluid, Cooper pairs",
}

# ============================================
# BOSE-EINSTEIN CONDENSATE
# ============================================

BEC_DATA = [
    # (atom, Tc_nK, N_atoms, year, source)
    ("Rb-87", 170, 2000, 1995, "Cornell, Wieman - JILA"),
    ("Na-23", 2000, 5e5, 1995, "Ketterle - MIT"),
    ("Li-7", 300, 1e4, 1995, "Hulet - Rice"),
    ("H-1", 50, 1e9, 1998, "Kleppner - MIT"),
    ("He-4", 0.03, 1e6, 2003, "ENS Paris"),  # Very low for bosonic He
]

# ============================================
# CRITICAL TEMPERATURES
# ============================================

CRITICAL_TEMPERATURES = {
    "He-4_superfluid": 2.1768,  # K
    "He-3_superfluid_A": 0.002491,  # K (2.491 mK)
    "He-3_superfluid_B": 0.001,  # K
    "Pb_superconductor": 7.19,  # K
    "Nb_superconductor": 9.26,  # K
    "YBCO_superconductor": 92,  # K (high-Tc)
    "MgB2_superconductor": 39,  # K
}

# ============================================
# PHASE TRANSITION RELATIONS
# ============================================


def superfluid_fraction(T_K: float, Tc_K: float = 2.1768) -> float:
    """
    Superfluid fraction below critical temperature.

    ρ_s/ρ = 1 - (T/Tc)^α

    For He-4, α ≈ 5.6 near lambda point
    """
    if T_K >= Tc_K:
        return 0.0

    alpha = 5.6
    return 1 - (T_K / Tc_K) ** alpha


def bec_critical_temp_K(n_density_m3: float, m_kg: float) -> float:
    """
    BEC critical temperature:

    Tc = (2π hbar^2 / (m k_B)) * (n / zeta(3/2))^(2/3)

    zeta(3/2) ≈ 2.612
    """
    import numpy as np
    import sys, os

    # Add docs root path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    from docs.theory.utility.universal_constants import hbar, kB

    zeta_3_2 = 2.612

    Tc = (2 * np.pi * hbar**2 / (m_kg * kB)) * (n_density_m3 / zeta_3_2) ** (2 / 3)
    return Tc


if __name__ == "__main__":
    print("=" * 60)
    print("SUPERFLUID DATA SUMMARY")
    print("=" * 60)

    print(f"\nHe-4 Lambda Point: {HELIUM_4_SUPERFLUID['lambda_point_K']} K")
    print(f"He-3 A Phase: {HELIUM_3_SUPERFLUID['critical_temp_A_mK']} mK")

    print("\nBEC Critical Temperatures:")
    for atom, Tc, N, year, _ in BEC_DATA[:3]:
        print(f"  {atom}: {Tc} nK ({N} atoms, {year})")

    print("\nSuperconductor Tc:")
    for name, Tc in list(CRITICAL_TEMPERATURES.items())[3:6]:
        print(f"  {name}: {Tc} K")
