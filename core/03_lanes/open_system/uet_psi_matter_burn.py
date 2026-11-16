"""Wave B8: layers 2-3 for the psi field itself, with ordinary matter as its bath.

Wave B7 derived F = T KL(rho || Gibbs), P = T sigma and tau = integral dF / P for a Caldeira-Leggett
mode. Wave B6 showed that in the parent action the only bath psi has is ordinary matter (portal
(1/2) g_c psi |chi|^2). This wave asks what burns and how fast when the bath is that matter.

1. Free psi waves do not burn. A free particle absorbs a mode (omega, k) only if its velocity
   along k equals omega/k (Cherenkov condition). For psi, omega/k = sqrt(1 + m_psi^2/k^2) >= 1 (c = 1),
   and matter is non-relativistic, so the absorptive part
       Im chi_nn(omega, k) ~ (omega/(k sigma)) exp(-(omega/k)^2 / (2 sigma^2))
   is suppressed by at least exp(-1/(2 sigma^2)); for sigma = 1e-4 that is exp(-5e7). At linear order
   psi radiation keeps its free energy: tau -> infinity. (Collisional absorption is second order in
   the matter interactions and is outside this model.)
2. Sourced psi burns. The field a body carries moves through the medium at omega = k . v < k sigma,
   inside the absorptive band. The free energy is the kinetic energy of the relative motion,
   F = M v^2 / 2 (work extractable from body + field against the medium at rest), and
       dF/dt = -P,   P = F_drag(v) v = T sigma_S,
   with sigma_S the entropy the medium gains (energy deposited at temperature T) and P/(T ln 2) the
   bits written. tau = integral M dv / F_drag(v).
3. The B6 drag is linear response. Here it is checked against the exact closed dynamics: each medium
   particle scatters on the body's potential along its true orbit (no small-coupling expansion), and
       F = n m int d^3w f(w) |u| u_par sigma_m(|u|),   u = v - w,
       sigma_m(u) = 2 pi int b db (1 - cos chi(b, u)),
   must reduce to the linear-response formula as the coupling goes to zero.

The check uses a repulsive Gaussian potential U(r) = U0 exp(-r^2/(2 a^2)) so that every integral is
finite; the portal potential differs only in U_k. Units: m = 1, sigma = 1 unless stated.
"""

from __future__ import annotations

import importlib.util
import sys
from math import exp, log, pi, sin, sqrt

import numpy as np
from pathlib import Path

from scipy.integrate import quad
from scipy.optimize import brentq

_B6_PATH = Path(__file__).resolve().parent / "uet_portal_drag_derived.py"
_spec = importlib.util.spec_from_file_location("uet_portal_drag_derived", _B6_PATH)
b6 = sys.modules.setdefault("uet_portal_drag_derived", importlib.util.module_from_spec(_spec))
if not hasattr(b6, "linear_response_drag"):
    _spec.loader.exec_module(b6)


def gaussian_potential(r: float, u0: float, a: float) -> float:
    return u0 * exp(-0.5 * r * r / (a * a))


def gaussian_potential_k2(u0: float, a: float):
    """|U_k|^2 for U(r) = U0 exp(-r^2/2a^2): U_k = U0 (2 pi)^{3/2} a^3 exp(-k^2 a^2 / 2)."""
    return lambda k: (u0 * (2.0 * pi) ** 1.5 * a**3 * exp(-0.5 * k * k * a * a)) ** 2


def deflection_angle(b: float, u: float, u0: float, a: float, m: float = 1.0) -> float:
    """Exact classical deflection chi = pi - 2 b int_{r0}^inf dr / (r^2 sqrt(g)) for a repulsive potential."""
    e = 0.5 * m * u * u

    def g(r: float) -> float:
        return 1.0 - b * b / (r * r) - gaussian_potential(r, u0, a) / e

    if b <= 0.0:
        return 0.0 if e > u0 else pi
    hi = max(b, a) + 10.0 * a + 1.0
    r0 = brentq(g, 1e-12 * b, hi, xtol=1e-15 * b, rtol=1e-15, maxiter=500)
    beta = b / r0

    # chi = 2 int_0^1 dx [1/sqrt(1 - x^2) - beta / sqrt(g(r0/x))], x = r0/r. The free part (pi/2) is
    # subtracted inside the integral so small angles do not cancel; both terms ~ 1/sqrt(1 - x) at x = 1,
    # removed by the algebraic weight.
    def h(x: float) -> float:
        x = min(x, 1.0 - 1e-15)
        if x <= 0.0:
            return 1.0 - beta
        free = sqrt(1.0 - x) / sqrt(1.0 - x * x)
        return free - beta * sqrt(1.0 - x) / sqrt(max(g(r0 / x), 1e-300))

    integral, _ = quad(h, 0.0, 1.0, weight="alg", wvar=(0.0, -0.5), limit=200, epsabs=1e-15, epsrel=1e-12)
    return 2.0 * integral


