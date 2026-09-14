from __future__ import annotations

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_state


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=96,
        cutoff_factor=48.0,
    )


def test_quantum_final_state_bose_branch_is_enabled_and_positive() -> None:
    quantum = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        _config(),
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=True,
    )
    assert quantum.final_state_bose_enhancement_included is True
    assert all(value > 0.0 for value in quantum.collision_width_by_species)
    assert quantum.kinetic_coefficient > 0.0


def test_quantum_bose_factor_increases_collision_width_over_dilute_baseline() -> None:
    config = _config()
    dilute = kinetic_collision_state(
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
    assert all(
        q >= d for q, d in zip(
            quantum.collision_width_by_species,
            dilute.collision_width_by_species,
        )
    )
    assert any(
        q > d * (1.0 + 1.0e-9) for q, d in zip(
            quantum.collision_width_by_species,
            dilute.collision_width_by_species,
        )
    )


def test_quantum_bose_branch_refines_stably() -> None:
    config = _config()
    reference = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=True,
    )
    refined = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
        include_final_state_bose_enhancement=True,
    )
    width_change = max(
        abs(a - b) / b
        for a, b in zip(
            refined.collision_width_by_species,
            reference.collision_width_by_species,
        )
    )
    response_change = abs(
        refined.kinetic_coefficient - reference.kinetic_coefficient
    ) / reference.kinetic_coefficient
    assert width_change <= 0.02
    assert response_change <= 0.02
