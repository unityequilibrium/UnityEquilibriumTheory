"""Layer 3 with trace feedback: the record left by earlier systems changes the environment of later ones.

Author (2026-11-19, AUTHOR_PROPOSITION.md section 4): the trace feeds back into the dynamics by changing the
environment of systems that come later, not as a force on matter (the space structure is not a fifth force,
2026-11-17).

Question: layer 3 without feedback (uet_layer3_from_action.py, C_L3_SELECTION_FORMAL) has a unique winner, the
type with the lowest R*, whatever happened before. What changes when the trace feeds back?

Model [AI choice of the simplest form; the author fixed only the channel]:
    dn_i/dt = (a_i(E) R - d_i) n_i
    dR/dt   = S - delta R - R sum_i a_i(E) F_i n_i
    dE/dt   = w R sum_i a_i(E) F_i n_i - kappa E
    a_i(E)  = a_i0 (1 + beta_i E)
E is the accumulated trace in the shared environment. It is written in proportion to the resource used
(w = trace per unit resource; with resource counted as free energy this is the author's reversed Landauer rule,
bits = energy / (k T ln 2)) and fades at rate kappa. beta_i > 0: the trace makes the environment easier for type i
(facilitation, e.g. soil left by earlier plants); beta_i < 0: harder (poisoning). With all beta_i = 0 or w = 0 the
model is layer 3 without feedback.

Derivation [AI derivation]:
1. Type j alone at steady state: R = R*_j(E) = d_j / a_j(E), and E solves
       kappa E = w (S - delta R*_j(E)),
   a quadratic in E. With beta_j > 0 it can have two positive roots: the upper one is the self-sustained state
   (trace_steady_state returns it), the lower one is the threshold the trace must pass to get there.
2. Type i invades the steady state of j iff R*_i(E*_j) < R*_j(E*_j). Without feedback R* does not depend on E,
   so exactly one type resists all others and the outcome does not depend on history or on the supply.
3. Take type 1 better at E = 0 (R*_1 < R*_2(0)), beta_1 = 0, and type 2 helped by the trace (beta_2 > 0).
   Type 2 beats type 1 at trace level E iff E > E_c = (R*_2(0)/R*_1 - 1)/beta_2. Type 1 as resident leaves
   E*_1 = w (S - delta R*_1)/kappa, so type 2 invades it iff
       S > S_c = delta R*_1 + kappa (R*_2(0)/R*_1 - 1) / (w beta_2).
   Above S_c type 2 wins from either order (when it can persist).
4. Below S_c type 1 resists type 2, but a type-2 resident sits on its own upper trace root, which can still lie
   above E_c. In that window (S_b < S < S_c, S_b where the upper root equals E_c) both residents keep the other
   out: two stable states. Type 2 cannot start from an empty environment there (S < delta R*_2(0) in the cases
   checked), so the history that matters is the supply's own history: lowering the supply from above S_c keeps
   type 2 down to S_b, raising it from below S_b keeps type 1 up to S_c (hysteresis).
5. Obligate succession: if type 2 cannot start in an empty environment (S < delta R*_2(0)) but S > S_c, it still
   replaces type 1 after type 1 has written the trace: a pioneer is required.

What is new for UET: with the trace fed back, the lowest-R* rule is replaced by "lowest R* at the trace the
residents leave". The winner then depends on the supply (switch at S_c), on history (window S_b to S_c), and
a later type may need a pioneer, all set by how much trace each unit of resource writes (w) and how fast it
fades (kappa). Nearest known theory: niche construction (Odling-Smee, Laland and Feldman 2003), facilitation in
succession (Connell and Slatyer 1977), plant-soil feedback and alternative stable states (Bever 1997; Scheffer
et al. 2001). Those models give the same kinds of behaviour. What would be UET-specific is tying w to energy use
(bits per joule); that link is a hypothesis, not tested here.
"""

from __future__ import annotations

from math import sqrt
from typing import Sequence

import numpy as np
from scipy.integrate import solve_ivp


def capture(a0: np.ndarray, beta: np.ndarray, E: float) -> np.ndarray:
    return np.maximum(a0 * (1.0 + beta * E), 0.0)


def r_star(a0: float, beta: float, d: float, E: float) -> float:
    a = a0 * (1.0 + beta * E)
    return float("inf") if a <= 0.0 else d / a


