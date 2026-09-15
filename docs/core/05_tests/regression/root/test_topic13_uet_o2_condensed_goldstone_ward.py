from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_goldstone_ward_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_condensed_stationarity_goldstone_boundary_is_closed_as_no_go() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_CONDENSED_GOLDSTONE_WARD_BOUNDARY"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_CONDENSED_GOLDSTONE_WARD_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_tree_boundary_is_gapless_but_stationary_witness_is_not() -> None:
    audit = load(AUDIT)
    reference = audit["reference"]
    assert abs(reference["tree_boundary_low_mode_sq"]) <= 1.0e-10
    assert reference["stationary_x"] > reference["x_boundary"]
    assert reference["stationary_low_mode_sq"] > 1.0e-4
    assert audit["external_literature_context"]["source_url"] == "https://arxiv.org/abs/0810.5510"


def test_goldstone_no_go_does_not_unlock_full_topic() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_condensed_goldstone_ward_no_go"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_AS_NO_GO"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
