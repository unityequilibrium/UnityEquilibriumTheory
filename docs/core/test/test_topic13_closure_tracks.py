from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_core_and_external_validation_tracks_are_separate() -> None:
    gate = load(GATE)
    core = gate["closure_tracks"]["o2_he4_core_ready"]
    graphite = gate["closure_tracks"]["graphite_ttg_external_validation"]

    assert core["major_result_id"] == "T13_O2_HE4_THERMODYNAMIC_BRIDGE_CORE_READY"
    assert core["requirements"]["he4_equilibrium_source_anchor"] == "PASS"
    assert "ding_or_accepted_independent_C_src" not in core["requirements"]
    assert graphite["requirements"]["ding_or_accepted_independent_C_src"] == "BLOCKED"
    assert graphite["dependency_unlocked"].startswith("None")


def test_track_split_does_not_promote_topic13_or_read_holdout() -> None:
    gate = load(GATE)
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert gate["closure_tracks"]["o2_he4_core_ready"]["status"] == "PARTIAL"
    assert gate["closure_tracks"]["graphite_ttg_external_validation"]["status"] == "OPEN"
    assert gate["verification_status"]["holdout_integrity"]["status"] == "PASS"
