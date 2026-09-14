"""Opt-in UET matter-space response candidate.

This normalized one-dimensional research operator evolves the physical state
``(C, Phi, Pi)`` from one declared functional. A retarded trace may be computed
from the resulting non-negative dissipation, but that trace never feeds back
into the dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from docs.core.uet_spatial import (
    gradient_energy_integral_1d,
    gradient_squared_cell_1d,
    integral_1d,
    laplacian_1d,
    validate_boundary,
    validate_dx,
    validate_field_1d,
)
from docs.core.uet_trace import TraceKernelConfig, UETStepResult, compute_spacetime_trace

MATTER_SPACE_OPERATOR_MODE = "matter_space_coupled_v1"


class MatterSpaceStabilityError(ValueError):
    """Raised when a requested fixed step exceeds the declared preflight bound."""

    def __init__(self, dt: float, recommended_max_dt: float):
        self.dt = float(dt)
        self.recommended_max_dt = float(recommended_max_dt)
        super().__init__(
            f"dt={self.dt:.6g} exceeds recommended_max_dt={self.recommended_max_dt:.6g}"
        )


@dataclass(frozen=True)
class MatterSpaceConfig:
    """Normalized coefficients for ``matter_space_coupled_v1``.

    Defaults are benchmark controls, not physical constants. The SI lane is
    intentionally rejected until a topic-specific units contract exists.
    """

    a_matter: float = -1.0
    b_matter: float = 1.0
    kappa_matter: float = 1.0
    mobility_matter: float = 1.0
    a_space: float = 1.0
    b_space: float = 1.0
    kappa_space: float = 1.0
    mobility_space: float = 1.0
    tau_space: float = 1.0
    coupling_g: float = 0.25
    matter_dynamics: str = "conserved"
    boundary_condition: str = "periodic"
    unit_lane: str = "normalized"
    stability_safety: float = 0.2
    ledger_tolerance: float = 1e-6

    def __post_init__(self) -> None:
        values = {
            "a_matter": self.a_matter,
            "b_matter": self.b_matter,
            "kappa_matter": self.kappa_matter,
            "mobility_matter": self.mobility_matter,
            "a_space": self.a_space,
            "b_space": self.b_space,
            "kappa_space": self.kappa_space,
            "mobility_space": self.mobility_space,
            "tau_space": self.tau_space,
            "coupling_g": self.coupling_g,
            "stability_safety": self.stability_safety,
            "ledger_tolerance": self.ledger_tolerance,
        }
        if not all(np.isfinite(float(value)) for value in values.values()):
            raise ValueError("matter-space coefficients must be finite")
        for name in (
            "b_matter",
            "kappa_matter",
            "mobility_matter",
            "b_space",
            "kappa_space",
            "mobility_space",
            "tau_space",
            "stability_safety",
            "ledger_tolerance",
        ):
            if float(getattr(self, name)) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.a_space < 0.0:
            raise ValueError("a_space must be non-negative in v1")
        if self.coupling_g < 0.0:
            raise ValueError("coupling_g must be non-negative in v1")
        if self.matter_dynamics not in {"conserved", "nonconserved"}:
            raise ValueError("matter_dynamics must be 'conserved' or 'nonconserved'")
        validate_boundary(self.boundary_condition)
        if self.unit_lane != "normalized":
            raise NotImplementedError("matter_space_coupled_v1 supports only unit_lane='normalized'")
        if self.stability_safety > 0.5:
            raise ValueError("stability_safety must not exceed 0.5 for the explicit v1 integrator")

    @property
    def space_speed(self) -> float:
        """Linearized propagation-speed control in normalized ``dx/dt`` units."""

        return float(np.sqrt(self.mobility_space * self.kappa_space / self.tau_space))


@dataclass
class MatterSpaceState:
    """Complete physical state of the matter-space candidate."""

    C: np.ndarray
    space_response: np.ndarray
    space_rate: np.ndarray

    def __post_init__(self) -> None:
        C = validate_field_1d(self.C, "C").copy()
        response = validate_field_1d(self.space_response, "space_response").copy()
        rate = validate_field_1d(self.space_rate, "space_rate").copy()
        if C.shape != response.shape or C.shape != rate.shape:
            raise ValueError("C, space_response, and space_rate must share one shape")
        self.C = C
        self.space_response = response
        self.space_rate = rate

    def copy(self) -> "MatterSpaceState":
        return MatterSpaceState(
            self.C.copy(), self.space_response.copy(), self.space_rate.copy()
        )


def _validate_sources(
    state: MatterSpaceState,
    matter_source: Optional[np.ndarray],
    space_source: Optional[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    zeros = np.zeros_like(state.C, dtype=float)
    matter = zeros if matter_source is None else validate_field_1d(matter_source, "matter_source")
    space = zeros if space_source is None else validate_field_1d(space_source, "space_source")
    if matter.shape != state.C.shape or space.shape != state.C.shape:
        raise ValueError("source arrays must match the physical state shape")
    return np.asarray(matter, dtype=float), np.asarray(space, dtype=float)


def matter_space_free_energy(
    state: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return the discrete candidate functional ``Omega[C, Phi]``."""

    spacing = validate_dx(dx)
    C = state.C
    Phi = state.space_response
    local_density = (
        0.5 * config.a_matter * C**2
        + 0.25 * config.b_matter * C**4
        + 0.5 * config.a_space * Phi**2
        + 0.25 * config.b_space * Phi**4
        - 0.5 * config.coupling_g * C**2 * Phi
    )
    local = integral_1d(local_density, spacing)
    matter_gradient = 0.5 * config.kappa_matter * gradient_energy_integral_1d(
        C, spacing, config.boundary_condition
    )
    space_gradient = 0.5 * config.kappa_space * gradient_energy_integral_1d(
        Phi, spacing, config.boundary_condition
    )
    return float(local + matter_gradient + space_gradient)


