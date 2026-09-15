"""Scoped continuum boundary for the Topic 13 heat-current response.

The finite-cutoff heat-current Kubo lane already matches the covariant
natural moment response at one state. This module tests whether that same
response is stable under the declared cutoff and quadrature refinements. It
does not extrapolate a continuum value or emit a physical coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_state,
)
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    covariant_entropy_heat_flux_balance_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS = (
    "PASS_SCOPED_HEAT_CURRENT_KUBO_CONTINUUM_NO_GO"
)
CONTINUUM_ACCEPTANCE_THRESHOLD = 1.0e-2
CUTOFF_SEQUENCE = (36.0, 48.0, 64.0, 80.0)
BASELINE_CUTOFF = 48.0
BASELINE_RADIAL_ORDER = 8
BASELINE_COLLISION_INTEGRATION_ORDER = 24
BASELINE_ANGULAR_ORDER = 24
BASELINE_TRANSITION_QUADRATURE_ORDER = 24
BASELINE_TRANSITION_CHANNEL_COUNT = 64
BASELINE_TRANSITION_INTERPOLATION_ORDER = 40
REFINED_RADIAL_ORDER = 10
REFINED_COLLISION_INTEGRATION_ORDER = 28
REFINED_ANGULAR_ORDER = 28
REFINED_TRANSITION_QUADRATURE_ORDER = 80
REFINED_TRANSITION_CHANNEL_COUNT = 48
REFINED_TRANSITION_INTERPOLATION_ORDER = 40


@dataclass(frozen=True)
class HeatCurrentKuboContinuumBoundaryState:
    """Responses and acceptance checks for the declared finite-cutoff scheme."""

    temperature: float
    chemical_potential: float
    space_response: float
    cutoff_factors: tuple[float, ...]
    cutoff_kappa_natural: tuple[float, ...]
    cutoff_relative_changes: tuple[float, ...]
    acceptance_threshold: float
    cutoff_maximum_relative_change: float
    cutoff_sequence_fails_acceptance: bool
    baseline_kappa_natural: float
    refined_kappa_natural: float
    baseline_to_refined_relative_change: float
    refinement_fails_acceptance: bool
    operator_family_is_shared: bool
    finite_cutoff_boundary_declared: bool
    extrapolated_response_emitted: bool = False
    physical_kubo_coefficient_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _heat_response(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    cutoff_factor: float,
    radial_order: int,
    collision_integration_order: int,
    angular_order: int,
    transition_quadrature_order: int,
    transition_channel_count: int,
    transition_interpolation_order: int,
) -> float:
    """Evaluate the existing heat-response observable with one resolution."""

    operator = continuum_collision_operator_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_order,
        collision_integration_order=collision_integration_order,
        angular_order=angular_order,
        cutoff_factor=cutoff_factor,
        transition_quadrature_order=transition_quadrature_order,
        transition_channel_count=transition_channel_count,
        transition_interpolation_order=transition_interpolation_order,
    )
    balance = covariant_entropy_heat_flux_balance_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        operator_state=operator,
    )
    value = float(balance.kappa_natural)
    if not isfinite(value):
        raise FloatingPointError("heat-current response is not finite")
    return value


def _relative_changes(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        abs(current - previous) / max(abs(previous), 1.0e-300)
        for previous, current in zip(values, values[1:])
    )


def heat_current_kubo_continuum_boundary_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> HeatCurrentKuboContinuumBoundaryState:
    """Run cutoff and independent order refinement for one normal state."""

    temperature = _finite(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    config = config or FiniteTemperatureO2QuasiparticleConfig()

    cutoff_values = tuple(
        _heat_response(
            temperature,
            chemical_potential,
            space_response,
            config,
            cutoff_factor=cutoff,
            radial_order=BASELINE_RADIAL_ORDER,
            collision_integration_order=BASELINE_COLLISION_INTEGRATION_ORDER,
            angular_order=BASELINE_ANGULAR_ORDER,
            transition_quadrature_order=BASELINE_TRANSITION_QUADRATURE_ORDER,
            transition_channel_count=BASELINE_TRANSITION_CHANNEL_COUNT,
            transition_interpolation_order=BASELINE_TRANSITION_INTERPOLATION_ORDER,
        )
        for cutoff in CUTOFF_SEQUENCE
    )
    relative_changes = _relative_changes(cutoff_values)
    refined_value = _heat_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        cutoff_factor=BASELINE_CUTOFF,
        radial_order=REFINED_RADIAL_ORDER,
        collision_integration_order=REFINED_COLLISION_INTEGRATION_ORDER,
        angular_order=REFINED_ANGULAR_ORDER,
        transition_quadrature_order=REFINED_TRANSITION_QUADRATURE_ORDER,
        transition_channel_count=REFINED_TRANSITION_CHANNEL_COUNT,
        transition_interpolation_order=REFINED_TRANSITION_INTERPOLATION_ORDER,
    )
    baseline_value = cutoff_values[1]
    refinement_change = abs(refined_value - baseline_value) / max(
        abs(baseline_value), 1.0e-300
    )
    return HeatCurrentKuboContinuumBoundaryState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        cutoff_factors=CUTOFF_SEQUENCE,
        cutoff_kappa_natural=cutoff_values,
        cutoff_relative_changes=relative_changes,
        acceptance_threshold=CONTINUUM_ACCEPTANCE_THRESHOLD,
        cutoff_maximum_relative_change=max(relative_changes),
        cutoff_sequence_fails_acceptance=max(relative_changes)
        > CONTINUUM_ACCEPTANCE_THRESHOLD,
        baseline_kappa_natural=baseline_value,
        refined_kappa_natural=refined_value,
        baseline_to_refined_relative_change=refinement_change,
        refinement_fails_acceptance=refinement_change
        > CONTINUUM_ACCEPTANCE_THRESHOLD,
        operator_family_is_shared=True,
        finite_cutoff_boundary_declared=True,
    )


def heat_current_kubo_continuum_boundary_contract() -> dict[str, object]:
    """Return the equations, units, and deliberately narrow claim boundary."""

    return {
        "status": HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS,
        "equations": {
            "heat_response": "kappa_natural=(1/3)*Tr[(b_q^perp)^T*L_cont^+*b_q^perp]",
            "adjacent_change": "r_i=abs(kappa_i-kappa_(i-1))/max(abs(kappa_(i-1)),1e-300)",
            "acceptance_controller": "max_i(r_i)<=1e-2 is required before continuum promotion",
            "current_result": "max_i(r_i)>1e-2 => no-go for the declared heat-current discretization",
        },
        "unit_contract": {
            "unit_lane": "natural finite-cutoff",
            "kappa_natural": "formal finite-cutoff natural-unit response",
            "threshold": "dimensionless relative change",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived finite-cutoff response boundary under cutoff and order refinement",
        "observable": "heat-current DC response stability under declared cutoff and quadrature refinement",
        "data_role": "ACTION_DERIVED_INTERNAL_CONVERGENCE_BOUNDARY_NO_SOURCE_ROWS",
        "closed_scope": [
            "the heat-current cutoff sequence is machine-readable",
            "the existing 1e-2 continuum-controller threshold is applied without adjustment",
            "the declared heat-current discretization is rejected for continuum promotion",
            "an independent radial/quadrature refinement also rejects promotion",
            "no extrapolated continuum response or physical coefficient is emitted",
        ],
        "excluded_scope": [
            "mathematical no-go for every future heat-current discretization",
            "loop-renormalized off-shell self-energy",
            "physical Kubo coefficient or SI mapping",
            "dimensional Phi-to-thermal-observable calibration",
            "TTG validation",
        ],
        "claim_boundary": (
            "This closes only a scoped no-go for continuum promotion of the declared "
            "finite-cutoff heat-current discretization. It does not prove that every "
            "future continuum formulation is impossible and does not close physical transport."
        ),
    }


__all__ = [
    "CONTINUUM_ACCEPTANCE_THRESHOLD",
    "HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS",
    "HeatCurrentKuboContinuumBoundaryState",
    "heat_current_kubo_continuum_boundary_contract",
    "heat_current_kubo_continuum_boundary_state",
]
