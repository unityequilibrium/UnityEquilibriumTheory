"""Tree-level quadratic fluctuations around the declared O(2) condensate.

The response scalar ``Phi`` is held fixed in this lane.  In a co-rotating
field basis, the condensate amplitude and phase fluctuations obey the exact
quadratic determinant of the conservative O(2) action.  This is a T=0,
tree-level spectrum, not a finite-temperature self-energy or two-fluid
completion.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
    o2_equilibrium_state,
)


@dataclass(frozen=True)
class O2CondensateFluctuationState:
    """Exact tree-level radial/Goldstone mode data at fixed ``Phi``."""

    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    amplitude_sq: float
    radial_curvature_sq: float
    zero_momentum_high_mode_sq: float
    unit_lane: str = "natural"
    response_fluctuation_included: bool = False
    finite_temperature_included: bool = False


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def condensate_fluctuation_state(
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> O2CondensateFluctuationState:
    """Return the condensed background coefficients at fixed ``Phi``."""

    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    eos_state = o2_equilibrium_state(mu, phi, config)
    if eos_state.branch != "condensed":
        raise ValueError("quadratic condensate fluctuations require the condensed branch")
    mass_sq = float(effective_mass_sq(phi, config))
    q = float(eos_state.condensate_control)
    amplitude_sq = q / float(config.matter.matter_quartic)
    radial_curvature_sq = 2.0 * q / float(config.matter.matter_kinetic)
    zero_momentum_high_mode_sq = 2.0 * (q / float(config.matter.matter_kinetic) + 2.0 * mu**2)
    values = (mass_sq, q, amplitude_sq, radial_curvature_sq, zero_momentum_high_mode_sq)
    if not all(isfinite(value) and value > 0.0 for value in values[1:]):
        raise FloatingPointError("condensate fluctuation state must be finite and positive")
    return O2CondensateFluctuationState(
        chemical_potential=mu,
        space_response=phi,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        amplitude_sq=amplitude_sq,
        radial_curvature_sq=radial_curvature_sq,
        zero_momentum_high_mode_sq=zero_momentum_high_mode_sq,
    )


def quadratic_fluctuation_polynomial(
    omega_sq: float,
    wavenumber: float,
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return the determinant in ``omega^2`` of the radial/phase system.

    With ``x=omega^2-k^2`` and ``a=q/Z``, the determinant is
    ``x*(x-2*a)-4*mu^2*omega^2``.
    """

    y = _finite(omega_sq, "omega_sq")
    k = _finite(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    a = state.condensate_control / float(config.matter.matter_kinetic)
    x = y - k * k
    return float(x * (x - 2.0 * a) - 4.0 * state.chemical_potential**2 * y)


def quadratic_mode_omega_sq(
    wavenumber: float,
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float]:
    """Return ``(Goldstone, radial)`` positive-frequency squared modes."""

    k = _finite(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    z = float(config.matter.matter_kinetic)
    a = state.condensate_control / z
    base = k * k + a + 2.0 * state.chemical_potential**2
    discriminant = (a + 2.0 * state.chemical_potential**2) ** 2 + 4.0 * state.chemical_potential**2 * k * k
    root = sqrt(discriminant)
    low = base - root
    high = base + root
    if low < -1.0e-12 or high <= 0.0:
        raise FloatingPointError("quadratic fluctuation spectrum is not non-negative")
    return float(max(low, 0.0)), float(high)


def quadratic_mode_frequencies(
    wavenumber: float,
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float]:
    """Return non-negative frequencies for the low and high branches."""

    low, high = quadratic_mode_omega_sq(wavenumber, state, config)
    return sqrt(low), sqrt(high)


def condensate_fluctuation_contract() -> dict[str, Any]:
    """Return the derivation scope and explicit exclusions."""

    return {
        "status": "TREE_LEVEL_O2_CONDENSATE_QUADRATIC_SPECTRUM",
        "equations": {
            "rotating_basis": "chi=exp(-i*mu*t)*(A+sigma+i*pi)",
            "background": "A^2=q/lambda, q=Z*mu^2-m_eff(Phi)^2",
            "linear_system": "[(omega^2-k^2-2*q/Z), 2*i*mu*omega; -2*i*mu*omega, (omega^2-k^2)]*(sigma,pi)=0",
            "determinant": "(omega^2-k^2)*(omega^2-k^2-2*q/Z)-4*mu^2*omega^2=0",
            "modes": "omega_+-^2=k^2+q/Z+2*mu^2 +- sqrt((q/Z+2*mu^2)^2+4*mu^2*k^2)",
            "hydrodynamic_limit": "lim_{k->0} omega_-^2/k^2=q/(3*Z*mu^2-m_eff^2)=c_s^2",
        },
        "scope": {
            "unit_lane": "natural",
            "background": "homogeneous condensed O(2) branch",
            "space_response": "Phi held fixed",
            "temperature": "T=0 tree-level only",
            "response_fluctuation": "excluded",
            "vacuum_loop": "excluded",
            "normal_component": "excluded",
            "dissipation": "excluded",
        },
        "ontology": {
            "C": "not identified with matter amplitude or O(2) charge",
            "Phi": "fixed action response input; not temperature or metric",
            "R_gen": "not a fluctuation state and has no feedback",
            "R_obs": "not included",
        },
        "data_role": "ACTION_DERIVED_T0_QUADRATIC_SPECTRUM_NOT_FINITE_TEMPERATURE_TRANSPORT",
        "claim_boundary": "This derives the fixed-Phi tree-level radial/Goldstone spectrum of the declared O(2) action. It does not derive finite-temperature self-energy, a normal component, dissipative transport, a renormalized loop action, an SI Phi map, or external validation.",
    }


__all__ = [
    "O2CondensateFluctuationState",
    "condensate_fluctuation_state",
    "quadratic_fluctuation_polynomial",
    "quadratic_mode_omega_sq",
    "quadratic_mode_frequencies",
    "condensate_fluctuation_contract",
]
