"""
Hadron Mass Data - PDG 2024 + Lattice QCD
==========================================
Real experimental and lattice QCD data for hadron masses.

Sources:
- PDG 2024: Phys. Rev. D 110, 030001 (2024)
- FLAG Review 2024 (Flavour Lattice Averaging Group)
- Hadron Spectrum Collaboration

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
# LIGHT MESONS (PDG 2024)
# ================================================================

MESON_MASSES = {
    # Pseudoscalar mesons (J^P = 0^-)
    "pi_pm": {
        "mass_MeV": 139.57039,
        "error": 0.00018,
        "quarks": ["u", "d̄"],
        "isospin": 1,
        "description": "Charged pion",
    },
    "pi_0": {
        "mass_MeV": 134.9768,
        "error": 0.0005,
        "quarks": ["uū-dd̄"],
        "isospin": 1,
        "description": "Neutral pion",
    },
    "K_pm": {
        "mass_MeV": 493.677,
        "error": 0.016,
        "quarks": ["u", "s̄"],
        "isospin": 0.5,
        "description": "Charged kaon",
    },
    "K_0": {
        "mass_MeV": 497.611,
        "error": 0.013,
        "quarks": ["d", "s̄"],
        "isospin": 0.5,
        "description": "Neutral kaon",
    },
    "eta": {
        "mass_MeV": 547.862,
        "error": 0.017,
        "quarks": ["uū+dd̄-2ss̄"],
        "isospin": 0,
        "description": "Eta meson",
    },
    "eta_prime": {
        "mass_MeV": 957.78,
        "error": 0.06,
        "quarks": ["uū+dd̄+ss̄"],
        "isospin": 0,
        "description": "Eta prime",
    },
    # Vector mesons (J^P = 1^-)
    "rho": {
        "mass_MeV": 775.26,
        "error": 0.23,
        "quarks": ["uū, dd̄"],
        "isospin": 1,
        "description": "Rho meson",
    },
    "omega": {
        "mass_MeV": 782.66,
        "error": 0.13,
        "quarks": ["uū+dd̄"],
        "isospin": 0,
        "description": "Omega meson (light)",
    },
    "phi": {
        "mass_MeV": 1019.461,
        "error": 0.016,
        "quarks": ["ss̄"],
        "isospin": 0,
        "description": "Phi meson",
    },
    "K_star": {
        "mass_MeV": 891.67,
        "error": 0.26,
        "quarks": ["us̄"],
        "isospin": 0.5,
        "description": "K* meson",
    },
}

# ================================================================
# BARYONS (PDG 2024)
# ================================================================

BARYON_MASSES = {
    # Octet baryons (J^P = 1/2^+)
    "proton": {
        "mass_MeV": 938.27208816,
        "error": 0.00000029,
        "quarks": ["u", "u", "d"],
        "isospin": 0.5,
        "description": "Proton",
    },
    "neutron": {
        "mass_MeV": 939.56542052,
        "error": 0.00000054,
        "quarks": ["u", "d", "d"],
        "isospin": 0.5,
        "description": "Neutron",
    },
    "Lambda": {
        "mass_MeV": 1115.683,
        "error": 0.006,
        "quarks": ["u", "d", "s"],
        "isospin": 0,
        "description": "Lambda baryon",
    },
    "Sigma_plus": {
        "mass_MeV": 1189.37,
        "error": 0.07,
        "quarks": ["u", "u", "s"],
        "isospin": 1,
        "description": "Sigma+",
    },
    "Sigma_0": {
        "mass_MeV": 1192.642,
        "error": 0.024,
        "quarks": ["u", "d", "s"],
        "isospin": 1,
        "description": "Sigma0",
    },
    "Sigma_minus": {
        "mass_MeV": 1197.449,
        "error": 0.030,
        "quarks": ["d", "d", "s"],
        "isospin": 1,
        "description": "Sigma-",
    },
    "Xi_0": {
        "mass_MeV": 1314.86,
        "error": 0.20,
        "quarks": ["u", "s", "s"],
        "isospin": 0.5,
        "description": "Xi0",
    },
    "Xi_minus": {
        "mass_MeV": 1321.71,
        "error": 0.07,
        "quarks": ["d", "s", "s"],
        "isospin": 0.5,
        "description": "Xi-",
    },
    # Decuplet baryons (J^P = 3/2^+)
    "Delta": {
        "mass_MeV": 1232,
        "error": 2,
        "quarks": ["u", "u", "u"],  # Δ++
        "isospin": 1.5,
        "description": "Delta resonance",
    },
    "Omega_minus": {
        "mass_MeV": 1672.45,
        "error": 0.29,
        "quarks": ["s", "s", "s"],
        "isospin": 0,
        "description": "Omega baryon",
    },
}

# ================================================================
# LATTICE QCD RESULTS (FLAG 2024)
# ================================================================

LATTICE_QCD_MASSES = {
    # FLAG 2024 averages with N_f = 2+1+1
    "pi_pm": {"mass_MeV": 138.5, "error": 1.2, "ref": "FLAG 2024"},
    "K_pm": {"mass_MeV": 492.8, "error": 1.5, "ref": "FLAG 2024"},
    "proton": {"mass_MeV": 936.2, "error": 2.0, "ref": "BMW 2021"},
    "neutron": {"mass_MeV": 937.8, "error": 2.1, "ref": "BMW 2021"},
    "Omega_minus": {"mass_MeV": 1670, "error": 4, "ref": "Hadron Spectrum"},
}

# ================================================================
# QUARK MASSES
# ================================================================

QUARK_MASSES = {
    # Current quark masses (MSbar at 2 GeV)
    "up_current": {"mass_MeV": 2.16, "error_plus": 0.49, "error_minus": 0.26},
    "down_current": {"mass_MeV": 4.67, "error_plus": 0.48, "error_minus": 0.17},
    "strange_current": {"mass_MeV": 93.4, "error_plus": 8.6, "error_minus": 3.4},
    "charm_current": {"mass_GeV": 1.27, "error": 0.02},
    "bottom_current": {"mass_GeV": 4.18, "error_plus": 0.03, "error_minus": 0.02},
    "top_pole": {"mass_GeV": 172.69, "error": 0.30},
    # Constituent quark masses (effective, model-dependent)
    "up_constituent": {"mass_MeV": 336, "note": "Effective, model-dependent"},
    "down_constituent": {"mass_MeV": 340, "note": "Effective, model-dependent"},
    "strange_constituent": {"mass_MeV": 486, "note": "Effective, model-dependent"},
}

# ================================================================
# CONFINEMENT PARAMETERS
# ================================================================

CONFINEMENT_PARAMS = {
    "string_tension": {
        "value_GeV2": 0.18,  # σ ≈ 0.18 GeV² ≈ 0.9 GeV/fm
        "value_GeV_per_fm": 0.9,
        "uncertainty": 0.02,
        "reference": "Lattice QCD average",
    },
    "hadron_radius": {
        "proton_fm": 0.87,  # Charge radius
        "pion_fm": 0.66,  # Charge radius
        "reference": "PDG 2024",
    },
}


# ================================================================
# Helper Functions
# ================================================================


def get_hadron_mass(name):
    """Get hadron mass from PDG data."""
    if name in MESON_MASSES:
        return MESON_MASSES[name]["mass_MeV"]
    elif name in BARYON_MASSES:
        return BARYON_MASSES[name]["mass_MeV"]
    return None


def constituent_mass_model(quarks, sigma=0.9, r=0.8):
    """
    Simple constituent quark model for hadron mass.

    M = Σ m_constituent + E_confinement

    E_confinement ~ σ × r (string energy)
    """
    m_q = {"u": 336, "d": 340, "s": 486, "c": 1550, "b": 4730}

    total_quark = sum(m_q.get(q, 340) for q in quarks)
    E_conf = sigma * r * 200  # Approximate in MeV

    return total_quark + E_conf


if __name__ == "__main__":
    print("=" * 60)
    print("Hadron Mass Data - PDG 2024")
    print("=" * 60)

    print("\nLight Mesons:")
    print(f"{'Name':<15} {'Mass (MeV)':<15} {'Error (MeV)':<12}")
    print("-" * 45)
    for name, data in list(MESON_MASSES.items())[:6]:
        print(f"{name:<15} {data['mass_MeV']:<15.3f} {data['error']:<12.5f}")

    print("\nBaryons:")
    print(f"{'Name':<15} {'Mass (MeV)':<15} {'Error (MeV)':<12}")
    print("-" * 45)
    for name, data in list(BARYON_MASSES.items())[:5]:
        print(f"{name:<15} {data['mass_MeV']:<15.3f} {data['error']:<12.5f}")

    print(
        f"\nString tension: σ = {CONFINEMENT_PARAMS['string_tension']['value_GeV_per_fm']} GeV/fm"
    )