def simulate(a0: Sequence[float], beta: Sequence[float], d: Sequence[float], F: Sequence[float], S: float,
             delta: float, w: float, kappa: float, n0: Sequence[float], R0: float, E0: float,
             horizon: float) -> tuple[np.ndarray, float, float]:
    """Integrate layer 3 with trace feedback; returns final (n, R, E)."""
    a0, beta, d, F = (np.asarray(x, dtype=float) for x in (a0, beta, d, F))

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        n, R, E = y[:-2], max(y[-2], 0.0), max(y[-1], 0.0)
        a = capture(a0, beta, E)
        use = R * float(np.sum(a * F * n))
        return np.concatenate([(a * R - d) * n, [S - delta * R - use, w * use - kappa * E]])

    sol = solve_ivp(rhs, (0.0, horizon), np.concatenate([np.asarray(n0, float), [R0, E0]]), method="LSODA",
                    rtol=1e-9, atol=1e-12)
    return sol.y[:-2, -1], float(sol.y[-2, -1]), float(sol.y[-1, -1])


def trace_steady_state(a0: float, beta: float, d: float, S: float, delta: float, w: float, kappa: float) -> float:
    """Positive root of kappa E = w (S - delta d / (a0 (1 + beta E))) for one type alone."""
    if w == 0.0:
        return 0.0
    if beta == 0.0:
        return w * (S - delta * d / a0) / kappa
    # kappa E (1 + beta E) a0 = w (S a0 (1 + beta E) - delta d)
    A = kappa * beta * a0
    B = kappa * a0 - w * S * a0 * beta
    C = -w * (S * a0 - delta * d)
    disc = B * B - 4.0 * A * C
    if disc < 0.0:
        return 0.0  # no steady state with the type present: it cannot persist at this supply
    roots = [(-B + s * sqrt(disc)) / (2.0 * A) for s in (1.0, -1.0)]
    valid = [r for r in roots if r >= 0.0 and 1.0 + beta * r > 0.0]
    return max(valid) if valid else 0.0


def critical_supply(r1: float, r2_0: float, beta2: float, delta: float, w: float, kappa: float) -> float:
    """S_c above which a self-facilitating type 2 keeps out type 1 (beta_1 = 0, R*_1 < R*_2(0))."""
    return delta * r1 + kappa * (r2_0 / r1 - 1.0) / (w * beta2)


def invasion_rates(a0, d, beta2: float, S: float, delta: float, w: float, kappa: float) -> tuple[float, float]:
    """(rate of type 2 entering type 1's steady state, rate of type 1 entering type 2's), beta_1 = 0.
    A resident that cannot persist leaves the empty environment (R = S/delta, E = 0)."""
    E1 = trace_steady_state(a0[0], 0.0, d[0], S, delta, w, kappa)
    E2 = trace_steady_state(a0[1], beta2, d[1], S, delta, w, kappa)
    R1 = min(r_star(a0[0], 0.0, d[0], E1), S / delta)
    E1 = E1 if R1 < S / delta else 0.0
    R2 = min(r_star(a0[1], beta2, d[1], E2), S / delta)
    E2 = E2 if R2 < S / delta else 0.0
    return a0[1] * (1.0 + beta2 * E1) * R1 - d[1], a0[0] * R2 - d[0]


def lower_priority_supply(a0, d, beta2: float, delta: float, w: float, kappa: float) -> float:
    """S_b: lowest supply at which a type-2 resident keeps type 1 out (bisection on the second invasion rate)."""
    s_c = critical_supply(d[0] / a0[0], d[1] / a0[1], beta2, delta, w, kappa)
    lo, hi = delta * d[0] / a0[0], s_c
    if invasion_rates(a0, d, beta2, hi * (1 - 1e-12), delta, w, kappa)[1] >= 0.0:
        return s_c  # no priority window
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if invasion_rates(a0, d, beta2, mid, delta, w, kappa)[1] > 0.0 else (lo, mid)
    return 0.5 * (lo + hi)


def resident_then_invader_state(resident: int, a0, beta, d, F, S, delta, w, kappa,
                                horizon) -> tuple[np.ndarray, float, float]:
    """Let `resident` settle alone, then introduce the other type at low density; return final (n, R, E)."""
    k = len(a0)
    n0 = np.zeros(k)
    n0[resident] = 1e-2
    n, R, E = simulate(a0, beta, d, F, S, delta, w, kappa, n0, S / delta, 0.0, horizon)
    n = np.where(np.arange(k) == resident, n, 1e-6)
    return simulate(a0, beta, d, F, S, delta, w, kappa, n, R, E, horizon)


def resident_then_invader(resident: int, a0, beta, d, F, S, delta, w, kappa, horizon) -> np.ndarray:
    return resident_then_invader_state(resident, a0, beta, d, F, S, delta, w, kappa, horizon)[0]
