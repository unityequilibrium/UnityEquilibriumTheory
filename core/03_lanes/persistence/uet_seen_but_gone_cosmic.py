"""Layer 3, wave S3: of the sources we see, how much still exists, in an expanding universe?

Question (follows S2, which used static Euclidean space): on the past light cone of flat
Lambda-CDM, a source seen at comoving distance chi emitted its light at cosmic time t_e(chi), a
look-back time t_L = t0 - t_e ago. With layer-3 lifetime tau = F/P, what fraction of the sources seen
out to a given depth still exists now, and what changes because the universe has a finite age?

Setting. Flat Lambda-CDM (radiation neglected) with a(t) and Planck 2018 parameters taken from wave
D6 (`uet_cosmic_divider`). Sources are born at a constant rate per unit comoving volume and cosmic
time from t = 0 on (an AI choice: real star formation peaked near z ~ 2). Fixed lifetime tau. Units:
Gyr and Gly (c = 1).

[AI derivation]
S3a Sources alive at emission time t_e have birth times t_b in [max(0, t_e - tau), t_e], so the
    comoving density seen on the shell at t_e is n_seen ~ b min(tau, t_e). A seen source is still
    alive at t0 iff t_b > t0 - tau, so the alive density is b max(0, min(t_e, tau - t_L)).
S3b The comoving shell volume is 4 pi chi^2 dchi with dchi = dt_e / a(t_e). The alive fraction of all
    sources seen with t_e >= t_min (a depth cut) is
        A = int chi^2 a^-1 max(0, min(t_e, tau - t_L)) dt_e / int chi^2 a^-1 min(tau, t_e) dt_e.
S3c Limits. Near the observer (t_L << t0, tau < t0) t_L ~ chi and S3b reduces to S2:
    A -> 1 - 3 lambda/4 with lambda = chi_max/tau. If tau >= t0, nobody born since t = 0 has died
    yet, so A = 1 exactly at every depth: a finite age caps the ghosts. Static space has no such cap.
S3d Numbers (whole light cone; the lifetimes are illustrative AI choices; t0 = 13.80 Gyr, comoving
    horizon 47.0 Gly without radiation): alive fraction 3.9e-9 for tau = 0.1 Gyr, 7.9e-6 for 1 Gyr,
    4.7e-4 for 3 Gyr, 0.107 for 10 Gyr, 0.558 for 13 Gyr, 1 for tau >= t0. Static space (S2 with
    lambda = 47.0/tau) gives 2.4e-3 for tau = 10 Gyr, 44 times fewer survivors: the finite age
    removes the oldest light, whose sources would be the most certainly gone. Out to z = 1 only
    (chi = 11.1 Gly): 2.0e-4 for 1 Gyr and 0.494 for 10 Gyr.

Nearest known theory: look-back time and comoving volume in Lambda-CDM (for example Hogg 1999,
"Distance measures in cosmology"). Not UET-distinct. Left out: evolving birth rate, random
lifetimes, flux limits with K-corrections, radiation era, extinction.
"""

from __future__ import annotations

import importlib
from math import asinh, sinh, sqrt

import numpy as np
from scipy.integrate import quad

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")

GYR = 1e9 * cd.YEAR
H_L_GYR = cd.H_L * GYR          # Lambda-era Hubble rate in 1/Gyr
RATIO = cd.OMEGA_M / cd.OMEGA_L


def a_of_t(t: float) -> float:
    """Scale factor at cosmic time t (Gyr), closed form of wave D6."""

    return RATIO ** (1.0 / 3.0) * sinh(1.5 * H_L_GYR * t) ** (2.0 / 3.0)


def age() -> float:
    return 2.0 / (3.0 * H_L_GYR) * asinh(sqrt(1.0 / RATIO))


T0 = age()


def comoving_distance(t_e: float) -> float:
    """chi(t_e) = int_{t_e}^{t0} dt / a(t) in Gly, with t = s^3 to remove the t^(-2/3) end point."""

    s0, s1 = t_e ** (1.0 / 3.0), T0 ** (1.0 / 3.0)
    value, _ = quad(lambda s: 3.0 * s * s / a_of_t(s ** 3), s0, s1, epsabs=0.0, epsrel=1e-12, limit=200)
    return value


def seen_weight(t_e: float, tau: float) -> float:
    return min(tau, t_e)


def alive_weight(t_e: float, tau: float) -> float:
    return max(0.0, min(t_e, tau - (T0 - t_e)))


def _shell_integral(weight, t_min: float, tau: float) -> float:
    s_min, s_max = t_min ** (1.0 / 3.0), T0 ** (1.0 / 3.0)
    pts = [p ** (1.0 / 3.0) for p in (tau, T0 - tau, (T0 - tau) / 2.0) if t_min < p < T0]

    def f(s):
        t = s ** 3
        chi = comoving_distance(t)
        return chi * chi / a_of_t(t) * weight(t, tau) * 3.0 * s * s

    value, _ = quad(f, s_min, s_max, points=pts or None, epsabs=0.0, epsrel=1e-10, limit=400)
    return value


def alive_fraction(t_min: float, tau: float) -> float:
    """Fraction of seen sources with emission time t_e >= t_min that still exist at t0."""

    return _shell_integral(alive_weight, t_min, tau) / _shell_integral(seen_weight, t_min, tau)


def whole_cone_table(taus=(0.01, 0.1, 1.0, 3.0, 10.0, 13.0)) -> dict:
    return {tau: alive_fraction(0.0, tau) for tau in taus}


def simulate_light_cone(tau: float, t_min: float, n_sources: int, rng: np.random.Generator):
    """Independent route: comoving positions uniform in the ball out to chi(t_min), birth times
    uniform in [0, t0]; t_e(chi) from an interpolated table of chi(t). A source is seen if it existed
    when its light left (t_b <= t_e < t_b + tau) and alive if t_b + tau > t0."""

    grid = np.linspace(t_min, T0, 4001)
    chi_grid = np.array([comoving_distance(t) for t in grid])   # decreasing in t
    R = chi_grid[0]
    r = R * rng.random(n_sources) ** (1.0 / 3.0)
    t_e = np.interp(r, chi_grid[::-1], grid[::-1])
    t_b = T0 * rng.random(n_sources)
    seen = (t_b <= t_e) & (t_e < t_b + tau)
    alive = seen & (t_b + tau > T0)
    return int(seen.sum()), int(alive.sum())
