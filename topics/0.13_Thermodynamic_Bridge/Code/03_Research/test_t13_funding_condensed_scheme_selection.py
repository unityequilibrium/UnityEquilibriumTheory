"""Guard the source-backed condensed scheme decision against claim drift."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
DECISION = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_funding_condensed_scheme_selection_2026-09-28.json"
)


def test_scheme_selection_sources_are_current():
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["closure_level"] == "CLOSED_FOR_LANE"
    assert decision["status"] == "PASS_ROUTE_SELECTION_ONLY"
    for path, expected_hash in decision["source_hashes"].items():
        actual_hash = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, path
    assert len(decision["primary_sources"]) >= 4
    assert len({item["id"] for item in decision["primary_sources"]}) == len(
        decision["primary_sources"]
    )


def test_scheme_selection_cannot_unlock_physical_claims():
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["full_core_unlock"] is False
    assert decision["g1_physical_unlock"] is False
    assert decision["g2_science_unlock"] is False
    assert decision["xie_2026_accessed"] is False
    assert all(
        route["physical_operator_admitted"] is False
        for route in decision["candidate_routes"]
    )
    assert "UNRESOLVED" in decision["stop_rule"]
    assert "source" in decision["selected_next_question"]
