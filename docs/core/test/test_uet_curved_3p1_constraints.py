"""Tests for the curved 3+1 ADM constraint-interface wave."""

from __future__ import annotations

import hashlib
import json
from math import pi
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_constraints import (
    ADMGeometryState,
    ADMMatterProjection,
    adm_constraint_contract,
    evaluate_adm_constraints,
    flat_flrw_adm_control,
    minkowski_adm_control,
)


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/curved_3p1_adm_constraint_interface_audit.json"
GATE = ROOT / "docs/core/artifacts/core_curved_3p1_parent_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def test_minkowski_vacuum_constraints_vanish() -> None:
    geometry, matter = minkowski_adm_control((2, 3))
    result = evaluate_adm_constraints(geometry, matter)
    assert result.max_abs_hamiltonian_residual == 0.0
    assert result.max_abs_momentum_residual == 0.0
    assert result.diagnostics["metric_evolution"] is False


def test_flat_flrw_control_satisfies_friedmann_constraint() -> None:
    geometry, matter = flat_flrw_adm_control(1.8, 0.17, shape=(4,))
    result = evaluate_adm_constraints(geometry, matter)
    assert result.max_abs_hamiltonian_residual <= 1e-15
    assert result.max_abs_momentum_residual == 0.0
    assert np.allclose(result.trace_extrinsic_curvature, -3.0 * 0.17)


def test_wrong_flrw_density_is_detected() -> None:
    geometry, matter = flat_flrw_adm_control(1.2, 0.2)
    result = evaluate_adm_constraints(
        geometry,
        ADMMatterProjection(1.1 * matter.energy_density, matter.momentum_density),
    )
    expected = 16.0 * pi * 0.1 * matter.energy_density
    assert abs(result.max_abs_hamiltonian_residual - expected) <= 1e-15


def test_momentum_source_is_not_silently_ignored() -> None:
    geometry, _ = minkowski_adm_control()
    momentum = np.array([0.1, -0.2, 0.3])
    result = evaluate_adm_constraints(
        geometry, ADMMatterProjection(0.0, momentum)
    )
    assert np.allclose(result.momentum_residual, -8.0 * pi * momentum)


def test_invalid_metric_lapse_and_shapes_are_rejected() -> None:
    geometry, matter = minkowski_adm_control()
    with pytest.raises(ValueError, match="positive definite"):
        evaluate_adm_constraints(
            ADMGeometryState(1.0, geometry.shift, np.diag([-1.0, 1.0, 1.0]), geometry.extrinsic_curvature, 0.0, geometry.momentum_tensor_divergence),
            matter,
        )
    with pytest.raises(ValueError, match="lapse"):
        evaluate_adm_constraints(
            ADMGeometryState(0.0, geometry.shift, geometry.spatial_metric, geometry.extrinsic_curvature, 0.0, geometry.momentum_tensor_divergence),
            matter,
        )
    with pytest.raises(ValueError, match="momentum_density"):
        evaluate_adm_constraints(geometry, ADMMatterProjection(0.0, np.zeros(2)))


def test_contract_preserves_ontology_and_blocks_solver_claim() -> None:
    contract = adm_constraint_contract()
    assert contract["ontology"]["spatial_metric"] == "standard 3-metric; not Phi"
    assert contract["ontology"]["R_gen"] == "excluded derived history trace"
    assert "spatial-metric and extrinsic-curvature evolution" in contract["not_implemented"]


def test_generated_artifacts_are_hash_linked_and_partial() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    source = ROOT / audit["source"]["path"]
    assert audit["status"] == "PASS_CURVED_3P1_ADM_CONSTRAINT_INTERFACE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == audit["source"]["sha256"]
    assert gate["major_result"]["closure_level"] == "PARTIAL"
    assert gate["requirements"]["adm_constraint_interface"] == "PASS"
    assert (
        gate["requirements"]["metric_and_extrinsic_curvature_evolution"]
        == "PARTIAL_RHS_OPERATOR_ONLY"
    )
    assert gate["requirements"]["fixed_gauge_adm_hyperbolicity"] == "CLOSED_AS_NO_GO"
    assert gate["claim_promotion"] is False


def test_register_and_dependency_gate_keep_gravity_blocked() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    dependency = json.loads(DEPENDENCY.read_text(encoding="utf-8"))
    levels = {
        entry["major_result_id"]: entry["closure_level"]
        for entry in register["entries"]
    }
    assert levels["CORE_CURVED_3P1_ADM_CONSTRAINT_INTERFACE_READY"] == "CLOSED_FOR_LANE"
    assert levels["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"] == "PARTIAL"
    gravity = dependency["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]
    assert gravity["status"] == "BLOCKED_DEPENDENCY"
    assert gravity["unmet_dependencies"][0]["current_level"] == "PARTIAL"
    assert dependency["curved_3p1_progress"]["gravity_unlock_status"] == "BLOCKED_DEPENDENCY"
