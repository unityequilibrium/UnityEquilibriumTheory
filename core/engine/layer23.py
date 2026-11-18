"""UET engine, layers 2-3: burn free energy, live tau, abundance N = b tau, selection, bits written.

The same law for every scale (author path A, 2026-11-10). A topic supplies, from the standard
physics of its own system and with independently measured inputs:
    F   the free energy relative to the environment that the structure holds
    P   the burn power, as a function of F (P = P0 (F/F0)^n)
    b   the formation rate (only ratios of b cancel when it is common)
and the engine returns lifetimes, abundances, the selection outcome and the record written.

Derived and tested in core/03_lanes: A4 (uet_layer2_to_3.py), B7 (uet_free_energy_burn.py),
path-A models (uet_path_a_models.py). Confronted with data in T002, T007, T008, T009, T014.
This file adds no new physics.
"""

from __future__ import annotations

from math import log

from ._load import load

_l23 = load("03_lanes/persistence/uet_layer2_to_3.py")
_path_a = load("03_lanes/persistence/uet_path_a_models.py")
_growing = load("03_lanes/persistence/uet_growing_abundance.py")
_asym = load("03_lanes/persistence/uet_asymmetric_division.py")

K_B_J_PER_K = 1.380649e-23


# --- layer 2 -> 3: lifetime from the burn law ---------------------------------------------------

def burn_power(f: float, f0: float, p0: float, n: float) -> float:
    """P(F) = P0 (F/F0)^n: n = 0 regulated burner (star), n = 1 passive friction, n = 7/2 Mestel cooling."""
    return _l23.power_law_burn(f, f0, p0, n)


def lifetime(f0: float, p0: float, n: float = 0.0, f_min: float = 0.0) -> float:
    """tau = integral_{f_min}^{f0} dF / P(F) in closed form (n >= 1 needs f_min > 0)."""
    return _l23.lifetime_power_law(f0, p0, n, f_min)


def lifetime_numerical(burn, f0: float, f_min: float, dt: float) -> float:
    """tau for any burn rule P(F), by integrating dF/dt = -P(F)."""
    return _l23.lifetime_by_integration(burn, f0, f_min, dt)


def burn_exponent(luminosity_power_of_temperature: float, energy_power_of_temperature: float = 1.0) -> float:
    return _path_a.burn_exponent_from_luminosity_law(luminosity_power_of_temperature, energy_power_of_temperature)


# --- layer 3: abundance (Little's law) and selection ------------------------------------------

def abundance(formation_rate: float, tau: float) -> float:
    """N = b tau for a steady flow through a phase."""
    return formation_rate * tau


def abundance_ratio(tau_a: float, tau_b: float) -> float:
    """N_a / N_b = tau_a / tau_b when both phases share one formation rate."""
    return tau_a / tau_b


def abundance_growing(b_now: float, growth_rate: float, entry_age: float, duration: float) -> float:
    """N for a formation rate growing as e^{lambda t}; tends to b tau as lambda -> 0."""
    return _growing.abundance_growing(b_now, growth_rate, entry_age, duration)


def phase_fraction_dividing(a1: float, a2: float, cycle: float) -> float:
    """Fraction of an asynchronously dividing population in the phase [a1, a2] of a fixed cycle."""
    return _growing.phase_fraction_dividing(a1, a2, cycle)


def mitotic_index(t_mitosis: float, cycle: float) -> float:
    return _growing.mitotic_index(t_mitosis, cycle)


def doubling_time_asymmetric(parent_cycle: float, daughter_cycle: float) -> float:
    """Unequal division: T from 2^{-P/T} + 2^{-D/T} = 1."""
    return _asym.doubling_time(parent_cycle, daughter_cycle)


def unbudded_daughter_fraction(parent_cycle: float, daughter_cycle: float, budded: float, doubling: float) -> float:
    return _asym.unbudded_daughter_fraction(parent_cycle, daughter_cycle, budded, doubling)


def budded_fraction(budded: float, doubling: float) -> float:
    """Fraction of cells in the final period B of their cycle: 2^{B/T} - 1."""
    return _asym.budded_fraction(budded, doubling)


def luminosity_function_slope_per_mag(n: float) -> float:
    return _path_a.luminosity_function_slope_per_mag(n)


def r_star(capture_rate: float, tau: float) -> float:
    """Single resource: a type replaces itself at R* = 1/(a tau); the lowest R* wins."""
    return 1.0 / (capture_rate * tau)


coexistence_resources = _l23.coexistence_resources
invasion_fitness = _l23.invasion_fitness
simulate_fixed_lifetime_competition = _l23.simulate_fixed_lifetime_competition


# --- record written (reversed Landauer) -------------------------------------------------------

def bits_written(free_energy_j: float, temperature_k: float) -> float:
    """Bits written into an environment at fixed temperature T when F is burned: F / (k_B T ln 2)."""
    return free_energy_j / (K_B_J_PER_K * temperature_k * log(2.0))


def bit_rate(power_w: float, temperature_k: float) -> float:
    return power_w / (K_B_J_PER_K * temperature_k * log(2.0))
