"""Candidate SI 3D mass-density measurement operator.

This module closes a dimensional/operator contract, not the missing physical
meaning of ``C``.  A declared, unit-integral code-space shape is converted by

    rho_3D(x_phys) = A_m * rho_hat(x_code) / (L_x L_y L_z)

where ``A_m`` is an explicit source amplitude in kg and the three ``L`` values
are explicit metre scales.  The shape, source provenance, uncertainty,
calibration state, and holdout policy remain separate records so a synthetic
operator cannot be reported as a galaxy measurement or as a derivation of
mass from ``C``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import List, Sequence, Tuple


Grid3D = List[List[List[float]]]
Spacing3D = Tuple[float, float, float]

SI_VOLUME_DENSITY_UNIT = "kg_per_m3"
SI_MASS_UNIT = "kg"
ALLOWED_EVIDENCE_STATUS = {"SIMULATION_ONLY", "EXTERNAL_SOURCE_LOCKED"}
ALLOWED_CALIBRATION_STATUS = {
    "NOT_REQUIRED_FOR_SYNTHETIC",
    "EXTERNAL_CALIBRATION_REQUIRED",
    "INDEPENDENTLY_CALIBRATED",
}


@dataclass(frozen=True)
class MassDensity3DSource:
    """Explicit amplitude/provenance contract for the 3D density operator."""

    mass_kg: float
    length_scale_x_m: float
    length_scale_y_m: float
    length_scale_z_m: float
    source_id: str
    source_locator: str
    source_hash: str
    uncertainty_kg: float = 0.0
    evidence_status: str = "SIMULATION_ONLY"
    calibration_status: str = "NOT_REQUIRED_FOR_SYNTHETIC"
    holdout_policy: str = "LOCKED_BEFORE_EXTERNAL_COMPARISON"
    fitted: bool = False

    @property
    def length_scales_m(self) -> Spacing3D:
        return (
            self.length_scale_x_m,
            self.length_scale_y_m,
            self.length_scale_z_m,
        )

    def validate(self) -> None:
        scalar_values = (
            self.mass_kg,
            self.length_scale_x_m,
            self.length_scale_y_m,
            self.length_scale_z_m,
            self.uncertainty_kg,
        )
        if not all(isfinite(float(value)) for value in scalar_values):
            raise ValueError("3D density source values must be finite")
        if self.mass_kg <= 0.0:
            raise ValueError("mass_kg must be positive")
        if any(value <= 0.0 for value in self.length_scales_m):
            raise ValueError("all length scales must be positive")
        if self.uncertainty_kg < 0.0:
            raise ValueError("uncertainty_kg must be non-negative")
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")
        if not self.source_locator.strip() or not self.source_hash.strip():
            raise ValueError("source locator and hash are required")
        if self.evidence_status not in ALLOWED_EVIDENCE_STATUS:
            raise ValueError("unsupported 3D density evidence status")
        if self.calibration_status not in ALLOWED_CALIBRATION_STATUS:
            raise ValueError("unsupported 3D density calibration status")
        if not self.holdout_policy.strip():
            raise ValueError("holdout_policy must be declared")

    def prediction_ready(self) -> bool:
        """Return whether the declared operator can run without target fitting."""

        self.validate()
        return not self.fitted

    def physical_mapping_ready(self) -> bool:
        """Return whether the source is eligible for an external physical claim."""

        self.validate()
        return (
            self.evidence_status == "EXTERNAL_SOURCE_LOCKED"
            and self.calibration_status == "INDEPENDENTLY_CALIBRATED"
            and not self.fitted
            and self.holdout_policy.startswith("LOCKED")
        )


def _validate_spacing(spacing: Spacing3D) -> None:
    if len(spacing) != 3 or not all(isfinite(float(value)) for value in spacing):
        raise ValueError("3D spacing must contain three finite values")
    if any(value <= 0.0 for value in spacing):
        raise ValueError("3D spacing values must be positive")


def _shape_dimensions(shape: Sequence[Sequence[Sequence[float]]]) -> Tuple[int, int, int]:
    nx = len(shape)
    if nx < 2:
        raise ValueError("3D shape requires at least two samples per axis")
    ny = len(shape[0])
    if ny < 2:
        raise ValueError("3D shape requires at least two samples per axis")
    nz = len(shape[0][0]) if ny else 0
    if nz < 2:
        raise ValueError("3D shape requires at least two samples per axis")
    if any(len(row) != ny for row in shape):
        raise ValueError("3D shape must be rectangular on the y axis")
    if any(len(cell) != nz for row in shape for cell in row):
        raise ValueError("3D shape must be rectangular on the z axis")
    return nx, ny, nz


def integrated_density_3d(
    density: Sequence[Sequence[Sequence[float]]],
    spacing: Spacing3D,
) -> float:
    """Integrate a cell-centred 3D density using a finite-volume sum."""

    _validate_spacing(spacing)
    _shape_dimensions(density)
    cell_volume = spacing[0] * spacing[1] * spacing[2]
    total = 0.0
    for row in density:
        for cell in row:
            for value in cell:
                value_float = float(value)
                if not isfinite(value_float) or value_float < 0.0:
                    raise ValueError("3D density values must be finite and non-negative")
                total += value_float
    return total * cell_volume


def normalized_shape_3d(
    shape: Sequence[Sequence[Sequence[float]]],
    spacing: Spacing3D,
) -> Grid3D:
    """Normalize a non-negative code-space shape to unit integral."""

    total = integrated_density_3d(shape, spacing)
    if total <= 0.0:
        raise ValueError("3D shape integral must be positive")
    return [
        [
            [float(value) / total for value in cell]
            for cell in row
        ]
        for row in shape
    ]


def gaussian_shape_3d(
    grid_points: Tuple[int, int, int] = (25, 25, 25),
    extent: Tuple[float, float, float] = (3.0, 3.0, 3.0),
    center: Tuple[float, float, float] = (0.25, -0.15, 0.1),
    width: Tuple[float, float, float] = (0.65, 0.8, 0.55),
) -> Tuple[Grid3D, Spacing3D]:
    """Create a deterministic cell-centred synthetic 3D shape."""

    if len(grid_points) != 3 or any(value < 2 for value in grid_points):
        raise ValueError("grid_points must contain three values >= 2")
    if len(extent) != 3 or any(value <= 0.0 for value in extent):
        raise ValueError("extent values must be positive")
    if len(width) != 3 or any(value <= 0.0 for value in width):
        raise ValueError("width values must be positive")
    spacing = tuple(
        2.0 * extent[index] / grid_points[index] for index in range(3)
    )
    axes = [
        [
            -extent[index] + (position + 0.5) * spacing[index]
            for position in range(grid_points[index])
        ]
        for index in range(3)
    ]
    shape: Grid3D = []
    for x_value in axes[0]:
        plane: List[List[float]] = []
        for y_value in axes[1]:
            line: List[float] = []
            for z_value in axes[2]:
                exponent = 0.5 * (
                    ((x_value - center[0]) / width[0]) ** 2
                    + ((y_value - center[1]) / width[1]) ** 2
                    + ((z_value - center[2]) / width[2]) ** 2
                )
                line.append(exp(-exponent))
            plane.append(line)
        shape.append(plane)
    return shape, spacing


def si_volume_density_from_shape(
    shape: Sequence[Sequence[Sequence[float]]],
    code_spacing: Spacing3D,
    source: MassDensity3DSource,
) -> Tuple[Grid3D, Spacing3D]:
    """Map a declared normalized shape to an SI kg/m^3 observable."""

    source.validate()
    normalized = normalized_shape_3d(shape, code_spacing)
    physical_spacing = tuple(
        code_spacing[index] * source.length_scales_m[index]
        for index in range(3)
    )
    volume_scale = (
        source.length_scale_x_m
        * source.length_scale_y_m
        * source.length_scale_z_m
    )
    density = [
        [
            [source.mass_kg * value / volume_scale for value in cell]
            for cell in row
        ]
        for row in normalized
    ]
    return density, physical_spacing


def mass_from_si_volume_density(
    density: Sequence[Sequence[Sequence[float]]],
    physical_spacing: Spacing3D,
) -> float:
    """Integrate a kg/m^3 field over physical metres."""

    return integrated_density_3d(density, physical_spacing)


__all__ = [
    "ALLOWED_CALIBRATION_STATUS",
    "ALLOWED_EVIDENCE_STATUS",
    "Grid3D",
    "MassDensity3DSource",
    "SI_MASS_UNIT",
    "SI_VOLUME_DENSITY_UNIT",
    "gaussian_shape_3d",
    "integrated_density_3d",
    "mass_from_si_volume_density",
    "normalized_shape_3d",
    "si_volume_density_from_shape",
]
