"""Tests for analytic GR correspondence controls."""

import numpy as np
import pytest

from docs.core.uet_gr_correspondence import (
    flat_flrw_control, gr_correspondence_contract, minkowski_null_control,
    newtonian_poisson_residual, schwarzschild_exterior_null_control,
)


def test_minkowski_flrw_and_schwarzschild_input_residuals_close() -> None:
    records = (
        minkowski_null_control(),
        flat_flrw_control(1.4, 0.2, -0.03, cosmological_constant=0.01),
        schwarzschild_exterior_null_control(10.0, 1.0),
    )
    assert max(float(np.max(np.abs(record.residual))) for record in records) <= 1e-12
    assert all(record.diagnostics["curvature_computed_from_metric"] is False for record in records)


def test_newtonian_poisson_correspondence() -> None:
    density = np.array([0.1, 0.2, 0.3])
    g = 0.4
    laplacian = 4.0 * np.pi * g * density
    assert np.max(np.abs(newtonian_poisson_residual(laplacian, density, g))) <= 1e-12


def test_schwarzschild_control_rejects_inside_horizon() -> None:
    with pytest.raises(ValueError, match="outside"):
        schwarzschild_exterior_null_control(1.5, 1.0)


def test_contract_blocks_geometric_and_numerical_claims() -> None:
    contract = gr_correspondence_contract()
    assert contract["curvature_from_metric"] == "NOT_IMPLEMENTED"
    assert contract["constraint_evolution"] == "NOT_IMPLEMENTED"
