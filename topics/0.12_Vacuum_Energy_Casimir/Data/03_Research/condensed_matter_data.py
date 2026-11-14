"""
Condensed Matter Physics Data
==============================
Superconductivity, BEC, Quantum Hall Effect

These quantum phenomena at macroscopic scales are fundamental
tests of our understanding of collective quantum behavior.

Sources:
- BCS Theory: Nobel Prize 1972
- BEC: Nobel Prize 2001
- Quantum Hall: Nobel Prize 1985, 1998

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# SUPERCONDUCTIVITY
# ============================================================

SUPERCONDUCTORS = {
    # BCS Type I & II
    "Hg": {
        "Tc_K": 4.15,
        "type": "Type I",
        "discovery": 1911,
        "note": "First superconductor discovered",
    },
    "Pb": {
        "Tc_K": 7.19,
        "type": "Type I",
    },
    "Nb": {
        "Tc_K": 9.26,
        "type": "Type II",
        "note": "Highest Tc elemental",
    },
    "Nb3Sn": {
        "Tc_K": 18.3,
        "type": "Type II (alloy)",
        "use": "MRI magnets, accelerators",
    },
    "NbTi": {
        "Tc_K": 10,
        "type": "Type II",
        "use": "Most used superconductor",
    },
    # High-Tc (Cuprates)
    "YBCO": {
        "formula": "YBa₂Cu₃O₇",
        "Tc_K": 92,
        "type": "High-Tc (Type II)",
        "discovery": 1987,
        "note": "First above liquid nitrogen!",
    },
    "BSCCO": {
        "formula": "Bi₂Sr₂Ca₂Cu₃O₁₀",
        "Tc_K": 110,
        "type": "High-Tc",
    },
    "HgBaCaCuO": {
        "Tc_K": 133,
        "type": "High-Tc",
        "note": "Record for cuprates (ambient)",
    },
    # Recent Discoveries
    "H3S": {
        "Tc_K": 203,
        "pressure_GPa": 150,
        "year": 2015,
        "note": "Record Tc under pressure!",
    },
    "LaH10": {
        "Tc_K": 250,
        "pressure_GPa": 170,
        "year": 2019,
        "note": "Near room temperature!",
    },
}

BCS_THEORY = {
    "gap_equation": "Δ(T=0) = 1.76 × k_B × T_c",
    "coherence_length": "ξ = ℏv_F / (π × Δ)",
    "electron_phonon": "λ = N(E_F) × V",
    "Tc_formula": "T_c ∝ ω_D × exp(-1/λ)",
}

# ============================================================
# BOSE-EINSTEIN CONDENSATION
# ============================================================

BEC_DATA = {
    "first_observation": {
        "element": "Rb-87",
        "year": 1995,
        "lab": "JILA (Cornell & Wieman)",
        "atoms": 2000,
        "temperature_nK": 170,
    },
    "critical_temperature": {
        "formula": "T_c = (2πℏ²/m×k_B) × (n/ζ(3/2))^(2/3)",
        "typical_values": "~100 nK for alkali atoms",
    },
    "key_experiments": {
        "Rb_87": {"Tc_nK": 170},
        "Na_23": {"Tc_nK": 2000},
        "Li_7": {"Tc_nK": 400},
        "H": {"Tc_nK": 50},
    },
    "superfluidity": {
        "He_4": {
            "Tc_K": 2.17,
            "name": "Lambda point",
            "note": "He-4 superfluid",
        },
        "He_3": {
            "Tc_mK": 2.6,
            "note": "Fermionic superfluid",
        },
    },
}

# ============================================================
# QUANTUM HALL EFFECT
# ============================================================

QUANTUM_HALL = {
    # Integer QHE (von Klitzing, 1980)
    "integer": {
        "discovery": 1980,
        "discoverer": "Klaus von Klitzing",
        "Nobel": 1985,
        "formula": "R_H = h/(n×e²)",
        "quantization": "Exact to 10⁻¹⁰",
        "n_values": [1, 2, 3, 4, 5],
        "use": "Resistance standard",
    },
    # Fractional QHE (Laughlin, 1982)
    "fractional": {
        "discovery": 1982,
        "discoverers": "Tsui, Störmer, Gossard",
        "Nobel": 1998,
        "formula": "R_H = h/(ν×e²)",
        "nu_values": [1 / 3, 2 / 5, 3 / 7, 2 / 3, 5 / 2],
        "physics": "Strongly correlated electrons",
    },
    # Quantum Spin Hall (2005)
    "spin_hall": {
        "discovery": 2005,
        "system": "HgTe/CdTe quantum wells",
        "physics": "Topological insulators",
    },
    # von Klitzing constant
    "R_K": {
        "value": 25812.80745,  # Ohms
        "definition": "h/e²",
        "precision": "exact (by definition since 2019)",
    },
}

# ============================================================
# FUNDAMENTAL CONSTANTS FROM CM
# ============================================================

CONDENSED_MATTER_CONSTANTS = {
    "R_K": {
        "name": "von Klitzing constant",
        "value": 25812.80745,
        "unit": "Ω",
        "definition": "h/e²",
    },
    "Phi_0": {
        "name": "Magnetic flux quantum",
        "value": 2.067833848e-15,
        "unit": "Wb",
        "definition": "h/(2e)",
    },
    "K_J": {
        "name": "Josephson constant",
        "value": 483597.8484e9,
        "unit": "Hz/V",
        "definition": "2e/h",
    },
}

# ============================================================
# UET PREDICTIONS
# ============================================================


def uet_superconductivity():
    """
    UET interpretation of superconductivity.

    In UET, Cooper pairs form due to C-I field mediated attraction.
    The gap Δ corresponds to C-I binding energy.
    """
    return {
        "interpretation": "Cooper pairs = C-I field bound states",
        "gap": "Δ ~ κ × phonon coupling energy",
        "Tc_prediction": "Not yet derived from κ",
        "high_Tc_mystery": "UET may explain via stronger C-I coupling",
        "status": "FRAMEWORK CONSISTENT, needs calculation",
    }


def uet_bec():
    """
    UET interpretation of BEC.

    BEC is a macroscopic quantum state - perfect for UET!
    """
    return {
        "interpretation": "BEC = C-I field coherent ground state",
        "Tc_formula": "Should emerge from C-I statistics",
        "superfluidity": "Zero viscosity = C-I field flow",
        "status": "FRAMEWORK CONSISTENT",
    }


def uet_quantum_hall():
    """
    UET interpretation of Quantum Hall Effect.

    The exact quantization is topological - similar to C-I field topology.
    """
    return {
        "interpretation": "QHE = C-I field winding numbers",
        "integer": "n = topological charge",
        "fractional": "ν = fractional C-I winding",
        "R_K": "h/e² should emerge from UET constants",
        "prediction": "R_K = (π/κ) × (fundamental unit)?",
        "status": "TOPOLOGY MATCHES",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("CONDENSED MATTER PHYSICS")
    print("=" * 60)

    print(f"\nSuperconductors:")
    print(f"  Record Tc (ambient): 133 K (HgBaCaCuO)")
    print(f"  Record Tc (pressure): 250 K (LaH10 @ 170 GPa)")

    print(f"\nBEC:")
    print(f"  First: Rb-87 at 170 nK (1995)")
    print(f"  He-4 lambda point: 2.17 K")

    print(f"\nQuantum Hall:")
    print(f"  R_K = {QUANTUM_HALL['R_K']['value']:.5f} Ω")
    print(f"  Precision: 10⁻¹⁰")
