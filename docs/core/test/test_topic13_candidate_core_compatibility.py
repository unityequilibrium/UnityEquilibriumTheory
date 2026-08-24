from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_candidate_core_compatibility_audit.json"


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_candidate_compatibility_keeps_all_routes_non_core() -> None:
    artifact = load()
    assert artifact["status"] == "PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN"
    assert artifact["summary"]["candidate_source_package_count"] == 5
    assert artifact["summary"]["core_accepted_route_count"] == 0
    assert artifact["summary"]["new_core_subresults_closed"] == 0
    assert artifact["summary"]["canonical_full_topic13_unlocked"] is False
    assert artifact["holdout_policy"] == {
        "xie_2026_accessed": False,
        "target_fit_performed": False,
        "calibration_path_may_read_holdout": False,
    }


def test_candidate_compatibility_preserves_the_three_blocker_groups() -> None:
    artifact = load()
    blockers = set(artifact["major_result"]["what_remains_open"])
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in blockers
    assert "alpha_Phi_K_independent_calibration_missing" in blockers
    assert "normalized_beta_and_SI_scale_correspondence_missing" in blockers
    assert "physical_Kubo_coefficient_record_missing" in blockers
    assert "dimensional_phi_to_thermal_observable_map_missing" in blockers
    assert "material_regime_mapping_to_TTG_not_closed" in blockers
    assert "c_v_source_uncertainty_not_closed" in blockers


def test_calorine_and_kim_boundaries_are_not_relabelled() -> None:
    artifact = load()
    records = {
        (item["contract_id"], item["candidate_id"]): item
        for item in artifact["candidate_records"]
    }
    calorine = records[("T13_INPUT_DING_TTG_SOURCE", "calorine_zenodo_nep_bte")]
    assert calorine["accepted_for_core"] is False
    assert "material_state_match_to_Ding" in calorine["missing_core_fields"]
    assert "source_grade_uncertainty" in calorine["missing_core_fields"]

    kim = records[("T13_INPUT_PHYSICAL_TRANSPORT_MATCH", "kim_2018_graphite_green_kubo")]
    assert kim["accepted_for_core"] is False
    assert "UET_Phi_state_and_anchor" in kim["missing_core_fields"]
    assert "retarded_correlator_or_KMS_match" in kim["missing_core_fields"]
