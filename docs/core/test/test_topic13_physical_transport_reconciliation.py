from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json"


def test_physical_transport_reconciliation_is_fail_closed() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_PHYSICAL_TRANSPORT_RECONCILIATION_OPEN"
    assert artifact["summary"] == {
        "candidate_count": 5,
        "formal_lane_count": 3,
        "natural_unit_uet_lane_count": 3,
        "external_physical_comparator_count": 1,
        "physical_uet_coefficient_count": 0,
        "accepted_for_full_topic13_count": 0,
    }
    assert artifact["major_result"]["controlling_blocker"] == "physical_Kubo_coefficient_record_missing"
    assert all(artifact["checks"].values())
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["alpha_Phi_K_fit_used"] is False


def test_external_and_natural_lanes_are_not_uet_physical_coefficients() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    candidates = {item["candidate_id"]: item for item in artifact["candidates"]}
    assert candidates["kim_2018_external_graphite_green_kubo"]["external_input_accepted"] is True
    assert candidates["kim_2018_external_graphite_green_kubo"]["physical_uet_coefficient"] is False
    assert candidates["uet_condensed_relative_flow_natural_kubo"]["numeric_coefficient_present"] is True
    assert candidates["uet_condensed_relative_flow_natural_kubo"]["si_units"] is False
    assert candidates["uet_condensed_relative_flow_natural_kubo"]["physical_anchor_supplied"] is False
