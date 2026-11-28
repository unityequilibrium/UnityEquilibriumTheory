"""Layer 3, wave D20: a survival process as a burn that follows the store (new L0 hypothesis).

Question (after T030 FAILED and T034's trend; author 2026-11-23: "what we see must have a survival process,
not guaranteed"): constant-rate depletion of a closed store (D14, exponential) failed on a fasting man, whose
specific loss rate fell as he shrank. Layer 3 already allows a store-dependent burn, tau = int dF / P(F)
(C_L3_BURN_LAW_SELECTION). The simplest survival process [AI hypothesis, L0]: once the supply stops, the
system lowers its burn as its store falls,
    dR/dt = -P(R),   P(R) = P0 (R/R0)^beta,
with beta = 0 constant burn (empties in finite time, linear), beta = 1 constant leak (D14, exponential),
beta > 1 a burn that falls faster than the store (the system protects what is left).

[AI derivation]
D20a Closed form, beta != 1:  R(t)^(1-beta) = R0^(1-beta) + (beta - 1) P0 R0^(-beta) t;  beta = 1: R = R0 e^(-P0 t/R0).
D20b Specific loss rate k = P/R = (P0/R0) (R/R0)^(beta-1): it falls as R shrinks exactly when beta > 1.
D20c Survival: the time to fall from R0 to a threshold R* is
         t* = R0 [(R*/R0)^(1-beta) - 1] / ((beta - 1) P0),
     finite for every beta; for beta >= 1 the store never empties (R -> 0 only as t -> infinity), and for
     beta > 1 the time to reach R* grows as (R*)^(1-beta) when R* -> 0: the survival process buys time but
     guarantees nothing, since a structure with threshold R* still dies at t*.
D20d Two-window estimator: for points (t, R) on one solution, the end-point specific rates of an early and a
     late window obey r = k_late/k_early, and to first order in the window length
         beta - 1 = ln r / ln(R_late/R_early)   (R_early, R_late: window mean stores),
     so one fast's curvature gives beta; it must be checked on a different fast (a calibration is not a test).

Consequence [AI interpretation]: the failed T030 and the falling protein loss of T034 both point to beta > 1,
a system that lowers its burn as it shrinks. That is the author's survival process in one number; whether one
beta carries from one body to another is the test. Nearest known theory: adaptive thermogenesis and
metabolic adaptation in starvation (Keys 1950; Hall 2008 models), allometric P ~ M^beta. Not UET-distinct.
"""

from __future__ import annotations

from math import exp, log

import numpy as np
from scipy.integrate import solve_ivp


def burn(R, P0: float, R0: float, beta: float):
    return P0 * (np.asarray(R) / R0) ** beta


def store(t, R0: float, P0: float, beta: float):
    t = np.asarray(t, float)
    if abs(beta - 1.0) < 1e-12:
        return R0 * np.exp(-P0 * t / R0)
    base = R0 ** (1.0 - beta) + (beta - 1.0) * P0 * R0 ** (-beta) * t
    out = np.where(base > 0, np.abs(base) ** (1.0 / (1.0 - beta)), 0.0)
    return out


def store_numeric(t_end: float, R0: float, P0: float, beta: float, n: int = 201):
    ts = np.linspace(0.0, t_end, n)
    sol = solve_ivp(lambda t, y: [-burn(max(y[0], 0.0), P0, R0, beta)], (0.0, t_end), [R0], t_eval=ts,
                    method="DOP853", rtol=1e-12, atol=1e-14 * R0)
    return ts, sol.y[0]


def specific_rate(R, P0: float, R0: float, beta: float):
    return (P0 / R0) * (np.asarray(R) / R0) ** (beta - 1.0)


def time_to_threshold(R0: float, R_star: float, P0: float, beta: float) -> float:
    if abs(beta - 1.0) < 1e-12:
        return R0 / P0 * log(R0 / R_star)
    return R0 * ((R_star / R0) ** (1.0 - beta) - 1.0) / ((beta - 1.0) * P0)


def window_rate(points):
    """End-point specific rate of a run of (t, R) points and its mean store (as in T030)."""

    (t0, m0), (t1, m1) = points[0], points[-1]
    mm = sum(m for _, m in points) / len(points)
    return (m0 - m1) / ((t1 - t0) * mm), mm


def beta_from_two_windows(points) -> dict:
    """Split at the mid-time (as in T030) and invert r = (R_late/R_early)^(beta - 1)."""

    pts = sorted(points)
    t_mid = 0.5 * (pts[0][0] + pts[-1][0])
    early = [p for p in pts if p[0] <= t_mid]
    late = [p for p in pts if p[0] >= t_mid]
    k_e, m_e = window_rate(early)
    k_l, m_l = window_rate(late)
    r = k_l / k_e
    return {"r": r, "beta": 1.0 + log(r) / log(m_l / m_e), "m_early": m_e, "m_late": m_l}


def predicted_r(m_early: float, m_late: float, beta: float) -> float:
    return (m_late / m_early) ** (beta - 1.0)


if __name__ == "__main__":
    t = np.arange(0, 26)
    print(beta_from_two_windows(list(zip(t, store(t, 56.0, 0.37, 2.0)))))
