"""Fifth force from the UET portal when chi is ordinary matter (wave B1b).

Author decision 2026-11-10: the O(2) field chi of the parent action is ordinary
matter. Then the portal term +1/2 g_c psi |chi~|^2 couples psi linearly to matter.

1. Particle content. A uniformly rotating O(2) mode chi~ = A (cos m t, sin m t)
   carries conserved charge and energy density rho = m_chi^2 A^2, so for
   non-relativistic matter X = |chi~|^2 = rho / m_chi^2.
2. Static field equation (canonical psi, flat space):
       nabla^2 psi - m_psi^2 psi = -(g_c / (2 m_chi^2)) rho
   A point mass M gives psi = (g_c M / (2 m_chi^2)) e^{-m_psi r} / (4 pi r).
3. The potential energy of a second mass m2 is -1/2 (g_c/m_chi^2) m2 psi, so
       V(r) = -G M m2 / r * [1 + alpha e^{-r/lambda}],
       alpha = g_c^2 / (2 kappa m_chi^4),   lambda = 1 / m_psi,   kappa = 8 pi G.
   The coupling is proportional to mass for a single matter species, so it is
   composition independent: equivalence-principle tests do not see it, while
   inverse-square-law, lunar and planetary tests do.

Natural units (hbar = c = 1). Single-species idealization: real matter has several
species (nucleons, electrons); with one chi all of it couples in proportion to mass.
"""

from __future__ import annotations

from math import cosh, sinh, sqrt

REDUCED_PLANCK_MASS_EV = 2.435e27  # (8 pi G)^{-1/2} in eV
NUCLEON_MASS_EV = 0.9389e9         # mean nucleon mass in eV
HBAR_C_EV_M = 1.973269804e-7       # eV * m


def nonrelativistic_x(rho: float, m_chi2: float) -> float:
    """X = |chi~|^2 carried by matter of energy density rho."""

    if m_chi2 <= 0.0:
        raise ValueError("ordinary matter requires m_chi^2 > 0")
    return rho / m_chi2


def yukawa_alpha(g_c: float, m_chi2: float, kappa: float) -> float:
    """Strength alpha of the portal Yukawa force relative to gravity."""

    if m_chi2 <= 0.0 or kappa <= 0.0:
        raise ValueError("need m_chi^2 > 0 and kappa > 0")
    return g_c * g_c / (2.0 * kappa * m_chi2 * m_chi2)


def g_c_for_alpha(alpha: float, m_chi: float, kappa: float) -> float:
    """Portal coupling g_c (mass dimension 1) that gives Yukawa strength alpha."""

    return m_chi * m_chi * sqrt(2.0 * kappa * alpha)


def yukawa_range_m(m_psi_ev: float) -> float:
    """lambda = hbar c / (m_psi c^2) in metres."""

    return HBAR_C_EV_M / m_psi_ev


def sphere_form_factor(m_psi: float, radius: float) -> float:
    """Exterior Yukawa field of a uniform sphere relative to a point mass: 3 (x cosh x - sinh x) / x^3."""

    x = m_psi * radius
    if x < 1e-4:
        return 1.0 + x * x / 10.0
    return 3.0 * (x * cosh(x) - sinh(x)) / x**3


def exterior_psi_uniform_sphere(r: float, mass: float, radius: float, m_psi: float, g_c: float, m_chi2: float) -> float:
    """Analytic psi outside a uniform sphere of total mass ``mass``."""

    from math import exp, pi

    if r < radius:
        raise ValueError("exterior solution only")
    return g_c * mass / (2.0 * m_chi2) * sphere_form_factor(m_psi, radius) * exp(-m_psi * r) / (4.0 * pi * r)
