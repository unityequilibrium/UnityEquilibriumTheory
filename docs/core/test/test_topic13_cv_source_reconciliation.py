from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"


def test_topic13_cv_reconciliation_is_fail_closed() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN"
    assert artifact["summary"]["candidate_count"] == 9
    assert artifact["summary"]["direct_or_derived_cv_count"] == 2
    assert artifact["summary"]["source_grade_cv_uncertainty_count"] == 0
    assert artifact["summary"]["ding_matched_cv_count"] == 0
    assert artifact["summary"]["eligible_for_full_topic13_count"] == 0
    assert artifact["major_result"]["controlling_blocker"] == "c_v_source_uncertainty_not_closed"
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["xie_2026_source_data_consumed"] is False
    assert artifact["holdout_policy"]["alpha_Phi_K_fit_used"] is False
