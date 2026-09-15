"""Formal Ward-constrained finite-temperature condensed stationarity lane.

The current Gaussian stationarity witness fails the zero-momentum Goldstone
condition.  This module derives one finite local counterterm coefficient from
that Ward condition, rather than fitting it to a target curve, and checks the
result on the tree condensate boundary.  It is a symmetry-constrained formal
lane, not a microscopic 2PI or 1/N completion.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_scheme_identifiability import (
    finite_local_counterterm,
)
from docs.core.uet_o2_finite_temperature_stationarity_scheme import (
    renormalized_gaussian_stationarity_derivative,
)
from docs.core.uet_o2_gaussian_offshell_background import off_shell_mode_omega_sq


@dataclass(frozen=True)
class O2WardConstrainedCondensedState:
    """A Ward-constrained stationary witness on the condensed boundary."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    quartic_coupling: float
    x_boundary: float
    reference_x: float
    reference_scale_sq: float
    base_boundary_derivative: float
    ward_counterterm_coefficient: float
    ward_boundary_derivative: float
    ward_boundary_low_mode_sq: float
    ward_boundary_high_mode_sq: float
    near_boundary_x: float
    near_boundary_derivative: float
    reference_derivative: float
    reference_counterterm_anchors: tuple[float, float, float]
    quadrature_order: int
    momentum_cutoff: float
    unit_lane: str = "natural"
    ward_constraint_included: bool = True
    physical_renormalization_included: bool = False
    physical_kubo_coefficient_included: bool = False
    normal_two_fluid_completion_included: bool = False
    external_calibration_included: bool = False
    data_role: str = "INTERNAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def ward_constrained_condensed_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    reference_factor: float = 2.0,
    one_sided_fraction: float = 1.0e-2,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
) -> O2WardConstrainedCondensedState:
    """Derive the finite counterterm coefficient from the Ward condition.

    The coefficient is selected by requiring the tree Goldstone boundary
    ``x=q/lambda`` to also be stationary.  No target curve, holdout, or
    external observable enters this construction.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    reference_factor = _positive(reference_factor, "reference_factor")
    if reference_factor <= 1.0:
        raise ValueError("reference_factor must place reference_x above x_boundary")
    one_sided_fraction = _positive(one_sided_fraction, "one_sided_fraction")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 32:
        raise ValueError("quadrature_order must be >= 32")

    mass_sq = float(effective_mass_sq(space_response, config))
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    q = z * chemical_potential**2 - mass_sq
    if q <= 0.0:
        raise ValueError("Ward-constrained condensed lane requires q > 0")
    x_boundary = q / lam
    reference_x = reference_factor * x_boundary
    reference_scale_sq = reference_x
    base_boundary_derivative = renormalized_gaussian_stationarity_derivative(
        x_boundary,
        temperature,
        chemical_potential,
        space_response,
        config,
        reference_x,
        0.0,
        reference_scale_sq=reference_scale_sq,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
    )
    derivative_factor = 3.0 * (x_boundary - reference_x) ** 2 / reference_scale_sq
    ward_counterterm_coefficient = -base_boundary_derivative / derivative_factor

    def derivative(x: float) -> float:
        return renormalized_gaussian_stationarity_derivative(
            x,
            temperature,
            chemical_potential,
            space_response,
            config,
            reference_x,
            ward_counterterm_coefficient,
            reference_scale_sq=reference_scale_sq,
            quadrature_order=quadrature_order,
            cutoff_factor=cutoff_factor,
        )

    ward_boundary_derivative = derivative(x_boundary)
    near_boundary_x = x_boundary * (1.0 + one_sided_fraction)
    near_boundary_derivative = derivative(near_boundary_x)
    reference_derivative = derivative(reference_x)
    low_mode_sq, high_mode_sq = off_shell_mode_omega_sq(
        0.0,
        sqrt(x_boundary),
        chemical_potential,
        space_response,
        config,
    )
    anchors = finite_local_counterterm(
        reference_x,
        reference_x,
        reference_scale_sq,
        ward_counterterm_coefficient,
    )
    values = (
        mass_sq,
        q,
        x_boundary,
        reference_x,
        base_boundary_derivative,
        ward_counterterm_coefficient,
        ward_boundary_derivative,
        low_mode_sq,
        high_mode_sq,
        near_boundary_x,
        near_boundary_derivative,
        reference_derivative,
        *anchors,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("Ward-constrained condensed witness is not finite")
    return O2WardConstrainedCondensedState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        quartic_coupling=lam,
        x_boundary=x_boundary,
        reference_x=reference_x,
        reference_scale_sq=reference_scale_sq,
        base_boundary_derivative=base_boundary_derivative,
        ward_counterterm_coefficient=ward_counterterm_coefficient,
        ward_boundary_derivative=ward_boundary_derivative,
        ward_boundary_low_mode_sq=float(low_mode_sq),
        ward_boundary_high_mode_sq=float(high_mode_sq),
        near_boundary_x=near_boundary_x,
        near_boundary_derivative=near_boundary_derivative,
        reference_derivative=reference_derivative,
        reference_counterterm_anchors=tuple(float(value) for value in anchors),
        quadrature_order=quadrature_order,
        momentum_cutoff=float(
            max(
                cutoff_factor * temperature,
                cutoff_factor * abs(chemical_potential),
                cutoff_factor * sqrt(max(mass_sq, 0.0)),
                cutoff_factor * sqrt(reference_x),
                1.0,
            )
        ),
    )


def ward_constrained_condensed_contract() -> dict[str, Any]:
    """Return equations, units, and claim boundaries for the formal lane."""

    return {
        "status": "FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY",
        "equations": {
            "tree_ward_boundary": "x_W=q/lambda, q=Z*mu^2-m_eff(Phi)^2",
            "off_shell_modes": "(y-k^2-r_sigma/Z)(y-k^2-r_pi/Z)-4*mu^2*y=0",
            "goldstone_condition": "omega_G^2(k=0;x_W)=0",
            "stationarity_derivative": "D_a(x)=D_0(x)+3*a*(x-x_*)^2/Lambda_*^2",
            "ward_constrained_coefficient": "a_W=-D_0(x_W)*Lambda_*^2/[3*(x_W-x_*)^2]",
            "constrained_stationarity": "D_{a_W}(x_W)=0",
        },
        "units": {
            "unit_lane": "natural",
            "x_and_mode_squared": "natural energy squared",
            "temperature_and_chemical_potential": "natural energy",
            "finite_coefficient": "dimensionless local counterterm parameter",
            "Phi": "fixed effective response input; no SI map",
        },
        "derivation_class": "action-derived O(2) determinant plus algebraically Ward-constrained finite local counterterm; not microscopic 2PI or 1/N matching",
        "scope": {
            "closed": "formal compatibility of the tree Goldstone boundary and the declared stationarity derivative under one symmetry-constrained local completion",
            "physical_renormalization": "NOT_INCLUDED",
            "condensed_eos": "NOT_INCLUDED",
            "normal_two_fluid": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace only; not an independent state",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "data_role": "INTERNAL_WARD_CONSTRAINED_FORMAL_WITNESS_NO_SOURCE_ROWS",
        "claim_boundary": "This closes only a formal Ward-constrained stationarity lane. The coefficient is derived from symmetry compatibility, not fitted, but it is not a microscopic finite-temperature renormalization, a complete condensed EOS, physical transport, SI calibration, TTG validation, or Full Topic 13 closure.",
    }


__all__ = [
    "O2WardConstrainedCondensedState",
    "ward_constrained_condensed_state",
    "ward_constrained_condensed_contract",
]
