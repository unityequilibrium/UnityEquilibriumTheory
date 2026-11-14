"""Cross-layer candidate for a UET-distinct effect (wave B4): portal drag.

Layer 1 (chi = ordinary matter) makes every body a source of psi through the portal.
Layer 2 says an open field burns energy into its environment: applied to psi itself,
the field equation gains a friction term in the environment rest frame u:

    box psi - m_psi^2 psi = Gamma u.d psi - (g_c / (2 m_chi^2)) rho

A body moving at speed v (v << 1) through that frame carries its field along, so
d_t psi = -v . grad psi and the burned power is

    P = Gamma integral (d_t psi)^2 dV = Gamma v^2 (1/3) integral |grad psi|^2 dV

For a sphere of radius R with exterior Yukawa field psi = q e^{-m r}/(4 pi r),
q = g_c M / (2 m_chi^2), and m R << 1, the exterior integral is q^2/(4 pi R), so

    F_drag = P / v = Gamma v q^2 / (12 pi R)

Neither GR nor the standard model of matter has this term: it is a velocity-dependent
drag relative to a preferred frame (the environment rest frame). Its size is set by
three free parameters (g_c, Gamma, m_psi), so without an author commitment on their
values it can only be bounded, not predicted.

Natural units. Leading order in v and in Gamma (field profile taken from the static solution).
"""

from __future__ import annotations

from math import exp, pi

from scipy.integrate import quad


def portal_charge(g_c: float, mass: float, m_chi2: float) -> float:
    return g_c * mass / (2.0 * m_chi2)


def exterior_gradient_energy(q: float, radius: float, m_psi: float) -> float:
    """integral_{r > R} |grad psi|^2 dV for psi = q e^{-m r}/(4 pi r)."""

    def integrand(r: float) -> float:
        dpsi = q * exp(-m_psi * r) * (1.0 + m_psi * r) / (4.0 * pi * r * r)
        return dpsi * dpsi * 4.0 * pi * r * r

    value, _ = quad(integrand, radius, float("inf"), limit=200)
    return value


def drag_force(gamma: float, v: float, q: float, radius: float, m_psi: float) -> float:
    """Leading-order drag F = Gamma v (1/3) integral |grad psi|^2 dV (exterior field only)."""

    return gamma * v * exterior_gradient_energy(q, radius, m_psi) / 3.0


def drag_force_light_limit(gamma: float, v: float, q: float, radius: float) -> float:
    return gamma * v * q * q / (12.0 * pi * radius)
