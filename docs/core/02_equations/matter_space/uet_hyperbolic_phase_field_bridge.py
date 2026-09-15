"""Causal-feasibility and mapping audit for the hyperbolic phase comparator.

The sourced first-order phase-field system has characteristic speeds

``v_C**2 = (alpha + g''(C)) / tau`` and ``v_aux**2 = gamma / beta``.

For the symmetric double well and the declared amplitude interval
``|C| <= C_max``, this module derives the exact normalized parameter bounds
needed to keep both speed families inside a fixed cone ``c_hat``.  It also
makes explicit why the exact parabolic Cahn-Hilliard limit and a fixed finite
cone cannot be taken uniformly at the same time.

The second purpose is deliberately narrower: under the algebraic change of
variables ``J = q / tau``, the external comparator's flux equation has the
same local Maxwell-Cattaneo form as the mobility-one current law used by the
UET constitutive bridge.  This is not a map of the comparator order parameter
to the UET Noether density, and it is not a covariant derivation.

No history trace is accepted and no derived trace can feed back into any
physical equation here.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from .uet_hyperbolic_phase_field import HyperbolicPhaseFieldConfig

HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS: Final[str] = (
    "ANALYTIC_NORMALIZED_CAUSAL_FEASIBILITY_NOT_COVARIANT_DERIVATION"
)
HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER: Final[str] = (
    "noether_density_to_phase_field_order_parameter_map_missing"
)


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive_scalar(value: float, name: str) -> float:
    result = _finite_scalar(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _amplitude(value: float) -> float:
    result = _finite_scalar(value, "max_abs_C")
    if result < 0.0:
        raise ValueError("max_abs_C must be non-negative")
    return result


def _matching_vectors(**values: Any) -> dict[str, np.ndarray]:
    arrays = {name: np.asarray(value, dtype=float) for name, value in values.items()}
    shapes = {array.shape for array in arrays.values()}
    if len(shapes) != 1 or next(iter(shapes), ()) == ():
        raise ValueError("sequence inputs must be non-scalar arrays with matching shape")
    if any(not np.all(np.isfinite(array)) for array in arrays.values()):
        raise ValueError("sequence inputs must be finite")
    return arrays


@dataclass(frozen=True)
class LocalCurrentLawMap:
    """Algebraic map from source ``q`` to physical current ``J=q/tau``."""

    physical_current: np.ndarray
    flux_impulse_rate: np.ndarray
    physical_current_rate: np.ndarray
    current_law_residual: np.ndarray
    max_abs_residual: float


def shifted_curvature_domain_bounds(
    max_abs_C: float,
    alpha_penalty: float,
) -> dict[str, float]:
    """Return exact bounds of ``alpha + 3*C**2 - 1`` on ``[-Cmax,Cmax]``.

    The symmetric interval always contains the spinodal origin.  Consequently
    the minimum is ``alpha-1`` and the maximum is
    ``alpha+3*Cmax**2-1``.
    """

    amplitude = _amplitude(max_abs_C)
    alpha = _positive_scalar(alpha_penalty, "alpha_penalty")
    return {
        "minimum_shifted_curvature": alpha - 1.0,
        "maximum_shifted_curvature": alpha + 3.0 * amplitude**2 - 1.0,
        "strict_hyperbolicity_margin": alpha - 1.0,
    }


def subluminal_parameter_bounds(
    max_abs_C: float,
    config: HyperbolicPhaseFieldConfig,
) -> dict[str, Any]:
    """Return exact lower bounds on ``tau`` and ``beta`` for a fixed cone.

    For ``|C|<=Cmax`` and ``c_hat>0`` the necessary and sufficient normalized
    inequalities for the two analytic speed families are

    ``tau >= (alpha + 3*Cmax**2 - 1)/c_hat**2`` and
    ``beta >= gamma/c_hat**2``.

    Strict hyperbolicity over the whole symmetric interval additionally
    requires ``alpha>1``.
    """

    curvature = shifted_curvature_domain_bounds(
        max_abs_C, config.alpha_penalty
    )
    light_speed = _positive_scalar(
        config.normalized_light_speed, "normalized_light_speed"
    )
    tau_min = curvature["maximum_shifted_curvature"] / light_speed**2
    beta_min = config.gamma_gradient / light_speed**2
    return {
        **curvature,
        "max_abs_C": _amplitude(max_abs_C),
        "normalized_light_speed": light_speed,
        "strictly_hyperbolic_on_domain": bool(
            curvature["strict_hyperbolicity_margin"] > 0.0
        ),
        "minimum_tau_flux_for_cone": tau_min,
        "minimum_beta_wave_for_cone": beta_min,
        "matter_bound_formula": (
            "tau_flux >= (alpha_penalty + 3*max_abs_C**2 - 1) / c_hat**2"
        ),
        "auxiliary_bound_formula": (
            "beta_wave >= gamma_gradient / c_hat**2"
        ),
    }


def fixed_light_cone_feasibility(
    max_abs_C: float,
    config: HyperbolicPhaseFieldConfig,
    *,
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Evaluate strict hyperbolicity and fixed-cone feasibility on a domain."""

    tol = _finite_scalar(tolerance, "tolerance")
    if tol < 0.0:
        raise ValueError("tolerance must be non-negative")
    bounds = subluminal_parameter_bounds(max_abs_C, config)
    matter_speed = float(
        np.sqrt(
            bounds["maximum_shifted_curvature"] / config.tau_flux
        )
    )
    auxiliary_speed = float(
        np.sqrt(config.gamma_gradient / config.beta_wave)
    )
    tau_margin = config.tau_flux - bounds["minimum_tau_flux_for_cone"]
    beta_margin = config.beta_wave - bounds["minimum_beta_wave_for_cone"]
    matter_pass = bool(tau_margin >= -tol)
    auxiliary_pass = bool(beta_margin >= -tol)
    strict = bool(bounds["strictly_hyperbolic_on_domain"])
    if not strict:
        status = "BLOCKED_NOT_STRICTLY_HYPERBOLIC_ON_SYMMETRIC_DOMAIN"
    elif not matter_pass and not auxiliary_pass:
        status = "FAIL_BOTH_CHARACTERISTIC_FAMILIES_OUTSIDE_FIXED_CONE"
    elif not matter_pass:
        status = "FAIL_MATTER_CHARACTERISTIC_OUTSIDE_FIXED_CONE"
    elif not auxiliary_pass:
        status = "FAIL_AUXILIARY_CHARACTERISTIC_OUTSIDE_FIXED_CONE"
    else:
        status = "PASS_NORMALIZED_FIXED_LIGHT_CONE_DOMAIN"
    return {
        **bounds,
        "status": status,
        "tau_flux": config.tau_flux,
        "beta_wave": config.beta_wave,
        "tau_margin": tau_margin,
        "beta_margin": beta_margin,
        "matter_characteristic_speed_max": matter_speed,
        "auxiliary_characteristic_speed": auxiliary_speed,
        "maximum_characteristic_speed": max(matter_speed, auxiliary_speed),
        "matter_family_within_cone": matter_pass,
        "auxiliary_family_within_cone": auxiliary_pass,
        "within_fixed_light_cone": bool(strict and matter_pass and auxiliary_pass),
        "parameter_fitting": False,
    }


