"""UET engine, layer 1: the parent action (core/THEORY_CARD.md) in canonical variables and SI units.

Canonical action (natural units hbar = c = 1):
    L = (1 + kappa xi_c psi^2)(R - 2 Lambda)/(2 kappa) - 1/2 (d psi)^2 - 1/2 m_psi^2 psi^2 - 1/4 lam_psi psi^4
        - 1/2 (d chi)^2 - 1/2 m_chi^2 |chi|^2 - 1/4 lam_chi |chi|^4 + 1/2 g_c psi |chi|^2

Free physical parameters: m_psi, g_c, xi_c (plus lam_psi, Lambda_eff). Their registered limits are
below; a topic may not invent values for them. Every function wraps a derived module that already
has physics tests; this file adds no new physics.

Lane rule (Theory Card section 7, T005, T015): chi is ordinary matter counted per nucleon. chi as a
whole atom at tree level FAILED for He II (T015).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

from ._load import load

_fifth = load("03_lanes/scalar_tensor/uet_portal_fifth_force.py")
_mapping = load("02_equations/covariant/uet_scalar_tensor_mapping.py")
_si = load("03_lanes/open_system/uet_si_bose_fluid.py")
_drag = load("03_lanes/open_system/uet_portal_drag_derived.py")

HBAR_C_EV_M = _si.HBAR_C_EV_M
G_NAT_EV2 = _si.G_NAT_EV2
KAPPA_NAT_EV2 = 8.0 * pi * G_NAT_EV2
M_NUCLEON_EV = _si.M_NUCLEON_EV

# Registered limits (claims in docs/standard/claims.json). Use these, never topic-local values.
REGISTERED_LIMITS = {
    "C_T005_PORTAL_G_C": "g_c < 5.1e-10 eV for m_psi <= 5.1e-3 eV (torsion balance); see T005 for other ranges",
    "C_T001_BINARY_PULSAR_XI_C": "xi_c in [2.0, 2.4] excluded for m_psi <= 2.5e-18 eV (binary pulsars)",
    "C_T015_HE_II_TREE_LEVEL_LANE": "chi = He-4 atom at tree level FAILED; He II is outside the action",
}


@dataclass(frozen=True)
class CanonicalParameters:
    m_psi_ev: float
    g_c_ev: float
    xi_c: float  # dimensionless non-minimal coupling, F = 1 + kappa xi_c psi^2
    m_chi_ev: float = M_NUCLEON_EV


def canonical_from_action(k: float, Z: float, eps: float, xi: float, mu2: float, lam_phi: float,
                          h: float, m2: float, lam_chi: float, kappa: float) -> dict[str, float]:
    """Theory Card section 3: absorb k, Z and eps into canonical parameters."""
    if k <= 0.0 or Z <= 0.0 or eps <= 0.0:
        raise ValueError("k, Z and eps must be positive")
    return {
        "xi_c": xi / (kappa * k),
        "m_psi2": mu2 / k,
        "lam_psi": lam_phi / (eps * k * k),
        "g_c": h * sqrt(eps / k) / Z,
        "m_chi2": m2 / Z,
        "lam_chi": lam_chi / (Z * Z),
    }


# --- weak-field gravity and the portal fifth force -------------------------------------------

def portal_alpha(p: CanonicalParameters) -> float:
    """Yukawa strength relative to gravity, alpha = g_c^2 / (2 kappa m_chi^4) (claim C_PORTAL_FIFTH_FORCE)."""
    return _fifth.yukawa_alpha(p.g_c_ev, p.m_chi_ev**2, KAPPA_NAT_EV2)


def yukawa_range_m(p: CanonicalParameters) -> float:
    return _fifth.yukawa_range_m(p.m_psi_ev)


def two_body_potential_si(r_m: float, mass1_kg: float, mass2_kg: float, p: CanonicalParameters) -> float:
    """V(r) = -G M m / r [1 + alpha exp(-r/lambda)] in joules."""
    from math import exp
    g_si = 6.67430e-11
    return -g_si * mass1_kg * mass2_kg / r_m * (1.0 + portal_alpha(p) * exp(-r_m / yukawa_range_m(p)))


def def_parameters(p: CanonicalParameters, psi0: float = 0.0) -> dict[str, float]:
    """Damour-Esposito-Farese and PPN parameters (beta0 = -2 xi_c at psi0 = 0; claim C_UET_DEF_MAPPING).

    psi0 is the asymptotic scalar value in units of the reduced Planck mass (kappa = 1)."""
    return _mapping.uet_def_parameters(p.xi_c, 1.0, psi0)


# --- Bose fluid of chi quanta (wave SI-1) ----------------------------------------------------

def gp_lambda_from_scattering_length(a_m: float, particle_mass_ev: float) -> float:
    return _si.lam_from_scattering_length(a_m, particle_mass_ev)


def bogoliubov_sound_speed_si(n_m3: float, a_m: float, particle_mass_kg: float) -> float:
    return _si.bogoliubov_speed_si(n_m3, a_m, particle_mass_kg)


def diluteness(n_m3: float, a_m: float) -> float:
    """n a^3; tree-level GP applies only when this is << 1."""
    return _si.diluteness(n_m3, a_m)


def portal_scattering_length_shift_m(p: CanonicalParameters, atom_mass_ev: float) -> float:
    return _si.scattering_length_shift_m(portal_alpha(p), atom_mass_ev, p.m_psi_ev)


# --- friction of psi from matter (wave B6) ---------------------------------------------------

linear_response_drag = _drag.linear_response_drag
chandrasekhar_drag = _drag.chandrasekhar_drag
