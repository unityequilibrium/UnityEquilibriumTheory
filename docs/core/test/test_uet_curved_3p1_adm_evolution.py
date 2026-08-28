"""Tests for the ADM RHS and fixed-gauge hyperbolicity no-go wave."""

from __future__ import annotations

import hashlib
import json
from math import pi
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_adm_evolution import (
    ADMStressProjection,
    adm_evolution_contract,
    compute_adm_evolution_rhs,
    fixed_gauge_adm_principal_symbol,
)
from docs.scripts.audit.audit_uet_curved_3p1_adm_evolution import build_artifacts


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs/core/artifacts"


def _flat(resolution: int, scale: float = 1.0) -> np.ndarray:
    return np.broadcast_to(scale**2 * np.eye(3), (resolution,) * 3 + (3, 3)).copy()


def _vacuum(resolution: int) -> tuple[np.ndarray, ADMStressProjection]:
    vector = np.zeros((resolution,) * 3 + (3,))
    tensor = np.zeros((resolution,) * 3 + (3, 3))
    return vector, ADMStressProjection(0.0, vector, tensor)


def test_minkowski_is_exact_fixed_point() -> None:
    metric = _flat(5)
    shift, matter = _vacuum(5)
    result = compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=np.zeros_like(metric), lapse=1.0, shift=shift, matter=matter, spacing=(1.0,) * 3)
    assert np.max(np.abs(result.spatial_metric_rhs)) == 0.0
    assert np.max(np.abs(result.extrinsic_curvature_rhs)) == 0.0
    assert result.diagnostics["time_integrator"] == "NOT_IMPLEMENTED"


def test_flat_dust_flrw_instantaneous_rhs_matches() -> None:
    resolution = 5
    scale = 1.8
    hubble = 0.17
    metric = _flat(resolution, scale)
    curvature = -hubble * metric
    shift, _ = _vacuum(resolution)
    density = 3.0 * hubble**2 / (8.0 * pi)
    matter = ADMStressProjection(density, shift, np.zeros_like(metric))
    result = compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=curvature, lapse=1.0, shift=shift, matter=matter, spacing=(1.0,) * 3)
    assert np.max(np.abs(result.spatial_metric_rhs - 2.0 * hubble * metric)) <= 1e-14
    assert np.max(np.abs(result.extrinsic_curvature_rhs + 0.5 * hubble**2 * metric)) <= 1e-14


def test_lapse_and_shift_terms_show_second_order_convergence() -> None:
    lapse_errors = []
    shift_errors = []
    for resolution in (10, 20, 40):
        length = 2.0 * pi
        step = length / resolution
        x = (np.arange(resolution) * step)[:, None, None]
        metric = _flat(resolution)
        curvature = np.zeros_like(metric)
        shift, matter = _vacuum(resolution)
        lapse = np.broadcast_to(1.0 + 0.05 * np.cos(x), metric.shape[:3])
        lapse_result = compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=curvature, lapse=lapse, shift=shift, matter=matter, spacing=(step,) * 3)
        expected_k = np.zeros_like(metric)
        expected_k[..., 0, 0] = 0.05 * np.cos(x)
        lapse_errors.append(float(np.sqrt(np.mean((lapse_result.extrinsic_curvature_rhs - expected_k) ** 2))))
        shift[..., 0] = 0.05 * np.sin(x)
        shift_result = compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=curvature, lapse=1.0, shift=shift, matter=matter, spacing=(step,) * 3)
        expected_g = np.zeros_like(metric)
        expected_g[..., 0, 0] = 0.1 * np.cos(x)
        shift_errors.append(float(np.sqrt(np.mean((shift_result.spatial_metric_rhs - expected_g) ** 2))))
    assert min(np.log2(np.asarray(lapse_errors[:-1]) / np.asarray(lapse_errors[1:]))) >= 1.8
    assert min(np.log2(np.asarray(shift_errors[:-1]) / np.asarray(shift_errors[1:]))) >= 1.8


@pytest.mark.parametrize("direction", ([1.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.2, -0.3, 0.7]))
def test_fixed_gauge_adm_symbol_has_jordan_defect(direction: list[float]) -> None:
    result = fixed_gauge_adm_principal_symbol(direction)
    assert result.zero_algebraic_multiplicity == 6
    assert result.zero_geometric_multiplicity == 3
    assert result.eigenvector_rank == 9
    assert result.complete_eigenbasis is False
    assert result.classification == "DEFECTIVE_ZERO_SPEED_JORDAN_BLOCK"


def test_invalid_lapse_stress_and_direction_are_rejected() -> None:
    metric = _flat(5)
    shift, matter = _vacuum(5)
    with pytest.raises(ValueError, match="lapse"):
        compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=np.zeros_like(metric), lapse=0.0, shift=shift, matter=matter, spacing=(1.0,) * 3)
    with pytest.raises(ValueError, match="spatial_stress"):
        compute_adm_evolution_rhs(spatial_metric=metric, extrinsic_curvature=np.zeros_like(metric), lapse=1.0, shift=shift, matter=ADMStressProjection(0.0, shift, np.zeros(metric.shape[:3] + (2, 2))), spacing=(1.0,) * 3)
    with pytest.raises(ValueError, match="nonzero"):
        fixed_gauge_adm_principal_symbol([0.0, 0.0, 0.0])


def test_artifacts_are_stable_hash_linked_and_select_gh_without_claiming_it() -> None:
    names = ("curved_3p1_adm_evolution_operator_verification.json", "curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json", "curved_3p1_adm_evolution_formula_audit.json", "curved_3p1_formulation_selection_gate.json")
    generated = build_artifacts()
    persisted = tuple(json.loads((ARTIFACTS / name).read_text(encoding="utf-8")) for name in names)
    for live, stored in zip(generated, persisted):
        live.pop("generated_at", None)
        stored.pop("generated_at", None)
        assert live == stored
    verification, no_go, _, selection = persisted
    for relative_path, expected_hash in verification["source_hashes"].items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
    assert verification["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert no_go["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert selection["selected_next_branch"] == "first_order_generalized_harmonic"
    assert selection["selected_next_branch_status"] == "PREREGISTERED_NOT_IMPLEMENTED"
    assert selection["claim_promotion"] is False


def test_contract_keeps_uet_ontology_and_solver_claim_blocked() -> None:
    contract = adm_evolution_contract()
    assert contract["ontology"]["gamma_ij"] == "standard spatial metric; not Phi"
    assert contract["ontology"]["K_ij"] == "standard extrinsic curvature; not Pi"
    assert contract["ontology"]["R_gen"] == "excluded derived history trace"
    assert contract["branch_decision"]["fixed_geodesic_adm"] == "REJECTED_FOR_STRONG_HYPERBOLIC_PARENT"
    assert "strongly-hyperbolic generalized-harmonic evolution" in contract["not_implemented"]
