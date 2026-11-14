"""
Muon g-2 Experimental Data
==========================
Fermilab Muon g-2 Experiment - Final Results (June 2025)

Reference: Muon g-2 Collaboration, Phys. Rev. Lett. (2025)
           a_μ = 0.001165920705(114)
           Precision: 127 ppb

Updated for UET V3.0
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)



# Import from UET V3.0 Master Equation
import sys
from pathlib import Path
_root = Path(__file__).parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from docs.core.uet_master_equation import (
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import numpy as np

# ================================================================
# MUON G-2: FUNDAMENTAL CONSTANTS
# ================================================================

# Experimental value (Fermilab 2025 - FINAL)
A_MU_EXPERIMENT = 0.001165920705
A_MU_UNCERTAINTY = 0.000000000114  # 114 × 10^-12

# Standard Model predictions
SM_PREDICTIONS = {
    # 2020 Data-Driven (e+e- → hadrons)
    "2020_data_driven": {
        "value": 0.00116591810,
        "uncertainty": 0.00000000043,
        "reference": "Aoyama et al. 2020 Physics Reports",
        "discrepancy_sigma": 5.1,  # from experiment
    },
    # 2021 Lattice QCD (Budapest-Marseille-Wuppertal)
    "2021_lattice_qcd": {
        "value": 0.00116591954,
        "uncertainty": 0.00000000055,
        "reference": "Borsanyi et al. 2021 Nature",
        "discrepancy_sigma": 1.0,  # from experiment
    },
    # 2025 Theory Initiative (Latest)
    "2025_theory_initiative": {
        "value": 0.00116591950,  # Approximate
        "uncertainty": 0.00000000040,
        "reference": "Muon g-2 Theory Initiative 2025",
        "discrepancy_sigma": 1.2,
    },
}

# ================================================================
# PHYSICAL PARAMETERS
# ================================================================

# Muon properties
MUON_MASS_MEV = 105.6583755  # MeV/c²
MUON_LIFETIME_US = 2.1969811  # microseconds
MUON_G_FACTOR = 2.0023318418  # Approximate

# Fine structure constant
ALPHA_EM = 1 / 137.035999206

# ================================================================
# G-2 CONTRIBUTIONS (Standard Model)
# ================================================================

SM_CONTRIBUTIONS = {
    # QED contribution (most precise)
    "qed": {
        "value": 0.00116584718,
        "description": "Quantum Electrodynamics loops",
        "precision": "sub-ppb",
    },
    # Electroweak contribution
    "electroweak": {
        "value": 0.000000001536,
        "description": "W, Z boson loops",
        "precision": "well-known",
    },
    # Hadronic Vacuum Polarization (HVP) - MAIN UNCERTAINTY
    "hvp": {
        "value": 0.000000069,  # Approximate
        "description": "Quark loops in photon propagator",
        "precision": "challenging - main source of theory uncertainty",
    },
    # Hadronic Light-by-Light (HLbL)
    "hlbl": {
        "value": 0.0000000092,
        "description": "Hadronic scattering of light",
        "precision": "improving with lattice QCD",
    },
}

# ================================================================
# UET INTERPRETATION
# ================================================================

UET_INTERPRETATION = {
    "concept": "Information Field couples to vacuum polarization",
    "mechanism": """
        In UET framework:
        - Muon creates local Information disturbance I(r)
        - Vacuum polarization = response of I-field
        - g-2 anomaly = βCI term contribution
        
        a_μ(UET) = a_μ(SM) + Δa(Information)
        
        The "excess" over SM could be Information-mediated.
    """,
    "prediction": """
        If UET β term contributes:
        Δa_μ(UET) ~ β × (muon mass / vacuum energy scale)
        
        The ~5σ discrepancy (2020 SM) could be explained by:
        β_μ ≈ 2.5 × 10^-9 (Information coupling to muon)
    """,
}


# ================================================================
# HELPER FUNCTIONS
# ================================================================


def get_experimental_value():
    """Return Fermilab experimental value."""
    return {
        "a_mu": A_MU_EXPERIMENT,
        "uncertainty": A_MU_UNCERTAINTY,
        "precision_ppb": 127,
        "reference": "Fermilab Muon g-2 Collaboration (2025)",
    }


def get_sm_prediction(version="2025_theory_initiative"):
    """Return Standard Model prediction."""
    return SM_PREDICTIONS.get(version, SM_PREDICTIONS["2025_theory_initiative"])


def calculate_discrepancy(sm_version="2020_data_driven"):
    """Calculate discrepancy between experiment and theory."""
    sm = SM_PREDICTIONS[sm_version]
    delta = A_MU_EXPERIMENT - sm["value"]
    combined_error = np.sqrt(A_MU_UNCERTAINTY**2 + sm["uncertainty"] ** 2)
    sigma = delta / combined_error

    return {
        "delta_a_mu": delta,
        "combined_uncertainty": combined_error,
        "sigma": sigma,
        "sm_version": sm_version,
    }


def get_uet_interpretation():
    """Return UET interpretation of g-2 anomaly."""
    return UET_INTERPRETATION
