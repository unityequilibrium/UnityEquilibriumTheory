from __future__ import annotations

import pytest

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import (
    KINETIC_COLLISION_KUBO_STATUS,
    kinetic_collision_contract,
    kinetic_collision_state,
)


def test_normal_collision_kernel_is_positive_and_finite() -> None:
    state = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        FiniteTemperatureO2QuasiparticleConfig(
            quadrature_order=96,
            cutoff_factor=55.0,
        ),
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
    )
    assert all(value > 0.0 for value in state.collision_width_by_species)
    assert state.kinetic_coefficient > 0.0
    assert state.final_state_bose_enhancement_included is False
    assert state.ladder_vertex_resummation_included is False
    assert state.physical_kubo_coefficient_emitted is False


def test_collision_lane_is_stable_under_refinement() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    coarse = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
    )
    refined = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
    )
    assert refined.kinetic_coefficient == pytest.approx(
        coarse.kinetic_coefficient,
        rel=0.02,
    )


def test_contract_keeps_physical_kubo_scope_open() -> None:
    contract = kinetic_collision_contract()
    assert contract["status"] == KINETIC_COLLISION_KUBO_STATUS
    assert contract["excluded"]["microscopic_SK_KMS_match"] is True
    assert "not temperature" in contract["unit_contract"]["Phi"]
