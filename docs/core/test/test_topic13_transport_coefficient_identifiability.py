from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_transport_coefficient_identifiability_no_go.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_transport_identifiability_no_go_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY"
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_transport_no_go_keeps_physical_coefficient_open() -> None:
    audit = load()
    assert len(audit["witnesses"]) == 2
    assert audit["witnesses"][0]["onsager_matrix"] != audit["witnesses"][1]["onsager_matrix"]
    assert "physical_Kubo_coefficient_record_missing" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
