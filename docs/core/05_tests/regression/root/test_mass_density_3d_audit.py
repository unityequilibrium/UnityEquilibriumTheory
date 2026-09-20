"""Artifact-boundary tests for the candidate SI 3D density operator."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import json
from pathlib import Path


ROOT = repo_root()
SCRIPT = ROOT / "docs/scripts/audit/audit_mass_density_3d.py"
ARTIFACT = ROOT / "docs/core/07_artifacts/verification/mass_density_3d_contract_verification.json"


def _module():
    spec = importlib.util.spec_from_file_location("mass_density_3d_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_persisted_artifact_matches_current_generator() -> None:
    persisted = _artifact()
    generated = _module().build_artifact()
    assert persisted == generated


def test_3d_unit_and_integral_contract_passes_without_physical_promotion() -> None:
    artifact = _artifact()
    assert artifact["audit_status"] == "PASS_WITH_BLOCKED_EXTERNAL_3D_MAPPING"
    assert artifact["mapping_status"] == "SI_3D_SYNTHETIC_MEASUREMENT_OPERATOR_ONLY"
    assert artifact["claim_status"] == "SIMULATION_ONLY"
    assert all(artifact["gates"].values())
    assert artifact["observable_operator"]["status"] == (
        "C_TO_SHAPE_OPEN_SYNTHETIC_SHAPE_CONTRACT_CHECKED"
    )


def test_3d_source_has_uncertainty_calibration_and_holdout_boundary() -> None:
    source = _artifact()["source_contract"]
    assert source["uncertainty_status"] == (
        "declared_source_amplitude_only_no_external_propagation"
    )
    assert source["calibration_status"] == "NOT_REQUIRED_FOR_SYNTHETIC"
    assert source["holdout_policy"].startswith("LOCKED")
    assert source["fit_status"] == "NOT_FITTED"


def test_3d_claim_boundary_keeps_c_to_density_open() -> None:
    artifact = _artifact()
    assert "C does not determine rho_hat or A_m in this artifact" in artifact[
        "limitations"
    ]
    assert "external 3D density operator" in artifact["next_controller"]
