"""Opt-in dynamical-stability diagnostics for normalized UET research lanes.

Chaos is treated here as a property of a declared evolution operator, not as a
new UET state variable or a new term in the matter-space equations.  The
physical tangent state is ``(delta_C, delta_Phi, delta_Pi)``; derived traces and
observer records are deliberately excluded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Sequence

import numpy as np

from docs.core.uet_matter_space import (
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_rhs,
    matter_space_stability_limit,
)
from docs.core.uet_spatial import laplacian_1d, validate_dx


TANGENT_MAP_ID = "uet.dynamics.tangent_map"
LYAPUNOV_SPECTRUM_ID = "uet.dynamics.lyapunov_spectrum"
REGIME_CLASSIFIER_ID = "uet.dynamics.regime_classifier"
GRADIENT_BOUNDARY_ID = "uet.dynamics.closed_gradient_no_sustained_chaos_boundary"

CLASSIFICATIONS = {
    "NUMERICAL_INSTABILITY",
    "NONCHAOTIC_STABLE_DIAGNOSTIC",
    "TRANSIENT_SENSITIVITY_ONLY",
    "MARGINAL_OR_UNRESOLVED",
    "CHAOS_CANDIDATE_DIAGNOSTIC",
}


@dataclass(frozen=True)
class LyapunovEstimate:
    """A normalized-lane Lyapunov estimate and its numerical resolution."""

    lambda_max: float
    block_standard_error: float
    samples: int
    elapsed_time: float
    estimator: str


def pack_matter_space_state(state: MatterSpaceState) -> np.ndarray:
    """Pack only the physical ``(C, Phi, Pi)`` state into one vector."""

    return np.concatenate((state.C, state.space_response, state.space_rate)).astype(float)


def unpack_matter_space_state(vector: np.ndarray, field_size: int) -> MatterSpaceState:
    """Build a matter-space state from a packed physical-state vector."""

    values = np.asarray(vector, dtype=float)
    if values.ndim != 1 or values.size != 3 * field_size:
        raise ValueError("packed matter-space state must contain exactly 3 * field_size values")
    return MatterSpaceState(
        values[:field_size],
        values[field_size : 2 * field_size],
        values[2 * field_size :],
    )


def normalized_block_norm(vector: np.ndarray, field_size: int) -> float:
    """Return an equal-block normalized L2 norm for ``C``, ``Phi``, and ``Pi``."""

    state = unpack_matter_space_state(vector, field_size)
    block_means = (
        np.mean(np.square(state.C)),
        np.mean(np.square(state.space_response)),
        np.mean(np.square(state.space_rate)),
    )
    return float(np.sqrt(sum(block_means)))


def matter_space_tangent_chemical_potentials(
    state: MatterSpaceState,
    perturbation: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate the exact discrete Jacobian action on ``(delta_C, delta_Phi)``."""

    spacing = validate_dx(dx)
    C = state.C
    Phi = state.space_response
    delta_C = perturbation.C
    delta_Phi = perturbation.space_response
    delta_mu_C = (
        (config.a_matter + 3.0 * config.b_matter * C**2 - config.coupling_g * Phi)
        * delta_C
        - config.coupling_g * C * delta_Phi
        - config.kappa_matter
        * laplacian_1d(delta_C, spacing, config.boundary_condition)
    )
    delta_mu_Phi = (
        (config.a_space + 3.0 * config.b_space * Phi**2) * delta_Phi
        - config.coupling_g * C * delta_C
        - config.kappa_space
        * laplacian_1d(delta_Phi, spacing, config.boundary_condition)
    )
    return delta_mu_C, delta_mu_Phi


