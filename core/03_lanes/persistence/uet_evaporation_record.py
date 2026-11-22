"""Layer 2 -> 3, wave D9: one mass that disappears completely - what keeps the record, space or not?

Question (author, 2026-11-22): model a universe with one mass that dissolves completely, in space
of the first kind only (the AI mapping: Lambda, de Sitter), and keep apart "space" and "the record".
When the mass is gone, does space remember it? Where is the record, and does it stay?

Model. One Schwarzschild black hole of mass M0 in de Sitter space with H = H_L (wave D6). It emits
photon-only Hawking radiation P_H = hbar c^6/(15360 pi G^2 M^2) (wave D5) and absorbs the horizon
bath at T_dS through its area, so
    c^2 dM/dt = -P_H(M) + sigma A(M) T_dS^4 = -(a c^2 / M^2) (1 - (M/M_eq)^4),
with a = hbar c^4/(15360 pi G^2) and M_eq the mass with T_H = T_dS (5.6e52 kg, wave D6).
Frame caveat (author, 2026-11-22): T_H is the temperature seen by a distant static observer, T_dS
the one seen by a freely falling observer; Schwarzschild-de Sitter has no single observer for whom
both are equilibrium temperatures. The model adds them as fluxes, a standard but frame-mixed step.

[AI derivation]
D9a Lifetime. With x0 = M0/M_eq < 1,
        tau = M_eq^3 (atanh x0 - atan x0) / (2 a)  ->  M0^3 / (3 a) = F0/(3 P0)  for x0 -> 0,
    the same function as the cooling law of wave D7. A hole at or above M_eq never disappears.
D9b The record leaves. A photon emitted from the hole at t_e is at proper distance
    (c/H)(exp(H (t - t_e)) - 1), so it passes the hole's own horizon c/H after ln2/H = 12.1 Gyr and
    never returns; its energy measured by comoving observers falls as exp(-H (t - t_e)).
D9c Space does not keep a wave memory. The gravitational-wave memory of an energy flux dE/dOmega is
    Delta h_ij^TT = (4G/(c^4 r)) int dE/dOmega' [n'_i n'_j / (1 - n'.N)]^TT dOmega'
    (Wiseman and Will 1991; Thorne 1992). For isotropic Hawking emission (any flux symmetric about
    the line of sight) it is exactly zero; for a two-sided jet it is not. Outside the outgoing shell
    the metric is Schwarzschild-de Sitter with the mass still inside; behind it, pure de Sitter
    (Birkhoff's theorem with Lambda): once the radiation has passed, space is as if the hole had
    never been there.
D9d The record that stays is in clocks, which are matter. A clock held at radius r >> r_s ran slow
    by G M(t)/(r c^2) for the whole life of the hole; afterwards it stays behind a distant clock by
        Delta tau(r) = (G / (r c^2)) int M dt = -(G M_eq^4 / (4 a r c^2)) ln(1 - x0^4)
                     -> (3/4) (G M0/(r c^2)) tau   for x0 -> 0.
D9e Numbers (illustrative AI choice M0 = 1e12 kg): tau = 2.7e12 yr; a clock at 1 m has lost
    (3/4) G M0/c^2 per metre of radius times tau, 5.6e-16 of the lifetime, 1.5e-3 yr.

Consequence [AI interpretation]: in the space-only universe, space (first kind) returns exactly to
what it was; the record of the mass is (1) the radiation, which leaves every local region after
ln2/H and redshifts, and (2) the lag of any clock that was near it, which needs matter to exist.
This supports the author's 2026-11-22 split: space and record are different things. In the real
universe (second kind present), the radiation is absorbed by other matter and stays there as heat,
the CMB must first cool below T_H (wave D5/D6), and anisotropic events (mergers, wave D8) do leave a
wave memory in the geometry.

Nearest known theory: Hawking evaporation, Schwarzschild-de Sitter, Birkhoff's theorem,
gravitational-wave memory, gravitational time dilation. Not UET-distinct. Left out: greybody
factors and other species, back-reaction near the end of evaporation, the information problem,
the Nariai limit, quantum memory effects.
"""

from __future__ import annotations

import importlib
from math import exp, log, pi, sqrt

import numpy as np
from scipy.integrate import dblquad, quad, solve_ivp

bh = importlib.import_module("docs.core.03_lanes.persistence.uet_black_hole_divider")
cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")
lb = importlib.import_module("docs.core.03_lanes.persistence.uet_lone_body_horizon")

G, C_LIGHT, HBAR, YEAR = bh.G_NEWTON, bh.C_LIGHT, bh.HBAR, bh.YEAR
H_L = cd.H_L
A_EVAP = HBAR * C_LIGHT ** 4 / (15360.0 * pi * G ** 2)      # kg^3 / s
M_EQ = cd.largest_mass_that_evaporates(H_L)


