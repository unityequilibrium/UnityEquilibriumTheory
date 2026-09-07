"""Regression tests for the Topic 13 lattice heat parent."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_lattice_momentum_relaxing_heat_parent import (
    lattice_momentum_relaxing_heat_parent_state,
)


def test_normal_collisions_preserve_crystal_momentum():
    state = lattice_momentum_relaxing_heat_parent_state()
    assert state.normal_minimum_eigenvalue >= -1.0e-12
    assert state.normal_momentum_null_residual <= 1.0e-12
    assert state.source_momentum_overlap >= 1.0 - 1.0e-12


def test_zero_resistive_rate_has_no_finite_steady_conductivity():
    state = lattice_momentum_relaxing_heat_parent_state(resistive_rate=0.0)
    assert not state.finite_steady_conductivity
    assert state.conductivity_natural is None
    assert state.total_minimum_eigenvalue <= 1.0e-12


def test_resistive_rate_opens_positive_finite_heat_response():
    state = lattice_momentum_relaxing_heat_parent_state()
    assert state.finite_steady_conductivity
    assert state.total_minimum_eigenvalue > 0.0
    assert state.minimum_entropy_quadratic_eigenvalue > 0.0
    assert state.conductivity_natural > 0.0
    assert state.conductivity_relative_residual <= 1.0e-11


def test_conductivity_scales_inverse_with_resistive_rate():
    slow = lattice_momentum_relaxing_heat_parent_state(resistive_rate=0.0125)
    fast = lattice_momentum_relaxing_heat_parent_state(resistive_rate=0.05)
    ratio = slow.conductivity_natural / fast.conductivity_natural
    assert ratio == pytest.approx(4.0, rel=1.0e-11)


def test_natural_unit_energy_scaling_is_e_squared():
    reference = lattice_momentum_relaxing_heat_parent_state()
    scaled = lattice_momentum_relaxing_heat_parent_state(
        temperature=0.5,
        normal_rate=0.4,
        resistive_rate=0.05,
    )
    ratio = scaled.conductivity_natural / reference.conductivity_natural
    assert ratio == pytest.approx(4.0, rel=1.0e-11)


def test_quadrature_refinement_converges():
    coarse = lattice_momentum_relaxing_heat_parent_state(radial_order=24)
    fine = lattice_momentum_relaxing_heat_parent_state(radial_order=48)
    relative = abs(fine.conductivity_natural - coarse.conductivity_natural) / abs(
        fine.conductivity_natural
    )
    assert relative <= 1.0e-8


@pytest.mark.parametrize(
    "kwargs",
    [
        {"temperature": 0.0},
        {"sound_speed": 0.0},
        {"sound_speed": 1.1},
        {"normal_rate": 0.0},
        {"resistive_rate": -0.1},
        {"radial_order": 3},
    ],
)
def test_invalid_inputs_fail_closed(kwargs):
    with pytest.raises(ValueError):
        lattice_momentum_relaxing_heat_parent_state(**kwargs)


def test_no_fit_holdout_or_uet_mapping_is_emitted():
    state = lattice_momentum_relaxing_heat_parent_state()
    assert state.unit_lane == "natural_3p1_hbar_c_kB_1"
    assert state.conductivity_unit == "E^2"
    assert not state.physical_kubo_coefficient_emitted
    assert not state.uet_mapping_claimed
    assert not state.xie_2026_accessed
    assert not state.parameter_fitting_performed


def test_generated_artifact_and_registry_are_strict_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = root / "docs/core/artifacts/t13_lattice_momentum_relaxing_heat_parent_audit.json"
    registry_path = root / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_lattice_heat_parent_addendum.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == evidence["sha256"]
    assert registry["full_core_unlock"] is False
    assert registry["claim_promotion"] is False
