from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_ding_public_supplementary_payload_boundary_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_public_supplementary_inventory_boundary_is_closed_for_lane() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION"
    assert lane["source"]["inventory_object_count"] == 11
    assert len(lane["source"]["supplementary_objects"]) == 3
    assert lane["source"]["numeric_payload_objects"] == []
    assert lane["review_boundary"]["holdout_accessed"] is False
    assert lane["review_boundary"]["alpha_Phi_K_fit_performed"] is False
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in major["open_blockers"]


def test_full_gate_keeps_public_boundary_separate_from_full_source_closure() -> None:
    full = load(FULL)
    source = full["verification_status"]["source_package"]
    lane = source["ding_public_supplementary_payload_boundary"]
    assert lane["major_result_id"] == "T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert source["status"] == "BLOCKED"
    assert source["raw_author_C_src_route_ready"] is False
    assert source["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    assert any(
        item["path"] == "docs/core/artifacts/t13_ding_public_supplementary_payload_boundary_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
