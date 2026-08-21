from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_numeric_input_availability_package.json"
)
AUDIT = ROOT / "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json"
ENERGY = ROOT / "docs/core/artifacts/t13_energy_response_bridge_audit.json"
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_oa_package_inventory_is_explicit_and_scoped() -> None:
    package = load(PACKAGE)
    assert package["source_identity"]["publisher_url"] == (
        "https://www.nature.com/articles/s41467-021-27907-z"
    )
    assert package["source_identity"]["publisher_data_availability_locator"] == (
        "Nature Communications article, Data availability section"
    )
    inventory = package["official_object_inventory"]
    assert inventory["object_count"] == 11
    assert inventory["media_payload_count"] == 7
    assert inventory["numeric_or_reproduction_payload_count"] == 0
    assert package["availability_contract"]["author_request_route"] == (
        "OPEN_NOT_EXECUTED"
    )
    roles = {item["role"] for item in package["archived_records"]}
    assert {
        "SUPPLEMENTARY_INFORMATION",
        "SUPPLEMENTARY_MATERIALS_2",
        "SUPPLEMENTARY_MATERIALS_3",
    } <= roles


def test_availability_audit_closes_only_the_oa_search_route() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["inventory_witness"]["reproduction_payload_candidates"] == []
    assert audit["checks"]["all_three_supplementary_pdfs_are_archived"] is True
    assert len(audit["inventory_witness"]["supplementary_files"]) == 3
    assert "only to the captured official PMC OA distribution" in audit[
        "major_result"
    ]["claim_boundary"]


def test_gate_preserves_full_blocker_and_records_next_acquisition_route() -> None:
    gate = load(GATE)
    result = gate["verification_status"]["alpha_Phi_K"][
        "named_energy_response_branch"
    ]["pbte_numeric_input_availability_no_go"]
    assert result["status"] == "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO"
    assert result["direct_oa_numeric_route"] == "CLOSED_AS_SCOPED_NO_GO"
    assert gate["controlling_blocker"] == (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    assert gate["source_acquisition_controller"] == (
        "ding_pbte_author_data_or_independent_reproduction_package_missing"
    )
    assert gate["claim_promotion"] is False


def test_energy_and_register_records_do_not_unlock_core() -> None:
    energy = load(ENERGY)
    register = load(REGISTER)
    entries = {
        item["major_result_id"]: item for item in register["entries"]
    }
    result = entries["T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO"]
    assert energy["pbte_numeric_input_availability"]["author_request_route"] == (
        "OPEN_NOT_EXECUTED"
    )
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert "no Core dependency is unlocked" in result["dependency_unlocked"]
    assert register["claim_promotion"] is False
