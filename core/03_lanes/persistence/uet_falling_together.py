"""Layer 2 -> 3, wave D8 (model B): many bodies falling together - frying and mixing.

Question (author, 2026-11-22): bodies do not fall alone; they fall together, pile up in one place
(mixing, "คลุก") and rub against each other on the way (frying, "ผัด"). How much energy and entropy
does each step move, who divides whose entropy, and is mass lost?

Standard inputs. Frying between masses is dynamical friction (Chandrasekhar 1943): a body of mass M
moving at v through a sea of light bodies (mass m, density rho, Maxwellian dispersion sigma) feels
    dv/dt = -4 pi G^2 M rho lnL / v^2 * f(X),   X = v / (sqrt(2) sigma),
where f(X) is the fraction of the sea slower than v, f = erf X - (2X/sqrt(pi)) exp(-X^2). The sea is
a singular isothermal sphere, rho = sigma^2/(2 pi G r^2), circular speed v_c = sqrt(2) sigma (X = 1).
Mixing of two black holes obeys the area theorem (Hawking 1971): horizon area, so S ~ M^2 for
non-spinning holes, cannot decrease. A test mass on circular Schwarzschild orbits has specific
energy E/(mu c^2) = (1 - 2x)/sqrt(1 - 3x), x = GM/(r c^2), with the innermost stable orbit at x = 1/6.

[AI derivation]
D8a Frying: on a circular orbit the angular momentum r v_c is lost at r F, so r dr/dt =
    -f(1) G M lnL / v_c and the sinking time from r_i is
        t_fry = r_i^2 v_c / (2 f(1) G M lnL) = 1.17 r_i^2 v_c / (G M lnL),   f(1) = 0.4276.
D8b Who divides: the orbit loses E = M v_c^2 ln(r_i/r_f) (isothermal potential) to the sea, whose
    kinetic temperature is k T_sea = m sigma^2. Entropy given to the sea:
        dS/k = M v_c^2 ln(r_i/r_f) / (m sigma^2) = 2 (M/m) ln(r_i/r_f).
    The heavy body's "temperature" M v_c^2 is 2 M/m times the sea's, so energy flows from the heavy
    body into the light ones: the sea is the divider of the heavy body.
D8c Mixing loses mass, within bounds. Inspiral down to the innermost stable orbit radiates at
    least 1 - sqrt(8/9) = 5.72 % of mu c^2 (test-mass limit; mu = m1 m2/(m1+m2)); the area theorem
    caps the total at 1 - sqrt(m1^2 + m2^2)/(m1 + m2), 29.3 % of the total mass for equal masses.
    Equal masses: at least 1.43 % and at most 29.3 % of (m1 + m2) c^2 leaves as gravitational waves.
D8d Mixing makes the entropy. For equal non-spinning holes losing a fraction eps of their mass,
    S_f/S_i = 2 (1 - eps)^2: 1.94 at the inspiral bound, 1 (no gain) at the area-theorem cap.
    The radiated wave is coherent, so it carries energy with almost no entropy [AI inference]: what
    leaves the pile is an ordered record (compare T010), while the disorder stays in the horizon.
D8e Illustrative AI choice (M = 1e6 M_sun, m = 1 M_sun, r_i = 1 kpc -> r_f = 10 pc, v_c = 220 km/s,
    lnL = 10): frying takes 5.9 Gyr and gives the sea 9.2e6 k; merging two such holes (eps = 5 %)
    adds about 1.7e89 k. Mixing out-produces frying by about 82 orders of magnitude.

Nearest known theory: Chandrasekhar dynamical friction (Binney and Tremaine, Galactic Dynamics,
section 8.1), Hawking area theorem, Schwarzschild circular orbits. Not UET-distinct. Left out:
spin, eccentric orbits, the sea's own negative heat capacity (wave D4), tidal stripping, numerical
relativity of the final plunge, and any friction with space itself (portal drag).
"""

from __future__ import annotations

import importlib
from math import erf, exp, log, pi, sqrt

from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")
G, C_LIGHT, M_SUN, K_B, HBAR = cd.G_NEWTON, cd.C_LIGHT, cd.M_SUN, cd.K_B, cd.HBAR
KPC = 1e3 * cd.MPC / 1e6
GYR = 1e9 * cd.YEAR


def slower_fraction_closed_form(X: float) -> float:
    return erf(X) - 2.0 * X / sqrt(pi) * exp(-X * X)


def slower_fraction_numeric(X: float) -> float:
    """General path: fraction of a 3-D Maxwellian (speeds in units of sqrt(2) sigma) below X."""

    value, _ = quad(lambda u: 4.0 / sqrt(pi) * u * u * exp(-u * u), 0.0, X, epsabs=0.0, epsrel=1e-13)
    return value


def friction_force(M: float, v: float, sigma: float, rho: float, lnL: float) -> float:
    X = v / (sqrt(2.0) * sigma)
    return 4.0 * pi * G * G * M * M * rho * lnL / (v * v) * slower_fraction_numeric(X)


def sinking_time_closed_form(M: float, r_i: float, v_c: float, lnL: float, r_f: float = 0.0) -> float:
    return (r_i ** 2 - r_f ** 2) * v_c / (2.0 * slower_fraction_closed_form(1.0) * G * M * lnL)


def sinking_time_ode(M: float, r_i: float, v_c: float, lnL: float, r_f: float) -> float:
    """Second route: integrate dL/dt = -r F with L = M r v_c in the isothermal sphere."""

    sigma = v_c / sqrt(2.0)

    def rhs(_t, y):
        r = y[0]
        rho = sigma ** 2 / (2.0 * pi * G * r * r)
        return [-r * friction_force(M, v_c, sigma, rho, lnL) / (M * v_c)]

    hit = lambda _t, y: y[0] - r_f  # noqa: E731
    hit.terminal = True
    t_guess = 2.0 * sinking_time_closed_form(M, r_i, v_c, lnL)
    sol = solve_ivp(rhs, (0.0, t_guess), [r_i], events=hit, rtol=1e-11, atol=r_f * 1e-12, method="DOP853")
    return float(sol.t_events[0][0])


def entropy_to_sea(M: float, m: float, r_i: float, r_f: float, v_c: float) -> float:
    """dS/k = orbital energy lost / (m sigma^2)."""

    sigma = v_c / sqrt(2.0)
    return M * v_c ** 2 * log(r_i / r_f) / (m * sigma ** 2)


def circular_energy(x: float) -> float:
    return (1.0 - 2.0 * x) / sqrt(1.0 - 3.0 * x)


def isco_x_numeric() -> float:
    """General path: the innermost stable orbit is where the circular energy E(x) is lowest."""

    res = minimize_scalar(lambda x: circular_energy(x), bounds=(0.05, 0.3), method="bounded",
                          options={"xatol": 1e-12})
    return float(res.x)


def inspiral_fraction_of_mu() -> float:
    return 1.0 - circular_energy(isco_x_numeric())


def area_theorem_cap(m1: float, m2: float) -> float:
    return 1.0 - sqrt(m1 * m1 + m2 * m2) / (m1 + m2)


def hole_entropy(M: float) -> float:
    """Bekenstein-Hawking entropy in units of k: 4 pi G M^2 / (hbar c)."""

    return 4.0 * pi * G * M * M / (HBAR * C_LIGHT)


def merger_entropy_ratio(eps: float) -> float:
    return 2.0 * (1.0 - eps) ** 2
