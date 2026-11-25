"""Observation layer, wave O5: two delays between seeing an event and being present with it.

Question (author, 2026-11-21, conversation note "ตอส.md"): seeing a distant event does not put the
observer with it; becoming present together with what is seen costs distance, time and resources,
and this should relate to mass. Which part of the delay can resources remove, and at what cost?

Setting. Flat spacetime, units c = 1. The source sits at rest at distance d in the observer's
inertial frame. The event E is emitted at t = 0, its record reaches the observer at t_o = d.
The traveller leaves at t_o (no decision informed by the record can start earlier) and moves on
a timelike worldline with proper acceleration a(tau). Rapidity eta(tau) = int_0^tau a dtau',
dt/dtau = cosh eta, dx/dtau = sinh eta. Arrival is the first tau with x = d.

[AI derivation]
D1  Record delay. dx/dt = tanh eta < 1 on any timelike worldline, so t_arr - t_o > d and the
    record age at arrival a_arr = t_arr > 2 d. Both events (emission of E, arrival) lie on the
    source's worldline, so a_arr is the proper time of a single clock at the source: it does not
    depend on the one-way synchronisation convention. Spending more resources only pushes a_arr
    down towards 2 d; it never goes below it.
D2  Traveller ageing. For a cruise at constant rapidity eta (instant boosts),
    tau_trip = d / sinh eta, so any tau_trip > 0 is reachable with gamma*beta = sinh eta = d / tau.
    For constant proper acceleration alpha all the way (fly-by), tau_trip = arccosh(1 + alpha d)/alpha.
    For constant proper acceleration alpha, flipped at half way (arrive at rest),
    tau_trip = (2/alpha) arccosh(1 + alpha d / 2), t_trip = (2/alpha) sinh(alpha tau_trip / 2).
D3  Resource cost. A reaction drive with exhaust speed w changes rapidity by
    d eta = -(w) d ln m in the rest frame of the drive, so the mass ratio is
    m0/m1 = exp(Delta_eta / w) and w = 1 (photon rocket) is the least massive one. For start and stop,
    Delta_eta = 2 eta_max, so m0/m1 >= exp(2 eta_max) = (gamma (1 + beta))^2 for a cruise.
    The cost is rest mass converted into radiation that leaves at the speed of light:
    (m0 - m1) c^2 = m1 c^2 (exp(2 eta_max) - 1). The same ratio follows from four-momentum
    conservation of photon emission, m0 = m1 gamma (1 + beta) per boost (second route).
D4  Consequence for the record gap of P2: at arrival the source has changed by
    Delta ~ dX_s/dt * a_arr with a_arr > 2 d, whatever was spent on the journey.

Nearest known theory: special relativity (twin effect, hyperbolic motion, relativistic rocket
equation of Ackeret 1946). Every relation here is textbook; the wave only states, in the
observation-layer language of THOUGHT_EXPERIMENT v3, which delay is fixed by geometry and which is
bought with mass. Not UET-distinct. The parent action fixes none of these numbers (no field of the
action enters); gravity, cosmic expansion and the source's own motion are left out.
"""

from __future__ import annotations

from math import acosh, asinh, cosh, exp, sinh, sqrt, tanh
from typing import Callable

from scipy.integrate import quad
from scipy.optimize import brentq

ProperAcceleration = Callable[[float], float]


# --- general path: any proper-acceleration profile -------------------------------------------

def _segmented_quad(f: Callable[[float], float], tau: float, breakpoints: tuple[float, ...],
                    epsrel: float) -> float:
    """int_0^tau f, split at the breakpoints so that each piece is smooth."""

    edges = [0.0] + sorted(p for p in breakpoints if 0.0 < p < tau) + [tau]
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi > lo:
            value, _ = quad(f, lo, hi, epsabs=0.0, epsrel=epsrel, limit=200)
            total += value
    return total


def rapidity(profile: ProperAcceleration, tau: float, breakpoints: tuple[float, ...] = ()) -> float:
    """eta(tau) = int_0^tau a(s) ds."""

    if tau <= 0.0:
        return 0.0
    return _segmented_quad(profile, tau, breakpoints, 1e-13)


