from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_status_boundary_closes_formal_lane_without_physical_promotion() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_SCOPED_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["physical_closure_status"] == "BLOCKED"
    assert artifact["claim_promotion"] is False
    assert artifact["checks"]["conservative_action_identifiability_no_go_passes"] is True
    assert artifact["checks"]["formal_sk_kms_entropy_interface_passes"] is True
    assert artifact["checks"]["natural_covariant_entropy_balance_lane_passes"] is True
    assert artifact["checks"]["physical_coefficient_is_not_emitted"] is True
    assert "physical_Kubo_coefficient_record_missing" in artifact["major_result"]["open_blockers"]


def test_status_boundary_is_integrated_into_full_gate_and_dependency() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"]["transport_kms_entropy_status_boundary"]
    assert lane["major_result_id"] == "T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"
    assert lane["structural_lane_status"] == "PASS"
    assert lane["physical_closure_status"] == "BLOCKED"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False

    register = load(REGISTER)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"]["closure_level"] == "CLOSED_FOR_LANE"

    dependency = load(DEPENDENCY)
    partial = dependency["topic13_partial_evidence"]
    assert partial["transport_kms_entropy_status_boundary"]["summary"]["full_core_unlock"] is False
