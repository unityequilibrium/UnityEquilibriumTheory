"""Layer 2 -> 3, wave D3: a chain of entropy dividers joined by radiation (or any power-law contact).

Question (follow-up to wave D2): the sun, a planet and space exchange heat by radiation, J ~ T^4,
not by a linear contact. Does the split of work between the stages of a chain still leave the total
unchanged, or does the way an upstream stage uses its share change what the whole chain gets?

Setting. As in uet_entropy_chain (wave D2): reversible stages with hot side a_k and cold side b_k,
entropy flux s_k = J_{k-1}/a_k = J_k/b_k, source at T0, final divider at T_N. Every contact now
follows the power law
    J = G (T_h^n - T_c^n) / n ,
with n = 1 the linear contact of D2 and n = 4 radiation (G = 4 sigma A for black surfaces; the
factor 1/n keeps G > 0 for every n != 0). A middle reservoir between two contacts of the same n
still merges into one: both carry the same J, so T_mid^n drops out and G_mid = G_l G_r/(G_l + G_r).

[AI derivation]
D1  Middle contact. b_k = J_k/s_k and a_{k+1} = J_k/s_{k+1} in J_k = G (b_k^n - a_{k+1}^n)/n give
        s_{k+1}^{-n} = s_k^{-n} - n J_k^{1-n} / G_mid_k .
    For n = 1 the heat passed on, J_k, drops out (D2: zero-sum sharing). For n != 1 it does not.
D2  Sign. At a given entropy flux s_1 the heat drawn from the source, J_0, is fixed, and the heat
    dumped, J_N, grows with s_N. Since d(J^{1-n})/dJ = (1-n) J^{-n}:
      n > 1 (radiation): passing on more heat lowers s_N, so J_N falls and the total J_0 - J_N rises.
            A unit of work taken upstream costs the downstream stages more than a unit.
      n < 1: the opposite; taking more upstream raises the total.
      n = 1: no effect (zero-sum).
    The marginal cost to the rest of the chain of one more unit of work taken by stage k is
        c_k = - d(P_rest)/d(P_k) = 1 + d(J_0 - J_N)/d J_k ,
    with c_k > 1 for n > 1, c_k < 1 for n < 1, c_k = 1 for n = 1.
D3  Limits. As s_1 -> 0 the efficiency of any chain tends to 1 - T_N/T0 for every n (the
    reversible chain telescopes); every contact produces entropy J (1/T_c - 1/T_h) >= 0.

Nearest known theory: endoreversible engines with radiative (Stefan-Boltzmann) contacts, the
solar-engine models of De Vos (1985, 1992) and the Muser engine; dependence of finite-time results
on the heat-transfer law (for example Chen and Yan 1989). Not UET-distinct. The parent action fixes
none of G, n, T0, T_N. Left out: sky geometry and dilution of sunlight, dividers that warm up.
"""

from __future__ import annotations

from typing import Sequence

from scipy.optimize import brentq


def series(*G: float) -> float:
    return 1.0 / sum(1.0 / g for g in G)


def transfer(G: float, T_h: float, T_c: float, n: float) -> float:
    """Heat flow J = G (T_h^n - T_c^n)/n (positive from hot to cold for every n != 0)."""

    return G * (T_h ** n - T_c ** n) / n


def _source_side(s1: float, T0: float, G0: float, n: float) -> float:
    """Hot side a_1 of stage 1: s1 a1 = G0 (T0^n - a1^n)/n, unique root in (0, T0)."""

    f = lambda a: transfer(G0, T0, a, n) - s1 * a  # noqa: E731  decreasing in a
    return brentq(f, T0 * 1e-12, T0, xtol=1e-15, rtol=1e-15, maxiter=500)


