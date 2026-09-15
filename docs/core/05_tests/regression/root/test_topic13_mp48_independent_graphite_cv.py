"""Regression checks for the independent Topic 13 mp-48 source lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_mp48_audit_is_passing_and_holdout_is_locked() -> None:
    package = load(PACKAGE_REL)
    audit = load(AUDIT_REL)
    assert audit["status"] == "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert package["major_result"]["data_role"] == "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION"
    assert package["holdout_policy"] == {
        "xie_2026_accessed": False,
        "xie_2026_source_data_consumed": False,
        "xie_2026_role": "locked external holdout",
        "calibration_path_may_read_holdout": False,
        "target_curve_used": False,
        "alpha_fit_used": False,
    }


def test_all_archived_members_match_package_hashes() -> None:
    package = load(PACKAGE_REL)
    for member in package["archive_members"]:
        path = member["local_path"]
        assert (ROOT / path).is_file()
        assert (ROOT / path).stat().st_size == member["size_bytes"]
        assert sha256(path) == member["sha256"]


def test_gate_exposes_comparator_without_unlocking_core() -> None:
    full = load(FULL_REL)
    route = full["verification_status"]["independent_graphite_cv_route"]
    assert route["status"] == "PASS"
    assert route["closure_level"] == "CLOSED_FOR_LANE"
    assert route["calibration_consumed"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert full["controlling_blocker"] == "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"


def test_register_and_dependency_gate_are_hash_linked() -> None:
    register = load(REGISTER_REL)
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    assert any("mp-48" in item for item in entry["what_is_closed"])
    assert "ding_pbte_author_data_or_independent_reproduction_package_missing" not in json.dumps(entry)
    full_evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == FULL_REL)
    assert full_evidence["sha256"] == sha256(FULL_REL)
    package_evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == PACKAGE_REL)
    assert package_evidence["sha256"] == sha256(PACKAGE_REL)

    dependency = load(DEPENDENCY_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
    assert dependency["topic13_partial_evidence"]["full_core_unlock"] is False
