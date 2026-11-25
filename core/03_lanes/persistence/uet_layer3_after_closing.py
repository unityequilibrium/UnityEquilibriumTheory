"""Layer 3, wave D15: what does the full layer-3 equation do after the supply stops?

Question (after T030 FAILED, 2026-11-23): wave D14 closed a pool with a constant leak, dR/dt = -delta R,
so the stock fell with a constant specific rate; a fasting man's specific mass-loss rate fell instead.
D14 left out the structures that live on the pool. The full layer-3 model (uet_persistence_selection.py,
one structure type) is

    dn/dt = (a R - 1/tau) n,        dR/dt = S - delta R - a F R n,

with n the number of structures, F the store each holds and tau = F/P its burn time. What does the stock
M = R + F n do after S drops to zero, and what does it do while S is on (author, 2026-11-24: "behaviour
uses energy; with nothing to share it, a system behaves to the end of its resources")?

[AI derivation]
D15a Stock identity: dM/dt = -delta R - F n / tau. The draw a F R n moves pool into structures and does
     not leave the stock, so the specific loss rate is a weighted mean of the two leaks,
         k = (delta R + F n / tau) / (R + F n).
D15b While supplied: with few structures the pool sits at S/delta and structures grow by compounding at
         lambda = a S / delta - 1/tau;
     they then pull the pool down to R* = 1/(a tau), which does not depend on S, and the rest of the supply
     becomes structures, n* = (S - delta R*)/(a F R*). They use the pool down to their threshold, not to
     zero; below R* they cannot use it.
D15c After closing from that steady state: k(0) = (delta R* + F n*/tau)/(R* + F n*), and k(t) -> min(delta,
     1/tau) as t -> infinity, which is below k(0) whenever both parts are present and delta != 1/tau: the
     stock's loss always slows in the end, towards the slower of its two parts.
D15d If delta > 1/tau (the free pool leaks faster than structures burn) k falls monotonically, since
     d ln(R / n)/dt = -delta - a F n - a R + 1/tau < 0. If delta < 1/tau, k first rises (the pool is drawn
     into structures) and then falls to delta once the structures die.
D15e With no structures (n* = 0) or delta = 1/tau, k = delta at all times: D14 is the one-part special case.
     The limit is not uniform in time: if delta > 1/tau, however few structures there are, they hold the
     stock in the end and k -> 1/tau; D14 is good only for times short against ln(R*/(F n*))/(delta - 1/tau).

Consequence [AI interpretation]: a constant specific loss rate (D14, FAILED in T030) needs a store of one
kind. A store held in two forms, a free pool and structures living on it, slows its loss after closing
without any adaptive rule added; the slowing is a property of composition. This was derived after T030
was seen, so T030 cannot test it; it needs other data and its own Test Card. Nearest known theory:
consumer-resource (chemostat) models, two-compartment depletion. Not UET-distinct.
"""

from __future__ import annotations

from math import isfinite

import numpy as np
from scipy.integrate import solve_ivp


def rhs(t: float, y, a: float, tau: float, F: float, delta: float, S: float = 0.0):
    R, n = y
    return [S - delta * R - a * F * R * n, (a * R - 1.0 / tau) * n]


def threshold_pool(a: float, tau: float) -> float:
    return 1.0 / (a * tau)


def steady_state(a: float, tau: float, F: float, delta: float, S: float) -> tuple[float, float]:
    """(R*, n*) while supplied; n* = 0 and R = S/delta if the supply is below delta R*."""

    Rs = threshold_pool(a, tau)
    if S <= delta * Rs:
        return S / delta, 0.0
    return Rs, (S - delta * Rs) / (a * F * Rs)


def growth_rate(a: float, tau: float, delta: float, S: float) -> float:
    """Compound growth rate of a few structures on a full pool R = S/delta."""

    return a * S / delta - 1.0 / tau


def stock(R, n, F: float):
    return np.asarray(R) + F * np.asarray(n)


def stock_loss_rate(R, n, F: float, tau: float, delta: float):
    """-dM/dt from the identity D15a."""

    return delta * np.asarray(R) + F * np.asarray(n) / tau


def specific_loss_rate(R, n, F: float, tau: float, delta: float):
    return stock_loss_rate(R, n, F, tau, delta) / stock(R, n, F)


def initial_specific_rate(a: float, tau: float, F: float, delta: float, S: float) -> float:
    R, n = steady_state(a, tau, F, delta, S)
    return float(specific_loss_rate(R, n, F, tau, delta))


def late_specific_rate(tau: float, delta: float) -> float:
    return min(delta, 1.0 / tau)


def after_closing(a: float, tau: float, F: float, delta: float, S: float, t_end: float, n_t: int = 401,
                  rtol: float = 1e-11, atol: float = 1e-300):
    """Integrate from the supplied steady state with S = 0; returns t, R, n, k."""

    R0, n0 = steady_state(a, tau, F, delta, S)
    ts = np.linspace(0.0, t_end, n_t)
    sol = solve_ivp(rhs, (0.0, t_end), [R0, n0], t_eval=ts, args=(a, tau, F, delta, 0.0), method="LSODA",
                    rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError(sol.message)
    R, n = sol.y
    return ts, R, n, specific_loss_rate(R, n, F, tau, delta)


def while_supplied(a: float, tau: float, F: float, delta: float, S: float, n0: float, t_end: float,
                   n_t: int = 401):
    """Integrate from a full pool S/delta and a few structures n0 with the supply on."""

    ts = np.linspace(0.0, t_end, n_t)
    sol = solve_ivp(rhs, (0.0, t_end), [S / delta, n0], t_eval=ts, args=(a, tau, F, delta, S), method="LSODA",
                    rtol=1e-11, atol=1e-300)
    if not sol.success:
        raise RuntimeError(sol.message)
    return ts, sol.y[0], sol.y[1]


def illustration() -> dict:
    """One illustrative system (AI-chosen numbers, not fitted to any data): delta tau = 4."""

    a, tau, F, delta = 1.0, 1.0, 1.0, 4.0
    S = 2.0 * delta * threshold_pool(a, tau)
    t, R, n, k = after_closing(a, tau, F, delta, S, 8.0 * tau)
    half = len(t) // 2
    out = {"k0_tau": float(k[0] * tau), "k_end_tau": float(k[-1] * tau),
           "r_late_over_early": float(k[half:].mean() / k[:half].mean()),
           "growth_rate_tau_few_structures": growth_rate(a, tau, delta, S) * tau}
    assert all(isfinite(v) for v in out.values())
    return out


if __name__ == "__main__":
    print(illustration())