def matter_space_chemical_potentials(
    state: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return the exact discrete functional derivatives ``mu_C`` and ``mu_Phi``."""

    spacing = validate_dx(dx)
    C = state.C
    Phi = state.space_response
    lap_C = laplacian_1d(C, spacing, config.boundary_condition)
    lap_Phi = laplacian_1d(Phi, spacing, config.boundary_condition)
    mu_C = (
        config.a_matter * C
        + config.b_matter * C**3
        - config.kappa_matter * lap_C
        - config.coupling_g * C * Phi
    )
    mu_Phi = (
        config.a_space * Phi
        + config.b_space * Phi**3
        - config.kappa_space * lap_Phi
        - 0.5 * config.coupling_g * C**2
    )
    return mu_C, mu_Phi


def matter_space_extended_energy(
    state: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return ``Omega + tau_Phi/(2 M_Phi) integral Pi^2 dx``."""

    kinetic = (
        config.tau_space
        / (2.0 * config.mobility_space)
        * integral_1d(np.square(state.space_rate), dx)
    )
    return float(matter_space_free_energy(state, dx, config) + kinetic)


def matter_space_dissipation(
    state: MatterSpaceState,
    mu_matter: np.ndarray,
    dx: float,
    config: MatterSpaceConfig,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return non-negative matter, space, and total dissipation densities."""

    if config.matter_dynamics == "conserved":
        sigma_matter = config.mobility_matter * gradient_squared_cell_1d(
            mu_matter, dx, config.boundary_condition
        )
    else:
        sigma_matter = config.mobility_matter * np.square(mu_matter)
    sigma_space = np.square(state.space_rate) / config.mobility_space
    return sigma_matter, sigma_space, sigma_matter + sigma_space


def matter_space_rhs(
    state: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate the physical right-hand side without computing a trace."""

    matter_drive, space_drive = _validate_sources(state, matter_source, space_source)
    if config.matter_dynamics == "conserved":
        net_drive = abs(integral_1d(matter_drive, dx))
        drive_scale = max(integral_1d(np.abs(matter_drive), dx), 1.0)
        if net_drive > 1e-12 * drive_scale:
            raise ValueError("conserved matter_source must satisfy integral J_C dx = 0")

    mu_matter, mu_space = matter_space_chemical_potentials(state, dx, config)
    if config.matter_dynamics == "conserved":
        dC = config.mobility_matter * laplacian_1d(
            mu_matter, dx, config.boundary_condition
        ) + matter_drive
    else:
        dC = -config.mobility_matter * mu_matter + matter_drive
    dPhi = state.space_rate.copy()
    dPi = (
        -state.space_rate
        - config.mobility_space * mu_space
        + space_drive
    ) / config.tau_space
    return dC, dPhi, dPi, mu_matter, mu_space


def matter_space_stability_limit(
    state: MatterSpaceState,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return a conservative explicit-step preflight bound."""

    spacing = validate_dx(dx)
    matter_lipschitz = (
        abs(config.a_matter)
        + 3.0 * config.b_matter * float(np.max(np.square(state.C)))
        + config.coupling_g * float(np.max(np.abs(state.space_response)))
    )
    if config.matter_dynamics == "conserved":
        matter_rate = config.mobility_matter * (
            4.0 * matter_lipschitz / spacing**2
            + 16.0 * config.kappa_matter / spacing**4
        )
    else:
        matter_rate = config.mobility_matter * (
            matter_lipschitz + 4.0 * config.kappa_matter / spacing**2
        )
    matter_dt = np.inf if matter_rate <= 0.0 else 2.0 / matter_rate

    space_lipschitz = (
        config.a_space
        + 3.0 * config.b_space * float(np.max(np.square(state.space_response)))
        + 4.0 * config.kappa_space / spacing**2
    )
    space_frequency = np.sqrt(
        max(config.mobility_space * space_lipschitz / config.tau_space, 0.0)
    )
    oscillation_dt = np.inf if space_frequency <= 0.0 else 1.0 / space_frequency
    propagation_dt = spacing / max(config.space_speed, np.finfo(float).tiny)
    base_limit = min(matter_dt, config.tau_space, oscillation_dt, propagation_dt)
    return float(config.stability_safety * base_limit)


def _source_power(
    state: MatterSpaceState,
    mu_matter: np.ndarray,
    matter_source: np.ndarray,
    space_source: np.ndarray,
    dx: float,
    config: MatterSpaceConfig,
) -> Tuple[float, float]:
    matter_power = integral_1d(mu_matter * matter_source, dx)
    space_power = integral_1d(
        state.space_rate * space_source / config.mobility_space, dx
    )
    return matter_power, space_power


def causal_linear_space_step(
    state: MatterSpaceState,
    previous_space_response: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
    space_source: Optional[np.ndarray] = None,
) -> Tuple[MatterSpaceState, np.ndarray]:
    """Advance a strict-CFL linearized space-response control lane.

    This is deliberately separate from ``matter_space_step``.  It evolves the
    damped hyperbolic Phi sector with a centered second-order recurrence and a
    nearest-neighbor finite-volume Laplacian.  The contract requires CFL=1,
    so the discrete support cone advances by at most one cell per step.  C is
    frozen and acts only as a local source; this is a causal control/reference,
    not the full coupled matter-space operator.
    """

    step_size = float(dt)
    spacing = validate_dx(dx)
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("dt must be finite and positive")
    previous = validate_field_1d(previous_space_response, "previous_space_response")
    if previous.shape != state.space_response.shape:
        raise ValueError("previous_space_response must match state.space_response")
    source = (
        np.zeros_like(state.C)
        if space_source is None
        else validate_field_1d(space_source, "space_source")
    )
    if source.shape != state.C.shape:
        raise ValueError("space_source must match the physical state shape")

    speed = config.space_speed
    cfl = speed * step_size / spacing
    if not np.isclose(cfl, 1.0, rtol=1.0e-10, atol=1.0e-12):
        raise ValueError(
            "causal_linear_space_step requires CFL=1; "
            f"received CFL={cfl:.12g}, recommended_dt={spacing / speed:.12g}"
        )

    phi = state.space_response
    lap_phi = laplacian_1d(phi, spacing, config.boundary_condition)
    local_force = -config.mobility_space * (
        config.a_space * phi
        + config.b_space * phi**3
        - 0.5 * config.coupling_g * state.C**2
    ) + source
    tau = config.tau_space
    half_damping = step_size / (2.0 * tau)
    numerator = (
        2.0 * phi
        - (1.0 - half_damping) * previous
        + (config.mobility_space * config.kappa_space * step_size**2 / tau) * lap_phi
        + (step_size**2 / tau) * local_force
    )
    next_phi = numerator / (1.0 + half_damping)
    next_pi = (next_phi - previous) / (2.0 * step_size)
    updated = MatterSpaceState(state.C.copy(), next_phi, next_pi)
    return updated, phi.copy()

def matter_space_step(
    state: MatterSpaceState,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
    trace_history: Optional[Sequence[np.ndarray]] = None,
    trace_config: Optional[TraceKernelConfig] = None,
) -> UETStepResult:
    """Advance one Heun/RK2 step and report a complete normalized ledger."""

    step_size = float(dt)
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("dt must be finite and positive")
    spacing = validate_dx(dx)
    physical = state.copy()
    matter_drive, space_drive = _validate_sources(
        physical, matter_source, space_source
    )
    max_dt = matter_space_stability_limit(physical, spacing, config)
    if step_size > max_dt * (1.0 + 1e-12):
        raise MatterSpaceStabilityError(step_size, max_dt)

    energy_before = matter_space_extended_energy(physical, spacing, config)
    k1_C, k1_Phi, k1_Pi, mu_C_before, _ = matter_space_rhs(
        physical, spacing, config, matter_drive, space_drive
    )
    sigma_C_before, sigma_Phi_before, sigma_before = matter_space_dissipation(
        physical, mu_C_before, spacing, config
    )
    matter_power_before, space_power_before = _source_power(
        physical, mu_C_before, matter_drive, space_drive, spacing, config
    )

    predictor = MatterSpaceState(
        physical.C + step_size * k1_C,
        physical.space_response + step_size * k1_Phi,
        physical.space_rate + step_size * k1_Pi,
    )
    k2_C, k2_Phi, k2_Pi, _, _ = matter_space_rhs(
        predictor, spacing, config, matter_drive, space_drive
    )
    updated = MatterSpaceState(
        physical.C + 0.5 * step_size * (k1_C + k2_C),
        physical.space_response + 0.5 * step_size * (k1_Phi + k2_Phi),
        physical.space_rate + 0.5 * step_size * (k1_Pi + k2_Pi),
    )

    energy_after = matter_space_extended_energy(updated, spacing, config)
    mu_C_after, _ = matter_space_chemical_potentials(updated, spacing, config)
    sigma_C_after, sigma_Phi_after, sigma_after = matter_space_dissipation(
        updated, mu_C_after, spacing, config
    )
    matter_power_after, space_power_after = _source_power(
        updated, mu_C_after, matter_drive, space_drive, spacing, config
    )

    dissipation_before = integral_1d(sigma_before, spacing)
    dissipation_after = integral_1d(sigma_after, spacing)
    dissipation_average = 0.5 * (dissipation_before + dissipation_after)
    matter_power_average = 0.5 * (matter_power_before + matter_power_after)
    space_power_average = 0.5 * (space_power_before + space_power_after)
    predicted_delta = step_size * (
        -dissipation_average + matter_power_average + space_power_average
    )
    actual_delta = energy_after - energy_before
    closure_residual = actual_delta - predicted_delta
    closure_scale = max(
        abs(actual_delta), abs(predicted_delta), step_size * dissipation_average, 1e-12
    )
    closure_relative = abs(closure_residual) / closure_scale

    trace_source = 0.5 * (sigma_before + sigma_after)
    trace_observable: Optional[np.ndarray] = None
    if trace_config is not None:
        history: List[np.ndarray] = [
            validate_field_1d(sample, "trace_history_sample").copy()
            for sample in (trace_history or [])
        ]
        if any(sample.shape != physical.C.shape for sample in history):
            raise ValueError("trace_history samples must match the physical state shape")
        trace_observable = compute_spacetime_trace(
            history + [trace_source],
            spacing,
            step_size,
            trace_config,
            shape=physical.C.shape,
        )

    matter_before = integral_1d(physical.C, spacing)
    matter_after = integral_1d(updated.C, spacing)
    no_external_drive = not np.any(matter_drive) and not np.any(space_drive)
    energy_tolerance = config.ledger_tolerance * max(abs(energy_before), 1.0)
    energy_descent = (not no_external_drive) or actual_delta <= energy_tolerance
    ledger_gate = closure_relative <= config.ledger_tolerance

    energy_ledger: Dict[str, Any] = {
        "units_lane": config.unit_lane,
        "free_plus_space_kinetic_before": energy_before,
        "free_plus_space_kinetic_after": energy_after,
        "actual_delta": actual_delta,
        "predicted_delta": predicted_delta,
        "closure_residual": closure_residual,
        "closure_relative": closure_relative,
        "dissipation_matter_before": integral_1d(sigma_C_before, spacing),
        "dissipation_matter_after": integral_1d(sigma_C_after, spacing),
        "dissipation_space_before": integral_1d(sigma_Phi_before, spacing),
        "dissipation_space_after": integral_1d(sigma_Phi_after, spacing),
        "matter_input_power": matter_power_average,
        "space_input_power": space_power_average,
        "ledger_gate": "PASS" if ledger_gate else "FAIL",
        "energy_descent_gate": "PASS" if energy_descent else "FAIL",
        "joule_claim": False,
    }
    diagnostics: Dict[str, Any] = {
        "operator_mode": MATTER_SPACE_OPERATOR_MODE,
        "ontology": "physical_C_Phi_Pi_with_derived_trace_only",
        "trace_backreaction": False,
        "matter_dynamics": config.matter_dynamics,
        "boundary_condition": config.boundary_condition,
        "space_speed_normalized": config.space_speed,
        "recommended_max_dt": max_dt,
        "stability_ratio": step_size / max_dt,
        "matter_integral_before": matter_before,
        "matter_integral_after": matter_after,
        "matter_integral_drift": matter_after - matter_before,
        "source_nonnegative": bool(float(np.min(trace_source)) >= -1e-12),
        "source_snapshot": trace_source,
        "field_clipping_applied": False,
        "parameter_fitting_applied": False,
    }
    return UETStepResult(
        C=updated.C,
        V=None,
        trace_observable=trace_observable,
        energy_ledger=energy_ledger,
        diagnostics=diagnostics,
        space_response=updated.space_response,
        space_rate=updated.space_rate,
    )
