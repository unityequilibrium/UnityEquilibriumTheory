"""Opt-in finite-cone ``C`` realization for the matter-space program.

This module is deliberately separate from the conserved-C matter-space
operator.  It treats ``C`` as a non-conserved collective order/behaviour
coordinate with a damped telegraph equation,

    tau_C C_tt + C_t = -M_C mu_C + J_C,

and evolves the effective space response with the same functional derivatives
used by the normalized matter-space candidate.  It is a candidate numerical
lane, not a mass-density law, a covariant completion, or a proof that the
conserved Cahn-Hilliard lane has a finite response cone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

from docs.core.uet_spatial import (
    gradient_energy_integral_1d,
    integral_1d,
    laplacian_1d,
    validate_boundary,
    validate_dx,
    validate_field_1d,
)
from docs.core.uet_trace import TraceKernelConfig, UETStepResult, compute_spacetime_trace


FINITE_CONE_C_OPERATOR_MODE = "matter_space_finite_cone_c_v1"


class FiniteConeCStabilityError(ValueError):
    """Raised when the requested explicit step exceeds the preflight bound."""

    def __init__(self, dt: float, recommended_max_dt: float):
        self.dt = float(dt)
        self.recommended_max_dt = float(recommended_max_dt)
        super().__init__(
            f"dt={self.dt:.6g} exceeds recommended_max_dt="
            f"{self.recommended_max_dt:.6g}"
        )


@dataclass(frozen=True)
class FiniteConeCConfig:
    """Normalized configuration for the non-conserved telegraph C lane."""

    a_C: float = -1.0
    b_C: float = 1.0
    kappa_C: float = 1.0
    mobility_C: float = 1.0
    tau_C: float = 1.0
    a_space: float = 1.0
    b_space: float = 1.0
    kappa_space: float = 1.0
    mobility_space: float = 1.0
    tau_space: float = 1.0
    coupling_g: float = 0.25
    boundary_condition: str = "periodic"
    unit_lane: str = "normalized"
    stability_safety: float = 0.1
    ledger_tolerance: float = 1e-6
    c_limit: Optional[float] = None

    def __post_init__(self) -> None:
        names = (
            "a_C", "b_C", "kappa_C", "mobility_C", "tau_C",
            "a_space", "b_space", "kappa_space", "mobility_space",
            "tau_space", "coupling_g", "stability_safety", "ledger_tolerance",
        )
        if not all(np.isfinite(float(getattr(self, name))) for name in names):
            raise ValueError("finite-cone C coefficients must be finite")
        for name in (
            "b_C", "kappa_C", "mobility_C", "tau_C", "b_space",
            "kappa_space", "mobility_space", "tau_space", "stability_safety",
            "ledger_tolerance",
        ):
            if float(getattr(self, name)) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.a_space < 0.0:
            raise ValueError("a_space must be non-negative in v1")
        if self.coupling_g < 0.0:
            raise ValueError("coupling_g must be non-negative in v1")
        if self.stability_safety > 0.5:
            raise ValueError("stability_safety must not exceed 0.5")
        validate_boundary(self.boundary_condition)
        if self.unit_lane != "normalized":
            raise NotImplementedError(
                "matter_space_finite_cone_c_v1 supports only normalized units"
            )
        if self.c_limit is not None:
            if not np.isfinite(float(self.c_limit)) or self.c_limit <= 0.0:
                raise ValueError("c_limit must be finite and positive")
            if self.matter_speed > self.c_limit * (1.0 + 1e-12):
                raise ValueError(
                    "finite-cone C speed exceeds the configured normalized limit"
                )
            if self.space_speed > self.c_limit * (1.0 + 1e-12):
                raise ValueError(
                    "space-response speed exceeds the configured normalized limit"
                )

    @property
    def matter_speed(self) -> float:
        return float(np.sqrt(self.mobility_C * self.kappa_C / self.tau_C))

    @property
    def space_speed(self) -> float:
        return float(
            np.sqrt(self.mobility_space * self.kappa_space / self.tau_space)
        )


@dataclass
class FiniteConeCState:
    """Complete state for the finite-cone candidate."""

    C: np.ndarray
    C_rate: np.ndarray
    space_response: np.ndarray
    space_rate: np.ndarray

    def __post_init__(self) -> None:
        fields = {
            "C": self.C,
            "C_rate": self.C_rate,
            "space_response": self.space_response,
            "space_rate": self.space_rate,
        }
        validated = {
            name: validate_field_1d(value, name).copy()
            for name, value in fields.items()
        }
        shape = validated["C"].shape
        if any(value.shape != shape for value in validated.values()):
            raise ValueError("all finite-cone C state arrays must share one shape")
        for name, value in validated.items():
            setattr(self, name, value)

    def copy(self) -> "FiniteConeCState":
        return FiniteConeCState(
            self.C.copy(),
            self.C_rate.copy(),
            self.space_response.copy(),
            self.space_rate.copy(),
        )


def finite_cone_c_free_energy(
    state: FiniteConeCState, dx: float, config: FiniteConeCConfig
) -> float:
    """Return the shared normalized matter-space functional."""

    spacing = validate_dx(dx)
    C = state.C
    Phi = state.space_response
    local = integral_1d(
        0.5 * config.a_C * C**2
        + 0.25 * config.b_C * C**4
        + 0.5 * config.a_space * Phi**2
        + 0.25 * config.b_space * Phi**4
        - 0.5 * config.coupling_g * C**2 * Phi,
        spacing,
    )
    gradients = 0.5 * config.kappa_C * gradient_energy_integral_1d(
        C, spacing, config.boundary_condition
    ) + 0.5 * config.kappa_space * gradient_energy_integral_1d(
        Phi, spacing, config.boundary_condition
    )
    return float(local + gradients)


def finite_cone_c_chemical_potentials(
    state: FiniteConeCState, dx: float, config: FiniteConeCConfig
) -> Tuple[np.ndarray, np.ndarray]:
    """Return the exact discrete derivatives of the shared functional."""

    spacing = validate_dx(dx)
    C = state.C
    Phi = state.space_response
    mu_C = (
        config.a_C * C
        + config.b_C * C**3
        - config.kappa_C * laplacian_1d(C, spacing, config.boundary_condition)
        - config.coupling_g * C * Phi
    )
    mu_Phi = (
        config.a_space * Phi
        + config.b_space * Phi**3
        - config.kappa_space * laplacian_1d(Phi, spacing, config.boundary_condition)
        - 0.5 * config.coupling_g * C**2
    )
    return mu_C, mu_Phi


def finite_cone_c_extended_energy(
    state: FiniteConeCState, dx: float, config: FiniteConeCConfig
) -> float:
    """Return ``Omega + tau_C*C_rate^2/(2M_C) + tau_Phi*Pi^2/(2M_Phi)``."""

    kinetic_C = config.tau_C / (2.0 * config.mobility_C) * integral_1d(
        state.C_rate**2, dx
    )
    kinetic_Phi = config.tau_space / (2.0 * config.mobility_space) * integral_1d(
        state.space_rate**2, dx
    )
    return float(finite_cone_c_free_energy(state, dx, config) + kinetic_C + kinetic_Phi)


def finite_cone_c_rhs(
    state: FiniteConeCState,
    dx: float,
    config: FiniteConeCConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate the physical first-order form without trace feedback."""

    matter = np.zeros_like(state.C) if matter_source is None else validate_field_1d(
        matter_source, "matter_source"
    )
    space = np.zeros_like(state.C) if space_source is None else validate_field_1d(
        space_source, "space_source"
    )
    if matter.shape != state.C.shape or space.shape != state.C.shape:
        raise ValueError("source arrays must match the finite-cone state shape")
    mu_C, mu_Phi = finite_cone_c_chemical_potentials(state, dx, config)
    dC = state.C_rate
    dC_rate = (
        -state.C_rate - config.mobility_C * mu_C + matter
    ) / config.tau_C
    dPhi = state.space_rate
    dPhi_rate = (
        -state.space_rate - config.mobility_space * mu_Phi + space
    ) / config.tau_space
    return dC, dC_rate, dPhi, dPhi_rate, mu_C, mu_Phi


