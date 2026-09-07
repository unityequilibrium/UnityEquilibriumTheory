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


def test_acceptance_breaks_the_derived_register_hash_cycle_explicitly() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    derived = audit["derived_consistency_inputs"]
    assert derived["hash_cycle_forbidden"] is True
    assert derived["values_are_verified"] is True
    records = {
        item["path"]: item
        for item in audit["major_result"]["evidence_artifacts"]
    }
    for path in derived["paths"]:
        assert records[path]["identity_mode"] == "NON_HASHED_DERIVED_CONSISTENCY_INPUT"
        assert "sha256" not in records[path]