def deflection_angle_first_order(b: float, u: float, u0: float, a: float, m: float = 1.0) -> float:
    """Impulse approximation chi_1 = -(1/(m u^2)) d/db int U dz (linear in U0)."""
    return u0 * sqrt(2.0 * pi) * (b / a) * exp(-0.5 * b * b / (a * a)) / (m * u * u)


def momentum_transfer_cross_section(u: float, u0: float, a: float, m: float = 1.0, exact: bool = True) -> float:
    chi = deflection_angle if exact else deflection_angle_first_order
    if exact:
        val, _ = quad(lambda b: b * 2.0 * sin(0.5 * chi(b, u, u0, a, m)) ** 2, 0.0, 12.0 * a, limit=200, epsrel=1e-8)
    else:
        val, _ = quad(lambda b: b * 0.5 * chi(b, u, u0, a, m) ** 2, 0.0, 12.0 * a, limit=200, epsrel=1e-10)
    return 2.0 * pi * val


def tabulated_cross_section(u0: float, a: float, u_lo: float, u_hi: float, points: int = 60, m: float = 1.0):
    """Exact sigma_m on a log grid, interpolated as log(u^4 sigma_m) (smooth); below u_lo use u_lo's value."""
    grid = np.geomspace(u_lo, u_hi, points)
    vals = np.array([momentum_transfer_cross_section(u, u0, a, m) * u**4 for u in grid])
    lg, lv = np.log(grid), np.log(vals)

    def sigma_m(u: float) -> float:
        uu = min(max(u, u_lo), u_hi)
        return float(np.exp(np.interp(np.log(uu), lg, lv))) / max(u, 1e-300) ** 4 if u >= u_lo else float(vals[0]) / u_lo**4

    return sigma_m


def momentum_transfer_cross_section_born(u: float, u0: float, a: float, m: float = 1.0) -> float:
    """Closed form of the first-order cross section: pi^2 U0^2 a^2 / (m^2 u^4)."""
    return pi**2 * u0**2 * a**2 / (m**2 * u**4)


def kinetic_drag(sigma_m, v: float, n: float, m: float, sigma: float, u_max_factor: float = 9.0) -> float:
    """F = n m int d^3w f(w) |u| u_par sigma_m(|u|), Maxwellian f with dispersion sigma, u = v - w."""

    def angular(u: float) -> float:
        # int dOmega cos(theta) exp(-(u^2 + v^2 - 2 u v cos)/2 sigma^2), written without overflow
        s = u * v / sigma**2
        base = -0.5 * (u - v) ** 2 / sigma**2  # exp(-(u-v)^2/2s^2) = exp(-(u^2+v^2)/2s^2 + s)
        if s < 1e-4:
            core = (s / 3.0) * exp(-s)  # 2(s cosh s - sinh s)/s^2 ~ 2 s/3, times e^{-s}/2
            return 2.0 * pi * 2.0 * core * exp(base)
        # 2 (s cosh s - sinh s)/s^2 * e^{-s} = [(s - 1) + (s + 1) e^{-2s}] / s^2
        core = ((s - 1.0) + (s + 1.0) * exp(-2.0 * s)) / (s * s)
        return 2.0 * pi * core * exp(base)

    norm = (2.0 * pi * sigma**2) ** -1.5
    upper = v + u_max_factor * sigma
    val, _ = quad(lambda u: u**4 * sigma_m(u) * angular(u), 0.0, upper, limit=300, epsrel=1e-8)
    return n * m * norm * val


def free_wave_absorption_log(omega_over_k: float, sigma_over_c: float) -> float:
    """ln of the Landau absorption factor exp(-(omega/k)^2 / (2 sigma^2)) for a free psi wave."""
    return -0.5 * (omega_over_k / sigma_over_c) ** 2


def burn_power(force: float, v: float) -> float:
    return force * v


def bits_per_second(power_w: float, temperature_k: float) -> float:
    return power_w / (b6.K_BOLTZMANN * temperature_k * log(2.0))


def lifetime_by_integration(drag, mass: float, v0: float, v_min: float) -> float:
    """tau = int_{v_min}^{v0} M dv / F(v), i.e. integral dF / P with F = M v^2 / 2 and P = F_drag v."""
    val, _ = quad(lambda v: mass / drag(v), v_min, v0, limit=200)
    return val
