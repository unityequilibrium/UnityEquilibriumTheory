"""Layer 2 -> 3, wave D13: does more openness give more order, and who makes the order?

Question (author, 2026-11-23): no system is fixed open or closed; "the more open, the more order",
but the order comes from the systems' own shared behaviour, not from space, and space is a limit, not
a condition that determines. A closed system in a dynamic world dies, so what we see must have a
process that keeps it alive, without a guarantee. Can this be put in one equation?

Model (AI choice of the simplest standard model). A system sits between a hot side T_h and a cold side
T_c. Its openness is the pair of heat conductances g_h, g_c to the two sides (Newtonian transfer,
Q = g dT). Inside, it may run an engine (its own behaviour) that turns part of the heat flow into
work; that work is what can keep an ordered structure against decay. A structure that would decay by
producing entropy at rate sigma_d needs work T_c sigma_d to be kept.

[AI derivation]
D13a Openness sets the ceiling. With a reversible core (Q_h/T_1 = Q_c/T_2), the largest work rate is
         P_max = K (sqrt T_h - sqrt T_c)^2 ,   K = g_h g_c / (g_h + g_c) ,
     at efficiency 1 - sqrt(T_c/T_h) (steady-flow engine, Novikov 1957; the same efficiency as the
     Curzon-Ahlborn cycle of 1975). K is the series conductance of the two contacts. P_max grows
     linearly with the openness K: more open, more order can be kept.
D13b Openness alone makes no order. With the same conductances but no engine, heat flows straight
     through, Q = K (T_h - T_c) with the same K, work is 0 and the entropy made,
     Q (1/T_c - 1/T_h), is the largest possible. The order needs the system's own engine.
D13c Persistence threshold. The structure survives only if P_max >= T_c sigma_d, i.e.
         K >= K* = T_c sigma_d / (sqrt T_h - sqrt T_c)^2 .
     A closed system (K -> 0) cannot keep any order; an open one can, if it runs the engine; nothing
     guarantees it does.
D13d The environment is a limit, not a choice: T_h and T_c fix (sqrt T_h - sqrt T_c)^2 and the
     Carnot ceiling 1 - T_c/T_h; how much of it is used is set by the system (illustrative: between
     the Sun's surface 5772 K and Earth's emission 255 K the efficiency at maximum power is 0.79).

Consequence [AI interpretation, in the author's terms]: "the more open, the more order" holds as a
ceiling (P_max proportional to K), "order comes from the system, not from space" holds because the
same openness without an engine gives zero order, and "a closed system dies" is K* > 0.

Nearest known theory: endoreversible thermodynamics (Novikov 1957; Curzon and Ahlborn 1975),
dissipative structures (Prigogine), maximum power principle (Lotka 1922; Odum). Not UET-distinct.
Left out: radiative (T^4) transfer, internal irreversibility, how a structure finds its engine.
"""

from __future__ import annotations

from math import sqrt

from scipy.optimize import minimize_scalar


def openness(g_h: float, g_c: float) -> float:
    return g_h * g_c / (g_h + g_c)


def max_power_closed_form(T_h: float, T_c: float, g_h: float, g_c: float) -> float:
    return openness(g_h, g_c) * (sqrt(T_h) - sqrt(T_c)) ** 2


def efficiency_at_max_power(T_h: float, T_c: float) -> float:
    return 1.0 - sqrt(T_c / T_h)


def power_at(T1: float, T_h: float, T_c: float, g_h: float, g_c: float) -> tuple[float, float]:
    """Work rate and cold-side core temperature T2 for a hot-side core temperature T1 (reversible core)."""

    r = g_h * (T_h - T1) / T1          # entropy flow through the core
    if r >= g_c:
        return float("-inf"), float("inf")
    T2 = g_c * T_c / (g_c - r)
    return g_h * (T_h - T1) - g_c * (T2 - T_c), T2


def max_power_numeric(T_h: float, T_c: float, g_h: float, g_c: float) -> float:
    """General path: maximise the work rate over the core temperature T1 directly."""

    lo = max(T_c, g_h * T_h / (g_h + g_c)) * (1.0 + 1e-9)   # below this the cold contact cannot carry the entropy
    res = minimize_scalar(lambda T1: -power_at(T1, T_h, T_c, g_h, g_c)[0], bounds=(lo, T_h),
                          method="bounded", options={"xatol": 1e-12 * T_h, "maxiter": 2000})
    w = 1e-3 * (T_h - lo)   # second pass in a narrow bracket around the first optimum
    res = minimize_scalar(lambda T1: -power_at(T1, T_h, T_c, g_h, g_c)[0],
                          bounds=(max(lo, res.x - w), min(T_h, res.x + w)),
                          method="bounded", options={"xatol": 1e-14 * T_h, "maxiter": 2000})
    return -res.fun


def conduction_only(T_h: float, T_c: float, g_h: float, g_c: float) -> dict:
    Q = openness(g_h, g_c) * (T_h - T_c)
    return {"heat": Q, "work": 0.0, "entropy_rate": Q * (1.0 / T_c - 1.0 / T_h)}


def entropy_rate_with_engine(T1: float, T_h: float, T_c: float, g_h: float, g_c: float) -> float:
    Q_h = g_h * (T_h - T1)
    P, _ = power_at(T1, T_h, T_c, g_h, g_c)
    Q_c = Q_h - P
    return Q_c / T_c - Q_h / T_h


def openness_threshold(T_h: float, T_c: float, sigma_decay: float) -> float:
    """K* = T_c sigma_d / (sqrt T_h - sqrt T_c)^2: smallest openness that can keep the structure."""

    return T_c * sigma_decay / (sqrt(T_h) - sqrt(T_c)) ** 2


def persists(T_h: float, T_c: float, g_h: float, g_c: float, sigma_decay: float) -> bool:
    return max_power_closed_form(T_h, T_c, g_h, g_c) >= T_c * sigma_decay
