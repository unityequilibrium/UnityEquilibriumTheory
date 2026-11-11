"""Observation layer, wave O4: the parent-action scalar field propagates inside the light cone.

In the canonical variables of Theory Card UET_PARENT v1 (docs/core/THEORY_CARD.md section 3) the response
scalar psi obeys, on a flat background and to linear order,

    (d_t^2 - d_x^2 + m_psi^2) psi = S(t, x)            (1+1 dimensions here)

whose retarded Green function is

    G_R(t, x) = (1/2) theta(t - |x|) J0( m sqrt(t^2 - x^2) ),

supported only inside the future light cone. A source switched on as an initial velocity g(x) gives
psi(t, x) = integral G_R(t, x - y) g(y) dy.

Three references for the same solution are used in the tests:
  * exact retarded solution through J0 (Gauss-Legendre quadrature over the cone);
  * massless d'Alembert solution through error functions (m = 0 limit, independent closed form);
  * a leapfrog finite-difference solution of the PDE itself (the general path under test).
The quasi-static (instantaneous screened-Poisson) response is the acausal alternative used as a negative control.

Units: c = 1.
"""

from __future__ import annotations

from math import sqrt

import numpy as np
from scipy.special import erf, erfc, j0

SQRT2 = sqrt(2.0)
SQRT_2PI = sqrt(2.0 * np.pi)


def gaussian(x, sigma: float):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * (x / sigma) ** 2) / (sigma * SQRT_2PI)


def retarded_green_1d(t: float, x, mass: float):
    x = np.asarray(x, dtype=float)
    inside = np.abs(x) < t
    arg = np.where(inside, t * t - x * x, 0.0)
    return np.where(inside, 0.5 * j0(mass * np.sqrt(arg)), 0.0)


def exact_response(t: float, x, mass: float, sigma: float, nodes: int = 400):
    """psi(t, x) = integral_{-t}^{t} G_R(t, u) g(x - u) du by Gauss-Legendre (smooth integrand)."""

    x = np.atleast_1d(np.asarray(x, dtype=float))
    u, w = np.polynomial.legendre.leggauss(nodes)
    u, w = t * u, t * w
    green = 0.5 * j0(mass * np.sqrt(np.maximum(t * t - u * u, 0.0)))
    return np.array([float(np.sum(w * green * gaussian(xi - u, sigma))) for xi in x])


def massless_dalembert(t: float, x, sigma: float):
    """psi = (1/2) integral_{x-t}^{x+t} g = (1/4)[erf((x+t)/(sigma sqrt2)) - erf((x-t)/(sigma sqrt2))]."""

    x = np.asarray(x, dtype=float)
    return 0.25 * (erf((x + t) / (sigma * SQRT2)) - erf((x - t) / (sigma * SQRT2)))


def instantaneous_screened_response(x, mass: float, sigma: float):
    """Acausal quasi-static response: solution of (-d_x^2 + m^2) psi = g at every time (Gaussian * e^{-m|x|}/2m)."""

    x = np.asarray(x, dtype=float)
    a = mass * sigma * sigma
    return np.exp(0.5 * (mass * sigma) ** 2) / (4.0 * mass) * (
        np.exp(-mass * x) * erfc((a - x) / (sigma * SQRT2)) + np.exp(mass * x) * erfc((a + x) / (sigma * SQRT2)))


def leapfrog_response(mass: float, sigma: float, dx: float, t_end: float, half_width: float, courant: float = 0.5):
    """Second-order leapfrog solution of (d_t^2 - d_x^2 + m^2) psi = 0 with psi(0) = 0, d_t psi(0) = g.

    Returns (x, psi at t_end). The first step uses the Taylor expansion through third order so the whole
    scheme stays second order.
    """

    n = int(round(2.0 * half_width / dx))
    x = -half_width + dx * np.arange(n + 1)
    dt = courant * dx
    steps = int(round(t_end / dt))
    dt = t_end / steps
    v0 = gaussian(x, sigma)

    def laplacian(f):
        out = np.zeros_like(f)
        out[1:-1] = (f[2:] - 2.0 * f[1:-1] + f[:-2]) / dx**2
        return out

    psi_prev = np.zeros_like(x)
    # psi(dt) = dt v0 + dt^3/6 (v0_xx - m^2 v0)   [psi(0) = 0, psi_tt(0) = 0]
    psi = dt * v0 + dt**3 / 6.0 * (laplacian(v0) - mass**2 * v0)
    for _ in range(steps - 1):
        psi_next = 2.0 * psi - psi_prev + dt**2 * (laplacian(psi) - mass**2 * psi)
        psi_prev, psi = psi, psi_next
    return x, psi