def evaluate_parameter_sequence(
    *,
    alpha_values: Any,
    tau_values: Any,
    beta_values: Any,
    gamma_values: Any,
    max_abs_C: float,
    normalized_light_speed: float = 1.0,
) -> dict[str, Any]:
    """Evaluate the analytic inequalities for an explicitly supplied sequence."""

    arrays = _matching_vectors(
        alpha_values=alpha_values,
        tau_values=tau_values,
        beta_values=beta_values,
        gamma_values=gamma_values,
    )
    if any(np.any(arrays[name] <= 0.0) for name in arrays):
        raise ValueError("all parameter sequence values must be positive")
    light_speed = _positive_scalar(
        normalized_light_speed, "normalized_light_speed"
    )
    amplitude = _amplitude(max_abs_C)
    max_curvature = arrays["alpha_values"] + 3.0 * amplitude**2 - 1.0
    tau_required = max_curvature / light_speed**2
    beta_required = arrays["gamma_values"] / light_speed**2
    strict = arrays["alpha_values"] > 1.0
    matter_speed = np.sqrt(max_curvature / arrays["tau_values"])
    auxiliary_speed = np.sqrt(
        arrays["gamma_values"] / arrays["beta_values"]
    )
    matter_pass = arrays["tau_values"] >= tau_required
    auxiliary_pass = arrays["beta_values"] >= beta_required
    feasible = strict & matter_pass & auxiliary_pass
    return {
        **arrays,
        "max_abs_C": amplitude,
        "normalized_light_speed": light_speed,
        "minimum_tau_values": tau_required,
        "minimum_beta_values": beta_required,
        "matter_characteristic_speeds": matter_speed,
        "auxiliary_characteristic_speeds": auxiliary_speed,
        "maximum_characteristic_speeds": np.maximum(
            matter_speed, auxiliary_speed
        ),
        "strict_hyperbolicity": strict,
        "matter_cone_pass": matter_pass,
        "auxiliary_cone_pass": auxiliary_pass,
        "feasible": feasible,
        "all_feasible": bool(np.all(feasible)),
        "tau_violation_factors": tau_required / arrays["tau_values"],
        "beta_violation_factors": beta_required / arrays["beta_values"],
    }


