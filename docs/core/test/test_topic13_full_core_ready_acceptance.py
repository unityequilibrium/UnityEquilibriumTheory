from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_full_core_ready_acceptance_audit.json"


def test_full_topic13_core_ready_acceptance_passes_every_declared_criterion() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_T13_FULL_CORE_READY_ACCEPTANCE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_CORE"
    assert audit["major_result"]["open_blockers"] == []
    assert all(audit["criteria"].values())
    assert audit["claim_promotion"] is False


def test_acceptance_preserves_external_and_global_claim_boundaries() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    external = audit["external_tracks_still_open"]
    assert external["graphite_ttg"]["status"] == "OPEN"
    assert external["raw_author_ding_source"] is False
    assert external["curved_3p1_result_ready"] is False
    assert external["gravity_ready"] is False
    assert audit["quantitative_witnesses"]["causal_prearrival_leakage_fraction"] <= audit["quantitative_witnesses"]["causal_locked_threshold"]
    assert "not external-ready" in audit["claim_boundary"]