def worldline(profile: ProperAcceleration, tau: float, breakpoints: tuple[float, ...] = ()) -> tuple[float, float]:
    """(t - t_o, x) after proper time tau, by direct integration of cosh/sinh of the rapidity."""

    if tau <= 0.0:
        return 0.0, 0.0
    t = _segmented_quad(lambda s: cosh(rapidity(profile, s, breakpoints)), tau, breakpoints, 1e-13)
    x = _segmented_quad(lambda s: sinh(rapidity(profile, s, breakpoints)), tau, breakpoints, 1e-13)
    return t, x


def arrival(profile: ProperAcceleration, distance: float, tau_max: float,
            breakpoints: tuple[float, ...] = ()) -> dict[str, float]:
    """Proper time and coordinate time of the journey, and the record age at arrival."""

    tau = brentq(lambda s: worldline(profile, s, breakpoints)[1] - distance, 0.0, tau_max,
                 xtol=1e-14, rtol=1e-14, maxiter=200)
    t_trip, _ = worldline(profile, tau, breakpoints)
    return {"tau_trip": tau, "t_trip": t_trip, "record_age_at_arrival": distance + t_trip}


def mass_ratio_reaction_drive(profile: ProperAcceleration, tau_end: float, exhaust_speed: float = 1.0,
                              breakpoints: tuple[float, ...] = ()) -> float:
    """m0/m1 from integrating d ln m = -|a| dtau / w over the whole burn (rocket equation)."""

    burn = _segmented_quad(lambda s: abs(profile(s)), tau_end, breakpoints, 1e-13)
    return exp(burn / exhaust_speed)


# --- closed forms (references) ----------------------------------------------------------------

def flip_profile(alpha: float, distance: float) -> tuple[ProperAcceleration, float]:
    """Constant proper acceleration alpha, reversed at half way. Returns (profile, flip tau)."""

    tau_half = acosh(1.0 + alpha * distance / 2.0) / alpha
    return (lambda s: alpha if s < tau_half else -alpha), tau_half


def flyby_closed_form(alpha: float, distance: float) -> dict[str, float]:
    """Constant proper acceleration alpha all the way (arrive moving): x = (cosh(alpha tau) - 1)/alpha."""

    tau_trip = acosh(1.0 + alpha * distance) / alpha
    t_trip = sinh(alpha * tau_trip) / alpha
    return {"tau_trip": tau_trip, "t_trip": t_trip, "record_age_at_arrival": distance + t_trip,
            "mass_ratio_photon": exp(alpha * tau_trip)}


def flip_closed_form(alpha: float, distance: float) -> dict[str, float]:
    tau_trip = 2.0 * acosh(1.0 + alpha * distance / 2.0) / alpha
    t_trip = 2.0 * sinh(alpha * tau_trip / 2.0) / alpha
    return {"tau_trip": tau_trip, "t_trip": t_trip, "record_age_at_arrival": distance + t_trip,
            "mass_ratio_photon": exp(alpha * tau_trip)}


def cruise_for_proper_time(distance: float, tau_trip: float) -> dict[str, float]:
    """Cruise (instant boosts) that ages the traveller by tau_trip over the distance."""

    k = distance / tau_trip
    eta = asinh(k)
    gamma, beta = cosh(eta), tanh(eta)
    t_trip = distance / beta
    return {"gamma": gamma, "beta": beta, "gamma_beta": k, "rapidity": eta, "t_trip": t_trip,
            "record_age_at_arrival": distance + t_trip,
            "mass_ratio_photon": exp(2.0 * eta),
            "rest_mass_converted_per_payload": exp(2.0 * eta) - 1.0}


def photon_boost_mass_ratio(beta: float) -> float:
    """Second route: four-momentum conservation for a body that emits photons backwards.

    m0 (1, 0) = m1 gamma (1, beta) + E (1, -1)  =>  m0 = m1 gamma (1 + beta).
    """

    gamma = 1.0 / sqrt(1.0 - beta * beta)
    return gamma * (1.0 + beta)