def fixed_cone_parabolic_limit_no_go(
    *,
    max_abs_C: float,
    normalized_light_speed: float = 1.0,
) -> dict[str, Any]:
    """Return the analytic incompatibility of two simultaneous exact limits.

    At fixed finite ``c_hat``, Cahn-Hilliard recovery asks for
    ``alpha->infinity`` and ``tau->0``.  The matter characteristic bound asks
    for ``tau >= (alpha+3*Cmax**2-1)/c_hat**2``, whose right-hand side instead
    diverges.  Therefore no parameter sequence can satisfy both exact limits.

    This statement is only about this normalized comparator and its declared
    speed formula.  It is not a theorem about every causal phase-field theory.
    """

    amplitude = _amplitude(max_abs_C)
    light_speed = _positive_scalar(
        normalized_light_speed, "normalized_light_speed"
    )
    return {
        "status": "ANALYTIC_NO_COMMON_EXACT_LIMIT",
        "scope": "normalized_external_comparator_on_symmetric_amplitude_domain",
        "max_abs_C": amplitude,
        "normalized_light_speed": light_speed,
        "fixed_cone_lower_bound": (
            "tau_flux >= (alpha_penalty + 3*max_abs_C**2 - 1) / c_hat**2"
        ),
        "parabolic_target": "alpha_penalty -> infinity and tau_flux -> 0",
        "asymptotic_consequence": (
            "tau_flux_lower_bound -> infinity as alpha_penalty -> infinity"
        ),
        "common_exact_sequence_exists": False,
        "allowed_interpretation": (
            "retain finite relaxation/auxiliary dynamics, or use parabolic "
            "Cahn-Hilliard only as a long-time low-wavenumber approximation"
        ),
        "forbidden_generalization": (
            "this does not rule out all causal phase-field completions"
        ),
    }


def map_external_flux_law_to_current(
    flux_impulse: Any,
    chemical_gradient: Any,
    tau_flux: float,
) -> LocalCurrentLawMap:
    """Map ``q_t + grad(mu) = -q/tau`` to ``tau*J_t+J=-grad(mu)``.

    The exact map uses constant positive ``tau`` and ``J=q/tau``.  Its mobility
    is one.  Different spatial staggering or a non-unit mobility requires an
    additional discretization/constitutive map and is not silently inferred.
    """

    arrays = _matching_vectors(
        flux_impulse=flux_impulse,
        chemical_gradient=chemical_gradient,
    )
    tau = _positive_scalar(tau_flux, "tau_flux")
    q = arrays["flux_impulse"]
    gradient = arrays["chemical_gradient"]
    q_rate = -gradient - q / tau
    current = q / tau
    current_rate = q_rate / tau
    residual = tau * current_rate + current + gradient
    return LocalCurrentLawMap(
        physical_current=np.asarray(current, dtype=float),
        flux_impulse_rate=np.asarray(q_rate, dtype=float),
        physical_current_rate=np.asarray(current_rate, dtype=float),
        current_law_residual=np.asarray(residual, dtype=float),
        max_abs_residual=float(np.max(np.abs(residual))),
    )


def hyperbolic_phase_field_bridge_contract() -> dict[str, Any]:
    """Return achieved scope, mapping layers, and the next blocker."""

    return {
        "status": HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS,
        "role": "normalized_analytic_feasibility_and_mapping_readiness_gate",
        "achieved": {
            "fixed_amplitude_curvature_bounds": "DERIVED_EXACT",
            "fixed_light_cone_parameter_inequalities": "DERIVED_EXACT",
            "exact_parabolic_fixed_cone_common_limit": "ANALYTIC_NO_GO",
            "external_q_to_local_current_law": "EXACT_MOBILITY_ONE_ALGEBRAIC_MAP",
        },
        "mapping_layers": {
            "algebraic_local_current_law": "PASS",
            "source_order_parameter_to_uet_noether_density": "BLOCKED",
            "normalized_1d_to_covariant_current": "BLOCKED",
            "classical_entropy_current_and_bianchi_closure": "BLOCKED",
            "thermal_stochastic_sk_kms_completion": "BLOCKED_DOWNSTREAM",
        },
        "forbidden_identifications": [
            "external_C_is_not_yet_the_UET_Noether_density",
            "external_auxiliary_phase_is_not_UET_space_response",
            "external_auxiliary_phase_is_not_information_or_trace",
            "a_local_flux_map_is_not_a_covariant_UET_derivation",
            "a_fixed_cone_parameter_bound_is_not_physical_validation",
        ],
        "trace_input": False,
        "trace_backreaction": False,
        "global_universe_closure": "UNRESOLVED",
        "gr_null_branch": "epsilon_nc_equals_zero_remains_exact_GR_response_null",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    }
