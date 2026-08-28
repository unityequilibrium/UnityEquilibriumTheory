"""Tests for periodic curved 3+1 differential-geometry operators."""

from __future__ import annotations

import hashlib
import json
from math import pi
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_constraints import ADMMatterProjection, evaluate_adm_constraints
from docs.core.uet_curved_3p1_geometry import (
    adm_geometry_from_periodic_grid,
    compute_periodic_momentum_tensor_divergence,
    compute_periodic_spatial_geometry,
    curved_3p1_geometry_operator_contract,
    periodic_central_derivative,
)
from docs.scripts.audit.audit_uet_curved_3p1_geometry import build_artifacts


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "docs/core/artifacts/curved_3p1_geometry_operator_verification.json"
FORMULA = ROOT / "docs/core/artifacts/curved_3p1_geometry_operator_formula_audit.json"
GATE = ROOT / "docs/core/artifacts/core_curved_3p1_parent_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def _flat_metric(resolution: int) -> np.ndarray:
    return np.broadcast_to(np.eye(3), (resolution,) * 3 + (3, 3)).copy()


def test_flat_metric_has_exact_zero_connection_and_curvature() -> None:
    result = compute_periodic_spatial_geometry(_flat_metric(6), (0.2, 0.2, 0.2))
    assert np.max(np.abs(result.christoffel_symbols)) == 0.0
    assert np.max(np.abs(result.ricci_tensor)) == 0.0
    assert np.max(np.abs(result.ricci_scalar)) == 0.0
    assert result.max_abs_metric_compatibility_residual == 0.0


def test_conformal_metric_ricci_converges_at_second_order() -> None:
    errors = []
    for resolution in (10, 20, 40):
        length = 2.0 * pi
        x_grid = (np.arange(resolution) * length / resolution)[:, None, None]
        psi = np.broadcast_to(1.0 + 0.05 * np.cos(x_grid), (resolution,) * 3)
        metric = psi[..., None, None] ** 4 * np.eye(3)
        expected = np.broadcast_to(8.0 * 0.05 * np.cos(x_grid) / psi**5, psi.shape)
        result = compute_periodic_spatial_geometry(metric, (length / resolution,) * 3)
        errors.append(float(np.sqrt(np.mean((result.ricci_scalar - expected) ** 2))))
    orders = [np.log2(errors[index] / errors[index + 1]) for index in range(2)]
    assert min(orders) >= 1.8


def test_momentum_divergence_converges_for_off_diagonal_k() -> None:
    errors = []
    for resolution in (10, 20, 40):
        length = 2.0 * pi
        x_grid = (np.arange(resolution) * length / resolution)[:, None, None]
        metric = _flat_metric(resolution)
        curvature = np.zeros_like(metric)
        curvature[..., 0, 1] = curvature[..., 1, 0] = 0.1 * np.sin(x_grid)
        expected = np.zeros(metric.shape[:3] + (3,))
        expected[..., 1] = 0.1 * np.cos(x_grid)
        actual = compute_periodic_momentum_tensor_divergence(
            metric, curvature, (length / resolution,) * 3
        )
        errors.append(float(np.sqrt(np.mean((actual - expected) ** 2))))
    orders = [np.log2(errors[index] / errors[index + 1]) for index in range(2)]
    assert min(orders) >= 1.8


def test_adm_adapter_uses_computed_geometry_without_relabelling_state() -> None:
    resolution = 8
    metric = _flat_metric(resolution)
    curvature = np.zeros_like(metric)
    geometry, spatial = adm_geometry_from_periodic_grid(
        lapse=1.0,
        shift=np.zeros((resolution,) * 3 + (3,)),
        spatial_metric=metric,
        extrinsic_curvature=curvature,
        spacing=(0.25, 0.25, 0.25),
    )
    result = evaluate_adm_constraints(
        geometry,
        ADMMatterProjection(0.0, np.zeros((resolution,) * 3 + (3,))),
    )
    assert result.max_abs_hamiltonian_residual == 0.0
    assert result.max_abs_momentum_residual == 0.0
    assert spatial.diagnostics["metric_evolution"] is False
    assert curved_3p1_geometry_operator_contract()["ontology"]["gamma_ij"] == "standard spatial metric; not Phi"


def test_invalid_grid_spacing_shape_and_metric_are_rejected() -> None:
    with pytest.raises(ValueError, match="spacing"):
        periodic_central_derivative(np.zeros((5, 5, 5)), axis=0, spacing=0.0)
    with pytest.raises(ValueError, match="at least five"):
        compute_periodic_spatial_geometry(_flat_metric(4), (1.0, 1.0, 1.0))
    invalid = _flat_metric(5)
    invalid[..., 0, 0] = -1.0
    with pytest.raises(ValueError, match="positive definite"):
        compute_periodic_spatial_geometry(invalid, (1.0, 1.0, 1.0))
    cached = compute_periodic_spatial_geometry(_flat_metric(5), (1.0, 1.0, 1.0))
    conformal = 1.1 * _flat_metric(5)
    with pytest.raises(ValueError, match="does not match"):
        compute_periodic_momentum_tensor_divergence(
            conformal,
            np.zeros_like(conformal),
            (1.0, 1.0, 1.0),
            geometry=cached,
        )


def test_generated_geometry_artifacts_are_stable_and_source_linked() -> None:
    generated = build_artifacts()
    stored = (
        json.loads(VERIFY.read_text(encoding="utf-8")),
        json.loads(FORMULA.read_text(encoding="utf-8")),
    )
    for live, persisted in zip(generated, stored):
        live.pop("generated_at", None)
        persisted.pop("generated_at", None)
        assert live == persisted
    verification = json.loads(VERIFY.read_text(encoding="utf-8"))
    source = ROOT / verification["source"]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == verification["source"]["sha256"]
    for relative_path, expected_hash in verification["source_hashes"].items():
        path = ROOT / relative_path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
    assert verification["status"] == "PASS_CURVED_3P1_GEOMETRY_OPERATOR"
    assert verification["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert verification["claim_promotion"] is False


def test_parent_and_dependency_gates_remain_partial_and_block_gravity() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    dependency = json.loads(DEPENDENCY.read_text(encoding="utf-8"))
    levels = {entry["major_result_id"]: entry["closure_level"] for entry in register["entries"]}
    assert gate["requirements"]["metric_to_ricci_operator"] == "PASS"
    assert gate["requirements"]["metric_and_extrinsic_curvature_evolution"] == "OPEN"
    assert gate["major_result"]["closure_level"] == "PARTIAL"
    assert levels["CORE_CURVED_3P1_GEOMETRY_OPERATOR_READY"] == "CLOSED_FOR_LANE"
    assert dependency["curved_3p1_progress"]["geometry_operator"]["closure_level"] == "CLOSED_FOR_LANE"
    assert dependency["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"] == "BLOCKED_DEPENDENCY"
