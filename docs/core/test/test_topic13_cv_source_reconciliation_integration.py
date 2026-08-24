from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
RECONCILIATION = "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"


def test_cv_reconciliation_is_projected_into_input_package_audit() -> None:
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    package = next(
        item for item in audit["packages"]
        if item["package_id"] == "T13_INPUT_DING_TTG_SOURCE"
    )
    evidence_paths = {item["path"] for item in audit["evidence_artifacts"]}
    assert RECONCILIATION in evidence_paths
    assert package["current_evidence"]["cv_source_reconciliation_status"] == (
        "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN"
    )
    assert package["current_evidence"]["direct_or_derived_cv_count"] == 2
    assert package["current_evidence"]["source_grade_cv_uncertainty_count"] == 0
    assert package["current_evidence"]["eligible_cv_input_count"] == 0
    assert audit["checks"]["cv_source_reconciliation_is_fail_closed"] is True
