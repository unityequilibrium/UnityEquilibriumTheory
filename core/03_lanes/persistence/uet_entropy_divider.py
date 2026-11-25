"""Layer 2 -> 3, wave D1: the environment that takes a system's entropy (the "divider").

Question (author, 2026-11-21: "alone, nobody divides the entropy"): how do the lifetime of a
structure and its ability to persist at all depend on the temperature T_c of the environment that
receives its entropy?

Setting. A structure needs work at the rate W_m to keep itself away from equilibrium. Its
resource is heat that arrives from, or is stored at, a hotter body; the waste heat goes to the
divider at T_c. Only the part of the heat that can become work counts as resource (free energy
relative to the divider, as in C_B7_FREE_ENERGY_BURN).

[AI derivation]
D1  Finite store (heat capacity C(T), initially at T0), reversible extraction. Heat C dT drawn at
    temperature T gives work C dT (1 - T_c/T), so the usable resource is the exergy
        Ex(T_c) = int_{T_c}^{T0} C(T) (1 - T_c/T) dT
    and the lifetime is tau = Ex / W_m. For constant C,
        Ex = C [ (T0 - T_c) - T_c ln(T0/T_c) ].
    Limits: T_c -> T0 (the divider is as warm as the store, i.e. alone) gives
    Ex ~ C (T0 - T_c)^2 / (2 T0) -> 0; T_c -> 0 gives Ex -> int C dT (all stored heat usable).
    The entropy balance closes: the store loses int C dT/T and the divider gains exactly that.
D2  Steady flow through finite conductances (endoreversible engine, Novikov 1957): heat enters
    from a source at T_h through K_h and leaves to the divider at T_c through K_c, both at once.
    The largest steady work rate is
        P_max = K (sqrt(T_h) - sqrt(T_c))^2 ,  K = K_h K_c / (K_h + K_c)   (series conductance),
    reached at efficiency 1 - sqrt(T_c/T_h). (The Curzon-Ahlborn cycle, which touches the two
    reservoirs in turn, has the same efficiency but K = K_h K_c / (sqrt(K_h) + sqrt(K_c))^2.) A structure that needs W_m persists only if
    W_m <= P_max, i.e. only if the divider is cold enough:
        T_c <= T_c* = (sqrt(T_h) - sqrt(W_m / K))^2      (exists only if W_m < K T_h).
    This is a sink threshold beside the supply threshold S* of C_L3_SUPPLY: a source alone is not
    enough, the structure also needs somewhere cold enough to put its entropy.

Nearest known theory: classical thermodynamics of exergy (Gouy-Stodola) and endoreversible
(finite-time) thermodynamics. Not UET-distinct. The parent action does not fix C, K_h, K_c, T_h or
W_m; this wave only adds the divider temperature to the layer-3 resource and persistence language.
Left out: radiative (T^4) transfer laws, a divider that warms up, chains of dividers.
"""

from __future__ import annotations

from math import log, sqrt
from typing import Callable

from scipy.integrate import quad
from scipy.optimize import minimize_scalar

HeatCapacity = Callable[[float], float]


# --- D1: finite store --------------------------------------------------------------------------

def exergy(heat_capacity: HeatCapacity, T0: float, T_c: float) -> float:
    """Usable work of a store cooling from T0 to the divider temperature T_c (general C(T))."""

    if not (0.0 < T_c <= T0):
        raise ValueError("need 0 < T_c <= T0")
    value, _ = quad(lambda T: heat_capacity(T) * (1.0 - T_c / T), T_c, T0, epsabs=0.0, epsrel=1e-13, limit=200)
    return value


def exergy_constant_c(C: float, T0: float, T_c: float) -> float:
    return C * ((T0 - T_c) - T_c * log(T0 / T_c))


def lifetime(heat_capacity: HeatCapacity, T0: float, T_c: float, W_m: float) -> float:
    return exergy(heat_capacity, T0, T_c) / W_m


def entropy_balance(heat_capacity: HeatCapacity, T0: float, T_c: float) -> dict[str, float]:
    """Store entropy loss, heat to the divider and divider entropy gain for reversible extraction."""

    ds_store, _ = quad(lambda T: heat_capacity(T) / T, T_c, T0, epsabs=0.0, epsrel=1e-13, limit=200)
    heat_out, _ = quad(lambda T: heat_capacity(T), T_c, T0, epsabs=0.0, epsrel=1e-13, limit=200)
    work = exergy(heat_capacity, T0, T_c)
    q_divider = heat_out - work
    return {"store_entropy_loss": ds_store, "heat_drawn": heat_out, "work": work,
            "heat_to_divider": q_divider, "divider_entropy_gain": q_divider / T_c}


# --- D2: steady flow through finite conductances -----------------------------------------------

def endoreversible_power(eta: float, T_h: float, T_c: float, K_h: float, K_c: float) -> float:
    """Work rate at inner efficiency eta = 1 - T_cw/T_hw, solving the two conductance equations.

    Q_h = K_h (T_h - T_hw),  Q_c = K_c (T_cw - T_c),  Q_c = (1 - eta) Q_h,  T_cw = (1 - eta) T_hw.
    """

    x = 1.0 - eta
    # K_c (x T_hw - T_c) = x K_h (T_h - T_hw)  ->  T_hw (K_c x + K_h x) = x K_h T_h + K_c T_c
    T_hw = (x * K_h * T_h + K_c * T_c) / (x * (K_h + K_c))
    Q_h = K_h * (T_h - T_hw)
    return eta * Q_h


def max_power_numeric(T_h: float, T_c: float, K_h: float, K_c: float) -> tuple[float, float]:
    """(P_max, eta at P_max) by direct maximisation over the inner efficiency."""

    carnot = 1.0 - T_c / T_h
    res = minimize_scalar(lambda e: -endoreversible_power(e, T_h, T_c, K_h, K_c),
                          bounds=(0.0, carnot), method="bounded", options={"xatol": 1e-14})
    return -res.fun, res.x


def effective_conductance(K_h: float, K_c: float) -> float:
    """Series conductance of the two contacts for steady flow."""

    return K_h * K_c / (K_h + K_c)


def max_power_closed_form(T_h: float, T_c: float, K_h: float, K_c: float) -> float:
    return effective_conductance(K_h, K_c) * (sqrt(T_h) - sqrt(T_c)) ** 2


def divider_threshold(T_h: float, W_m: float, K_h: float, K_c: float) -> float | None:
    """Warmest divider that still lets a structure needing W_m persist; None if none does."""

    K = effective_conductance(K_h, K_c)
    if W_m >= K * T_h:
        return None
    return (sqrt(T_h) - sqrt(W_m / K)) ** 2
