"""Layer 3, wave S1: what we see is selected by brightness, not only by persistence.

Question (stress test of AUTHOR_PROPOSITION item 5 and the author's 2026-11-17 statement "what we
see is what was still alive when the light left"): layer 3 says that in steady state the abundance
of a type is n = b tau = b F/P, so slow burners (low P) are the most common. But a survey sees a
source only if its light is bright enough, and light comes from burning. Does the observed sample
show the persistence ranking, or the opposite?

Setting. Types i are born at rate b_i per unit volume, live tau_i = F_i/P_i, and emit a detectable
luminosity L_i = eps_i P_i (eps_i <= 1 is the part of the burn that leaves as light the survey sees).
Sources fill space uniformly in D dimensions (D = 3: a sphere of stars; D = 2: a thin disk seen from
inside beyond its thickness; D = 1: a line). A survey detects flux above f, so a source is seen out
to d_i = sqrt(L_i / (4 pi f)) and the surveyed "volume" is V_i ~ d_i^D ~ L_i^(D/2).

[AI derivation]
S1  Observed counts N_i = n_i V_i ~ b_i F_i eps_i^(D/2) P_i^(D/2 - 1).
    D = 3: N ~ b F eps^1.5 P^0.5. The persistence advantage 1/P is overturned: at equal b, F, eps the
    faster burner is seen more, although it is rarer. A type with 100 times the burn is 100 times
    rarer in space but 10 times more common in the sample.
    D = 2: N ~ b F eps, independent of P: the two selections cancel.
    D = 1: N ~ b F eps^0.5 P^-0.5: persistence still wins, weakened.
S2  The true abundance is recovered by weighting each detected source by 1/V_max(L) (Schmidt 1968):
    sum over detections of 1/V_i = n_i exactly in expectation.
S3  Consequence for layer-3 tests. A count can test N = b tau only if the sample is volume-limited,
    weighted by 1/V_max, or drawn from sources at one distance. T002 (stars in one globular cluster,
    one distance) is not affected by S1. T008 is not affected either: Hu, Wu and Wu (2007) bin-correct
    for selection effects and weight each white dwarf by 1/(V_max - V_min) (checked 2026-11-21).
    Any future test that counts sources at many distances must say how it removes S1.
S4  Consequence for the author's statement. "What we see is what persisted" needs one more filter:
    what we see is what persisted AND what spent enough energy as light to reach us. The best
    resource managers (low P, low eps) are the hardest to see. [AI interpretation]

Nearest known theory: Malmquist bias (1922) and the 1/V_max estimator (Schmidt 1968); the classic
example is that red dwarfs are most of the stars in the solar neighbourhood but none is visible to
the naked eye. Not UET-distinct. Left out: extinction, cosmological distances (past light cone and
redshift), detection that depends on spectrum rather than total light, and finite survey depth in a
disk of finite thickness.
"""

from __future__ import annotations

from math import gamma, pi, sqrt

import numpy as np
from scipy.integrate import quad


def unit_ball_volume(D: int) -> float:
    return pi ** (D / 2.0) / gamma(D / 2.0 + 1.0)


def detection_distance(L: float, flux_limit: float) -> float:
    return sqrt(L / (4.0 * pi * flux_limit))


def surveyed_volume(L: float, flux_limit: float, D: int) -> float:
    """Closed form: volume of the D-ball out to the detection distance."""

    return unit_ball_volume(D) * detection_distance(L, flux_limit) ** D


def surveyed_volume_numeric(L: float, flux_limit: float, D: int, r_max: float) -> float:
    """General path: integrate the D-dimensional shell area out to where the flux falls below the cut
    (or to the edge r_max of the distribution, whichever is nearer)."""

    shell = D * unit_ball_volume(D)  # surface of the unit (D-1)-sphere
    edge = min(detection_distance(L, flux_limit), r_max)
    value, _ = quad(lambda r: shell * r ** (D - 1), 0.0, edge, epsabs=0.0, epsrel=1e-13, limit=200)
    return value


def space_density(b: float, F: float, P: float) -> float:
    """Layer-3 steady abundance n = b F / P."""

    return b * F / P


def observed_count(b: float, F: float, P: float, eps: float, flux_limit: float, D: int) -> float:
    return space_density(b, F, P) * surveyed_volume(eps * P, flux_limit, D)


def observed_exponent_of_P(D: int) -> float:
    return D / 2.0 - 1.0


def simulate_survey(types: list[dict], flux_limit: float, D: int, R: float, rng: np.random.Generator):
    """Monte Carlo route: place sources uniformly in a D-ball of radius R (Poisson numbers with mean
    n_i V_ball), keep those above the flux limit, and return counts and 1/V_max estimates."""

    V_ball = unit_ball_volume(D) * R ** D
    seen_counts, vmax_estimates = [], []
    for t in types:
        n = space_density(t["b"], t["F"], t["P"])
        k = rng.poisson(n * V_ball)
        # radius distribution in a D-ball: r = R u^(1/D)
        r = R * rng.random(k) ** (1.0 / D)
        L = t["eps"] * t["P"]
        detected = L / (4.0 * pi * r * r) >= flux_limit
        n_det = int(detected.sum())
        seen_counts.append(n_det)
        V_max = min(surveyed_volume(L, flux_limit, D), V_ball)
        vmax_estimates.append(n_det / V_max)
    return np.array(seen_counts), np.array(vmax_estimates)
