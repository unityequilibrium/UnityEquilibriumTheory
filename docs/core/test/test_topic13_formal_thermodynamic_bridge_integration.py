"""Integration tests for the Topic 13 formal thermodynamic bridge."""

from __future__ import annotations

import json
from pathlib import Path

from docs.core.t13_formal_thermodynamic_bridge_integration import (
    formal_thermodynamic_bridge_witness,
)


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_formal_thermodynamic_bridge_integration_audit.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def test_formal_bridge_composes_all_declared_interfaces() -> None:
    witness = formal_thermodynamic_bridge_witness()
    assert witness["all_checks_pass"] is True
    assert witness["status"] == "PASS_FORMAL_T13_THERMODYNAMIC_BRIDGE_INTEGRATION"
    assert witness["witness"]["eos_stability"]["locally_stable"] is True
    assert witness["witness"]["onsager_entropy_value"] >= 0.0
    assert witness["witness"]["heat_flux_entropy_production"] >= 0.0


def test_formal_bridge_artifact_is_lane_closed_not_core_ready() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_FORMAL_T13_THERMODYNAMIC_BRIDGE_INTEGRATION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False
    assert artifact["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["xie_2026_accessed"] is False
    assert "physical_Kubo_coefficient_record_missing" in artifact["major_result"]["open_blockers"]


def test_formal_bridge_preserves_ontology_and_unit_boundary() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    equations = artifact["major_result"]["equation_or_mapping"]
    units = artifact["major_result"]["units"]
    assert "normalized_eos" in equations
    assert "kms_relation" in equations
    assert "entropy_current" in equations
    assert "heat_flux" in equations
    assert "effective response variable" in units["phi"]
    assert "beta_th remains" in units["beta_T13"]


def test_dependency_gate_exposes_formal_lane_without_downstream_unlock() -> None:
    dependency = json.loads(DEPENDENCY.read_text(encoding="utf-8-sig"))
    route = dependency["topic13_partial_evidence"]["formal_thermodynamic_bridge_integration"]
    assert route["summary"]["major_result_id"] == "T13_FORMAL_THERMODYNAMIC_BRIDGE_INTEGRATION"
    assert route["summary"]["closure_level"] == "CLOSED_FOR_LANE"
    assert route["summary"]["full_core_unlock"] is False