def finite_cone_c_stability_limit(
    state: FiniteConeCState, dx: float, config: FiniteConeCConfig
) -> float:
    """Return a conservative CFL/damping/force preflight bound."""

    spacing = validate_dx(dx)
    c_lipschitz = (
        abs(config.a_C)
        + 3.0 * config.b_C * float(np.max(state.C**2))
        + config.coupling_g * float(np.max(np.abs(state.space_response)))
        + 4.0 * config.kappa_C / spacing**2
    )
    phi_lipschitz = (
        config.a_space
        + 3.0 * config.b_space * float(np.max(state.space_response**2))
        + 4.0 * config.kappa_space / spacing**2
    )
    c_frequency = np.sqrt(config.mobility_C * c_lipschitz / config.tau_C)
    phi_frequency = np.sqrt(
        config.mobility_space * phi_lipschitz / config.tau_space
    )
    limits = [
        spacing / max(config.matter_speed, np.finfo(float).tiny),
        spacing / max(config.space_speed, np.finfo(float).tiny),
        config.tau_C,
        config.tau_space,
        1.0 / max(c_frequency, np.finfo(float).tiny),
        1.0 / max(phi_frequency, np.finfo(float).tiny),
    ]
    return float(config.stability_safety * min(limits))


def finite_cone_c_step(
    state: FiniteConeCState,
    dt: float,
    dx: float,
    config: FiniteConeCConfig,
    matter_source: Optional[np.ndarray] = None,
    space_source: Optional[np.ndarray] = None,
    trace_history: Optional[Sequence[np.ndarray]] = None,
    trace_config: Optional[TraceKernelConfig] = None,
) -> UETStepResult:
    """Advance one Heun step and return a backward-compatible result.

    ``UETStepResult.V`` carries ``C_rate`` in this operator and is labelled in
    diagnostics.  Legacy positional fields remain untouched; ``Phi`` and its
    rate continue to use the appended result fields.
    """

    step_size = float(dt)
    if not np.isfinite(step_size) or step_size <= 0.0:
        raise ValueError("dt must be finite and positive")
    spacing = validate_dx(dx)
    physical = state.copy()
    max_dt = finite_cone_c_stability_limit(physical, spacing, config)
    if step_size > max_dt * (1.0 + 1e-12):
        raise FiniteConeCStabilityError(step_size, max_dt)

    matter = np.zeros_like(physical.C) if matter_source is None else validate_field_1d(
        matter_source, "matter_source"
    )
    space = np.zeros_like(physical.C) if space_source is None else validate_field_1d(
        space_source, "space_source"
    )
    if matter.shape != physical.C.shape or space.shape != physical.C.shape:
        raise ValueError("source arrays must match the finite-cone state shape")

    energy_before = finite_cone_c_extended_energy(physical, spacing, config)
    k1_C, k1_C_rate, k1_Phi, k1_Phi_rate, mu_C_before, _ = finite_cone_c_rhs(
        physical, spacing, config, matter, space
    )
    predictor = FiniteConeCState(
        physical.C + step_size * k1_C,
        physical.C_rate + step_size * k1_C_rate,
        physical.space_response + step_size * k1_Phi,
        physical.space_rate + step_size * k1_Phi_rate,
    )
    k2_C, k2_C_rate, k2_Phi, k2_Phi_rate, _, _ = finite_cone_c_rhs(
        predictor, spacing, config, matter, space
    )
    updated = FiniteConeCState(
        physical.C + 0.5 * step_size * (k1_C + k2_C),
        physical.C_rate + 0.5 * step_size * (k1_C_rate + k2_C_rate),
        physical.space_response + 0.5 * step_size * (k1_Phi + k2_Phi),
        physical.space_rate + 0.5 * step_size * (k1_Phi_rate + k2_Phi_rate),
    )

    energy_after = finite_cone_c_extended_energy(updated, spacing, config)
    mu_C_after, _ = finite_cone_c_chemical_potentials(updated, spacing, config)
    sigma_before = integral_1d(
        physical.C_rate**2 / config.mobility_C
        + physical.space_rate**2 / config.mobility_space,
        spacing,
    )
    sigma_after = integral_1d(
        updated.C_rate**2 / config.mobility_C
        + updated.space_rate**2 / config.mobility_space,
        spacing,
    )
    source_before = integral_1d(
        physical.C_rate * matter / config.mobility_C
        + physical.space_rate * space / config.mobility_space,
        spacing,
    )
    source_after = integral_1d(
        updated.C_rate * matter / config.mobility_C
        + updated.space_rate * space / config.mobility_space,
        spacing,
    )
    dissipation = 0.5 * (sigma_before + sigma_after)
    source_power = 0.5 * (source_before + source_after)
    predicted_delta = step_size * (-dissipation + source_power)
    actual_delta = energy_after - energy_before
    closure_residual = actual_delta - predicted_delta
    closure_scale = max(abs(actual_delta), abs(predicted_delta), step_size * dissipation, 1e-12)
    closure_relative = abs(closure_residual) / closure_scale

    trace_source = 0.5 * (
        physical.C_rate**2 / config.mobility_C
        + physical.space_rate**2 / config.mobility_space
        + updated.C_rate**2 / config.mobility_C
        + updated.space_rate**2 / config.mobility_space
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
            history + [trace_source], spacing, step_size, trace_config, shape=physical.C.shape
        )

    no_external_drive = not np.any(matter) and not np.any(space)
    energy_tolerance = config.ledger_tolerance * max(abs(energy_before), 1.0)
    energy_descent = (not no_external_drive) or actual_delta <= energy_tolerance
    ledger_gate = closure_relative <= config.ledger_tolerance
    energy_ledger: Dict[str, Any] = {
        "units_lane": config.unit_lane,
        "operator_mode": FINITE_CONE_C_OPERATOR_MODE,
        "extended_energy_before": energy_before,
        "extended_energy_after": energy_after,
        "actual_delta": actual_delta,
        "predicted_delta": predicted_delta,
        "closure_residual": closure_residual,
        "closure_relative": closure_relative,
        "dissipation_before": sigma_before,
        "dissipation_after": sigma_after,
        "input_power": source_power,
        "ledger_gate": "PASS" if ledger_gate else "FAIL",
        "energy_descent_gate": "PASS" if energy_descent else "FAIL",
        "mass_conservation": "NOT_APPLICABLE_NONCONSERVATIVE_C_LANE",
        "joule_claim": False,
    }
    diagnostics: Dict[str, Any] = {
        "operator_mode": FINITE_CONE_C_OPERATOR_MODE,
        "ontology": "nonconserved_collective_C_with_Phi_Pi_and_derived_trace",
        "C_lane": "C_telegraph_candidate",
        "C_rate_semantics": "dC_dt",
        "trace_backreaction": False,
        "matter_dynamics": "nonconserved_telegraph",
        "boundary_condition": config.boundary_condition,
        "matter_speed_normalized": config.matter_speed,
        "space_speed_normalized": config.space_speed,
        "recommended_max_dt": max_dt,
        "stability_ratio": step_size / max_dt,
        "source_nonnegative": bool(float(np.min(trace_source)) >= -1e-12),
        "source_snapshot": trace_source,
        "field_clipping_applied": False,
        "parameter_fitting_applied": False,
        "mass_density_mapping": "NOT_DEFINED",
        "covariant_completion": "BLOCKED",
        "claim_boundary": "candidate normalized finite-cone collective-response lane",
    }
    return UETStepResult(
        C=updated.C,
        V=updated.C_rate,
        trace_observable=trace_observable,
        energy_ledger=energy_ledger,
        diagnostics=diagnostics,
        space_response=updated.space_response,
        space_rate=updated.space_rate,
    )


def finite_cone_c_contract() -> Dict[str, Any]:
    """Return the machine-readable contract used by audits and documentation."""

    return {
        "operator_mode": FINITE_CONE_C_OPERATOR_MODE,
        "equation": "tau_C*C_tt + C_t = -M_C*mu_C + J_C",
        "C_lane": "C_telegraph_candidate",
        "standard_counterpart": "damped hyperbolic nonconserved order-parameter dynamics",
        "unit_lane": "normalized_only_v1",
        "finite_speed": "sqrt(M_C*kappa_C/tau_C)",
        "conservation": "C_not_conserved_by_default",
        "trace_backreaction": False,
        "mass_mapping": "open_lane_specific_only",
        "SI_status": "BLOCKED",
        "covariant_status": "BLOCKED",
        "evidence_status": "CANDIDATE",
        "forbidden_identifications": [
            "C_is_universal_mass",
            "C_is_a_force",
            "Phi_is_metric_or_particle",
            "R_gen_is_independent_substance",
            "finite_speed_implies_photon_conversion",
        ],
    }
