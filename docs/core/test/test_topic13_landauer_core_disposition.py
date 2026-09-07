from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_landauer_core_disposition_audit.json"


def test_landauer_controllers_close_only_their_core_dependency_role() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_LANDAUER_CORE_ROLE_DISPOSITION"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_CORE"
    assert all(audit["checks"].values())
    assert all(not item["core_dependency_required"] for item in audit["controllers"].values())


def test_external_landauer_data_gaps_stay_open_and_cannot_calibrate_bridge() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert all(item["external_open_blockers"] for item in audit["controllers"].values())
    assert all(not item["external_numeric_dataset_closed"] for item in audit["controllers"].values())
    assert all(audit["physical_bridge_checks"].values())
    assert "not dataset closure" in audit["claim_boundary"].lower()
