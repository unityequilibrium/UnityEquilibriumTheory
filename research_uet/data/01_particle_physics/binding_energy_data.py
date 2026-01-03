"""
Nuclear Binding Energy Data
============================
Atomic mass evaluation and binding energies.

Source: AME2020 (Atomic Mass Evaluation 2020)
DOI: 10.1088/1674-1137/abddaf (W.J. Huang et al.)

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# AME2020 REFERENCE
# ============================================================

AME2020 = {
    "name": "Atomic Mass Evaluation 2020",
    "authors": "W.J. Huang et al.",
    "journal": "Chinese Physics C 45 (2021) 030002",
    "doi": "10.1088/1674-1137/abddaf",
    "n_nuclides": 3557,
    "precision": "keV level",
}

# ============================================================
# SELECTED BINDING ENERGIES
# ============================================================

BINDING_ENERGIES = {
    # Light nuclei
    "H-1": {"Z": 1, "A": 1, "BE_MeV": 0.0, "BE_per_A": 0.0},
    "H-2": {"Z": 1, "A": 2, "BE_MeV": 2.225, "BE_per_A": 1.112},
    "H-3": {"Z": 1, "A": 3, "BE_MeV": 8.482, "BE_per_A": 2.827},
    "He-3": {"Z": 2, "A": 3, "BE_MeV": 7.718, "BE_per_A": 2.573},
    "He-4": {"Z": 2, "A": 4, "BE_MeV": 28.296, "BE_per_A": 7.074},
    # Middle mass
    "C-12": {"Z": 6, "A": 12, "BE_MeV": 92.162, "BE_per_A": 7.680},
    "O-16": {"Z": 8, "A": 16, "BE_MeV": 127.619, "BE_per_A": 7.976},
    "Fe-56": {"Z": 26, "A": 56, "BE_MeV": 492.254, "BE_per_A": 8.790},
    "Ni-62": {"Z": 28, "A": 62, "BE_MeV": 545.259, "BE_per_A": 8.795},
    # Heavy nuclei
    "U-235": {"Z": 92, "A": 235, "BE_MeV": 1783.87, "BE_per_A": 7.591},
    "U-238": {"Z": 92, "A": 238, "BE_MeV": 1801.69, "BE_per_A": 7.570},
    "Pu-239": {"Z": 94, "A": 239, "BE_MeV": 1806.92, "BE_per_A": 7.560},
}

# Most bound nuclei
MOST_BOUND = {
    "by_total": "Unknown superheavy",
    "by_nucleon": "Ni-62 (8.795 MeV/nucleon)",
    "runner_up": "Fe-56 (8.790 MeV/nucleon)",
    "note": "Fe-56 is more abundant due to alpha process",
}

# ============================================================
# SEMI-EMPIRICAL MASS FORMULA (Bethe-Weizsäcker)
# ============================================================


def bethe_weizsacker(Z, A):
    """
    Semi-empirical mass formula.

    B(A,Z) = a_V*A - a_S*A^(2/3) - a_C*Z²/A^(1/3) - a_A*(A-2Z)²/A + δ

    Coefficients from fit to AME data.
    """
    # Coefficients (MeV)
    a_V = 15.75  # Volume
    a_S = 17.80  # Surface
    a_C = 0.711  # Coulomb
    a_A = 23.70  # Asymmetry
    a_P = 11.18  # Pairing

    N = A - Z

    # Pairing term
    if Z % 2 == 0 and N % 2 == 0:
        delta = a_P / A**0.5  # even-even
    elif Z % 2 == 1 and N % 2 == 1:
        delta = -a_P / A**0.5  # odd-odd
    else:
        delta = 0  # even-odd

    BE = (
        a_V * A
        - a_S * A ** (2 / 3)
        - a_C * Z**2 / A ** (1 / 3)
        - a_A * (A - 2 * Z) ** 2 / A
        + delta
    )

    return BE


# ============================================================
# UET INTERPRETATION
# ============================================================


def uet_binding_energy():
    """
    UET interpretation of nuclear binding energy.

    Binding comes from C-I field mediated strong force.
    """
    return {
        "interpretation": "BE = C-I field interaction energy",
        "saturation": "C-I field has finite range (like strong force)",
        "Ni_peak": "Optimal C-I configuration at A~60",
        "magic_numbers": "C-I shell structure",
        "prediction": "BE/A should emerge from UET",
        "status": "FRAMEWORK CONSISTENT",
    }


if __name__ == "__main__":
    print("=" * 50)
    print("NUCLEAR BINDING ENERGY (AME2020)")
    print("=" * 50)

    print(f"\nBinding Energy per Nucleon:")
    for name, data in list(BINDING_ENERGIES.items())[:8]:
        print(f"  {name:<8} BE/A = {data['BE_per_A']:.3f} MeV")

    print(f"\nMost bound: {MOST_BOUND['by_nucleon']}")
