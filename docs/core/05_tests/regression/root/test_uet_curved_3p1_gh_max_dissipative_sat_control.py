from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np


AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_curved_3p1_gh_max_dissipative_sat_control"
)
ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_max_diss_sat_control.json"
)


def test_common_tensor_metric_orthogonalizes_all_declared_boundary_projectors() -> None:
    result = AUDIT._projector_metric_audit(AUDIT._tensor_metric())
    assert result["normal_count"] == 26
    assert result["projector_ranks"] == {
        "constraint": 4,
        "physical": 2,
        "gauge": 4,
    }
    assert result["tensor_metric_min_eigenvalue"] > 0.0
    assert result["max_self_adjoint_residual"] < 1.0e-12
    assert result["max_sector_orthogonality_residual"] < 1.0e-12


def test_full_u1_energy_and_reduction_identities_pass() -> None:
    artifact = AUDIT.build_artifact()
    assert artifact["status"] == "PASS_FULL_U1_MAX_DISS_SAT_CONTROL"
    assert all(artifact["checks"].values())
    comparison = artifact["method_comparison"]
    assert comparison["status"] == "FAIL_STRONG_RINNE_LGL_SENSITIVITY"
    assert all(not item["pulse_absorption_pass"] for item in comparison["screens"])
    assert all(not item["reduction_constraint_pass"] for item in comparison["screens"])
    assert artifact["major_result"]["dependency_unlocked"].startswith("none;")
    assert artifact["scope"]["boundary_condition"].endswith(
        "not Rinne differential CPBC"
    )
    assert artifact["claim_promotion"] is False


def test_persisted_artifact_does_not_promote_the_curved_parent() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["status"] == "PASS_FULL_U1_MAX_DISS_SAT_CONTROL"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["dependency_unlocked"].startswith("none;")
    assert artifact["scope"]["positive_shift_u2_A"] is False
    assert artifact["scope"]["nonlinear_evolution"] is False
    assert artifact["claim_promotion"] is False
