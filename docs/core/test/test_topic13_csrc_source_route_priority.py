from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_csrc_source_route_priority_audit.json"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_csrc_route_priority_is_a_closed_lane_without_an_accepted_route() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_C_SRC_SOURCE_ROUTE_PRIORITY_NO_ACCEPTED_ROUTE"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["major_result_id"] == "T13_C_SRC_SOURCE_ROUTE_PRIORITY"
    assert audit["claim_promotion"] is False
    assert audit["holdout_policy"] == {
        "xie_2026_accessed": False,
        "calibration_path_may_read_holdout": False,
        "target_curve_used": False,
        "fit_or_tuning_used": False,
    }


def test_route_matrix_has_all_eleven_acceptance_fields_and_no_accepted_route() -> None:
    audit = load(AUDIT)
    required = audit["acceptance_contract"]["required_fields"]
    assert len(required) == 11
    assert len(audit["routes"]) == 8
    assert all(set(route["field_coverage"]) == set(required) for route in audit["routes"])
    assert all(route["accepted_for_full_topic13"] is False for route in audit["routes"])
    assert audit["priority_decision"]["selected_route_id"] == "ding_author_payload"
    assert audit["priority_decision"]["selected_route_priority"] == 1


def test_numeric_candidates_are_visible_but_material_and_uncertainty_gates_remain_missing() -> None:
    audit = load(AUDIT)
    candidates = {
        route["route_id"]: route
        for route in audit["routes"]
        if route["field_coverage"]["C_src_rows_with_J_m^-3_K^-1_units"]["status"] == "PRESENT"
    }
    assert set(candidates) == {"calorine_zenodo_pbte", "calorine_legacy_nep2_pbte"}
    for route in candidates.values():
        assert route["field_coverage"]["material_identity_morphology_isotope_defect_state"]["status"] == "MISSING"
        assert route["field_coverage"]["uncertainty_and_preprocessing"]["status"] == "MISSING"
        assert "material/state" in " ".join(route["rejection_reasons"])


def test_route_priority_is_projected_into_matrix_and_major_result_register() -> None:
    audit = load(AUDIT)
    matrix = load(MATRIX)
    register = load(REGISTER)
    source_requirement = next(
        item for item in matrix["requirements"] if item["requirement_id"] == "source_and_uncertainty"
    )
    assert "docs/core/artifacts/t13_csrc_source_route_priority_audit.json" in {
        ref["path"] for ref in source_requirement["evidence_artifacts"]
    }
    entry = next(
        item for item in register["entries"] if item.get("major_result_id") == "T13_C_SRC_SOURCE_ROUTE_PRIORITY"
    )
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert entry["claim_promotion"] is False
    assert audit["major_result"]["dependency_unlocked"].startswith("Source-route decision")
