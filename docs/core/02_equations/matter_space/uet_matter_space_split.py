"""Opt-in changing-C split bridge for the causal Phi/Pi lane.

The bridge is deliberately a research diagnostic, not a replacement for the
default matter-space operator.  It subcycles the conserved C gradient flow at
fixed time-averaged Phi, then advances Phi/Pi with the verified causal
discrete-gradient step.  The shared two-level ledger exposes the remaining
operator-splitting residual instead of hiding it.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np

from docs.core.uet_matter_space import (
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_chemical_potentials,
    matter_space_stability_limit,
)
from docs.core.uet_matter_space_causal import (
    causal_space_discrete_energy,
    causal_space_discrete_gradient_step,
)
from docs.core.uet_spatial import (
    gradient_energy_integral_1d,
    gradient_squared_cell_1d,
    integral_1d,
    laplacian_1d,
    validate_dx,
    validate_field_1d,
)


MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE = "matter_space_causal_split_v1"


def causal_split_energy(
    state: MatterSpaceState,
    previous_space_response: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return the shared two-level energy used by the split diagnostic."""

    spacing = validate_dx(dx)
    previous = validate_field_1d(previous_space_response, "previous_space_response")
    if previous.shape != state.space_response.shape:
        raise ValueError("previous_space_response must match the physical state shape")
    matter_local = (
        0.5 * config.a_matter * state.C**2
        + 0.25 * config.b_matter * state.C**4
    )
    matter_energy = integral_1d(matter_local, spacing)
    matter_energy += 0.5 * config.kappa_matter * gradient_energy_integral_1d(
        state.C, spacing, config.boundary_condition
    )
    return float(
        matter_energy
        + causal_space_discrete_energy(
            state.space_response,
            previous,
            state.C,
            dt,
            spacing,
            config,
        )
    )


def _validate_conserved_source(
    source: np.ndarray,
    dx: float,
    state_size: int,
) -> np.ndarray:
    value = validate_field_1d(source, "matter_source")
    if value.size != state_size:
        raise ValueError("matter_source must match the physical state shape")
    net = abs(integral_1d(value, dx))
    scale = max(integral_1d(np.abs(value), dx), 1.0)
    if net > 1.0e-12 * scale:
        raise ValueError("conserved matter_source must satisfy integral J_C dx = 0")
    return value


def _matter_rhs_and_ledger(
    C: np.ndarray,
    phi_average: np.ndarray,
    dx: float,
    config: MatterSpaceConfig,
    source: np.ndarray,
) -> Tuple[np.ndarray, float, float]:
    temporary = MatterSpaceState(C, phi_average, np.zeros_like(C))
    mu_C, _ = matter_space_chemical_potentials(temporary, dx, config)
    dC = config.mobility_matter * laplacian_1d(
        mu_C, dx, config.boundary_condition
    ) + source
    dissipation = integral_1d(
        config.mobility_matter
        * gradient_squared_cell_1d(mu_C, dx, config.boundary_condition),
        dx,
    )
    source_power = integral_1d(mu_C * source, dx)
    return dC, float(dissipation), float(source_power)


