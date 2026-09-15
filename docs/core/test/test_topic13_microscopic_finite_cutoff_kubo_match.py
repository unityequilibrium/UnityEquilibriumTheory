from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_uet_o2_microscopic_finite_cutoff_kubo_match_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_finite_cutoff_microscopic_match_is_closed_without_si_promotion() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_ACTION_MATCHED_MICROSCOPIC_FINITE_CUTOFF_KUBO_LANE"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["physical_closure_status"] == "BLOCKED"
    assert artifact["claim_promotion"] is False
    assert artifact["checks"]["microscopic_bethe_salpeter_match"] is True
    assert artifact["checks"]["microscopic_sk_kms_match"] is True
    assert artifact["checks"]["finite_cutoff_is_declared"] is True
    assert artifact["checks"]["physical_kubo_is_not_emitted"] is True
    assert artifact["checks"]["holdout_is_unread"] is True


def test_full_topic13_remains_blocked_and_retains_physical_boundary() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"]["microscopic_finite_cutoff_kubo_match"]
    assert lane["major_result_id"] == "T13_UET_O2_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["physical_closure_status"] == "BLOCKED"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
    assert "physical_Kubo_coefficient_record_missing" in full["major_result"]["what_remains_open"]
