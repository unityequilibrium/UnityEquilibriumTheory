"""Path-A models: the combined UET law applied across domains (2026-11-10).

1. White dwarf cooling as a passive burner (Mestel 1952): luminosity L ~ T_c^(7/2) while the
   stored thermal energy F ~ T_c, so the burn law is P(F) = P0 (F/F0)^n with n = 7/2.
   The layer-2 -> 3 lifetime (A4) to cool to luminosity L is t(L) ~ L^((1-n)/n) = L^(-5/7),
   and the abundance law gives dN/dlog L ~ t(L). With log L = -0.4 M_bol + const:
       d log10 N / d M_bol = 0.4 (n - 1)/n = 2/7.
2. Secular equilibrium of a decay chain (passive burner, P ~ F exactly): the abundance law
   N_i = b tau_i gives N_daughter/N_parent = T_half,daughter / T_half,parent.
3. Negative control: two NON-autocatalytic channels sharing one reagent. Products form in the
   fixed ratio k1/k2 and neither channel excludes the other; exclusion requires autocatalysis.
"""

from __future__ import annotations

from math import exp


def burn_exponent_from_luminosity_law(luminosity_power_of_temperature: float,
                                      energy_power_of_temperature: float = 1.0) -> float:
    """n in P ~ F^n when L ~ T^a and F ~ T^b: n = a / b."""

    return luminosity_power_of_temperature / energy_power_of_temperature


def luminosity_function_slope_per_mag(n: float) -> float:
    """d log10 N / d M_bol for a passive burner with P ~ F^n (n > 1), using t ~ L^((1-n)/n)."""

    if n <= 1.0:
        raise ValueError("cooling-time power law needs n > 1")
    return 0.4 * (n - 1.0) / n


def secular_equilibrium_ratio(t_half_daughter: float, t_half_parent: float) -> float:
    """N_daughter / N_parent in secular equilibrium (abundance law N = b tau)."""

    return t_half_daughter / t_half_parent


def parallel_channels(k1: float, k2: float, a0: float, t: float) -> tuple[float, float, float]:
    """Reagent A shared by two non-autocatalytic first-order channels: returns (A, P1, P2)."""

    k = k1 + k2
    a = a0 * exp(-k * t)
    used = a0 - a
    return a, used * k1 / k, used * k2 / k
