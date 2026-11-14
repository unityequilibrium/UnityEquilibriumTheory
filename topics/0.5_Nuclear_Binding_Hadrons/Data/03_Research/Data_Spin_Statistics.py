"""
Spin-Statistics Data
=====================
Source: PDG 2024, Quantum Field Theory

Connection between spin and quantum statistics:
- Integer spin (0, 1, 2...) → Bosons (Bose-Einstein)
- Half-integer spin (1/2, 3/2...) → Fermions (Fermi-Dirac)

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# PARTICLE SPIN CATALOG (PDG 2024)
# ============================================================

BOSONS = {
    # Spin-0 (Scalar)
    "Higgs": {"spin": 0, "mass_GeV": 125.04, "statistics": "Bose-Einstein"},
    "pion": {"spin": 0, "mass_MeV": 139.57, "statistics": "Bose-Einstein"},
    # Spin-1 (Vector)
    "photon": {"spin": 1, "mass": 0, "statistics": "Bose-Einstein"},
    "W_plus": {"spin": 1, "mass_GeV": 80.37, "statistics": "Bose-Einstein"},
    "W_minus": {"spin": 1, "mass_GeV": 80.37, "statistics": "Bose-Einstein"},
    "Z_boson": {"spin": 1, "mass_GeV": 91.19, "statistics": "Bose-Einstein"},
    "gluon": {"spin": 1, "mass": 0, "statistics": "Bose-Einstein"},
    # Spin-2 (Tensor)
    "graviton": {"spin": 2, "mass": 0, "statistics": "Bose-Einstein", "status": "hypothetical"},
}

FERMIONS = {
    # Spin-1/2 (Spinor)
    "electron": {"spin": 0.5, "mass_MeV": 0.511, "statistics": "Fermi-Dirac"},
    "muon": {"spin": 0.5, "mass_MeV": 105.66, "statistics": "Fermi-Dirac"},
    "tau": {"spin": 0.5, "mass_MeV": 1776.86, "statistics": "Fermi-Dirac"},
    "electron_neutrino": {"spin": 0.5, "mass": "< 0.8 eV", "statistics": "Fermi-Dirac"},
    "muon_neutrino": {"spin": 0.5, "mass": "< 0.19 MeV", "statistics": "Fermi-Dirac"},
    "tau_neutrino": {"spin": 0.5, "mass": "< 18.2 MeV", "statistics": "Fermi-Dirac"},
    # Quarks
    "up_quark": {"spin": 0.5, "mass_MeV": 2.16, "statistics": "Fermi-Dirac"},
    "down_quark": {"spin": 0.5, "mass_MeV": 4.67, "statistics": "Fermi-Dirac"},
    "strange_quark": {"spin": 0.5, "mass_MeV": 93.4, "statistics": "Fermi-Dirac"},
    "charm_quark": {"spin": 0.5, "mass_GeV": 1.27, "statistics": "Fermi-Dirac"},
    "bottom_quark": {"spin": 0.5, "mass_GeV": 4.18, "statistics": "Fermi-Dirac"},
    "top_quark": {"spin": 0.5, "mass_GeV": 172.5, "statistics": "Fermi-Dirac"},
    # Baryons (composite, but still fermions!)
    "proton": {"spin": 0.5, "mass_GeV": 0.938, "statistics": "Fermi-Dirac"},
    "neutron": {"spin": 0.5, "mass_GeV": 0.940, "statistics": "Fermi-Dirac"},
}

# ============================================================
# SPIN-STATISTICS THEOREM
# ============================================================

SPIN_STATISTICS_THEOREM = {
    "statement": "Particles with integer spin are bosons; half-integer spin are fermions",
    "proof_requires": ["Lorentz invariance", "Causality", "Positive energy"],
    "discovered_by": "Wolfgang Pauli (1940)",
    "no_violations_observed": True,
    "consequences": {
        "bosons": "Multiple particles in same state (lasers, BEC)",
        "fermions": "Pauli exclusion (matter structure)",
    },
}

# ============================================================
# UET INTERPRETATION
# ============================================================


def uet_spin_interpretation():
    """
    UET interpretation of spin-statistics.

    In UET C-I field language:
    - Spin = I-field rotation phase
    - Integer spin: 2π rotation → same state
    - Half-integer spin: 2π rotation → minus sign (spinor)

    Statistics from I-field exchange:
    - Bosons: Symmetric I-field exchange
    - Fermions: Antisymmetric I-field exchange
    """
    return {
        "spin_origin": "I-field rotational mode",
        "integer_spin": "Even I-field winding (boson)",
        "half_spin": "Odd I-field winding (fermion)",
        "statistics_from": "Exchange phase of C-I field",
        "pauli_from": "Antisymmetric fermion wavefunction",
    }


def uet_spin_prediction(kappa=0.5):
    """
    UET prediction for spin values.

    Spin quantization: s = n/2 where n = 0, 1, 2, ...

    This is geometric/topological in UET.
    """
    # Spin is quantized in units of ℏ/2
    # UET: Spin = π × (winding number) / (2π) = n/2

    allowed_spins = [0, 0.5, 1, 1.5, 2, 2.5, 3]

    # Matter particles (leptons, quarks) are spin-1/2
    # Force carriers (γ, W, Z, g) are spin-1
    # Higgs is spin-0
    # Graviton would be spin-2

    return {
        "matter": 0.5,  # Fundamental fermions
        "forces": 1,  # Gauge bosons
        "scalar": 0,  # Higgs
        "gravity": 2,  # Graviton
        "note": "Spin quantization is topological in UET",
    }
