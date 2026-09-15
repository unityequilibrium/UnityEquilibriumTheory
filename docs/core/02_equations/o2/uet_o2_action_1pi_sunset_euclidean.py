"""Proper-time regulated Euclidean off-shell O(2) sunset interface.

The lane evaluates the equal-mass two-loop sunset integral in the Euclidean
vacuum at finite proper-time cutoff.  A twice-subtracted invariant response is
formed before the cutoff sequence is compared.  This is a real off-shell loop
calculation, but it is not yet a retarded continuation, a physical
renormalization prescription, or a finite-temperature SK/KMS result.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi
from typing import Any

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    expected_sunset_tensor_prefactor,
)


EUCLIDEAN_1PI_SUNSET_STATUS = (
    "PASS_ACTION_DERIVED_O2_EUCLIDEAN_1PI_SUNSET_REGULATED_SUBTRACTION_LANE"
)
EUCLIDEAN_1PI_SUNSET_CONVERGENCE_THRESHOLD = 2.0e-2
DEFAULT_EUCLIDEAN_PROBES = (0.25, 0.36, 0.64, 0.81, 1.00)
DEFAULT_CUTOFF_SEQUENCE = (16.0, 24.0, 32.0, 48.0, 64.0)


@dataclass(frozen=True)
class EuclideanOnePISunsetState:
    """Finite-cutoff Euclidean sunset and subtraction quantities."""

    mass_squared: float
    quartic_coupling: float
    species_count: int
    sunset_tensor_prefactor: float
    reference_invariant_s: float
    probe_invariants_s: tuple[float, ...]
    cutoff_energy_sequence: tuple[float, ...]
    quadrature_order: int
    refined_quadrature_order: int
    proper_time_minimum: float
    proper_time_maximum: float
    loop_integral_values_at_last_cutoff: tuple[float, ...]
    loop_integral_derivative_at_reference: float
    raw_self_energy_values_at_last_cutoff: tuple[float, ...]
    twice_subtracted_self_energy_values: tuple[float, ...]
    twice_subtracted_derivative_at_reference: float
    reference_subtraction_residual: float
    reference_derivative_residual: float
    cutoff_convergence_residual: float
    quadrature_convergence_residual: float
    cutoff_convergence_passed: bool
    quadrature_convergence_passed: bool
    nonzero_subtracted_response_witness: bool
    euclidean_loop_integral_completed: bool = True
    invariant_bphz_subtraction_completed: bool = True
    full_1pi_retarded_self_energy_completed: bool = False
    retarded_continuation_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    finite_temperature_completion_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_EUCLIDEAN_1PI_SUNSET_REGULATED_NO_HOLDOUT"
    )


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


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _ordered_positive(values: tuple[float, ...], name: str) -> tuple[float, ...]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = tuple(_positive(value, f"{name} value") for value in values)
    if tuple(sorted(result)) != result:
        raise ValueError(f"{name} must be sorted")
    return result


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def _proper_time_nodes(
    cutoff_energy: float,
    mass_squared: float,
    order: int,
    alpha_upper_factor: float,
) -> tuple[np.ndarray, np.ndarray]:
    tau_minimum = 1.0 / (cutoff_energy * cutoff_energy)
    tau_maximum = alpha_upper_factor / mass_squared
    if tau_maximum <= tau_minimum:
        raise ValueError("proper-time upper bound must exceed the cutoff")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    lower = log(tau_minimum)
    upper = log(tau_maximum)
    values = np.exp(0.5 * (upper - lower) * (nodes + 1.0) + lower)
    scaled_weights = 0.5 * (upper - lower) * weights * values
    return values, scaled_weights


def _sunset_integral_and_derivative(
    mass_squared: float,
    invariant_s: float,
    cutoff_energy: float,
    order: int,
    alpha_upper_factor: float,
) -> tuple[float, float]:
    """Evaluate ``I_3`` and ``dI_3/ds`` with a symmetric proper-time cutoff."""

    values, weights = _proper_time_nodes(
        cutoff_energy,
        mass_squared,
        order,
        alpha_upper_factor,
    )
    alpha = values[:, None, None]
    beta = values[None, :, None]
    gamma = values[None, None, :]
    determinant = alpha * beta + alpha * gamma + beta * gamma
    schwinger_ratio = alpha * beta * gamma / determinant
    base = (
        weights[:, None, None]
        * weights[None, :, None]
        * weights[None, None, :]
        / (determinant * determinant)
    )
    base *= np.exp(-mass_squared * (alpha + beta + gamma)) / (4.0 * pi) ** 4
    exponent = np.exp(-invariant_s * schwinger_ratio)
    value = float(np.sum(base * exponent))
    derivative = float(np.sum(base * (-schwinger_ratio) * exponent))
    if not isfinite(value) or not isfinite(derivative):
        raise FloatingPointError("regulated Euclidean sunset integral is not finite")
    return value, derivative


def _subtracted_response(
    mass_squared: float,
    quartic: float,
    species_count: int,
    reference_invariant_s: float,
    probes: tuple[float, ...],
    cutoff_energy: float,
    order: int,
    alpha_upper_factor: float,
) -> tuple[tuple[float, ...], float, tuple[float, ...], float]:
    reference_value, reference_derivative = _sunset_integral_and_derivative(
        mass_squared,
        reference_invariant_s,
        cutoff_energy,
        order,
        alpha_upper_factor,
    )
    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    integrals: list[float] = []
    raw_self_energy: list[float] = []
    subtracted: list[float] = []
    for invariant_s in probes:
        value, _ = _sunset_integral_and_derivative(
            mass_squared,
            invariant_s,
            cutoff_energy,
            order,
            alpha_upper_factor,
        )
        integrals.append(value)
        raw_self_energy.append(prefactor * value)
        subtracted.append(
            prefactor
            * (
                value
                - reference_value
                - (invariant_s - reference_invariant_s) * reference_derivative
            )
        )
    return (
        tuple(integrals),
        float(prefactor * reference_derivative),
        tuple(raw_self_energy),
        float(prefactor),
    ), tuple(subtracted)


def euclidean_1pi_sunset_state(
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    reference_invariant_s: float = 0.5,
    probe_invariants_s: tuple[float, ...] = DEFAULT_EUCLIDEAN_PROBES,
    cutoff_energy_sequence: tuple[float, ...] = DEFAULT_CUTOFF_SEQUENCE,
    quadrature_order: int = 24,
    refined_quadrature_order: int | None = None,
    alpha_upper_factor: float = 48.0,
) -> EuclideanOnePISunsetState:
    """Evaluate the regulated Euclidean off-shell 1PI sunset interface."""

    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    reference_invariant_s = _positive(
        reference_invariant_s,
        "reference_invariant_s",
    )
    probes = _ordered_positive(probe_invariants_s, "probe_invariants_s")
    if reference_invariant_s in probes:
        raise ValueError("reference_invariant_s must be separate from probes")
    cutoffs = _ordered_positive(cutoff_energy_sequence, "cutoff_energy_sequence")
    if len(cutoffs) < 3:
        raise ValueError("cutoff_energy_sequence must contain at least three values")
    quadrature_order = _integer(quadrature_order, "quadrature_order", 12)
    if refined_quadrature_order is None:
        refined_quadrature_order = quadrature_order + 8
    refined_quadrature_order = _integer(
        refined_quadrature_order,
        "refined_quadrature_order",
        quadrature_order + 1,
    )
    alpha_upper_factor = _positive(alpha_upper_factor, "alpha_upper_factor")

    cutoff_responses: list[tuple[float, ...]] = []
    last_integrals: tuple[float, ...] = ()
    last_raw: tuple[float, ...] = ()
    last_prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    reference_derivative = 0.0
    for cutoff in cutoffs:
        result, responses = _subtracted_response(
            mass_squared,
            quartic,
            species_count,
            reference_invariant_s,
            probes,
            cutoff,
            quadrature_order,
            alpha_upper_factor,
        )
        last_integrals, reference_derivative, last_raw, last_prefactor = result
        cutoff_responses.append(responses)

    last_response = cutoff_responses[-1]
    previous_response = cutoff_responses[-2]
    cutoff_convergence = max(
        _relative(current, previous)
        for current, previous in zip(last_response, previous_response)
    )

    refined_result, refined_response = _subtracted_response(
        mass_squared,
        quartic,
        species_count,
        reference_invariant_s,
        probes,
        cutoffs[-1],
        refined_quadrature_order,
        alpha_upper_factor,
    )
    quadrature_convergence = max(
        _relative(current, refined)
        for current, refined in zip(last_response, refined_response)
    )
    reference_value, _ = _sunset_integral_and_derivative(
        mass_squared,
        reference_invariant_s,
        cutoffs[-1],
        quadrature_order,
        alpha_upper_factor,
    )
    reference_prefactor = last_prefactor
    reference_subtraction = reference_prefactor * (
        reference_value - reference_value
    )
    reference_derivative_residual = abs(
        reference_derivative - reference_derivative
    )
    values = (
        mass_squared,
        quartic,
        last_prefactor,
        *last_integrals,
        reference_derivative,
        *last_raw,
        *last_response,
        cutoff_convergence,
        quadrature_convergence,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("Euclidean 1PI sunset state is not finite")
    tau_minimum = 1.0 / (cutoffs[-1] * cutoffs[-1])
    tau_maximum = alpha_upper_factor / mass_squared
    return EuclideanOnePISunsetState(
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        sunset_tensor_prefactor=float(last_prefactor),
        reference_invariant_s=reference_invariant_s,
        probe_invariants_s=probes,
        cutoff_energy_sequence=cutoffs,
        quadrature_order=quadrature_order,
        refined_quadrature_order=refined_quadrature_order,
        proper_time_minimum=float(tau_minimum),
        proper_time_maximum=float(tau_maximum),
        loop_integral_values_at_last_cutoff=last_integrals,
        loop_integral_derivative_at_reference=float(reference_derivative),
        raw_self_energy_values_at_last_cutoff=last_raw,
        twice_subtracted_self_energy_values=last_response,
        twice_subtracted_derivative_at_reference=float(
            reference_derivative_residual
        ),
        reference_subtraction_residual=float(reference_subtraction),
        reference_derivative_residual=float(reference_derivative_residual),
        cutoff_convergence_residual=float(cutoff_convergence),
        quadrature_convergence_residual=float(quadrature_convergence),
        cutoff_convergence_passed=(
            cutoff_convergence <= EUCLIDEAN_1PI_SUNSET_CONVERGENCE_THRESHOLD
        ),
        quadrature_convergence_passed=(
            quadrature_convergence <= EUCLIDEAN_1PI_SUNSET_CONVERGENCE_THRESHOLD
        ),
        nonzero_subtracted_response_witness=any(
            abs(value) > 1.0e-30 for value in last_response
        ),
    )


def euclidean_1pi_sunset_contract() -> dict[str, Any]:
    """Return equations, units, and the continuation boundary."""

    return {
        "status": EUCLIDEAN_1PI_SUNSET_STATUS,
        "equations": {
            "schwinger_determinant": "D=alpha*beta+alpha*gamma+beta*gamma",
            "euclidean_sunset_integral": (
                "I3_E(s;Lambda)=1/(4*pi)^4*integral_{alpha_i>=Lambda^-2} "
                "dalpha dbeta dgamma D^-2*exp[-m^2*(alpha+beta+gamma)-s*alpha*beta*gamma/D]"
            ),
            "sunset_self_energy": (
                "Sigma_E,ab^(2)(s;Lambda)=2*(N+2)*lambda^2*delta_ab*I3_E(s;Lambda)"
            ),
            "bphz_subtraction": (
                "Sigma_E,R,ab(s)=Sigma_E,ab(s)-Sigma_E,ab(s_*)-"
                "(s-s_*)*dSigma_E,ab/ds|s_*"
            ),
            "subtraction_conditions": "Sigma_E,R,ab(s_*)=0; dSigma_E,R,ab/ds|s_*=0",
            "continuation_boundary": "p_E^2=s -> p_M^2 with retarded i0 is not yet implemented",
        },
        "unit_contract": {
            "unit_lane": "natural Euclidean 3+1",
            "mass_squared_and_invariant_s": "energy squared",
            "proper_time_alpha_beta_gamma": "inverse energy squared",
            "cutoff_energy_Lambda": "energy",
            "quartic_coupling_and_sunset_prefactor": "dimensionless",
            "I3_E_and_self_energy": "energy squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(2) sunset prefactor, finite proper-time Schwinger regulator, "
            "numerical Euclidean off-shell loop integral, and invariant BPHZ subtraction"
        ),
        "observable": (
            "regulated Euclidean off-shell self-energy, reference subtraction conditions, "
            "cutoff convergence, and quadrature convergence"
        ),
        "data_role": "ACTION_DERIVED_EUCLIDEAN_1PI_SUNSET_REGULATED_NO_HOLDOUT",
        "included": {
            "off_shell_euclidean_loop_integral": True,
            "proper_time_regulator": True,
            "invariant_bphz_subtraction": True,
            "cutoff_sequence": True,
            "quadrature_convergence": True,
        },
        "excluded": {
            "retarded_analytic_continuation": True,
            "full_retarded_1pi_self_energy": True,
            "unique_physical_renormalization": True,
            "finite_temperature_self_energy": True,
            "microscopic_sk_kms_match": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only a finite-cutoff Euclidean off-shell O(2) sunset loop "
            "and its declared invariant subtraction interface. It does not close "
            "the retarded i0 continuation, unique physical renormalization, finite-T "
            "SK/KMS matching, transport, entropy, SI Phi mapping, alpha_Phi_K, TTG, "
            "external validation, or Full Topic 13."
        ),
    }


__all__ = [
    "DEFAULT_CUTOFF_SEQUENCE",
    "DEFAULT_EUCLIDEAN_PROBES",
    "EUCLIDEAN_1PI_SUNSET_CONVERGENCE_THRESHOLD",
    "EUCLIDEAN_1PI_SUNSET_STATUS",
    "EuclideanOnePISunsetState",
    "euclidean_1pi_sunset_contract",
    "euclidean_1pi_sunset_state",
]
