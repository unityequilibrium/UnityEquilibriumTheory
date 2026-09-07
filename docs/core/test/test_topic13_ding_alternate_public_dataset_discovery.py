from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_ding_alternate_public_dataset_discovery_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_public_alternate_routes_are_closed_as_a_scoped_boundary() -> None:
    audit = load(AUDIT_REL)
    assert audit["status"] == "PASS_SCOPED_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    observations = {item["candidate_id"]: item for item in audit["candidate_observations"]}
    assert observations["stfc_isis_99714235"]["decision"] == "REJECTED_AS_DING_C_SRC_ROUTE"
    assert observations["stfc_isis_99714235"]["compatibility"]["material_matches_ding_natural_graphite"] is False
    assert observations["caltech_c_axis_graphite_mfp_2016"]["compatibility"]["observable_matches_mode_resolved_C_src"] is False
    assert observations["nims_mdr_huang_2023_graphite_poiseuille"]["decision"] == "REJECTED_AS_DING_C_SRC_ROUTE"
    assert observations["nims_mdr_huang_2023_graphite_poiseuille"]["access_route"]["format"] == "ARTICLE_PDF_ONLY"
    assert observations["nims_mdr_huang_2023_graphite_poiseuille"]["access_route"]["local_payload_imported"] is False
    assert observations["nims_mdr_huang_2023_graphite_poiseuille"]["compatibility"]["unitful_C_src_present"] is False
    assert audit["major_result"]["data_role"] == "SOURCE_DISCOVERY_BOUNDARY_NOT_CALIBRATION"
    registry = audit["major_result"]["evidence_artifacts"][-1]["summary"]
    assert registry["target_doi"] == "10.1038/s41467-021-27907-z"
    assert registry["xie_2026_consumed"] is False
    assert all(
        item["exact_target_matches"] == 0
        for item in registry["queries"]
        if "exact_target_matches" in item
    )
    assert all(
        item["exact_target_matches_in_returned_page"] == 0
        for item in registry["queries"]
        if "exact_target_matches_in_returned_page" in item
    )
    crossref = next(item for item in registry["queries"] if item["registry"] == "Crossref")
    assert crossref["dataset_relation_present"] is False


def test_public_route_boundary_is_projected_without_topic13_promotion() -> None:
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    dependency = load(DEPENDENCY_REL)
    projected = full["verification_status"]["source_package"]["ding_alternate_public_dataset_discovery_boundary"]
    assert projected["major_result_id"] == "T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["path"] == AUDIT_REL
    assert projected["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in full["major_result"]["what_remains_open"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(item.get("major_result_id") == "T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY" for item in register["entries"])
    assert dependency["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]["status"] == "UNLOCKED"
