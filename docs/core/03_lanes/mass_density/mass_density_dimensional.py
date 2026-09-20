"""Synthetic SI unit contract for the augmented one-dimensional density lane.

This module closes only a dimensional bookkeeping question:

    rho_1D(x) = A_m * rho_hat(x) / L_scale

where ``A_m`` is in kg, ``L_scale`` is in m, and ``rho_hat`` is a unit-integral
shape in the dimensionless code coordinate. The result is a line-mass density
in kg/m. It is intentionally not a three-dimensional galaxy measurement map.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .mass_density_amplitude import (
    MassDensityAmplitudeSource,
    normalized_geometry_density_shape,
)
from .mass_density_correspondence import MassDensityLaneConfig, integrated_density
from docs.core.relational_two_body_baseline import TwoBodyState


SI_LINE_DENSITY_UNIT = "kg_per_m"
SI_AMPLITUDE_UNIT = "kg"


@dataclass(frozen=True)
class SIDensityAmplitudeSource:
    """Explicit SI source contract for a synthetic one-dimensional lane."""

    amplitude_kg: float
    length_scale_m: float
    source_id: str
    source_locator: str = "synthetic://uet/mass-density/v1"
    source_hash: str = "synthetic-config-v1"
    uncertainty_kg: float = 0.0
    fitted: bool = False

    def validate(self) -> None:
        if self.amplitude_kg <= 0.0:
            raise ValueError("SI amplitude must be positive")
        if self.length_scale_m <= 0.0:
            raise ValueError("length_scale_m must be positive")
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")
        if not self.source_locator.strip() or not self.source_hash.strip():
            raise ValueError("source locator and hash are required")
        if self.uncertainty_kg < 0.0:
            raise ValueError("uncertainty_kg must be non-negative")

    def prediction_ready(self) -> bool:
        self.validate()
        return not self.fitted


def si_line_density_from_shape(
    shape: List[float],
    dx_code: float,
    source: SIDensityAmplitudeSource,
) -> Tuple[List[float], float]:
    """Convert a unit-integral code shape to a kg/m line density."""

    source.validate()
    if dx_code <= 0.0:
        raise ValueError("dx_code must be positive")
    if len(shape) < 2:
        raise ValueError("shape requires at least two samples")
    shape_integral = integrated_density(shape, dx_code)
    if shape_integral <= 0.0:
        raise ValueError("shape integral must be positive")
    normalized = [value / shape_integral for value in shape]
    dx_m = dx_code * source.length_scale_m
    line_density = [
        source.amplitude_kg * value / source.length_scale_m for value in normalized
    ]
    return line_density, dx_m


def augmented_si_line_density(
    state: TwoBodyState,
    config: MassDensityLaneConfig,
    source: SIDensityAmplitudeSource,
) -> Tuple[List[float], float]:
    """Build the synthetic SI 1D observable from explicit source inputs."""

    shape, dx_code = normalized_geometry_density_shape(state, config)
    return si_line_density_from_shape(shape, dx_code, source)


__all__ = [
    "SI_AMPLITUDE_UNIT",
    "SI_LINE_DENSITY_UNIT",
    "SIDensityAmplitudeSource",
    "augmented_si_line_density",
    "si_line_density_from_shape",
]
