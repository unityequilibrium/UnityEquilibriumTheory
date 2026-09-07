from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_topic13_input_package_audit_keeps_all_three_packages_open() -> None:
    artifact = load()
    assert artifact["status"] == "PASS_SCOPED_T13_CLOSURE_INPUT_AUDIT_OPEN"
    assert artifact["major_result"]["closure_level"] == "PARTIAL"
    assert artifact["holdout_policy"] == {
        "xie_2026_accessed": False,
        "target_fit_performed": False,
        "calibration_path_may_read_holdout": False,
    }
    assert {package["package_id"] for package in artifact["packages"]} == {
        "T13_INPUT_DING_TTG_SOURCE",
        "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    }
    assert all(package["accepted_for_core"] is False for package in artifact["packages"])


def test_topic13_input_package_audit_preserves_candidate_vs_acceptance_boundary() -> None:
    artifact = load()
    packages = {package["package_id"]: package for package in artifact["packages"]}
    ding = packages["T13_INPUT_DING_TTG_SOURCE"]
    assert ding["current_evidence"]["numeric_candidate_rows_present"] is True
    assert ding["current_evidence"]["mesh_convergence_pass"] is True
    assert ding["current_evidence"]["material_state_match_to_ding"] is False
    assert ding["current_evidence"]["source_grade_uncertainty_present"] is False
    assert "Ding_material_state_match" in ding["missing_acceptance_fields"]
    assert "source_grade_uncertainty" in ding["missing_acceptance_fields"]

    phi = packages["T13_INPUT_BASE_PHI_SI_ALPHA_BETA"]
    assert phi["current_evidence"]["eligible_paired_alpha_records"] == 0
    assert phi["current_evidence"]["numeric_alpha_emitted"] is False
    assert phi["current_evidence"]["holdout_accessed"] is False

    transport = packages["T13_INPUT_PHYSICAL_TRANSPORT_MATCH"]
    assert transport["current_evidence"]["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert transport["current_evidence"]["natural_kubo_is_SI"] is False
