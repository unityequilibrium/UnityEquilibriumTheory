"""Weak maximally dissipative incoming-u1 SAT control for a 1D GH slab.

This is a full ten-component frozen-background control branch. It prescribes
the incoming characteristic data directly and is not the differential Rinne
constraint/Weyl boundary condition.
"""

from __future__ import annotations

from math import isfinite
from typing import Any

import numpy as np

from .uet_curved_3p1_gh_full_u1_slab import GHSlabState


def gh_max_dissipative_u1_sat_rhs(
    state: GHSlabState,
    derivative: Any,
    norm_weights: Any,
    gamma2: float,
    incoming_data: Any | None = None,
) -> GHSlabState:
    """Evaluate the 1D linear GH RHS with weak incoming-characteristic data.

    The SAT penalty acts only on the normal-derivative RHS, so the reduction
    constraint obeys ``Cdot = -gamma2*C`` independently of boundary data.
    ``incoming_data`` has left/right rows and ten packed symmetric-tensor
    components per row.
    """

    d_matrix = np.asarray(derivative, dtype=float)
    weights = np.asarray(norm_weights, dtype=float)
    if d_matrix.ndim != 2 or d_matrix.shape[0] != d_matrix.shape[1]:
        raise ValueError("derivative must be a square matrix")
    node_count = d_matrix.shape[0]
    if node_count < 2 or not np.all(np.isfinite(d_matrix)):
        raise ValueError("derivative must be finite and have at least two nodes")
    if weights.shape != (node_count,) or not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise ValueError("norm_weights must be positive, finite, and match nodes")
    if not isfinite(float(gamma2)) or gamma2 <= 0.0:
        raise ValueError("gamma2 must be finite and positive")

    expected = (node_count, 10)
    fields = tuple(
        np.asarray(value, dtype=float)
        for value in (
            state.metric,
            state.normal_derivative,
            state.normal_spatial_derivative,
        )
    )
    if any(value.shape != expected or not np.all(np.isfinite(value)) for value in fields):
        raise ValueError(f"all GH slab fields must be finite with shape {expected}")
    metric, pi, phi = fields

    if incoming_data is None:
        data = np.zeros((2, 10), dtype=float)
    else:
        data = np.asarray(incoming_data, dtype=float)
        if data.shape != (2, 10) or not np.all(np.isfinite(data)):
            raise ValueError("incoming_data must be a finite array with shape (2,10)")

    metric_rhs = -pi.copy()
    pi_rhs = -(d_matrix @ phi)
    phi_rhs = (
        -(d_matrix @ pi)
        + float(gamma2) * (d_matrix @ metric)
        - float(gamma2) * phi
    )

    for face_index, normal, data_index in (
        (0, -1, 0),
        (node_count - 1, 1, 1),
    ):
        incoming = (
            pi[face_index]
            - normal * phi[face_index]
            - float(gamma2) * metric[face_index]
            - data[data_index]
        )
        pi_rhs[face_index] -= incoming / weights[face_index]

    return GHSlabState(metric_rhs, pi_rhs, phi_rhs)


__all__ = ["gh_max_dissipative_u1_sat_rhs"]
