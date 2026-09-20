"""Periodic time evolution for the verified nonlinear vacuum GH operator.

The implementation is deliberately bounded: classical RK4, a fixed CFL
coefficient, periodic finite differences, and prescribed time-independent
harmonic-source arrays. It does not project constraints or add filtering.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from typing import Any, Final

import numpy as np

from .uet_curved_3p1_generalized_harmonic import (
    GHNonlinearParameters,
    compute_nonlinear_vacuum_gh_rhs,
    derive_gh_kinematics,
    gh_curl_constraint,
    gh_gauge_constraint_grid,
    gh_reduction_constraint,
)


GH_TIME_EVOLUTION_STATUS: Final[str] = "GH_PERIODIC_VACUUM_TIME_EVOLUTION_READY"


@dataclass(frozen=True)
class GHEvolutionState:
    spacetime_metric: np.ndarray
    normal_derivative: np.ndarray
    spatial_derivative: np.ndarray


@dataclass(frozen=True)
class GHTimeIntegrationParameters:
    cfl: float = 0.08
    maximum_cfl: float = 0.20
    maximum_steps: int = 100_000
    diagnostic_stride: int = 1

    def __post_init__(self) -> None:
        if not isfinite(float(self.cfl)) or self.cfl <= 0.0:
            raise ValueError("cfl must be finite and positive")
        if not isfinite(float(self.maximum_cfl)) or self.maximum_cfl <= 0.0:
            raise ValueError("maximum_cfl must be finite and positive")
        if self.cfl > self.maximum_cfl:
            raise ValueError("cfl exceeds the preregistered maximum")
        if self.maximum_steps <= 0 or self.diagnostic_stride <= 0:
            raise ValueError("step and diagnostic limits must be positive")


@dataclass(frozen=True)
class GHConstraintNorms:
    time: float
    gauge_l2: float
    gauge_linf: float
    reduction_l2: float
    reduction_linf: float
    curl_l2: float
    curl_linf: float
    minimum_lapse: float
    minimum_spatial_inverse_eigenvalue: float
    metric_symmetry_linf: float


@dataclass(frozen=True)
class GHTimeEvolutionResult:
    state: GHEvolutionState
    final_time: float
    step_count: int
    minimum_dt: float
    maximum_dt: float
    maximum_observed_courant: float
    diagnostics: tuple[GHConstraintNorms, ...]
    run_contract: dict[str, Any]


def _spacing_tuple(spacing: Any) -> tuple[float, float, float]:
    values = tuple(float(value) for value in spacing)
    if len(values) != 3 or any(not isfinite(value) or value <= 0.0 for value in values):
        raise ValueError("spacing must contain three finite positive values")
    return values


def _state_arrays(state: GHEvolutionState) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    psi = np.asarray(state.spacetime_metric, dtype=float)
    pi_state = np.asarray(state.normal_derivative, dtype=float)
    phi = np.asarray(state.spatial_derivative, dtype=float)
    if psi.ndim != 5 or psi.shape[-2:] != (4, 4) or pi_state.shape != psi.shape:
        raise ValueError("metric and normal derivative must have shape (nx,ny,nz,4,4)")
    if phi.shape != psi.shape[:3] + (3, 4, 4):
        raise ValueError("spatial derivative must have shape (nx,ny,nz,3,4,4)")
    if any(size < 5 for size in psi.shape[:3]):
        raise ValueError("each periodic grid axis must have at least five points")
    if not all(np.all(np.isfinite(value)) for value in (psi, pi_state, phi)):
        raise ValueError("GH evolution state must be finite")
    return psi, pi_state, phi


def _combine(
    state: GHEvolutionState,
    terms: tuple[tuple[float, GHEvolutionState], ...],
) -> GHEvolutionState:
    psi, pi_state, phi = _state_arrays(state)
    out_psi = psi.copy()
    out_pi = pi_state.copy()
    out_phi = phi.copy()
    for coefficient, term in terms:
        out_psi += coefficient * term.spacetime_metric
        out_pi += coefficient * term.normal_derivative
        out_phi += coefficient * term.spatial_derivative
    return GHEvolutionState(out_psi, out_pi, out_phi)


def _rhs_state(
    state: GHEvolutionState,
    gauge_source: np.ndarray,
    gauge_source_covariant_derivative: np.ndarray,
    spacing: tuple[float, float, float],
    parameters: GHNonlinearParameters,
) -> GHEvolutionState:
    rhs = compute_nonlinear_vacuum_gh_rhs(
        state.spacetime_metric,
        state.normal_derivative,
        state.spatial_derivative,
        gauge_source,
        gauge_source_covariant_derivative,
        spacing,
        parameters,
    )
    return GHEvolutionState(
        rhs.metric_rhs,
        rhs.normal_derivative_rhs,
        rhs.spatial_derivative_rhs,
    )


def gh_constraint_norms(
    state: GHEvolutionState,
    gauge_source: Any,
    spacing: Any,
    *,
    time: float = 0.0,
) -> GHConstraintNorms:
    """Return unprojected gauge, reduction, and curl constraint norms."""

    psi, pi_state, phi = _state_arrays(state)
    source = np.asarray(gauge_source, dtype=float)
    if source.shape != psi.shape[:3] + (4,) or not np.all(np.isfinite(source)):
        raise ValueError("gauge_source must be finite with shape (nx,ny,nz,4)")
    steps = _spacing_tuple(spacing)
    kin = derive_gh_kinematics(psi)
    gauge = gh_gauge_constraint_grid(psi, pi_state, phi, source, kin)
    reduction = gh_reduction_constraint(psi, phi, steps)
    curl = gh_curl_constraint(phi, steps)
    spatial_eigenvalues = np.linalg.eigvalsh(kin.spatial_inverse_metric)

    def l2(value: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(value))))

    def linf(value: np.ndarray) -> float:
        return float(np.max(np.abs(value)))

    return GHConstraintNorms(
        time=float(time),
        gauge_l2=l2(gauge),
        gauge_linf=linf(gauge),
        reduction_l2=l2(reduction),
        reduction_linf=linf(reduction),
        curl_l2=l2(curl),
        curl_linf=linf(curl),
        minimum_lapse=float(np.min(kin.lapse)),
        minimum_spatial_inverse_eigenvalue=float(np.min(spatial_eigenvalues)),
        metric_symmetry_linf=linf(psi - np.swapaxes(psi, -1, -2)),
    )


def gh_cfl_timestep(
    state: GHEvolutionState,
    spacing: Any,
    cfl: float,
) -> tuple[float, float]:
    """Return a conservative local characteristic CFL step and max speed."""

    psi, _, _ = _state_arrays(state)
    steps = _spacing_tuple(spacing)
    coefficient = float(cfl)
    if not isfinite(coefficient) or coefficient <= 0.0:
        raise ValueError("cfl must be finite and positive")
    kin = derive_gh_kinematics(psi)
    max_speed = float(np.max(kin.lapse + np.linalg.norm(kin.shift, axis=-1)))
    if not isfinite(max_speed) or max_speed <= 0.0:
        raise ValueError("maximum characteristic speed must be finite and positive")
    return coefficient * min(steps) / max_speed, max_speed


def rk4_periodic_vacuum_gh_step(
    state: GHEvolutionState,
    gauge_source: Any,
    gauge_source_covariant_derivative: Any,
    spacing: Any,
    dt: float,
    parameters: GHNonlinearParameters = GHNonlinearParameters(),
) -> GHEvolutionState:
    """Advance one classical RK4 step without filtering or projection."""

    step = float(dt)
    if not isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    psi, _, _ = _state_arrays(state)
    source = np.asarray(gauge_source, dtype=float)
    source_derivative = np.asarray(gauge_source_covariant_derivative, dtype=float)
    if source.shape != psi.shape[:3] + (4,):
        raise ValueError("gauge_source shape does not match the evolution grid")
    if source_derivative.shape != psi.shape[:3] + (4, 4):
        raise ValueError("gauge-source derivative shape does not match the evolution grid")
    steps = _spacing_tuple(spacing)
    k1 = _rhs_state(state, source, source_derivative, steps, parameters)
    k2 = _rhs_state(_combine(state, ((0.5 * step, k1),)), source, source_derivative, steps, parameters)
    k3 = _rhs_state(_combine(state, ((0.5 * step, k2),)), source, source_derivative, steps, parameters)
    k4 = _rhs_state(_combine(state, ((step, k3),)), source, source_derivative, steps, parameters)
    return _combine(
        state,
        (
            (step / 6.0, k1),
            (step / 3.0, k2),
            (step / 3.0, k3),
            (step / 6.0, k4),
        ),
    )


def evolve_periodic_vacuum_gh(
    initial_state: GHEvolutionState,
    gauge_source: Any,
    gauge_source_covariant_derivative: Any,
    spacing: Any,
    final_time: float,
    parameters: GHNonlinearParameters = GHNonlinearParameters(),
    integration: GHTimeIntegrationParameters = GHTimeIntegrationParameters(),
) -> GHTimeEvolutionResult:
    """Evolve the periodic vacuum GH state with a fixed CFL coefficient."""

    target = float(final_time)
    if not isfinite(target) or target <= 0.0:
        raise ValueError("final_time must be finite and positive")
    steps = _spacing_tuple(spacing)
    psi, _, _ = _state_arrays(initial_state)
    source = np.asarray(gauge_source, dtype=float)
    source_derivative = np.asarray(gauge_source_covariant_derivative, dtype=float)
    if source.shape != psi.shape[:3] + (4,) or source_derivative.shape != psi.shape[:3] + (4, 4):
        raise ValueError("gauge-source arrays do not match the evolution grid")
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(source_derivative)):
        raise ValueError("gauge-source arrays must be finite")

    state = GHEvolutionState(*(value.copy() for value in _state_arrays(initial_state)))
    time = 0.0
    count = 0
    dt_values: list[float] = []
    maximum_courant = 0.0
    diagnostics = [gh_constraint_norms(state, source, steps, time=time)]
    while time < target:
        if count >= integration.maximum_steps:
            raise RuntimeError("maximum_steps reached before final_time")
        cfl_dt, max_speed = gh_cfl_timestep(state, steps, integration.cfl)
        dt = min(cfl_dt, target - time)
        courant = dt * max_speed / min(steps)
        if courant > integration.maximum_cfl + 1e-14:
            raise RuntimeError("observed Courant factor exceeds the preregistered maximum")
        state = rk4_periodic_vacuum_gh_step(
            state, source, source_derivative, steps, dt, parameters
        )
        time += dt
        count += 1
        dt_values.append(dt)
        maximum_courant = max(maximum_courant, courant)
        if count % integration.diagnostic_stride == 0 or time >= target:
            diagnostics.append(gh_constraint_norms(state, source, steps, time=time))
    return GHTimeEvolutionResult(
        state=state,
        final_time=time,
        step_count=count,
        minimum_dt=min(dt_values),
        maximum_dt=max(dt_values),
        maximum_observed_courant=maximum_courant,
        diagnostics=tuple(diagnostics),
        run_contract={
            "integrator": "CLASSICAL_RK4",
            "cfl_coefficient": integration.cfl,
            "maximum_cfl": integration.maximum_cfl,
            "boundary": "PERIODIC",
            "gauge_source": "PRESCRIBED_TIME_INDEPENDENT_ARRAY",
            "constraint_projection": False,
            "numerical_filtering": False,
            "artificial_dissipation": False,
            "field_clipping": False,
            "parameter_fitting": False,
            "matter_source": "VACUUM_ONLY",
        },
    )


def harmonic_gauge_wave_state(
    shape: tuple[int, int, int],
    domain_lengths: tuple[float, float, float],
    *,
    time: float = 0.0,
    amplitude: float = 0.05,
    cycles: int = 1,
) -> tuple[GHEvolutionState, np.ndarray, np.ndarray, tuple[float, float, float]]:
    """Return the exact periodic harmonic gauge-wave state in vacuum."""

    if len(shape) != 3 or any(int(size) < 5 for size in shape):
        raise ValueError("shape must contain three sizes of at least five")
    lengths = _spacing_tuple(domain_lengths)
    amp = float(amplitude)
    if not isfinite(amp) or not 0.0 < abs(amp) < 1.0:
        raise ValueError("amplitude magnitude must lie between zero and one")
    if int(cycles) != cycles or cycles <= 0:
        raise ValueError("cycles must be a positive integer")
    spacing = tuple(lengths[i] / int(shape[i]) for i in range(3))
    x = np.arange(shape[0], dtype=float) * spacing[0]
    phase = 2.0 * pi * int(cycles) * (x - float(time)) / lengths[0]
    wave = 1.0 - amp * np.sin(phase)
    d_wave_dt = amp * (2.0 * pi * int(cycles) / lengths[0]) * np.cos(phase)
    d_wave_dx = -d_wave_dt
    wave = np.broadcast_to(wave[:, None, None], shape)
    d_wave_dt = np.broadcast_to(d_wave_dt[:, None, None], shape)
    d_wave_dx = np.broadcast_to(d_wave_dx[:, None, None], shape)

    metric = np.zeros(shape + (4, 4), dtype=float)
    metric[..., 0, 0] = -wave
    metric[..., 1, 1] = wave
    metric[..., 2, 2] = 1.0
    metric[..., 3, 3] = 1.0
    pi_state = np.zeros_like(metric)
    sqrt_wave = np.sqrt(wave)
    pi_state[..., 0, 0] = d_wave_dt / sqrt_wave
    pi_state[..., 1, 1] = -d_wave_dt / sqrt_wave
    phi = np.zeros(shape + (3, 4, 4), dtype=float)
    phi[..., 0, 0, 0] = -d_wave_dx
    phi[..., 0, 1, 1] = d_wave_dx
    source = np.zeros(shape + (4,), dtype=float)
    source_derivative = np.zeros(shape + (4, 4), dtype=float)
    return GHEvolutionState(metric, pi_state, phi), source, source_derivative, spacing


def generalized_harmonic_time_evolution_contract() -> dict[str, Any]:
    return {
        "status": GH_TIME_EVOLUTION_STATUS,
        "state": ["psi_ab", "Pi_ab", "Phi_iab"],
        "integrator": "classical explicit RK4",
        "cfl": "dt <= cfl * min(dx_i) / max(alpha + ||beta||_2)",
        "constraints": ["C_a", "C_iab", "C_ijab"],
        "controls": ["Minkowski fixed point", "exact harmonic gauge wave", "reduction-constraint damping"],
        "excluded_state": ["UET Phi", "UET Pi", "C", "R_gen", "R_obs"],
        "not_implemented": [
            "constraint-preserving non-periodic boundaries",
            "matter stress-energy wiring",
            "detector or SI observable mapping",
        ],
        "claim_boundary": (
            "periodic vacuum time-integration and constraint-diagnostic lane only; "
            "not a production numerical-relativity solver or Gravity validation"
        ),
    }


__all__ = [
    "GH_TIME_EVOLUTION_STATUS",
    "GHEvolutionState",
    "GHTimeIntegrationParameters",
    "GHConstraintNorms",
    "GHTimeEvolutionResult",
    "gh_constraint_norms",
    "gh_cfl_timestep",
    "rk4_periodic_vacuum_gh_step",
    "evolve_periodic_vacuum_gh",
    "harmonic_gauge_wave_state",
    "generalized_harmonic_time_evolution_contract",
]
