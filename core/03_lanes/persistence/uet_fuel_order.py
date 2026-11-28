"""Layer 3, wave D21: layer-3 persistence selection mapped onto state-dependent survival optimisation (fuel order).

Question (author, 2026-11-26, after the fasting literature map): the field explains why a fasting body burns fat first
and spares protein, and why protein loss returns in phase III (Robin 1988; Bernard 2002; Lowell 1987), and treats the
lipid/protein split as an optimal allocation (Noren and Mangel 2004, after Clark and Mangel 2000). Does layer 3's
persistence selection give the same rule? This is a synthesis check, not a new result.

Model (mainstream ingredients, AI assembly): a faster needs e kcal/day. A share q0 must come from protein whatever
happens (obligate gluconeogenesis; Benedict's L. ran at about 16-18 percent). The rest can come from fat, but fat
release is limited by fat mass, D_F,max = k F^(2/3) g/day (Hall 2010, Eq. 11: lipolysis scales as (F/F_Keys)^(2/3) and
rises at most A_L = 3.8 fold in a fast). Protein covers whatever fat does not. Death comes when protein falls to P_c
(about half of body protein can be mobilised; Rebello et al. 2025, citing Cahill). Energy densities rho_F, rho_P.
    dF/dt = -u,   dP/dt = -(e - rho_F u)/rho_P,   0 <= u <= min(k F^(2/3), (1 - q0) e / rho_F).

[AI derivation]
D21a Optimal rule (maximum survival time = layer-3 persistence): every gram of fat burned saves rho_F/rho_P grams of
     protein, and protein is what kills, so burning as much fat as allowed at every moment (bang-bang
     u* = min(k F^(2/3), (1 - q0) e / rho_F)) is never beaten. It is not the only optimum: by energy conservation
     every rule that has used up all its fat before protein reaches P_c survives exactly as long; a rule loses only
     if it still holds fat when it dies. Selection therefore removes rules that waste the ceiling, not every slower
     rule. A backward dynamic programme on a (F, P) grid (survival_dp) reaches the same survival time.
D21b Phase II -> III: the fat ceiling binds when k F^(2/3) = (1 - q0) e / rho_F, i.e. below
         F* = [(1 - q0) e / (rho_F k)]^(3/2);
     above F* protein supplies the obligate share q0 only (phase II), below it protein's share rises (phase III).
D21c Closed-form survival: phase II lasts t2 = rho_F (F0 - F*)/((1 - q0) e) and costs protein q0 e t2 / rho_P;
     in phase III F^(1/3) = F*^(1/3) - k t/3 until fat is gone at t3 = 3 F*^(1/3)/k, with protein use
     (e t - rho_F (F* - F(t)))/rho_P; afterwards protein alone at e/rho_P per day.

Consequence [AI interpretation]: layer 3 needs no new term to reproduce the mainstream fuel order: persistence
selection is the survival objective of the state-dependent model, and the phase-III onset comes from the fat-release
limit already in Hall's model. UET adds the cross-scale wording (a store spent to keep structures above threshold),
not a new prediction. Nearest theory: Clark-Mangel dynamic state variable models, Hall 2010 lipolysis. Not UET-distinct.
"""

from __future__ import annotations

from math import inf

import numpy as np
from scipy.integrate import solve_ivp


def fat_ceiling(F: float, k: float) -> float:
    return k * max(F, 0.0) ** (2.0 / 3.0)


def greedy_fat_use(F: float, e: float, q0: float, k: float, rho_F: float) -> float:
    return min(fat_ceiling(F, k), (1.0 - q0) * e / rho_F)


def phase3_threshold(e: float, q0: float, k: float, rho_F: float) -> float:
    return ((1.0 - q0) * e / (rho_F * k)) ** 1.5


def protein_used_closed(t: float, F0: float, e: float, q0: float, k: float, rho_F: float, rho_P: float) -> float:
    """Protein burned (g) by time t under the optimal rule."""

    Fs = phase3_threshold(e, q0, k, rho_F)
    if F0 <= Fs:
        t2, Fstart = 0.0, F0
    else:
        t2, Fstart = rho_F * (F0 - Fs) / ((1.0 - q0) * e), Fs
    if t <= t2:
        return q0 * e * t / rho_P
    used = q0 * e * t2 / rho_P
    t3 = 3.0 * Fstart ** (1.0 / 3.0) / k
    s = min(t - t2, t3)
    F_s = (Fstart ** (1.0 / 3.0) - k * s / 3.0) ** 3
    used += (e * s - rho_F * (Fstart - F_s)) / rho_P
    if t - t2 > t3:
        used += e * (t - t2 - t3) / rho_P
    return used


