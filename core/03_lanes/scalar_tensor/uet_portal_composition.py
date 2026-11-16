"""Equivalence-principle signal of the UET portal (topic 0.19 through the engine).

Lane (Theory Card section 7, as used in T005): chi = nucleon, so the portal source is the nucleon
rest-energy density, X = n_N m_N / m_N^2, while gravity couples to the total mass-energy M
(nuclear binding, electrons and the neutron-proton difference included). The portal charge per
unit mass of a body is therefore
    eps = N_nucleons m_N / M = (A / A_r) (m_N / u)
which differs between materials at the 1e-3 level. AI interpretation: whether binding energy
sources the portal is not fixed by the action, because nuclear forces are not in it; this module
takes the nucleon-number reading. With the other reading (portal charge = total mass) eps is the
same for every body and eta = 0 exactly.

Acceleration of test body i at distance r from a uniform sphere (radius R) of charge ratio eps_S:
    a_i = G M / r^2 [1 + alpha eps_S eps_i Phi(r, R, lambda)]
    Phi = F(R/lambda) e^{-r/lambda} (1 + r/lambda),  F(x) = 3 (x cosh x - sinh x) / x^3  (F -> 1 as x -> 0)
Eotvos parameter of a pair:  eta = 2 (a_1 - a_2)/(a_1 + a_2) ~= alpha eps_S (eps_1 - eps_2) Phi.
"""

from __future__ import annotations

from math import cosh, exp, sinh

U_EV = 931.49410242e6
M_NUCLEON_EV = 938.92e6


def charge_per_mass(mean_mass_number: float, atomic_weight: float) -> float:
    """eps = (A / A_r)(m_N / u) for a natural element (A = abundance-weighted nucleon number)."""
    return mean_mass_number / atomic_weight * (M_NUCLEON_EV / U_EV)


def alloy_charge_per_mass(parts: list[tuple[float, float]]) -> float:
    """Mass-fraction-weighted eps of an alloy: parts = [(mass_fraction, eps), ...]."""
    total = sum(w for w, _ in parts)
    return sum(w * e for w, e in parts) / total


def sphere_form_factor(radius_m: float, lam_m: float) -> float:
    x = radius_m / lam_m
    if x < 1e-3:
        return 1.0 + x * x / 10.0
    if x > 700.0:
        return 3.0 * (x - 1.0) / x**3 * 0.5 * exp(x)  # x cosh x - sinh x ~ (x - 1) e^x / 2
    return 3.0 * (x * cosh(x) - sinh(x)) / x**3


def yukawa_geometry(r_m: float, radius_m: float, lam_m: float) -> float:
    """Phi(r, R, lambda) for a uniform sphere, valid for r >= R."""
    x = radius_m / lam_m
    if x > 700.0:
        return 3.0 * (x - 1.0) / x**3 * 0.5 * exp(x - r_m / lam_m) * (1.0 + r_m / lam_m)
    return sphere_form_factor(radius_m, lam_m) * exp(-r_m / lam_m) * (1.0 + r_m / lam_m)


def eotvos(alpha: float, eps_source: float, eps_1: float, eps_2: float, r_m: float, radius_m: float, lam_m: float) -> float:
    phi = yukawa_geometry(r_m, radius_m, lam_m)
    a1 = 1.0 + alpha * eps_source * eps_1 * phi
    a2 = 1.0 + alpha * eps_source * eps_2 * phi
    return 2.0 * (a1 - a2) / (a1 + a2)


def alpha_max(eta_max: float, eps_source: float, d_eps: float, r_m: float, radius_m: float, lam_m: float) -> float:
    """Largest alpha with alpha eps_S d_eps Phi <= eta_max (positive d_eps, positive eta_max)."""
    return eta_max / (eps_source * d_eps * yukawa_geometry(r_m, radius_m, lam_m))
