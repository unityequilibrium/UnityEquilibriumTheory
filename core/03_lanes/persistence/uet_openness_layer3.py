"""Layer 2 -> 3, wave D14: does the openness ceiling of D13 compose with the layer-3 pool equation?

Question (synthesis gate, author 2026-11-22: judge UET by whether its pieces compose): wave D13 says a
system can draw at most P_max = K (sqrt T_h - sqrt T_c)^2 from its openness K, and wave L3-2
(uet_layer3_supply.py) says a layer-3 pool dR/dt = S - delta R keeps a structure i alive only if the
boundary supply S exceeds S* = delta R*_min, with S "set by an enclosing system". If the work the
system draws is what fills its pool, S = eta P_max(K) / e (eta: fraction of the work turned into pool
units, e: energy per pool unit), do the two thresholds and the two lifetimes agree?

[AI derivation]
D14a Steady pool from openness: R_ss = eta K (sqrt T_h - sqrt T_c)^2 / (e delta), linear in K.
D14b The thresholds are one condition. The pool keeps the cheapest structure iff R_ss >= R*_min, i.e.
         K >= K*_pool = e delta R*_min / (eta (sqrt T_h - sqrt T_c)^2),
     which is D13's K* = T_c sigma_d / (sqrt T_h - sqrt T_c)^2 with T_c sigma_d = e delta R*_min / eta:
     the work to keep a structure equals the energy cost of refilling its pool's leak.
D14c Closing the system (K -> 0 at t = 0, R(0) = R_ss): R = R_ss e^(-delta t), so a structure with
     threshold R*_i survives a time ln(R_ss / R*_i) / delta after the system closes; a more open past
     buys a longer survival, only logarithmically.
D14d Opening it (R(0) = 0): R = R_ss (1 - e^(-delta t)); structure i appears after
     -ln(1 - R*_i / R_ss) / delta, which diverges as K -> K*_i.

Consequence [AI interpretation]: D13 (thermodynamics of an open system) and layer 3 (persistence of
structures on a pool) compose without a new parameter: openness is the "enclosing system" that L3-2
left open, and the author's "a closed system dies" is D14c, with the dying time set by the leak delta.

Nearest known theory: chemostat and pump-threshold models, endoreversible thermodynamics. Not
UET-distinct. eta, e and delta are free here; the parent action fixes delta (wave L3-2), not eta or e.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
from scipy.integrate import solve_ivp

oo = importlib.import_module("docs.core.03_lanes.persistence.uet_openness_order")
sup = importlib.import_module("docs.core.03_lanes.persistence.uet_layer3_supply")


def supply(K: float, T_h: float, T_c: float, eta: float, e: float) -> float:
    return eta * K * (sqrt(T_h) - sqrt(T_c)) ** 2 / e


def steady_pool(K: float, T_h: float, T_c: float, eta: float, e: float, delta: float) -> float:
    return supply(K, T_h, T_c, eta, e) / delta


def pool_threshold_openness(T_h: float, T_c: float, eta: float, e: float, delta: float, r_star) -> float:
    """K at which the supply equals the L3-2 threshold S* = delta R*_min."""

    S_star = sup.persistence_threshold(delta, np.asarray(r_star, float))
    return S_star * e / (eta * (sqrt(T_h) - sqrt(T_c)) ** 2)


def equivalent_decay_entropy(T_c: float, eta: float, e: float, delta: float, r_star_min: float) -> float:
    """sigma_d of D13 that gives the same threshold: T_c sigma_d = e delta R*_min / eta."""

    return e * delta * r_star_min / (eta * T_c)


def survival_after_closing(R_ss: float, r_star_i: float, delta: float) -> float:
    return log(R_ss / r_star_i) / delta if R_ss > r_star_i else 0.0


def appearance_after_opening(R_ss: float, r_star_i: float, delta: float) -> float:
    return -log(1.0 - r_star_i / R_ss) / delta if R_ss > r_star_i else float("inf")


def pool_ode(S_of_t, delta: float, R0: float, t_end: float, event_level: float):
    """General path: integrate dR/dt = S(t) - delta R and return the first time R crosses event_level."""

    cross = lambda _t, y: y[0] - event_level  # noqa: E731
    cross.terminal = True
    sol = solve_ivp(lambda t, y: [S_of_t(t) - delta * y[0]], (0.0, t_end), [R0], events=cross,
                    method="DOP853", rtol=1e-12, atol=1e-14 * max(R0, event_level))
    return float(sol.t_events[0][0]) if sol.t_events[0].size else float("inf")
