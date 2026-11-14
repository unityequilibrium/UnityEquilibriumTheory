"""One-dimensional conservative spatial operators for UET research lanes.

The v1 matter-space operator deliberately supports only one-dimensional fields.
The finite-volume form keeps the discrete integral of a Laplacian at roundoff
for both periodic and zero-flux boundaries.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

BoundaryCondition = Literal["periodic", "zero_flux"]


def validate_field_1d(field: np.ndarray, name: str = "field") -> np.ndarray:
    """Return a finite float array and reject unsupported shapes explicitly."""

    array = np.asarray(field, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional in matter_space_coupled_v1")
    if array.size < 4:
        raise ValueError(f"{name} must contain at least four cells")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values")
    return array


def validate_dx(dx: float) -> float:
    """Validate and return the normalized grid spacing."""

    value = float(dx)
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError("dx must be finite and positive")
    return value


def validate_boundary(boundary: str) -> BoundaryCondition:
    """Validate the matter-space boundary convention."""

    if boundary not in {"periodic", "zero_flux"}:
        raise ValueError("boundary must be 'periodic' or 'zero_flux'")
    return boundary  # type: ignore[return-value]


def integral_1d(field: np.ndarray, dx: float) -> float:
    """Cell-centred finite-volume integral."""

    array = validate_field_1d(field)
    spacing = validate_dx(dx)
    return float(np.sum(array) * spacing)


def face_gradient_1d(
    field: np.ndarray,
    dx: float,
    boundary: BoundaryCondition = "periodic",
) -> np.ndarray:
    """Return forward gradients on cell faces.

    Periodic output has one face per cell. Zero-flux output has ``N+1`` faces
    with the two boundary fluxes fixed to zero.
    """

    array = validate_field_1d(field)
    spacing = validate_dx(dx)
    mode = validate_boundary(boundary)
    if mode == "periodic":
        return (np.roll(array, -1) - array) / spacing

    faces = np.zeros(array.size + 1, dtype=float)
    faces[1:-1] = (array[1:] - array[:-1]) / spacing
    return faces


def laplacian_1d(
    field: np.ndarray,
    dx: float,
    boundary: BoundaryCondition = "periodic",
) -> np.ndarray:
    """Return the conservative divergence of the face gradient."""

    array = validate_field_1d(field)
    spacing = validate_dx(dx)
    mode = validate_boundary(boundary)
    faces = face_gradient_1d(array, spacing, mode)
    if mode == "periodic":
        return (faces - np.roll(faces, 1)) / spacing
    return (faces[1:] - faces[:-1]) / spacing


def gradient_squared_cell_1d(
    field: np.ndarray,
    dx: float,
    boundary: BoundaryCondition = "periodic",
) -> np.ndarray:
    """Map squared face gradients to cells while preserving their integral."""

    array = validate_field_1d(field)
    mode = validate_boundary(boundary)
    faces_sq = np.square(face_gradient_1d(array, dx, mode))
    if mode == "periodic":
        return 0.5 * (faces_sq + np.roll(faces_sq, 1))
    return 0.5 * (faces_sq[1:] + faces_sq[:-1])


def gradient_energy_integral_1d(
    field: np.ndarray,
    dx: float,
    boundary: BoundaryCondition = "periodic",
) -> float:
    """Return ``integral |grad field|^2 dx`` in the discrete convention."""

    array = validate_field_1d(field)
    spacing = validate_dx(dx)
    faces = face_gradient_1d(array, spacing, validate_boundary(boundary))
    return float(np.sum(np.square(faces)) * spacing)
