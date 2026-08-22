import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_qh15_graphite_transport_boundary_audit.json"


def test_qh15_is_a_source_locked_comparator_without_promotion() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_QH15_CV_COMPARATOR_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["data_role"] == "COMPARISON_ONLY_NOT_CALIBRATION"
    assert audit["checks"]["all_archived_entries_match_hash_and_size"] is True
    assert audit["checks"]["declared_conversion_factor_is_si_closed"] is True
    assert audit["checks"]["equilibrium_crosscheck_computed"] is True
    assert audit["checks"]["ding_response_contract_not_claimed"] is True
    assert audit["checks"]["mode_resolved_payload_not_claimed"] is True
    assert audit["checks"]["source_uncertainty_not_promoted"] is True
    assert audit["checks"]["fit_unused"] is True
    assert audit["checks"]["alpha_fit_unused"] is True
    assert audit["checks"]["holdout_unconsumed"] is True
    assert audit["claim_promotion"] is False