def survival_closed(F0: float, P0: float, Pc: float, e: float, q0: float, k: float, rho_F: float, rho_P: float) -> float:
    """Time at which protein falls to Pc under the optimal rule (bisection on the closed-form protein use)."""

    need = P0 - Pc
    hi = 1.0
    while protein_used_closed(hi, F0, e, q0, k, rho_F, rho_P) < need:
        hi *= 2.0
    lo = 0.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if protein_used_closed(mid, F0, e, q0, k, rho_F, rho_P) < need:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def survival_numeric(rule, F0, P0, Pc, e, rho_F, rho_P, t_max=1e5):
    """Integrate a fat-use rule u(F) and return the time protein hits Pc."""

    def rhs(t, y):
        F, P = y
        u = rule(max(F, 0.0))
        return [-u, -(e - rho_F * u) / rho_P]

    def dead(t, y):
        return y[1] - Pc
    dead.terminal = True
    sol = solve_ivp(rhs, (0.0, t_max), [F0, P0], events=dead, method="LSODA", rtol=1e-12, atol=1e-10, max_step=0.5)
    return float(sol.t_events[0][0]) if sol.t_events[0].size else inf


def survival_stepwise(F0, P0, Pc, e, q0, k, rho_F, rho_P, dt: float, n_u: int = 6):
    """Discrete-time forward run that picks, each step, the allowed fat use that loses least protein."""

    F, P, t = F0, P0, 0.0
    while P > Pc:
        umax = greedy_fat_use(F, e, q0, k, rho_F)
        best = None
        for frac in np.linspace(0.0, 1.0, n_u + 1):
            u = frac * umax
            # one-step lookahead is exact here because protein is the only limit and fat saves protein
            score = -(e - rho_F * u)
            if best is None or score > best[0]:
                best = (score, u)
        u = best[1]
        dP = (e - rho_F * u) / rho_P * dt
        if P - dP <= Pc:
            t += dt * (P - Pc) / dP
            break
        F -= u * dt
        P -= dP
        t += dt
    return t


def survival_dp(F0, P0, Pc, e, q0, k, rho_F, rho_P, nF: int = 41, nP: int = 41, n_u: int = 5, dt: float = 1.0,
                n_iter: int = 400):
    """Backward dynamic programme (Clark and Mangel style) on a (F, P) grid: V(F, P) = max over fat-use choices of
    dt + V(F', P'), V = 0 at P <= Pc (linear interpolation, last step prorated). Returns V(F0, P0) and the share of
    states whose maximising choice is the largest allowed fat use."""

    from scipy.interpolate import RegularGridInterpolator

    Fg = np.linspace(0.0, F0, nF)
    Pg = np.linspace(Pc, P0, nP)
    V = np.zeros((nF, nP))
    fracs = np.linspace(0.0, 1.0, n_u + 1)
    for _ in range(n_iter):
        interp = RegularGridInterpolator((Fg, Pg), V, bounds_error=False, fill_value=None)
        Vn = np.zeros_like(V)
        choice = np.zeros_like(V)
        for i, F in enumerate(Fg):
            umax = greedy_fat_use(F, e, q0, k, rho_F)
            for j, P in enumerate(Pg):
                if j == 0:
                    continue
                best, bi = -1.0, 0
                for ci, fr in enumerate(fracs):
                    u = fr * umax
                    dP = (e - rho_F * u) / rho_P * dt
                    if P - dP <= Pc:
                        val = dt * (P - Pc) / dP
                    else:
                        val = dt + float(interp([[max(F - u * dt, 0.0), P - dP]])[0])
                    if val > best + 1e-12:
                        best, bi = val, ci
                Vn[i, j] = best
                choice[i, j] = bi
        if np.max(np.abs(Vn - V)) < 1e-9:
            V = Vn
            break
        V = Vn
    interp = RegularGridInterpolator((Fg, Pg), V)
    share = float(np.mean(choice[:, 1:] == n_u))
    return float(interp([[F0, P0]])[0]), share


def illustration() -> dict:
    """AI-chosen round numbers for a lean man (not fitted): e = 1400 kcal/day, q0 = 0.17 (Benedict L., phase II),
    rho_F = 9.44, rho_P = 4.7 kcal/g (Hall 2010), k from 140 g/day x 3.8 at a reference fat mass of 10 kg,
    F0 = 9 kg, P0 = 10 kg, Pc = 5 kg."""

    e, q0, rho_F, rho_P = 1400.0, 0.17, 9.44, 4.7
    k = 140.0 * 3.8 / 10000.0 ** (2.0 / 3.0)
    F0, P0, Pc = 9000.0, 10000.0, 5000.0
    return {"phase3_fat_g": phase3_threshold(e, q0, k, rho_F),
            "survival_days": survival_closed(F0, P0, Pc, e, q0, k, rho_F, rho_P)}


if __name__ == "__main__":
    print(illustration())
