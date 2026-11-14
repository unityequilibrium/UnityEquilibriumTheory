"""Identifiability checks for a candidate C-to-mass-density lane.

The first question is whether a geometry-only relational coordinate can uniquely
determine a mass-density field.  The answer is tested constructively by holding
the two-body geometry fixed and rescaling the masses.  The density changes while
the current ``C`` coordinate does not, so a direct ``rho=f(C)`` mapping is not
identified by this lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, pi, sqrt
from typing import List, Tuple

from docs.core.relational_two_body_baseline import TwoBodyState


@dataclass(frozen=True)
class MassDensityLaneConfig:
    """Normalized density-observable configuration.

    The density unit is code mass per code length.  This is a synthetic
    correspondence lane, not an SI mass-density contract.
    """

    grid_min: float = -4.0
    grid_max: float = 4.0
    grid_points: int = 401
    kernel_width: float = 0.15


def grid(config: MassDensityLaneConfig) -> Tuple[List[float], float]:
    if config.grid_points < 3:
        raise ValueError("grid_points must be at least 3")
    if config.grid_max <= config.grid_min:
        raise ValueError("grid_max must exceed grid_min")
    if config.kernel_width <= 0.0:
        raise ValueError("kernel_width must be positive")
    dx = (config.grid_max - config.grid_min) / (config.grid_points - 1)
    return [config.grid_min + index * dx for index in range(config.grid_points)], dx


def _gaussian_kernel(x: float, center: float, width: float) -> float:
    normalization = 1.0 / (sqrt(2.0 * pi) * width)
    return normalization * exp(-0.5 * ((x - center) / width) ** 2)


def mass_density_from_point_masses(
    state: TwoBodyState,
    mass_a: float,
    mass_b: float,
    config: MassDensityLaneConfig,
) -> Tuple[List[float], float]:
    """Build a normalized observable density using a declared smoothing kernel."""

    if mass_a <= 0.0 or mass_b <= 0.0:
        raise ValueError("masses must be positive")
    xs, dx = grid(config)
    density = [
        mass_a * _gaussian_kernel(x, state.position_a[0], config.kernel_width)
        + mass_b * _gaussian_kernel(x, state.position_b[0], config.kernel_width)
        for x in xs
    ]
    return density, dx


def integrated_density(density: List[float], dx: float) -> float:
    if len(density) < 2:
        raise ValueError("density requires at least two samples")
    return dx * (0.5 * density[0] + sum(density[1:-1]) + 0.5 * density[-1])


def normalized_shape(density: List[float], dx: float) -> List[float]:
    total = integrated_density(density, dx)
    if total <= 0.0:
        raise ValueError("density integral must be positive")
    return [value / total for value in density]


def max_relative_difference(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("arrays must have equal length")
    return max(
        abs(left - right) / max(1.0, abs(left), abs(right))
        for left, right in zip(a, b)
    )


def max_absolute_difference(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("arrays must have equal length")
    return max(abs(left - right) for left, right in zip(a, b))


__all__ = [
    "MassDensityLaneConfig",
    "grid",
    "integrated_density",
    "mass_density_from_point_masses",
    "max_absolute_difference",
    "max_relative_difference",
    "normalized_shape",
]