def _sink_side(sN: float, TN: float, GN: float, n: float) -> float:
    """Cold side b_N of the last stage: sN b = GN (b^n - TN^n)/n, root continuously connected to b = TN."""

    g = lambda b: transfer(GN, b, TN, n) - sN * b  # noqa: E731  g(TN) < 0
    if n > 1.0:
        hi = 2.0 * TN
        while g(hi) < 0.0:
            hi *= 2.0
            if hi > 1e300:
                raise ValueError("no sink-side temperature")
        return brentq(g, TN, hi, xtol=1e-15, rtol=1e-15, maxiter=500)
    if n == 1.0:
        if sN >= GN:
            raise ValueError("entropy flux above what the last contact can carry")
        return GN * TN / (GN - sN)
    b_star = (sN / GN) ** (1.0 / (n - 1.0))  # g'(b*) = GN b*^(n-1) - sN = 0; g concave for n < 1
    if b_star <= TN or g(b_star) < 0.0:
        raise ValueError("entropy flux above what the last contact can carry")
    return brentq(g, TN, b_star, xtol=1e-15, rtol=1e-15, maxiter=500)


def chain_state(s1: float, J_mid: Sequence[float], T0: float, TN: float, G0: float,
                G_mid: Sequence[float], GN: float, n: float) -> dict:
    """State of an N-stage chain for entropy flux s1 and intermediate heats J_1 ... J_{N-1}."""

    if len(J_mid) != len(G_mid):
        raise ValueError("one intermediate heat per middle contact")
    a1 = _source_side(s1, T0, G0, n)
    J = [s1 * a1]
    s = [s1]
    a = [a1]
    b = []
    for Jk, Gk in zip(J_mid, G_mid):
        if Jk > J[-1]:
            raise ValueError("intermediate heats must decrease along the chain (non-negative shares)")
        bk = Jk / s[-1]
        an = bk ** n - n * Jk / Gk
        if an <= 0.0 and n > 0.0:
            raise ValueError("middle contact cannot carry this heat")
        a_next = an ** (1.0 / n)
        if a_next <= TN:
            raise ValueError("stage below the final divider")
        b.append(bk)
        a.append(a_next)
        s.append(Jk / a_next)
        J.append(Jk)
    bN = _sink_side(s[-1], TN, GN, n)
    JN = s[-1] * bN
    if JN > J[-1]:
        raise ValueError("last stage would need negative work")
    b.append(bN)
    J.append(JN)
    shares = [J[k] - J[k + 1] for k in range(len(s))]
    sigma = [J[0] * (1.0 / a[0] - 1.0 / T0)]
    sigma += [J[k + 1] * (1.0 / a[k + 1] - 1.0 / b[k]) for k in range(len(s) - 1)]
    sigma.append(J[-1] * (1.0 / TN - 1.0 / b[-1]))
    return {"J": J, "s": s, "a": a, "b": b, "shares": shares, "total": J[0] - J[-1],
            "contact_entropy_production": sigma}


def total(s1: float, J_mid: Sequence[float], T0: float, TN: float, G0: float,
          G_mid: Sequence[float], GN: float, n: float) -> float:
    return chain_state(s1, J_mid, T0, TN, G0, G_mid, GN, n)["total"]


def marginal_cost(k: int, s1: float, J_mid: Sequence[float], T0: float, TN: float, G0: float,
                  G_mid: Sequence[float], GN: float, n: float, h: float | None = None) -> float:
    """c_k = -dP_rest/dP_k for moving heat J_k (k = 1 ... N-1) at fixed s1, by Richardson-extrapolated
    central differences. Taking one more unit of work at stage k lowers J_k by one unit."""

    J_mid = list(J_mid)
    x0 = J_mid[k - 1]
    h = h if h is not None else 1e-3 * x0

    def tot(x: float) -> float:
        J2 = J_mid.copy()
        J2[k - 1] = x
        return total(s1, J2, T0, TN, G0, G_mid, GN, n)

    d1 = (tot(x0 + h) - tot(x0 - h)) / (2.0 * h)
    d2 = (tot(x0 + h / 2) - tot(x0 - h / 2)) / h
    dtotal_dJk = (4.0 * d2 - d1) / 3.0
    # P_k = J_{k-1} - J_k rises by 1 when J_k falls by 1; the total changes by -dtotal/dJk
    return 1.0 + dtotal_dJk
