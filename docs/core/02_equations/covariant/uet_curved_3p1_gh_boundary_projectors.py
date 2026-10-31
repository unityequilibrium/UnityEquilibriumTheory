"""Local GH constraint/physical/gauge boundary projector algebra.

This module constructs the source-defined projectors on symmetric spacetime
two-tensors in a local orthonormal frame. It does not impose boundary data or
provide an initial-boundary evolution operator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

import numpy as np


SYMMETRIC_PAIRS = tuple((i, j) for i in range(4) for j in range(i, 4))
_SIGNATURE = np.diag([-1.0, 1.0, 1.0, 1.0])


@dataclass(frozen=True)
class GHBoundaryProjectors:
    normal: tuple[float, float, float]
    constraint: np.ndarray
    physical: np.ndarray
    gauge: np.ndarray
    ranks: dict[str, int]
    residuals: dict[str, float]
    spatial_projector_covariant: np.ndarray
    spatial_projector_contravariant: np.ndarray
    timelike_normal: np.ndarray


def _unit_normal(value: Any) -> np.ndarray:
    normal = np.asarray(value, dtype=float)
    if normal.shape != (3,) or not np.all(np.isfinite(normal)):
        raise ValueError("normal must be a finite three-vector")
    norm = float(np.linalg.norm(normal))
    if not isfinite(norm) or norm <= 0.0:
        raise ValueError("normal must be nonzero")
    return normal / norm


def _operator_matrix(operator: np.ndarray) -> np.ndarray:
    matrix = np.empty((len(SYMMETRIC_PAIRS), len(SYMMETRIC_PAIRS)), dtype=float)
    for column, (i, j) in enumerate(SYMMETRIC_PAIRS):
        tensor = np.zeros((4, 4), dtype=float)
        tensor[i, j] = 1.0
        if i != j:
            tensor[j, i] = 1.0
        projected = np.einsum("abcd,cd->ab", operator, tensor)
        matrix[:, column] = [projected[a, b] for a, b in SYMMETRIC_PAIRS]
    return matrix


def build_gh_boundary_projectors(normal: Any) -> GHBoundaryProjectors:
    """Build Rinne's local projectors on symmetric covariant tensors.

    The returned 10x10 maps split the incoming u1- tensor into four
    constraint, two physical, and four gauge components. The constraint and
    physical boundary conditions themselves remain differential conditions.
    """

    unit = _unit_normal(normal)
    t_up = np.array([1.0, 0.0, 0.0, 0.0])
    n_up = np.concatenate(([0.0], unit))
    t_down = _SIGNATURE @ t_up
    n_down = _SIGNATURE @ n_up
    k_up = (t_up - n_up) / sqrt(2.0)
    l_up = (t_up + n_up) / sqrt(2.0)
    l_down = _SIGNATURE @ l_up

    p_down = _SIGNATURE + np.outer(t_down, t_down) - np.outer(n_down, n_down)
    p_up = _SIGNATURE + np.outer(t_up, t_up) - np.outer(n_up, n_up)
    p_mixed = p_down @ _SIGNATURE

    p_constraint_tensor = 0.5 * np.einsum("ab,cd->abcd", p_down, p_up)
    p_constraint_tensor -= 0.5 * (
        np.einsum("a,bc,d->abcd", l_down, p_mixed, k_up)
        + np.einsum("a,bd,c->abcd", l_down, p_mixed, k_up)
        + np.einsum("b,ac,d->abcd", l_down, p_mixed, k_up)
        + np.einsum("b,ad,c->abcd", l_down, p_mixed, k_up)
    )
    p_constraint_tensor += np.einsum(
        "a,b,c,d->abcd", l_down, l_down, k_up, k_up
    )

    p_physical_tensor = np.einsum("ac,bd->abcd", p_mixed, p_mixed)
    p_physical_tensor -= 0.5 * np.einsum("ab,cd->abcd", p_down, p_up)

    p_constraint = _operator_matrix(p_constraint_tensor)
    p_physical = _operator_matrix(p_physical_tensor)
    identity = np.eye(len(SYMMETRIC_PAIRS), dtype=float)
    p_gauge = identity - p_constraint - p_physical

    residuals = {
        "constraint_idempotence": float(np.max(np.abs(p_constraint @ p_constraint - p_constraint))),
        "physical_idempotence": float(np.max(np.abs(p_physical @ p_physical - p_physical))),
        "gauge_idempotence": float(np.max(np.abs(p_gauge @ p_gauge - p_gauge))),
        "constraint_physical_annihilation": float(np.max(np.abs(p_constraint @ p_physical))),
        "physical_constraint_annihilation": float(np.max(np.abs(p_physical @ p_constraint))),
        "constraint_gauge_annihilation": float(np.max(np.abs(p_constraint @ p_gauge))),
        "gauge_constraint_annihilation": float(np.max(np.abs(p_gauge @ p_constraint))),
        "physical_gauge_annihilation": float(np.max(np.abs(p_physical @ p_gauge))),
        "gauge_physical_annihilation": float(np.max(np.abs(p_gauge @ p_physical))),
        "completeness": float(np.max(np.abs(p_constraint + p_physical + p_gauge - identity))),
    }
    ranks = {
        "constraint": int(np.linalg.matrix_rank(p_constraint, tol=1.0e-10)),
        "physical": int(np.linalg.matrix_rank(p_physical, tol=1.0e-10)),
        "gauge": int(np.linalg.matrix_rank(p_gauge, tol=1.0e-10)),
    }

    for value in (p_constraint, p_physical, p_gauge, p_down, p_up, t_up):
        value.setflags(write=False)
    return GHBoundaryProjectors(
        normal=tuple(float(value) for value in unit),
        constraint=p_constraint,
        physical=p_physical,
        gauge=p_gauge,
        ranks=ranks,
        residuals=residuals,
        spatial_projector_covariant=p_down,
        spatial_projector_contravariant=p_up,
        timelike_normal=t_up,
    )


def apply_gh_boundary_projector(
    tensor: Any,
    projector: Any,
) -> np.ndarray:
    """Apply a 10x10 boundary projector to a finite symmetric 4x4 tensor."""

    value = np.asarray(tensor, dtype=float)
    matrix = np.asarray(projector, dtype=float)
    if value.shape != (4, 4) or not np.all(np.isfinite(value)):
        raise ValueError("tensor must be a finite 4x4 array")
    if not np.allclose(value, value.T, atol=1.0e-12, rtol=0.0):
        raise ValueError("tensor must be symmetric")
    if matrix.shape != (len(SYMMETRIC_PAIRS), len(SYMMETRIC_PAIRS)):
        raise ValueError("projector must have shape (10,10)")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("projector must be finite")

    coordinates = np.array([value[i, j] for i, j in SYMMETRIC_PAIRS])
    output_coordinates = matrix @ coordinates
    output = np.zeros((4, 4), dtype=float)
    for coordinate, (i, j) in zip(output_coordinates, SYMMETRIC_PAIRS):
        output[i, j] = coordinate
        output[j, i] = coordinate
    return output


__all__ = [
    "GHBoundaryProjectors",
    "SYMMETRIC_PAIRS",
    "apply_gh_boundary_projector",
    "build_gh_boundary_projectors",
]
