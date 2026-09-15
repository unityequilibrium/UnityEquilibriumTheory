from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_ding_2017_acs_supplementary_payload_boundary_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_2017_acs_supplementary_boundary_is_closed_without_c_src_payload() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    source = lane["source"]
    assert lane["status"] == "PASS_DING_2017_ACS_SUPPLEMENTARY_BOUNDARY_NO_MACHINE_READABLE_C_SRC"
    assert major["major_result_id"] == "T13_DING_2017_ACS_SUPPLEMENTARY_PAYLOAD_BOUNDARY"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert source["reviewed_page_count"] == 18
    assert source["numeric_payload_objects"] == []
    assert source["payload_classification"]["machine_readable_C_src_rows"] is False
    assert source["payload_classification"]["raw_force_constants"] is False
    assert lane["review_boundary"]["target_fit_performed"] is False
    assert lane["review_boundary"]["alpha_Phi_K_fit_performed"] is False
    assert lane["review_boundary"]["holdout_accessed"] is False
    assert lane["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"


def test_full_gate_keeps_ding_2017_boundary_separate_from_source_closure() -> None:
    full = load(FULL)
    source = full["verification_status"]["source_package"]
    lane = source["ding_2017_acs_supplementary_payload_boundary"]
    assert lane["major_result_id"] == "T13_DING_2017_ACS_SUPPLEMENTARY_PAYLOAD_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    assert source["status"] == "BLOCKED"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(
        item["path"] == "docs/core/07_artifacts/topic13/t13_ding_2017_acs_supplementary_payload_boundary_audit.json"
        for item in full["evidence_artifacts"]
    )
