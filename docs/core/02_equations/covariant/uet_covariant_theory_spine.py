"""First-order hyperbolic control spine for UET parent integration.

Version 1 is deliberately limited to periodic Minkowski 1+1 controls with a
fixed metric.  It establishes the API, characteristic, CFL, constraint, and
ledger contracts required before a curved 3+1 implementation can be claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

import numpy as np


THEORY_SPINE_OPERATOR_MODE = "covariant_theory_spine_v1"
THEORY_SPINE_STATUS = "MINKOWSKI_1P1_STRONGLY_HYPERBOLIC_CONTROL_ONLY"


def _positive(value: float, name: str, allow_zero: bool = False) -> float:
    result = float(value)
    valid = result >= 0.0 if allow_zero else result > 0.0
    if not isfinite(result) or not valid:
        raise ValueError(f"{name} must be finite and {'non-negative' if allow_zero else 'positive'}")
    return result


def _field(value: Any, size: int | None, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or result.size < 8 or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite one-dimensional field with >=8 cells")
    if size is not None and result.size != size:
        raise ValueError(f"{name} must have {size} cells")
    return result


@dataclass(frozen=True)
class TheorySpineConfig:
    matter_speed: float
    response_speed: float
    matter_damping: float
    response_damping: float
    stability_safety: float
    boundary_condition: str
    unit_lane: str
    background_mode: str
    parameter_provenance: str

    def __post_init__(self) -> None:
        for name in ("matter_speed", "response_speed"):
            speed = _positive(getattr(self, name), name)
            if speed > 1.0:
                raise ValueError(f"{name} exceeds the natural-unit causal cone")
        _positive(self.matter_damping, "matter_damping", allow_zero=True)
        _positive(self.response_damping, "response_damping", allow_zero=True)
        safety = _positive(self.stability_safety, "stability_safety")
        if safety >= 1.0:
            raise ValueError("stability_safety must be less than one")
        if self.boundary_condition != "periodic":
            raise NotImplementedError("v1 supports periodic boundaries only")
        if self.unit_lane != "natural":
            raise ValueError("v1 supports the natural-unit lane only")
        if self.background_mode != "minkowski_1p1_fixed":
            raise NotImplementedError("curved 3+1 and dynamical metric evolution remain blocked")
        if not self.parameter_provenance.strip():
            raise ValueError("parameter_provenance is required")


@dataclass(frozen=True)
class Covariant3p1State:
    matter_coordinate: np.ndarray
    matter_rate: np.ndarray
    matter_gradient: np.ndarray
    response: np.ndarray
    response_rate: np.ndarray
    response_gradient: np.ndarray
    metric_state: np.ndarray

    def __post_init__(self) -> None:
        matter = _field(self.matter_coordinate, None, "matter_coordinate")
        size = matter.size
        for name in ("matter_rate", "matter_gradient", "response", "response_rate", "response_gradient"):
            object.__setattr__(self, name, _field(getattr(self, name), size, name))
        metric = np.asarray(self.metric_state, dtype=float)
        if metric.shape != (2, 2) or not np.allclose(metric, np.diag([-1.0, 1.0]), atol=1e-12, rtol=0.0):
            raise ValueError("v1 requires the fixed Minkowski 1+1 metric diag(-1,1)")
        object.__setattr__(self, "matter_coordinate", matter)
        object.__setattr__(self, "metric_state", metric)


@dataclass(frozen=True)
class CovariantConstraintState:
    matter_gradient_constraint_max_abs: float
    response_gradient_constraint_max_abs: float
    hamiltonian_constraint_status: str
    momentum_constraint_status: str


@dataclass(frozen=True)
class TheoryStepResult:
    physical_state: Covariant3p1State
    metric_state: np.ndarray
    matter_current: np.ndarray
    stress_energy: np.ndarray
    exchange_current: np.ndarray
    entropy_ledger: Mapping[str, float]
    generated_trace: float
    constraints: CovariantConstraintState
    diagnostics: Mapping[str, Any]


def _dx(field: np.ndarray, dx: float) -> np.ndarray:
    return (np.roll(field, -1) - np.roll(field, 1)) / (2.0 * dx)


def characteristic_analysis(config: TheorySpineConfig) -> dict[str, Any]:
    sectors = {}
    for name, speed in (("matter", config.matter_speed), ("response", config.response_speed)):
        principal = np.array([[0.0, -(speed ** 2)], [-1.0, 0.0]])
        eigenvalues, eigenvectors = np.linalg.eig(principal)
        sectors[name] = {
            "eigenvalues": sorted(float(value.real) for value in eigenvalues),
            "eigenvector_condition_number": float(np.linalg.cond(eigenvectors)),
            "real_characteristics": bool(np.max(np.abs(eigenvalues.imag)) <= 1e-12),
            "complete_eigenbasis": bool(np.linalg.matrix_rank(eigenvectors) == 2),
        }
    return {
        "status": "PASS_STRONG_HYPERBOLIC_LINEAR_CONTROL" if all(
            item["real_characteristics"] and item["complete_eigenbasis"]
            for item in sectors.values()
        ) else "FAIL",
        "sectors": sectors,
        "maximum_characteristic_speed": max(config.matter_speed, config.response_speed),
        "curved_3p1": "NOT_IMPLEMENTED",
    }


def recommended_max_dt(dx: float, config: TheorySpineConfig) -> float:
    spacing = _positive(dx, "dx")
    return config.stability_safety * spacing / max(config.matter_speed, config.response_speed)


def _rhs(state: Covariant3p1State, dx: float, config: TheorySpineConfig, matter_source: np.ndarray, response_source: np.ndarray) -> tuple[np.ndarray, ...]:
    return (
        state.matter_rate,
        config.matter_speed ** 2 * _dx(state.matter_gradient, dx) - config.matter_damping * state.matter_rate + matter_source,
        _dx(state.matter_rate, dx),
        state.response_rate,
        config.response_speed ** 2 * _dx(state.response_gradient, dx) - config.response_damping * state.response_rate + response_source,
        _dx(state.response_rate, dx),
    )


def _state_from(base: Covariant3p1State, values: tuple[np.ndarray, ...]) -> Covariant3p1State:
    return Covariant3p1State(*values, metric_state=base.metric_state.copy())


def _energy(state: Covariant3p1State, dx: float, config: TheorySpineConfig) -> float:
    density = 0.5 * (
        state.matter_rate ** 2 + config.matter_speed ** 2 * state.matter_gradient ** 2
        + state.response_rate ** 2 + config.response_speed ** 2 * state.response_gradient ** 2
    )
    return float(dx * np.sum(density))


def theory_spine_step(
    state: Covariant3p1State, dt: float, dx: float, config: TheorySpineConfig,
    matter_source: Any | None = None, response_source: Any | None = None,
) -> TheoryStepResult:
    step = _positive(dt, "dt")
    limit = recommended_max_dt(dx, config)
    if step > limit:
        raise ValueError(f"dt exceeds stability preflight; recommended_max_dt={limit:.16g}")
    size = state.matter_coordinate.size
    matter_input = np.zeros(size) if matter_source is None else _field(matter_source, size, "matter_source")
    response_input = np.zeros(size) if response_source is None else _field(response_source, size, "response_source")
    before = _energy(state, dx, config)
    k1 = _rhs(state, dx, config, matter_input, response_input)
    predictor = _state_from(state, tuple(value + step * slope for value, slope in zip((state.matter_coordinate, state.matter_rate, state.matter_gradient, state.response, state.response_rate, state.response_gradient), k1)))
    k2 = _rhs(predictor, dx, config, matter_input, response_input)
    updated_values = tuple(value + 0.5 * step * (s1 + s2) for value, s1, s2 in zip((state.matter_coordinate, state.matter_rate, state.matter_gradient, state.response, state.response_rate, state.response_gradient), k1, k2))
    updated = _state_from(state, updated_values)
    after = _energy(updated, dx, config)
    dissipation = float(dx * np.sum(config.matter_damping * updated.matter_rate ** 2 + config.response_damping * updated.response_rate ** 2))
    source_power = float(dx * np.sum(matter_input * updated.matter_rate + response_input * updated.response_rate))
    constraints = CovariantConstraintState(
        matter_gradient_constraint_max_abs=float(np.max(np.abs(updated.matter_gradient - _dx(updated.matter_coordinate, dx)))),
        response_gradient_constraint_max_abs=float(np.max(np.abs(updated.response_gradient - _dx(updated.response, dx)))),
        hamiltonian_constraint_status="NOT_APPLICABLE_FIXED_MINKOWSKI_CONTROL",
        momentum_constraint_status="NOT_APPLICABLE_FIXED_MINKOWSKI_CONTROL",
    )
    matter_current = np.stack([updated.matter_rate, -config.matter_speed ** 2 * updated.matter_gradient], axis=0)
    energy_density = 0.5 * (updated.matter_rate ** 2 + config.matter_speed ** 2 * updated.matter_gradient ** 2 + updated.response_rate ** 2 + config.response_speed ** 2 * updated.response_gradient ** 2)
    momentum_density = -(updated.matter_rate * updated.matter_gradient + updated.response_rate * updated.response_gradient)
    stress_energy = np.stack([energy_density, momentum_density, momentum_density, energy_density], axis=0).reshape(2, 2, size)
    return TheoryStepResult(
        physical_state=updated, metric_state=updated.metric_state,
        matter_current=matter_current, stress_energy=stress_energy,
        exchange_current=np.zeros((2, size)),
        entropy_ledger={"energy_before": before, "energy_after": after, "dissipation_rate": dissipation, "source_power": source_power, "one_step_balance_residual": (after - before) / step + dissipation - source_power},
        generated_trace=step * dissipation,
        constraints=constraints,
        diagnostics={"operator_mode": THEORY_SPINE_OPERATOR_MODE, "status": THEORY_SPINE_STATUS, "recommended_max_dt": limit, "field_clipping": False, "curved_3p1": False, "characteristics": characteristic_analysis(config)},
    )


def theory_spine_contract() -> dict[str, Any]:
    return {
        "operator_mode": THEORY_SPINE_OPERATOR_MODE, "status": THEORY_SPINE_STATUS,
        "supported_background": "fixed Minkowski 1+1", "first_order_reduction": True,
        "strong_hyperbolicity": "checked for linear matter and response sectors",
        "curved_3p1": "BLOCKED", "dynamical_metric": "BLOCKED",
        "hamiltonian_momentum_constraints": "not applicable to fixed-background control",
        "claim_boundary": "numerical causal-control spine, not curved GR evolution",
    }


__all__ = ["THEORY_SPINE_OPERATOR_MODE", "THEORY_SPINE_STATUS", "TheorySpineConfig", "Covariant3p1State", "CovariantConstraintState", "TheoryStepResult", "characteristic_analysis", "recommended_max_dt", "theory_spine_step", "theory_spine_contract"]
