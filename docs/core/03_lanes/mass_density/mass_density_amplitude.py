"""Explicit amplitude/source contract for the candidate C-to-density lane.

The relational coordinate can provide a normalized geometry/shape diagnostic, but
the identifiability audit shows that it cannot provide the density amplitude by
itself. This module keeps the missing degree of freedom explicit:

    rho(x) = A_m * rho_hat(x | geometry, relative source state)

``A_m`` is a declared source quantity. It is not inferred from ``C`` and this
module does not fit it to observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .mass_density_correspondence import (
    MassDensityLaneConfig,
    _gaussian_kernel,
    grid,
    integrated_density,
    max_relative_difference,
)
from docs.core.relational_two_body_baseline import TwoBodyState


NORMALIZED_AMPLITUDE_UNIT = "normalized_code_mass"
ALLOWED_PROVENANCE = {
    "DECLARED_SYNTHETIC",
    "DECLARED_EXTERNAL_SOURCE",
    "DERIVED_FROM_DECLARED_SOURCE",
}


@dataclass(frozen=True)
class MassDensityAmplitudeSource:
    """Declared total-density amplitude for the normalized candidate lane."""

    amplitude: float
    source_id: str
    provenance_status: str = "DECLARED_SYNTHETIC"
    unit_lane: str = NORMALIZED_AMPLITUDE_UNIT
    fitted: bool = False

    def validate(self) -> None:
        if self.amplitude <= 0.0:
            raise ValueError("mass-density amplitude must be positive")
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")
        if self.provenance_status not in ALLOWED_PROVENANCE:
            raise ValueError("unsupported amplitude provenance status")
        if self.unit_lane != NORMALIZED_AMPLITUDE_UNIT:
            raise ValueError("v1 accepts only the normalized amplitude unit lane")

    def prediction_ready(self) -> bool:
        """Return whether the source is explicit and not a fitted parameter."""

        self.validate()
        return not self.fitted


def _validate_relative_weights(weights: Sequence[float]) -> Tuple[float, float]:
    if len(weights) != 2:
        raise ValueError("the two-body v1 lane requires exactly two relative weights")
    if any(weight < 0.0 for weight in weights):
        raise ValueError("relative source weights must be non-negative")
    total = float(sum(weights))
    if total <= 0.0:
        raise ValueError("relative source weights must have a positive sum")
    return (float(weights[0]) / total, float(weights[1]) / total)


def normalized_geometry_density_shape(
    state: TwoBodyState,
    config: MassDensityLaneConfig,
    relative_weights: Sequence[float] = (0.5, 0.5),
) -> Tuple[List[float], float]:
    """Return a unit-integral shape from geometry and declared composition.

    This is a standard kernel observable definition. It is deliberately not a
    derivation of the UET coordinate or of a physical mass profile.
    """

    weights = _validate_relative_weights(relative_weights)
    xs, dx = grid(config)
    raw = [
        weights[0] * _gaussian_kernel(x, state.position_a[0], config.kernel_width)
        + weights[1] * _gaussian_kernel(x, state.position_b[0], config.kernel_width)
        for x in xs
    ]
    total = integrated_density(raw, dx)
    if total <= 0.0:
        raise ValueError("geometry shape integral must be positive")
    return [value / total for value in raw], dx


def mass_density_from_amplitude(
    shape: Sequence[float],
    dx: float,
    source: MassDensityAmplitudeSource,
) -> Tuple[List[float], float]:
    """Apply an explicit source amplitude to a normalized density shape."""

    source.validate()
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    if len(shape) < 2:
        raise ValueError("shape requires at least two samples")
    shape_values = [float(value) for value in shape]
    shape_integral = integrated_density(shape_values, dx)
    if shape_integral <= 0.0:
        raise ValueError("shape integral must be positive")
    normalized = [value / shape_integral for value in shape_values]
    return [source.amplitude * value for value in normalized], dx


def augmented_density_from_geometry(
    state: TwoBodyState,
    config: MassDensityLaneConfig,
    source: MassDensityAmplitudeSource,
    relative_weights: Sequence[float] = (0.5, 0.5),
) -> Tuple[List[float], float]:
    """Construct ``rho = A_m * rho_hat`` with all source inputs explicit."""

    shape, dx = normalized_geometry_density_shape(state, config, relative_weights)
    return mass_density_from_amplitude(shape, dx, source)


def amplitude_scaling_residual(
    density: Sequence[float], scaled_density: Sequence[float], scale: float
) -> float:
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    return max_relative_difference(
        list(scaled_density), [scale * value for value in density]
    )


__all__ = [
    "ALLOWED_PROVENANCE",
    "NORMALIZED_AMPLITUDE_UNIT",
    "MassDensityAmplitudeSource",
    "amplitude_scaling_residual",
    "augmented_density_from_geometry",
    "mass_density_from_amplitude",
    "normalized_geometry_density_shape",
]
