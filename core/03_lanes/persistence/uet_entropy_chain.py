"""Layer 2 -> 3, wave D2: dividing entropy along a chain (source -> stage 1 -> ... -> stage N -> divider).

Question (author, 2026-11-21): when the waste of one structure is the environment of the next
(sun -> earth -> space), does passing entropy along a chain create resource, how is it shared
between the stages, and what does each extra hand-off cost?

Setting. Heat flows from a source at T0 to a final divider at T_N through N structures in series.
Each structure is a reversible engine with hot side a_k and cold side b_k; heat moves between
neighbours through linear contacts. Contact 0 (conductance K_0) joins the source to stage 1,
contact N (K_N) joins stage N to the divider, and between stages k and k+1 a middle reservoir
(for example a planet surface) sits between two contacts, which act as one series contact
K_mid_k = K_left K_right / (K_left + K_right) because both carry the same heat.

[AI derivation]
D1  Entropy flux. Stage k passes entropy at s_k = J_{k-1}/a_k = J_k/b_k. Across a middle contact,
    b_k - a_{k+1} = J_k / K_mid_k gives 1/s_{k+1} = 1/s_k - 1/K_mid_k: every flux follows from s_1.
    The heat in and out are J_0 = s_1 K_0 T0/(K_0 + s_1) and J_N = s_N K_N T_N/(K_N - s_N), so the
    total work P_total = J_0 - J_N depends on s_1 alone.
D2  Sharing is zero-sum. The intermediate heats J_1 ... J_{N-1} are free apart from
    J_0 >= J_1 >= ... >= J_N, and stage k gets P_k = J_{k-1} - J_k. At a given entropy flux any
    split of P_total into non-negative shares is reachable and none changes the total: what one
    stage takes, the next one loses, one for one.
D3  The chain does not create resource. Maximising over s_1,
        P_max = K_chain (sqrt(T0) - sqrt(T_N))^2 ,   1/K_chain = 1/K_0 + sum_k 1/K_mid_k + 1/K_N ,
    the single-engine result of wave D1 with every contact in series. Only the two ends (T0, T_N)
    and the contacts enter; an extra stage only adds contacts and lowers K_chain. With 2N equal
    contacts of conductance k, K_chain = k/(2N): N stages share at most 1/N of what one stage with
    two such contacts could get. As s_1 -> 0 the chain's efficiency tends to 1 - T_N/T0 for any N
    (the reversible chain telescopes).
D4  Persistence of the whole chain. Stages needing W_1 ... W_N can all persist only if
    sum_k W_k <= P_max; below that, any assignment of the shares can be met.

Nearest known theory: endoreversible thermodynamics of engines in series (Novikov 1957 and
finite-time thermodynamics; series heat engines are a textbook case). Not UET-distinct. The parent
action fixes none of T0, T_N, K or W. Left out: radiative (T^4) contacts, which make the stage
temperatures matter beyond the flux, and dividers that warm up.
"""

from __future__ import annotations

from math import sqrt
from typing import Sequence

from scipy.optimize import minimize_scalar


def series(*conductances: float) -> float:
    return 1.0 / sum(1.0 / k for k in conductances)


def fluxes(s1: float, K_mid: Sequence[float]) -> list[float]:
    """Entropy fluxes s_1 ... s_N from 1/s_{k+1} = 1/s_k - 1/K_mid_k."""

    s = [s1]
    for k in K_mid:
        inv = 1.0 / s[-1] - 1.0 / k
        if inv <= 0.0:
            raise ValueError("entropy flux above what the contacts can carry")
        s.append(1.0 / inv)
    return s


def flux_cap(K_0: float, K_mid: Sequence[float], K_N: float) -> float:
    """Largest s_1 for which every flux stays finite and the last contact can take it (s_N < K_N)."""

    return series(*K_mid, K_N)  # 1/s_N = 1/s_1 - sum 1/K_mid > 1/K_N


def end_heats(s1: float, T0: float, TN: float, K_0: float, K_mid: Sequence[float], K_N: float) -> tuple[float, float, list[float]]:
    s = fluxes(s1, K_mid)
    sN = s[-1]
    J0 = s1 * K_0 * T0 / (K_0 + s1)
    JN = sN * K_N * TN / (K_N - sN)
    return J0, JN, s


def total_power(s1: float, T0: float, TN: float, K_0: float, K_mid: Sequence[float], K_N: float) -> float:
    J0, JN, _ = end_heats(s1, T0, TN, K_0, K_mid, K_N)
    return J0 - JN


def chain_state(s1: float, J_mid: Sequence[float], T0: float, TN: float, K_0: float,
                K_mid: Sequence[float], K_N: float) -> dict[str, list[float] | float]:
    """Full state for a chosen split (intermediate heats J_1 ... J_{N-1})."""

    J0, JN, s = end_heats(s1, T0, TN, K_0, K_mid, K_N)
    J = [J0, *J_mid, JN]
    if any(J[i] < J[i + 1] for i in range(len(J) - 1)):
        raise ValueError("intermediate heats must decrease along the chain (non-negative shares)")
    a = [J[k] / s[k] for k in range(len(s))]
    b = [J[k + 1] / s[k] for k in range(len(s))]
    shares = [J[k] - J[k + 1] for k in range(len(s))]
    # entropy production in each contact, computed from temperatures only
    sigma = [J[0] * (1.0 / a[0] - 1.0 / T0)]
    sigma += [J[k + 1] * (1.0 / a[k + 1] - 1.0 / b[k]) for k in range(len(s) - 1)]
    sigma.append(J[-1] * (1.0 / TN - 1.0 / b[-1]))
    return {"J": J, "s": s, "a": a, "b": b, "shares": shares, "total": J0 - JN, "contact_entropy_production": sigma}


def max_total_numeric(T0: float, TN: float, K_0: float, K_mid: Sequence[float], K_N: float) -> tuple[float, float]:
    cap = flux_cap(K_0, K_mid, K_N)
    res = minimize_scalar(lambda x: -total_power(x, T0, TN, K_0, K_mid, K_N),
                          bounds=(0.0, cap * (1.0 - 1e-12)), method="bounded", options={"xatol": 1e-14})
    return -res.fun, res.x


def max_total_closed_form(T0: float, TN: float, K_0: float, K_mid: Sequence[float], K_N: float) -> float:
    return series(K_0, *K_mid, K_N) * (sqrt(T0) - sqrt(TN)) ** 2


def chain_can_persist(needs: Sequence[float], T0: float, TN: float, K_0: float,
                      K_mid: Sequence[float], K_N: float) -> bool:
    return sum(needs) <= max_total_closed_form(T0, TN, K_0, K_mid, K_N)
