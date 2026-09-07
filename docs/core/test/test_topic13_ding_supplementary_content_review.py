from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_ding_supplementary_content_review_audit.json"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_supplementary_content_review_package.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_supplementary_content_boundary_is_locked_without_payload() -> None:
    artifact = load(ARTIFACT)
    package = load(PACKAGE)
    assert artifact["status"] == "PASS_SCOPED_DING_SUPPLEMENTARY_CONTENT_BOUNDARY_NO_NUMERIC_PAYLOAD"
    assert artifact["major_result"]["major_result_id"] == "T13_DING_SUPPLEMENTARY_CONTENT_BOUNDARY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert all(all(values.values()) for values in artifact["file_checks"].values())
    assert package["acceptance"]["accepted_for_ding_C_src"] is False
    assert package["acceptance"]["accepted_for_alpha_Phi_K_calibration"] is False
    assert package["acceptance"]["accepted_for_full_topic13"] is False


def test_ding_supplementary_content_review_has_page_locators_and_no_holdout() -> None:
    artifact = load(ARTIFACT)
    locators = {
        finding["locator"]
        for source in artifact["source_files"]
        for finding in source["content_findings"]
    }
    assert "MOESM1 p.3, Eqs. S1-S5" in locators
    assert "MOESM1 p.5, Eqs. S7-S10" in locators
    assert "MOESM2 p.16" in locators
    assert "MOESM3 pp.1-2" in locators
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["xie_2026_source_data_consumed"] is False
    assert artifact["holdout_policy"]["calibration_path_may_read_holdout"] is False
    assert artifact["holdout_policy"]["fit_performed"] is False
    assert artifact["holdout_policy"]["alpha_Phi_K_fit_used"] is False
    assert artifact["holdout_policy"]["threshold_changed"] is False
