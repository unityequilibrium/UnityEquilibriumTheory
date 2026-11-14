"""Wave B5: how large can the portal drag be? The only cross-layer UET effect, bounded by orbit survival.

Wave B4 (uet_portal_drag.py) found one effect that standard physics lacks: a body moving through the
environment rest frame u loses momentum to the field psi that layer 2 makes dissipative,

    F = Gamma v q^2 / (12 pi R),   q = g_c M / (2 m_chi^2)          (light-field limit, v << 1)

with three free parameters (g_c, Gamma, m_psi). For a body orbiting the Sun with the Sun's rest frame as
the environment frame, v is the orbital velocity, the force is a linear drag a = -lambda v with
lambda = Gamma q^2 / (12 pi R M), and the semi-major axis decays as

    d ln a / dt = -2 lambda = -Lambda,    Lambda = Gamma q^2 / (6 pi R M).

A planet that has survived for the age of the Solar System T needs Lambda <= 1/T. In terms of the
combination that the three parameters enter,

    Gamma g_c^2 <= (hbar / T) 24 pi m_chi^4 R / (M hbar c)  ... evaluated per body in eV^3,

and the most constraining body is the one with the largest M / R (Jupiter among the planets). The bound
does not depend on the orbital velocity. All inputs are in eV (hbar = c = 1 for the force law); the SI
conversion is kept separate so that the test can check the units two ways.

Assumptions, stated plainly: the environment rest frame is the Sun's frame; the orbit is circular and
the drag small (first order in Gamma); chi is ordinary matter with the mean nucleon mass (author
decision 2026-11-10); the field is light (m_psi R << 1).
"""

from __future__ import annotations

from math import pi

HBAR_EV_S = 6.582119569e-16
HBAR_C_EV_M = 1.973269804e-7
LIGHT_SPEED = 299_792_458.0
EV_JOULE = 1.602176634e-19
KG_TO_EV = LIGHT_SPEED**2 / EV_JOULE
NUCLEON_MASS_EV = 0.9389e9
YEAR_S = 3.15576e7
SOLAR_SYSTEM_AGE_S = 4.5672e9 * YEAR_S  # Pb-Pb age of the oldest solids (Connelly et al. 2012)


def portal_charge(g_c_ev: float, mass_kg: float, m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    """q = g_c M / (2 m_chi^2), dimensionless in natural units."""
    return g_c_ev * (mass_kg * KG_TO_EV) / (2.0 * m_chi_ev**2)


def decay_rate_ev(gamma_ev: float, g_c_ev: float, mass_kg: float, radius_m: float, m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    """Lambda = Gamma q^2 / (6 pi R M) in eV."""
    q = portal_charge(g_c_ev, mass_kg, m_chi_ev)
    inverse_radius = HBAR_C_EV_M / radius_m
    return gamma_ev * q * q * inverse_radius / (6.0 * pi * mass_kg * KG_TO_EV)


def decay_rate_per_second(gamma_ev: float, g_c_ev: float, mass_kg: float, radius_m: float, m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    return decay_rate_ev(gamma_ev, g_c_ev, mass_kg, radius_m, m_chi_ev) / HBAR_EV_S


def decay_rate_per_second_si(gamma_ev: float, g_c_ev: float, mass_kg: float, radius_m: float, m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    """Same quantity through SI force and acceleration.

    F = Gamma (v/c) q^2 (hbar c / R) / (12 pi) in eV^2, and 1 eV^2 = (eV in J) / (hbar c in eV m) newtons.
    The drag coefficient is k = F / v in N s / m, the damping rate of the velocity is lambda = k / M, and
    d ln a / dt = -2 lambda."""
    q = portal_charge(g_c_ev, mass_kg, m_chi_ev)
    force_per_c_ev2 = gamma_ev * q * q * (HBAR_C_EV_M / radius_m) / (12.0 * pi)  # eV^2 per unit v/c
    newton_per_ev2 = EV_JOULE / HBAR_C_EV_M
    k_si = force_per_c_ev2 * newton_per_ev2 / LIGHT_SPEED  # N / (m/s)
    return 2.0 * k_si / mass_kg


def max_gamma_g_c_squared_ev3(mass_kg: float, radius_m: float, age_s: float = SOLAR_SYSTEM_AGE_S,
                              m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    """Largest Gamma g_c^2 (eV^3) for which Lambda <= hbar / age."""
    unit = decay_rate_ev(1.0, 1.0, mass_kg, radius_m, m_chi_ev)  # Lambda for Gamma g_c^2 = 1 eV^3
    return (HBAR_EV_S / age_s) / unit


def max_gamma_ev(g_c_ev: float, mass_kg: float, radius_m: float, age_s: float = SOLAR_SYSTEM_AGE_S) -> float:
    return max_gamma_g_c_squared_ev3(mass_kg, radius_m, age_s) / g_c_ev**2


def damping_time_s(gamma_ev: float) -> float:
    return HBAR_EV_S / gamma_ev
