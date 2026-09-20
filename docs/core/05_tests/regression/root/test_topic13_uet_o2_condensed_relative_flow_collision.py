from __future__ import annotations

import numpy as np

from docs.core.uet_o2_condensed_relative_flow_collision import (
    condensed_relative_flow_collision_state,
)


def test_condensed_relative_flow_kernel_is_conservative_and_positive() -> None:
    state = condensed_relative_flow_collision_state(
        0.2,
        1.28,
        0.15,
        radial_order=32,
        angular_order=16,
        cutoff_factor=20.0,
    )
    matrix = np.asarray(state.collision_operator, dtype=float)
    assert state.branch == "condensed"
    assert state.relative_collision_rate > 0.0
    assert state.dc_relative_response > 0.0
    assert np.min(np.linalg.eigvalsh(matrix)) >= -1.0e-12
    assert state.common_flow_conservation_residual <= 1.0e-12
    assert state.source_common_mode_residual <= 1.0e-12
    assert state.entropy_production_at_unit_force > 0.0
    assert state.physical_kubo_coefficient_emitted is False


def test_condensed_relative_flow_kms_and_refinement_are_stable() -> None:
    coarse = condensed_relative_flow_collision_state(
        0.2,
        1.28,
        0.15,
        radial_order=32,
        angular_order=16,
        cutoff_factor=20.0,
    )
    refined = condensed_relative_flow_collision_state(
        0.2,
        1.28,
        0.15,
        radial_order=48,
        angular_order=24,
        cutoff_factor=24.0,
    )
    relative_change = abs(
        refined.dc_relative_response - coarse.dc_relative_response
    ) / coarse.dc_relative_response
    assert relative_change <= 1.0e-3
    assert refined.kms_residual <= 1.0e-10
    assert refined.fdt_residual <= 1.0e-10
    assert all(value >= -1.0e-12 for value in refined.spectral_density)
