from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
RECONCILIATION = "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json"


def test_transport_reconciliation_is_projected_into_input_package_audit() -> None:
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    package = next(
        item for item in audit["packages"]
        if item["package_id"] == "T13_INPUT_PHYSICAL_TRANSPORT_MATCH"
    )
    evidence_paths = {item["path"] for item in audit["evidence_artifacts"]}
    current = package["current_evidence"]
    assert RECONCILIATION in evidence_paths
    assert current["physical_transport_reconciliation_status"] == (
        "PASS_SCOPED_PHYSICAL_TRANSPORT_RECONCILIATION_OPEN"
    )
    assert current["formal_lane_count"] == 3
    assert current["external_physical_comparator_count"] == 1
    assert current["physical_uet_coefficient_count"] == 0
    assert current["eligible_physical_transport_input_count"] == 0
    assert audit["checks"]["physical_transport_reconciliation_is_fail_closed"] is True