def causal_matter_space_split_step(
    state: MatterSpaceState,
    previous_space_response: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
) -> Tuple[MatterSpaceState, np.ndarray, Dict[str, Any]]:
    """Advance a conserved-C split step and expose its shared ledger.

    ``C`` is subcycled with the average of current and previous Phi held fixed
    so that the coupling term matches the two-level Phi energy.  The causal
    Phi/Pi update then uses the changed C explicitly.  The method rejects the
    non-conserved C lane in v1 and never applies trace feedback.
    """

    if config.matter_dynamics != "conserved":
        raise NotImplementedError(
            "matter_space_causal_split_v1 currently requires conserved C"
        )
    spacing = validate_dx(dx)
    step = float(dt)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    previous = validate_field_1d(previous_space_response, "previous_space_response")
    if previous.shape != state.space_response.shape:
        raise ValueError("previous_space_response must match the physical state shape")
    matter_drive = (
        np.zeros_like(state.C)
        if matter_source is None
        else _validate_conserved_source(matter_source, spacing, state.C.size)
    )
    if space_source is None:
        space_drive = np.zeros_like(state.C)
    else:
        space_drive = validate_field_1d(space_source, "space_source")
        if space_drive.shape != state.C.shape:
            raise ValueError("space_source must match the physical state shape")

    total_before = causal_split_energy(state, previous, step, spacing, config)
    phi_average = 0.5 * (state.space_response + previous)
    C = state.C.copy()
    c_limit_state = MatterSpaceState(C, phi_average, np.zeros_like(C))
    c_limit = matter_space_stability_limit(c_limit_state, spacing, config)
    if not np.isfinite(c_limit) or c_limit <= 0.0:
        raise ValueError("conserved C substep has no positive stability limit")
    substeps = max(1, int(np.ceil(step / c_limit)))
    sub_dt = step / substeps
    matter_dissipation_work = 0.0
    matter_source_work = 0.0
    matter_ledger_residual = 0.0

    for _ in range(substeps):
        before_state = MatterSpaceState(C, phi_average, np.zeros_like(C))
        before_energy = causal_split_energy(
            before_state, previous, step, spacing, config
        )
        k1, dissipation_1, source_power_1 = _matter_rhs_and_ledger(
            C, phi_average, spacing, config, matter_drive
        )
        midpoint = C + sub_dt * k1
        k2, dissipation_2, source_power_2 = _matter_rhs_and_ledger(
            midpoint, phi_average, spacing, config, matter_drive
        )
        C = C + 0.5 * sub_dt * (k1 + k2)
        after_state = MatterSpaceState(C, phi_average, np.zeros_like(C))
        after_energy = causal_split_energy(
            after_state, previous, step, spacing, config
        )
        predicted_delta = sub_dt * (
            -0.5 * (dissipation_1 + dissipation_2)
            + 0.5 * (source_power_1 + source_power_2)
        )
        matter_ledger_residual += after_energy - before_energy - predicted_delta
        matter_dissipation_work += 0.5 * sub_dt * (dissipation_1 + dissipation_2)
        matter_source_work += 0.5 * sub_dt * (source_power_1 + source_power_2)

    changed_C_state = MatterSpaceState(C, state.space_response, state.space_rate)
    updated, old_phi, phi_ledger = causal_space_discrete_gradient_step(
        changed_C_state,
        previous,
        step,
        spacing,
        config,
        space_source=space_drive,
    )
    phi_before = causal_space_discrete_energy(
        state.space_response, previous, C, step, spacing, config
    )
    phi_after = causal_space_discrete_energy(
        updated.space_response, old_phi, C, step, spacing, config
    )
    phi_damping_work = (
        np.sum((updated.space_response - previous) ** 2)
        * spacing
        / (4.0 * config.mobility_space * step)
    )
    phi_ledger_residual = (
        phi_after
        - phi_before
        + phi_damping_work
        - phi_ledger["source_work"]
    )
    total_after = causal_split_energy(updated, old_phi, step, spacing, config)
    expected_delta = (
        -matter_dissipation_work
        + matter_source_work
        -phi_damping_work
        + phi_ledger["source_work"]
    )
    total_delta = total_after - total_before
    shared_residual = total_delta - expected_delta
    mass_before = integral_1d(state.C, spacing)
    mass_after = integral_1d(updated.C, spacing)
    ledger = {
        "operator_mode": MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE,
        "matter_substeps": substeps,
        "matter_sub_dt": sub_dt,
        "matter_stability_limit": c_limit,
        "matter_dissipation_work": float(matter_dissipation_work),
        "matter_source_work": float(matter_source_work),
        "matter_ledger_residual": float(matter_ledger_residual),
        "phi_damping_work": float(phi_damping_work),
        "phi_source_work": float(phi_ledger["source_work"]),
        "phi_ledger_residual": float(phi_ledger_residual),
        "shared_energy_delta": float(total_delta),
        "shared_ledger_expected_delta": float(expected_delta),
        "shared_ledger_residual": float(shared_residual),
        "mass_before": float(mass_before),
        "mass_after": float(mass_after),
        "mass_relative_drift": float(
            abs(mass_after - mass_before) / max(abs(mass_before), 1.0)
        ),
        "C_feedback": "changing_C_explicitly_enters_causal_Phi_step",
        "trace_feedback": False,
        "unit_lane": config.unit_lane,
    }
    return updated, old_phi, ledger


__all__ = [
    "MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE",
    "causal_split_energy",
    "causal_matter_space_split_step",
]