def mass_rate(M: float, M_eq: float = M_EQ) -> float:
    """dM/dt from the two fluxes, built from the general D5 power and sigma A T^4."""

    A = 16.0 * pi * G ** 2 * M ** 2 / C_LIGHT ** 4
    T_bath = bh.hawking_temperature(M_eq).real
    return (-bh.hawking_power(M) + lb.SIGMA_SB * A * T_bath ** 4) / C_LIGHT ** 2


def lifetime_closed_form(M0: float, M_eq: float = M_EQ) -> float:
    return M0 ** 3 * lb._h(M0 / M_eq) / (2.0 * A_EVAP)


def lifetime_numeric(M0: float, M_eq: float = M_EQ) -> float:
    value, _ = quad(lambda M: -1.0 / mass_rate(M, M_eq), 0.0, M0, epsabs=0.0, epsrel=1e-12, limit=400)
    return value


def mass_time_integral_closed_form(M0: float, M_eq: float = M_EQ) -> float:
    """int M dt over the life = -(M_eq^4/(4a)) ln(1 - x0^4), evaluated with log1p for small x0."""

    x4 = (M0 / M_eq) ** 4
    return -M_eq ** 4 / (4.0 * A_EVAP) * np.log1p(-x4)


def mass_time_integral_ode(M0: float, M_eq: float = M_EQ) -> float:
    """Second route: integrate u = M^3 (du/dt = 3 M^2 dM/dt, smooth to the end) together with
    int M dt, from the general flux balance mass_rate, until the mass is gone."""

    tau = lifetime_closed_form(M0, M_eq)

    def rhs(_t, y):
        M = max(y[0], 0.0) ** (1.0 / 3.0)
        dudt = 3.0 * M * M * mass_rate(M, M_eq) if M > 0 else -3.0 * A_EVAP
        return [dudt, M]

    gone = lambda _t, y: y[0]  # noqa: E731
    gone.terminal = True
    sol = solve_ivp(rhs, (0.0, 1.5 * tau), [M0 ** 3, 0.0], events=gone, method="DOP853",
                    rtol=1e-12, atol=[M0 ** 3 * 1e-15, M0 * tau * 1e-15])
    return float(sol.y_events[0][0][1])


def clock_lag(M0: float, r: float, M_eq: float = M_EQ) -> float:
    return G / (r * C_LIGHT ** 2) * mass_time_integral_closed_form(M0, M_eq)


def photon_proper_distance(dt: float, H: float = H_L) -> float:
    return C_LIGHT / H * (exp(H * dt) - 1.0)


def photon_proper_distance_numeric(dt: float, H: float = H_L) -> float:
    """General path: comoving distance int c/a dt with a = exp(H t), times a(dt)."""

    chi, _ = quad(lambda t: C_LIGHT * exp(-H * t), 0.0, dt, epsabs=0.0, epsrel=1e-13)
    return exp(H * dt) * chi


def record_leaves_after(H: float = H_L) -> float:
    return log(2.0) / H


def memory_tensor(flux, N=(0.0, 0.0, 1.0)) -> np.ndarray:
    """int flux(n') [n' n' / (1 - n'.N)]^TT dOmega' (units of the flux), TT with respect to N.
    The TT projection is taken inside the integral, where it removes the 1/(1 - n'.N) singularity."""

    N = np.asarray(N, float)
    P = np.eye(3) - np.outer(N, N)
    out = np.zeros((3, 3))
    for i in range(3):
        for j in range(i, 3):
            def f(phi, theta, i=i, j=j):
                n = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
                nt = P @ n
                tt = np.outer(nt, nt) - 0.5 * P * (nt @ nt)
                return flux(n) * tt[i, j] / (1.0 - n @ N) * np.sin(theta)
            val, _ = dblquad(f, 0.0, pi, 0.0, 2.0 * pi, epsabs=1e-11, epsrel=1e-10)
            out[i, j] = out[j, i] = val
    return out


def beam_memory(n0, N=(0.0, 0.0, 1.0)) -> np.ndarray:
    """Narrow-beam limit: [n0 n0]^TT / (1 - n0.N) per unit beam energy."""

    n0 = np.asarray(n0, float) / np.linalg.norm(n0)
    N = np.asarray(N, float)
    P = np.eye(3) - np.outer(N, N)
    nt = P @ n0
    return (np.outer(nt, nt) - 0.5 * P * (nt @ nt)) / (1.0 - n0 @ N)


def unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    return v / sqrt(v @ v)
