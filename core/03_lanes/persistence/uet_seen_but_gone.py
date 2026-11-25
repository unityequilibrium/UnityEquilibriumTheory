"""Layer 3, wave S2: of the sources we see, what fraction is still alive now?

Question (follows O5 and S1): light from a source at distance r left it r/c ago. Layer 3 gives each
source a finite life tau = F/P. A survey sees sources out to d = sqrt(L / (4 pi f)) with L = eps P
(wave S1). What fraction of the sources in a flux-limited sample still exists at the moment we
look, and how does it depend on the burn rate P?

Setting. Births at constant rate b per unit volume and time (steady state), fixed lifetime tau,
sources uniform in D dimensions, Euclidean and static space, light travel time r/c, no extinction.

[AI derivation]
S2a A source seen at r is one that was alive at t0 - r/c. In steady state its age a at that moment
    is uniform on [0, tau). It is still alive at t0 iff a + r/c < tau, so
        p_alive(r) = max(0, 1 - r/(c tau)).
    The number seen at r is unchanged by the delay (steady state): the delay changes which
    sources are seen, not how many.
S2b With lambda = d/(c tau) and the D-dimensional weight D r^(D-1)/d^D on [0, d], the fraction of
    the sample still alive is
        A_D(lambda) = 1 - D lambda/(D + 1)              for lambda <= 1,
        A_D(lambda) = lambda^(-D) / (D + 1)              for lambda >= 1.
    The two branches meet at lambda = 1 with value 1/(D + 1) and equal slope -D/(D + 1).
S2c With layer-3 burning, d ~ (eps P)^(1/2) and tau = F/P, so lambda ~ eps^(1/2) P^(3/2) / F:
    the faster burner is seen farther AND dies sooner. Illustrative AI choice (D = 3, the two types
    of S1): if the slow burner has lambda = 0.01, the type burning 100 times faster has
    lambda = 10. The slow type's sample is 99.25 % alive; the fast type's is 2.5e-4 alive, so the
    sample that S1 showed to be dominated by fast burners is 99.975 % already gone.
S2d Seen-and-alive count: N_alive = n V_D d^D A_D. For lambda >= 1 this is n V_D (c tau)^D/(D + 1)
    (V_D the unit-ball volume), which no longer depends on the flux limit: once a survey reaches
    past c tau, going deeper adds only sources that are already gone.

Consequence for the author's statement "what we see is what was still alive when the light left"
[AI interpretation]: the light certifies that the source was alive then, not now. Whether it is
alive now depends on lambda, a number set by the source's own burn (P, F, eps) and the survey
depth, not by the observer alone.

Nearest known theory: light-travel-time (look-back) arguments for stars and quasars, and the
steady-state "duty cycle" argument for short-lived sources; this is the Euclidean, steady-state
version. Not UET-distinct. Left out: cosmological expansion and redshift, evolving birth rates,
random lifetimes, extinction, and the source's motion during the delay.
"""

from __future__ import annotations

from math import pi, sqrt

import numpy as np
from scipy.integrate import quad


def detection_distance(L: float, flux_limit: float) -> float:
    return sqrt(L / (4.0 * pi * flux_limit))


def alive_probability(r: float, c: float, tau: float) -> float:
    """Probability that a source seen at distance r still exists now (fixed lifetime, steady state)."""

    return max(0.0, 1.0 - r / (c * tau))


def alive_fraction_numeric(d: float, c: float, tau: float, D: int) -> float:
    """General path: average p_alive over the D-dimensional surveyed volume out to d."""

    edge = min(d, c * tau)
    num, _ = quad(lambda r: D * r ** (D - 1) * alive_probability(r, c, tau), 0.0, edge,
                  epsabs=0.0, epsrel=1e-13, limit=200)
    return num / d ** D


def alive_fraction_closed_form(lam: float, D: int) -> float:
    if lam <= 1.0:
        return 1.0 - D * lam / (D + 1.0)
    return lam ** (-D) / (D + 1.0)


def depth_ratio(P: float, F: float, eps: float, flux_limit: float, c: float) -> float:
    """lambda = d / (c tau) for a layer-3 source with L = eps P and tau = F / P."""

    return detection_distance(eps * P, flux_limit) / (c * F / P)


def simulate_light_cone(n_birth: float, tau: float, c: float, d: float, D: int, R: float,
                        T: float, rng: np.random.Generator):
    """Independent route: Poisson births in space-time (positions uniform in a D-ball of radius R,
    birth times uniform in [-T, 0]); the observer at the origin at t0 = 0 sees a source at r if it
    existed when its light left (t_b <= -r/c < t_b + tau) and r <= d. Returns (number seen, number
    of those still alive at t0 = 0)."""

    from math import gamma
    V_ball = pi ** (D / 2.0) / gamma(D / 2.0 + 1.0) * R ** D
    k = rng.poisson(n_birth * V_ball * T)
    r = R * rng.random(k) ** (1.0 / D)
    t_b = -T * rng.random(k)
    emitted = -r / c
    seen = (r <= d) & (t_b <= emitted) & (emitted < t_b + tau)
    alive = seen & (t_b + tau > 0.0)
    return int(seen.sum()), int(alive.sum())
