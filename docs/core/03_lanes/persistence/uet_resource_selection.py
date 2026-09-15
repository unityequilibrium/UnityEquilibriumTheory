"""Non-agentic interaction-selection comparator for the persistence principle.

This lane uses a finite-state replicator-style dynamical system. The
interaction matrix is an explicit normalized compatibility/payoff comparator;
it is not an intention, utility-bearing agent, or universal optimization law.
The resource ledger is kept separate from the collective coordinate C.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Sequence, Tuple

RESOURCE_SELECTION_STATUS = "CANDIDATE_NORMALIZED_DYNAMIC_SELECTION"
RESOURCE_SELECTION_OPERATOR_MODE = "resource_selection_dynamic_game_v1"


class ResourceSelectionStabilityError(ValueError):
    """Raised when the declared time step cannot preserve the lane contract."""

    def __init__(self, message: str, recommended_max_dt: float | None = None) -> None:
        super().__init__(message)
        self.recommended_max_dt = recommended_max_dt


@dataclass(frozen=True)
class ResourceSelectionConfig:
    """Configuration for a deterministic, non-agentic interaction-selection lane."""

    interaction_matrix: Tuple[Tuple[float, ...], ...] = (
        (0.9, 0.8),
        (0.8, 0.9),
    )
    behavior_cost: Tuple[float, ...] = (0.02, 0.03)
    maintenance_cost: Tuple[float, ...] = (0.01, 0.01)
    initial_probabilities: Tuple[float, ...] = (0.5, 0.5)
    selection_weight: float = 0.5
    cost_weight: float = 0.5
    initial_available_resource: float = 1.0
    sustain_threshold: float = 0.2
    input_power: float = 0.0
    output_power: float = 0.0
    unit_lane: str = "normalized"

    def __post_init__(self) -> None:
        matrix = tuple(tuple(float(value) for value in row) for row in self.interaction_matrix)
        n = len(matrix)
        if n < 2 or any(len(row) != n for row in matrix):
            raise ValueError("interaction_matrix must be a square matrix with at least two states")
        if any(not isfinite(value) or value < -1.0 or value > 1.0 for row in matrix for value in row):
            raise ValueError("interaction_matrix entries must be finite and in [-1, 1]")
        costs = tuple(float(value) for value in self.behavior_cost)
        maintenance = tuple(float(value) for value in self.maintenance_cost)
        probabilities = tuple(float(value) for value in self.initial_probabilities)
        if len(costs) != n or len(maintenance) != n or len(probabilities) != n:
            raise ValueError("state vectors must match interaction_matrix dimension")
        if any(not isfinite(value) or value < 0.0 for value in costs + maintenance):
            raise ValueError("resource cost vectors must be finite and non-negative")
        if any(not isfinite(value) or value < 0.0 for value in probabilities):
            raise ValueError("initial_probabilities must be finite and non-negative")
        if abs(sum(probabilities) - 1.0) > 1e-12:
            raise ValueError("initial_probabilities must sum to one")
        for name, value in (
            ("selection_weight", self.selection_weight),
            ("cost_weight", self.cost_weight),
            ("initial_available_resource", self.initial_available_resource),
            ("sustain_threshold", self.sustain_threshold),
            ("input_power", self.input_power),
            ("output_power", self.output_power),
        ):
            if not isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
        if self.selection_weight < 0.0 or self.cost_weight < 0.0:
            raise ValueError("selection_weight and cost_weight must be non-negative")
        if self.initial_available_resource <= 0.0:
            raise ValueError("initial_available_resource must be positive")
        if self.sustain_threshold < 0.0 or self.sustain_threshold >= self.initial_available_resource:
            raise ValueError("sustain_threshold must be non-negative and below initial resource")
        if self.unit_lane != "normalized":
            raise NotImplementedError("resource selection v1 supports only unit_lane='normalized'")

    @property
    def state_count(self) -> int:
        return len(self.interaction_matrix)


@dataclass(frozen=True)
class ResourceSelectionResult:
    """Outputs from one deterministic resource-selection trajectory."""

    times: Tuple[float, ...]
    probabilities: Tuple[Tuple[float, ...], ...]
    collective_compatibility: Tuple[float, ...]
    fitness: Tuple[Tuple[float, ...], ...]
    behavior_power: Tuple[float, ...]
    maintenance_power: Tuple[float, ...]
    available_resource: Tuple[float, ...]
    behavior_work: float
    maintenance_work: float
    external_net_work: float
    ledger_closure_residual: float
    probability_simplex_drift: float
    minimum_probability: float
    persistence_time: float | None
    status: str = RESOURCE_SELECTION_STATUS


def _validate_time(horizon: float, dt: float) -> int:
    if not isfinite(float(horizon)) or horizon <= 0.0:
        raise ValueError("horizon must be finite and positive")
    if not isfinite(float(dt)) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    steps_float = horizon / dt
    steps = int(round(steps_float))
    if steps < 1 or abs(steps - steps_float) > 1e-10:
        raise ValueError("horizon/dt must be an integer for deterministic sampling")
    return steps


def _fitness(config: ResourceSelectionConfig, probabilities: Sequence[float]) -> Tuple[float, ...]:
    interaction = tuple(
        sum(row[j] * probabilities[j] for j in range(config.state_count))
        for row in config.interaction_matrix
    )
    return tuple(
        config.selection_weight * interaction[i]
        - config.cost_weight * config.behavior_cost[i]
        for i in range(config.state_count)
    )


def _collective_compatibility(
    config: ResourceSelectionConfig, probabilities: Sequence[float]
) -> float:
    return sum(
        probabilities[i] * config.interaction_matrix[i][j] * probabilities[j]
        for i in range(config.state_count)
        for j in range(config.state_count)
    )


def _advance_probabilities(
    config: ResourceSelectionConfig,
    probabilities: Sequence[float],
    dt: float,
) -> Tuple[float, ...]:
    fitness = _fitness(config, probabilities)
    mean_fitness = sum(probabilities[i] * fitness[i] for i in range(config.state_count))
    exponents = tuple(dt * (value - mean_fitness) for value in fitness)
    max_span = max(exponents) - min(exponents)
    if max_span > 50.0:
        recommended = 50.0 / max_span * dt
        raise ResourceSelectionStabilityError(
            "time step is too large for the exponential replicator update",
            recommended_max_dt=recommended,
        )
    weights = tuple(probabilities[i] * exp(exponents[i]) for i in range(config.state_count))
    normalizer = sum(weights)
    if not isfinite(normalizer) or normalizer <= 0.0:
        raise ResourceSelectionStabilityError("probability update became non-finite")
    next_probabilities = tuple(value / normalizer for value in weights)
    if min(next_probabilities) < -1e-14 or abs(sum(next_probabilities) - 1.0) > 1e-12:
        raise ResourceSelectionStabilityError("probability simplex contract failed")
    return next_probabilities


def simulate_resource_selection(
    config: ResourceSelectionConfig,
    horizon: float,
    dt: float,
) -> ResourceSelectionResult:
    """Run a deterministic replicator/resource ledger without clipping or fitting.

    C is reported as the quadratic collective compatibility p.T @ A @ p.
    The interaction matrix and cost vectors are constitutive inputs, so this
    result is a candidate comparator rather than a first-principles law.
    """

    steps = _validate_time(horizon, dt)
    probabilities = tuple(float(value) for value in config.initial_probabilities)
    resource = float(config.initial_available_resource)
    times = [0.0]
    probability_history = [probabilities]
    compatibility_history = [_collective_compatibility(config, probabilities)]
    fitness_history = [_fitness(config, probabilities)]
    resource_history = [resource]
    behavior_powers: list[float] = []
    maintenance_powers: list[float] = []

    for index in range(steps):
        midpoint_probabilities = _advance_probabilities(config, probabilities, dt / 2.0)
        midpoint_behavior = sum(
            midpoint_probabilities[i] * config.behavior_cost[i]
            for i in range(config.state_count)
        )
        midpoint_maintenance = sum(
            midpoint_probabilities[i] * config.maintenance_cost[i]
            for i in range(config.state_count)
        )
        resource += (
            config.input_power
            - config.output_power
            - midpoint_behavior
            - midpoint_maintenance
        ) * dt
        probabilities = _advance_probabilities(config, probabilities, dt)
        behavior_powers.append(midpoint_behavior)
        maintenance_powers.append(midpoint_maintenance)
        times.append((index + 1) * dt)
        probability_history.append(probabilities)
        compatibility_history.append(_collective_compatibility(config, probabilities))
        fitness_history.append(_fitness(config, probabilities))
        resource_history.append(resource)

    persistence_time = next(
        (times[i] for i, value in enumerate(resource_history) if value <= config.sustain_threshold),
        None,
    )
    behavior_work = sum(behavior_powers) * dt
    maintenance_work = sum(maintenance_powers) * dt
    external_net_work = (config.input_power - config.output_power) * horizon
    expected_resource = (
        config.initial_available_resource
        + external_net_work
        - behavior_work
        - maintenance_work
    )
    closure_residual = resource_history[-1] - expected_resource
    simplex_drift = max(abs(sum(row) - 1.0) for row in probability_history)
    minimum_probability = min(value for row in probability_history for value in row)

    return ResourceSelectionResult(
        times=tuple(times),
        probabilities=tuple(probability_history),
        collective_compatibility=tuple(compatibility_history),
        fitness=tuple(fitness_history),
        behavior_power=tuple(behavior_powers),
        maintenance_power=tuple(maintenance_powers),
        available_resource=tuple(resource_history),
        behavior_work=behavior_work,
        maintenance_work=maintenance_work,
        external_net_work=external_net_work,
        ledger_closure_residual=closure_residual,
        probability_simplex_drift=simplex_drift,
        minimum_probability=minimum_probability,
        persistence_time=persistence_time,
    )


__all__ = [
    "RESOURCE_SELECTION_OPERATOR_MODE",
    "RESOURCE_SELECTION_STATUS",
    "ResourceSelectionConfig",
    "ResourceSelectionResult",
    "ResourceSelectionStabilityError",
    "simulate_resource_selection",
]
