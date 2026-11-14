"""
Electroweak Parameters Data
===========================
PDG 2024 Standard Model Electroweak Parameters

Reference: Phys. Rev. D 110, 030001 (2024)

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
# GAUGE BOSON MASSES (PDG 2024)
# ================================================================

BOSON_MASSES = {
    "W_boson": {
        "mass_GeV": 80.3602,
        "uncertainty_GeV": 0.0099,
        "mass_MeV": 80360.2,
        "uncertainty_MeV": 9.9,
        "reference": "CMS 2024, PDG 2024",
        "SM_prediction_MeV": 80357.0,
        "SM_uncertainty_MeV": 6.0,
    },
    "Z_boson": {
        "mass_GeV": 91.1876,
        "uncertainty_GeV": 0.0021,
        "mass_MeV": 91187.6,
        "uncertainty_MeV": 2.1,
        "reference": "LEP 1, PDG 2024",
    },
    "Higgs": {
        "mass_GeV": 125.25,
        "uncertainty_GeV": 0.17,
        "reference": "ATLAS + CMS, PDG 2024",
    },
}

# ================================================================
# WEINBERG ANGLE (sin²θ_W)
# ================================================================

WEINBERG_ANGLE = {
    "sin2_theta_W": {
        "value": 0.23122,
        "uncertainty": 0.00015,
        "scale": "M_Z pole",
        "MS_bar_MZ": 0.23122,
        "reference": "PDG 2024 Electroweak Model",
    },
    "cos2_theta_W": {
        "value": 1 - 0.23122,
        "reference": "Derived from sin²θ_W",
    },
}

# ================================================================
# FERMI CONSTANT
# ================================================================

FERMI_CONSTANT = {
    "G_F": {
        "value": 1.1663787e-5,  # GeV^-2
        "uncertainty": 6e-12,
        "unit": "GeV^-2",
        "reference": "PDG 2024",
    },
    "G_F_MeV": {
        "value": 1.1663787e-11,  # MeV^-2
        "unit": "MeV^-2",
    },
}

# ================================================================
# COUPLING CONSTANTS
# ================================================================

COUPLING_CONSTANTS = {
    "alpha_EM": {
        "value": 1 / 137.035999206,
        "inverse": 137.035999206,
        "uncertainty": 0.000000011,
        "scale": "q² = 0",
        "reference": "PDG 2024",
    },
    "alpha_EM_MZ": {
        "value": 1 / 127.951,
        "inverse": 127.951,
        "uncertainty": 0.009,
        "scale": "M_Z pole",
        "reference": "PDG 2024",
    },
    "g_weak": {
        "description": "Weak SU(2) coupling",
        "relation": "g = e / sin(θ_W)",
    },
    "gprime": {
        "description": "Weak U(1) coupling",
        "relation": "g' = e / cos(θ_W)",
    },
}

# ================================================================
# ELECTROWEAK UNIFICATION
# ================================================================

EW_RELATIONS = {
    "W_Z_relation": {
        "formula": "M_W = M_Z × cos(θ_W)",
        "predicted_MW": 91.1876 * np.sqrt(1 - 0.23122),  # ~79.95 GeV
        "note": "Radiative corrections modify this",
    },
    "rho_parameter": {
        "value": 1.00038,
        "uncertainty": 0.00020,
        "SM_value": 1.0,
        "description": "ρ = M_W² / (M_Z² × cos²θ_W)",
        "reference": "PDG 2024",
    },
}

# ================================================================
# UET INTERPRETATION
# ================================================================

UET_INTERPRETATION = {
    "concept": "Electroweak symmetry breaking via Information gradients",
    "mechanism": """
        In UET framework:
        - Higgs field = Information density field I(x)
        - Vacuum expectation value = equilibrium βCI
        - Mass generation = coupling to I-field gradient
        
        M_W, M_Z arise from Information field curvature.
    """,
    "prediction": """
        EW precision tests probe Information field structure.
        sin²θ_W running = I-field energy dependence
    """,
}


# ================================================================
# HELPER FUNCTIONS
# ================================================================


def get_W_mass():
    """Return W boson mass."""
    return BOSON_MASSES["W_boson"]["mass_MeV"]


def get_Z_mass():
    """Return Z boson mass."""
    return BOSON_MASSES["Z_boson"]["mass_MeV"]


def get_weinberg_angle():
    """Return sin²θ_W at M_Z."""
    return WEINBERG_ANGLE["sin2_theta_W"]["value"]


def calculate_MW_from_MZ(mz_gev, sin2_theta):
    """Calculate M_W from M_Z using tree-level relation."""
    cos_theta = np.sqrt(1 - sin2_theta)
    return mz_gev * cos_theta


if __name__ == "__main__":
    print("=" * 60)
    print("Electroweak Parameters (PDG 2024)")
    print("=" * 60)
    print(f"M_W = {get_W_mass():.1f} ± 9.9 MeV")
    print(f"M_Z = {get_Z_mass():.1f} ± 2.1 MeV")
    print(f"sin²θ_W = {get_weinberg_angle():.5f} ± 0.00015")
    print(f"α_EM⁻¹ = {COUPLING_CONSTANTS['alpha_EM']['inverse']:.6f}")
