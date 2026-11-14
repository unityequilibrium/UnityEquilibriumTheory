"""Strict finite-cone recurrence for the non-conserved C/Phi candidate.

The recurrence is a separate opt-in lane. It uses a centered telegraph update
whose spatial stencil is one cell per macro step at strict CFL=1. It is not
used by the legacy or conserved-C operators, and it does not turn C into mass.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from docs.core.uet_matter_space_finite_cone import (
    FINITE_CONE_C_OPERATOR_MODE,
    FiniteConeCConfig,
    FiniteConeCState,
    finite_cone_c_chemical_potentials,
)
from docs.core.uet_spatial import (
    face_gradient_1d,
    integral_1d,
    laplacian_1d,
    validate_dx,
    validate_field_1d,
)
from docs.core.uet_trace import TraceKernelConfig, compute_spacetime_trace

CHARACTERISTIC_CONE_OPERATOR_MODE = "matter_space_characteristic_cone_v1"


class CharacteristicConeStabilityError(ValueError):
    """Raised when the strict compact-support CFL contract is not met."""

    def __init__(self, dt: float, required_dt: float) -> None:
        self.dt = float(dt)
        self.required_dt = float(required_dt)
        super().__init__(
            f"strict CFL=1 requires dt={self.required_dt:.12g}; received dt={self.dt:.12g}"
        )


def characteristic_cone_speed(config: FiniteConeCConfig) -> float:
    """Return the global declared speed used by the compact grid cone."""

    return max(config.matter_speed, config.space_speed)


def characteristic_cone_dt(dx: float, config: FiniteConeCConfig) -> float:
    spacing = validate_dx(dx)
    speed = characteristic_cone_speed(config)
    if not np.isfinite(speed) or speed <= 0.0:
        raise ValueError("characteristic cone speed must be finite and positive")
    return float(spacing / speed)


def _strict_cfl(dt: float, dx: float, config: FiniteConeCConfig) -> float:
    required = characteristic_cone_dt(dx, config)
    if not np.isclose(float(dt), required, rtol=1.0e-10, atol=1.0e-12):
        raise CharacteristicConeStabilityError(float(dt), required)
    return float(characteristic_cone_speed(config) * float(dt) / float(dx))


def _telegraph_recurrence(
    current: np.ndarray,
    previous: np.ndarray,
    other_current: np.ndarray,
    dt: float,
    dx: float,
    tau: float,
    mobility: float,
    kappa: float,
    local_force: np.ndarray,
    source: np.ndarray,
    boundary_condition: str,
) -> np.ndarray:
    """Advance one field using the centered damped-wave recurrence."""

    spacing = validate_dx(dx)
    coefficient = tau / (dt * dt)
    damping = 1.0 / (2.0 * dt)
    denominator = coefficient + damping
    laplacian = laplacian_1d(current, spacing, boundary_condition)
    numerator = (
        2.0 * coefficient * current
        + (-coefficient + damping) * previous
        + mobility * kappa * laplacian
        - mobility * local_force
        + source
    )
    return numerator / denominator


def _paired_energy(
    current_C: np.ndarray,
    previous_C: np.ndarray,
    current_Phi: np.ndarray,
    previous_Phi: np.ndarray,
    dt: float,
    dx: float,
    config: FiniteConeCConfig,
) -> float:
    """Energy paired with the centered recurrence, using centered velocities."""

    spacing = validate_dx(dx)
    C_velocity = (current_C - previous_C) / dt
    Phi_velocity = (current_Phi - previous_Phi) / dt
    C_gradient = face_gradient_1d(current_C, spacing, config.boundary_condition)
    previous_C_gradient = face_gradient_1d(previous_C, spacing, config.boundary_condition)
    Phi_gradient = face_gradient_1d(current_Phi, spacing, config.boundary_condition)
    previous_Phi_gradient = face_gradient_1d(previous_Phi, spacing, config.boundary_condition)

    def local(C: np.ndarray, Phi: np.ndarray) -> np.ndarray:
        return (
            0.5 * config.a_C * C**2
            + 0.25 * config.b_C * C**4
            + 0.5 * config.a_space * Phi**2
            + 0.25 * config.b_space * Phi**4
            - 0.5 * config.coupling_g * C**2 * Phi
        )

    kinetic = (
        config.tau_C / (2.0 * config.mobility_C) * integral_1d(C_velocity**2, spacing)
        + config.tau_space / (2.0 * config.mobility_space) * integral_1d(Phi_velocity**2, spacing)
    )
    gradient = 0.5 * config.kappa_C * float(
        np.sum(C_gradient * previous_C_gradient) * spacing
    )
    gradient += 0.5 * config.kappa_space * float(
        np.sum(Phi_gradient * previous_Phi_gradient) * spacing
    )
    local_energy = integral_1d(
        0.5 * (local(current_C, current_Phi) + local(previous_C, previous_Phi)),
        spacing,
    )
    return float(kinetic + gradient + local_energy)

def characteristic_cone_step(
    state: FiniteConeCState,
    dt: float,
    dx: float,
    config: FiniteConeCConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
    trace_history: Optional[list[np.ndarray]] = None,
    trace_config: Optional[TraceKernelConfig] = None,
):
    """Advance the selected non-conserved C/Phi candidate with compact support.

    C_rate and space_rate are forward rates in this lane. Therefore the
    previous field is reconstructed exactly as current - dt * rate, and no
    field clipping or cone padding is applied.
    """

    step = float(dt)
    spacing = validate_dx(dx)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    cfl = _strict_cfl(step, spacing, config)
    physical = state.copy()
    matter = (
        np.zeros_like(physical.C)
        if matter_source is None
        else validate_field_1d(matter_source, "matter_source")
    )
    space = (
        np.zeros_like(physical.C)
        if space_source is None
        else validate_field_1d(space_source, "space_source")
    )
    if matter.shape != physical.C.shape or space.shape != physical.C.shape:
        raise ValueError("source arrays must match the finite-cone state shape")

    previous_C = physical.C - step * physical.C_rate
    previous_Phi = physical.space_response - step * physical.space_rate
    mu_C, mu_Phi = finite_cone_c_chemical_potentials(physical, spacing, config)
    local_C = mu_C + config.kappa_C * laplacian_1d(
        physical.C, spacing, config.boundary_condition
    )
    local_Phi = mu_Phi + config.kappa_space * laplacian_1d(
        physical.space_response, spacing, config.boundary_condition
    )
    next_C = _telegraph_recurrence(
        physical.C,
        previous_C,
        physical.space_response,
        step,
        spacing,
        config.tau_C,
        config.mobility_C,
        config.kappa_C,
        local_C,
        matter,
        config.boundary_condition,
    )
    next_Phi = _telegraph_recurrence(
        physical.space_response,
        previous_Phi,
        physical.C,
        step,
        spacing,
        config.tau_space,
        config.mobility_space,
        config.kappa_space,
        local_Phi,
        space,
        config.boundary_condition,
    )
    updated = FiniteConeCState(
        next_C,
        (next_C - physical.C) / step,
        next_Phi,
        (next_Phi - physical.space_response) / step,
    )

    energy_before = _paired_energy(physical.C, previous_C, physical.space_response, previous_Phi, step, spacing, config)
    energy_after = _paired_energy(next_C, physical.C, next_Phi, physical.space_response, step, spacing, config)
    mid_C_rate = (next_C - previous_C) / (2.0 * step)
    mid_Phi_rate = (next_Phi - previous_Phi) / (2.0 * step)
    dissipation = integral_1d(
        mid_C_rate**2 / config.mobility_C
        + mid_Phi_rate**2 / config.mobility_space,
        spacing,
    )
    source_power = integral_1d(
        mid_C_rate * matter / config.mobility_C
        + mid_Phi_rate * space / config.mobility_space,
        spacing,
    )
    predicted_delta = step * (-dissipation + source_power)
    actual_delta = energy_after - energy_before
    closure_residual = actual_delta - predicted_delta
    closure_scale = max(abs(actual_delta), abs(predicted_delta), step * dissipation, 1e-12)
    closure_relative = abs(closure_residual) / closure_scale

    trace_source = 0.5 * (
        ((physical.C - previous_C) / step)**2 / config.mobility_C
        + ((physical.space_response - previous_Phi) / step)**2 / config.mobility_space
        + ((next_C - physical.C) / step)**2 / config.mobility_C
        + ((next_Phi - physical.space_response) / step)**2 / config.mobility_space
    )
    trace_observable = None
    if trace_config is not None:
        history = [
            validate_field_1d(sample, "trace_history_sample").copy()
            for sample in (trace_history or [])
        ]
        if any(sample.shape != physical.C.shape for sample in history):
            raise ValueError("trace_history samples must match the state shape")
        trace_observable = compute_spacetime_trace(
            history + [trace_source],
            spacing,
            step,
            trace_config,
            shape=physical.C.shape,
        )

    no_external_drive = not np.any(matter) and not np.any(space)
    energy_tolerance = config.ledger_tolerance * max(abs(energy_before), 1.0)
    energy_descent = (not no_external_drive) or actual_delta <= energy_tolerance
    ledger_gate = closure_relative <= config.ledger_tolerance
    diagnostics: Dict[str, Any] = {
        "operator_mode": CHARACTERISTIC_CONE_OPERATOR_MODE,
        "parent_candidate_mode": FINITE_CONE_C_OPERATOR_MODE,
        "C_lane": "C_telegraph_candidate",
        "rate_semantics": "forward_difference_rate",
        "trace_backreaction": False,
        "strict_cfl": cfl,
        "declared_cone_speed": characteristic_cone_speed(config),
        "matter_speed": config.matter_speed,
        "space_speed": config.space_speed,
        "required_dt": characteristic_cone_dt(spacing, config),
        "field_clipping_applied": False,
        "cone_padding_applied": False,
        "parameter_fitting_applied": False,
        "mass_density_mapping": "NOT_DEFINED",
        "covariant_completion": "BLOCKED",
        "claim_boundary": "candidate normalized compact-support finite-cone collective response",
    }
    energy_ledger: Dict[str, Any] = {
        "units_lane": config.unit_lane,
        "operator_mode": CHARACTERISTIC_CONE_OPERATOR_MODE,
        "extended_energy_before": energy_before,
        "extended_energy_after": energy_after,
        "actual_delta": actual_delta,
        "predicted_delta": predicted_delta,
        "closure_residual": closure_residual,
        "closure_relative": closure_relative,
        "dissipation": dissipation,
        "input_power": source_power,
        "ledger_gate": "PASS" if ledger_gate else "FAIL",
        "energy_descent_gate": "PASS" if energy_descent else "FAIL",
        "mass_conservation": "NOT_APPLICABLE_NONCONSERVATIVE_C_LANE",
        "joule_claim": False,
    }
    from docs.core.uet_trace import UETStepResult

    return UETStepResult(
        C=updated.C,
        V=updated.C_rate,
        trace_observable=trace_observable,
        energy_ledger=energy_ledger,
        diagnostics=diagnostics,
        space_response=updated.space_response,
        space_rate=updated.space_rate,
    )


def characteristic_cone_contract() -> Dict[str, Any]:
    return {
        "operator_mode": CHARACTERISTIC_CONE_OPERATOR_MODE,
        "parent_mode": FINITE_CONE_C_OPERATOR_MODE,
        "equation": "tau*u_tt+u_t=M*kappa*Laplacian(u)-M*local_force+source",
        "C_lane": "C_telegraph_candidate",
        "support_contract": "strict CFL=1, one spatial stencil cell per macro step",
        "declared_cone_speed": "max(sqrt(M_C*kappa_C/tau_C), sqrt(M_Phi*kappa_Phi/tau_Phi))",
        "trace_backreaction": False,
        "unit_lane": "normalized_only_v1",
        "clipping": False,
        "cone_padding": False,
        "SI_status": "BLOCKED",
        "physical_observable_mapping": "OPEN",
        "evidence_status": "CANDIDATE",
    }


__all__ = [
    "CHARACTERISTIC_CONE_OPERATOR_MODE",
    "CharacteristicConeStabilityError",
    "characteristic_cone_contract",
    "characteristic_cone_dt",
    "characteristic_cone_speed",
    "characteristic_cone_step",
]
