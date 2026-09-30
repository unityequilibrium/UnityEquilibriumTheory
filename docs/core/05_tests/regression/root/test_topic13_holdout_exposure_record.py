import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
EVENT_PATH = ROOT / "docs/core/99_review/unresolved_assets/T13_HOLDOUT_EXPOSURE_2026_09_26.json"


def test_holdout_article_exposure_is_separated_from_numeric_payload_use() -> None:
    event = json.loads(EVENT_PATH.read_text(encoding="utf-8"))
    exposure = event["exposure"]
    impact = event["research_impact"]

    assert exposure["article_text_returned_by_search"] is True
    assert exposure["article_numeric_statements_visible"] is True
    assert exposure["source_data_rows_or_table_payload_opened"] is False
    assert exposure["supplementary_numeric_payload_opened_or_downloaded"] is False
    assert exposure["source_curves_digitized"] is False
    assert impact["source_rows_consumed"] is False
    assert impact["used_for_fit"] is False
    assert impact["used_for_tuning"] is False
    assert impact["used_for_calibration"] is False
    assert impact["used_for_threshold_adjustment"] is False
    assert impact["numeric_payload_remains_locked"] is True
    assert impact["future_blind_holdout_eligibility"] == "REVIEW_REQUIRED"
    assert event["full_topic_unlock"] is False
    assert event["claim_promotion"] is False
