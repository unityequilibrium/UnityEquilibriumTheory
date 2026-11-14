from __future__ import annotations

import pytest

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_state


def test_explicit_outgoing_bose_factor_increases_collision_width() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=96,
        cutoff_factor=55.0,
    )
    classical = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=False,
    )
    quantum = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=True,
    )
    assert quantum.final_state_bose_enhancement_included is True
    assert all(
        quantum_width > classical_width
        for quantum_width, classical_width in zip(
            quantum.collision_width_by_species,
            classical.collision_width_by_species,
        )
    )
    assert quantum.kinetic_coefficient > 0.0
    assert quantum.physical_kubo_coefficient_emitted is False


def test_quantum_collision_lane_converges_under_refinement() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    reference = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
        include_final_state_bose_enhancement=True,
    )
    refined = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=80,
        angular_order=56,
        cutoff_factor=28.0,
        include_final_state_bose_enhancement=True,
    )
    assert refined.kinetic_coefficient == pytest.approx(
        reference.kinetic_coefficient,
        rel=0.02,
    )


def test_quantum_lane_does_not_emit_full_transport_claim() -> None:
    state = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        include_final_state_bose_enhancement=True,
    )
    assert state.ladder_vertex_resummation_included is False
    assert state.physical_kubo_coefficient_emitted is False