def matter_space_tangent_rhs(
    state: MatterSpaceState,
    perturbation: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> MatterSpaceState:
    """Return the tangent RHS for prescribed state-independent source histories."""

    spacing = validate_dx(dx)
    delta_mu_C, delta_mu_Phi = matter_space_tangent_chemical_potentials(
        state, perturbation, spacing, config
    )
    if config.matter_dynamics == "conserved":
        delta_dC = config.mobility_matter * laplacian_1d(
            delta_mu_C, spacing, config.boundary_condition
        )
    else:
        delta_dC = -config.mobility_matter * delta_mu_C
    delta_dPhi = perturbation.space_rate.copy()
    delta_dPi = (
        -perturbation.space_rate - config.mobility_space * delta_mu_Phi
    ) / config.tau_space
    return MatterSpaceState(delta_dC, delta_dPhi, delta_dPi)


def matter_space_tangent_heun_step(
    state: MatterSpaceState,
    perturbation: MatterSpaceState,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
) -> tuple[MatterSpaceState, MatterSpaceState]:
    """Advance a base state and tangent state with the same Heun/RK2 discretization.

    Sources are prescribed arrays and therefore have zero tangent contribution.
    State-dependent sources are intentionally unsupported until their JVP is
    declared explicitly.
    """

    step_size = float(dt)
    max_dt = matter_space_stability_limit(state, dx, config)
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("dt must be finite and positive")
    if step_size > max_dt * (1.0 + 1e-12):
        raise ValueError("dt exceeds the matter-space stability preflight bound")

    k1 = matter_space_rhs(state, dx, config, matter_source, space_source)[:3]
    dk1 = matter_space_tangent_rhs(state, perturbation, dx, config)
    predictor = MatterSpaceState(
        state.C + step_size * k1[0],
        state.space_response + step_size * k1[1],
        state.space_rate + step_size * k1[2],
    )
    delta_predictor = MatterSpaceState(
        perturbation.C + step_size * dk1.C,
        perturbation.space_response + step_size * dk1.space_response,
        perturbation.space_rate + step_size * dk1.space_rate,
    )
    k2 = matter_space_rhs(predictor, dx, config, matter_source, space_source)[:3]
    dk2 = matter_space_tangent_rhs(predictor, delta_predictor, dx, config)
    updated = MatterSpaceState(
        state.C + 0.5 * step_size * (k1[0] + k2[0]),
        state.space_response + 0.5 * step_size * (k1[1] + k2[1]),
        state.space_rate + 0.5 * step_size * (k1[2] + k2[2]),
    )
    updated_delta = MatterSpaceState(
        perturbation.C + 0.5 * step_size * (dk1.C + dk2.C),
        perturbation.space_response
        + 0.5 * step_size * (dk1.space_response + dk2.space_response),
        perturbation.space_rate
        + 0.5 * step_size * (dk1.space_rate + dk2.space_rate),
    )
    return updated, updated_delta


def _block_standard_error(values: Sequence[float]) -> float:
    samples = np.asarray(values, dtype=float)
    if samples.size < 2:
        return 0.0
    return float(np.std(samples, ddof=1) / np.sqrt(samples.size))


def benettin_qr(
    step: Callable[[np.ndarray, int], np.ndarray],
    tangent_step: Callable[[np.ndarray, np.ndarray, int], np.ndarray],
    initial_state: np.ndarray,
    dt: float,
    steps: int,
    transient_steps: int = 0,
    renormalization_interval: int = 1,
    spectrum_size: Optional[int] = None,
) -> dict[str, Any]:
    """Estimate a Lyapunov spectrum with tangent evolution and QR renormalization."""

    state = np.asarray(initial_state, dtype=float).copy()
    dimension = state.size
    count = dimension if spectrum_size is None else int(spectrum_size)
    if count < 1 or count > dimension:
        raise ValueError("spectrum_size must be between one and the state dimension")
    if steps <= transient_steps or renormalization_interval < 1 or dt <= 0.0:
        raise ValueError("invalid Lyapunov integration controls")
    basis = np.eye(dimension, count, dtype=float)
    logs: list[np.ndarray] = []
    interval_logs: list[float] = []
    for index in range(steps):
        previous = state
        state = np.asarray(step(previous, index), dtype=float)
        basis = np.asarray(tangent_step(previous, basis, index), dtype=float)
        if (index + 1) % renormalization_interval != 0:
            continue
        basis, upper = np.linalg.qr(basis, mode="reduced")
        if index + 1 <= transient_steps:
            continue
        diagonal = np.maximum(np.abs(np.diag(upper)), np.finfo(float).tiny)
        log_growth = np.log(diagonal)
        logs.append(log_growth)
        interval_logs.append(float(log_growth[0] / (dt * renormalization_interval)))
    if not logs:
        raise ValueError("no post-transient Lyapunov samples were collected")
    elapsed = len(logs) * dt * renormalization_interval
    spectrum = np.sum(np.asarray(logs), axis=0) / elapsed
    return {
        "lambda_spectrum": spectrum.tolist(),
        "lambda_max": float(spectrum[0]),
        "block_standard_error": _block_standard_error(interval_logs),
        "samples": len(logs),
        "elapsed_time": float(elapsed),
        "estimator": "BENETTIN_QR_TANGENT",
    }


def shadow_trajectory_exponent(
    step: Callable[[np.ndarray, int], np.ndarray],
    initial_state: np.ndarray,
    dt: float,
    steps: int,
    perturbation_amplitude: float,
    transient_steps: int = 0,
    renormalization_interval: int = 1,
    direction: Optional[np.ndarray] = None,
) -> dict[str, Any]:
    """Estimate the largest exponent from periodically renormalized shadow states."""

    reference = np.asarray(initial_state, dtype=float).copy()
    if direction is None:
        direction_values = np.ones_like(reference)
    else:
        direction_values = np.asarray(direction, dtype=float).copy()
    direction_norm = float(np.linalg.norm(direction_values))
    if direction_norm == 0.0 or perturbation_amplitude <= 0.0:
        raise ValueError("shadow perturbation must be nonzero and positive")
    direction_values /= direction_norm
    shadow = reference + perturbation_amplitude * direction_values
    interval_rates: list[float] = []
    for index in range(steps):
        reference = np.asarray(step(reference, index), dtype=float)
        shadow = np.asarray(step(shadow, index), dtype=float)
        if (index + 1) % renormalization_interval != 0:
            continue
        separation = shadow - reference
        distance = float(np.linalg.norm(separation))
        if not np.isfinite(distance) or distance <= np.finfo(float).tiny:
            distance = np.finfo(float).tiny
            separation = direction_values * distance
        rate = np.log(distance / perturbation_amplitude) / (
            dt * renormalization_interval
        )
        if index + 1 > transient_steps:
            interval_rates.append(float(rate))
        shadow = reference + perturbation_amplitude * separation / distance
    if not interval_rates:
        raise ValueError("no post-transient shadow samples were collected")
    values = np.asarray(interval_rates)
    return {
        "lambda_max": float(np.mean(values)),
        "block_standard_error": _block_standard_error(interval_rates),
        "samples": len(interval_rates),
        "elapsed_time": float(len(interval_rates) * dt * renormalization_interval),
        "estimator": "SHADOW_PERIODIC_RENORMALIZATION",
    }


def lyapunov_resolution(
    dt_difference: float,
    dx_difference: float,
    block_standard_error: float,
    method_disagreement: float,
) -> float:
    """Return the preregistered sign-resolution envelope."""

    values = (
        abs(float(dt_difference)),
        abs(float(dx_difference)),
        2.0 * abs(float(block_standard_error)),
        abs(float(method_disagreement)),
    )
    if not all(np.isfinite(value) for value in values):
        raise ValueError("resolution inputs must be finite")
    return max(values)


def classify_dynamical_regime(
    *,
    lambda_max: float,
    lambda_resolution_value: float,
    early_ftle_positive: bool,
    boundedness: bool,
    stationarity: bool,
    ledger_pass: bool,
    conservation_pass: bool,
    causal_pass: bool,
    method_agreement: bool,
) -> str:
    """Classify evidence without turning a positive finite-time slope into proof."""

    if not all((boundedness, ledger_pass, conservation_pass, causal_pass)):
        return "NUMERICAL_INSTABILITY"
    if not method_agreement or abs(lambda_max) <= lambda_resolution_value:
        return "MARGINAL_OR_UNRESOLVED"
    if lambda_max > lambda_resolution_value:
        if stationarity:
            return "CHAOS_CANDIDATE_DIAGNOSTIC"
        return "TRANSIENT_SENSITIVITY_ONLY"
    if early_ftle_positive:
        return "TRANSIENT_SENSITIVITY_ONLY"
    return "NONCHAOTIC_STABLE_DIAGNOSTIC"


def validate_diagnostic_contract(record: Mapping[str, Any]) -> None:
    """Validate the common machine-readable chaos diagnostic surface."""

    required = {
        "diagnostic_id",
        "owner_topic",
        "equation_registry_ids",
        "state_variables",
        "excluded_variables",
        "unit_lane",
        "forcing_class",
        "noise_coupling",
        "state_metric",
        "estimator",
        "transient_window",
        "renormalization_interval",
        "perturbation_amplitudes",
        "resolution_grid",
        "lambda_max",
        "lambda_spectrum",
        "confidence_or_block_error",
        "lambda_resolution",
        "boundedness",
        "stationarity",
        "ledger_status",
        "conservation_status",
        "causal_status",
        "method_agreement",
        "classification",
        "controlling_blocker",
        "evidence_hashes",
        "claim_boundary",
    }
    missing = sorted(required.difference(record))
    if missing:
        raise ValueError(f"missing chaos diagnostic fields: {missing}")
    if record["classification"] not in CLASSIFICATIONS:
        raise ValueError("unknown chaos diagnostic classification")
    if "R_gen" in record["state_variables"] or "R_obs" in record["state_variables"]:
        raise ValueError("R_gen and R_obs are not dynamical state variables")
    if not {"R_gen", "R_obs"}.issubset(set(record["excluded_variables"])):
        raise ValueError("the diagnostic must explicitly exclude R_gen and R_obs")
