from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_energy_temperature_source_package.json"
)
PDF = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_supplementary_information.pdf"
)
AUDIT = ROOT / "docs/core/artifacts/t13_ding_pbte_energy_temperature_mapping_audit.json"
ENERGY = ROOT / "docs/core/artifacts/t13_energy_response_bridge_audit.json"
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_pdf_and_package_identity_are_locked() -> None:
    package = load(PACKAGE)
    source = package["source"]
    assert PDF.stat().st_size == 1_893_976
    assert sha256(PDF) == source["local_raw_sha256"]
    assert source["local_raw_md5"] == source["official_metadata_md5"]
    assert source["doi"] == "10.1038/s41467-021-27907-z"
    assert source["pmcid"] == "PMC8755757"


def test_source_formula_units_and_ontology_are_explicit() -> None:
    package = load(PACKAGE)
    mapping = package["mapping_contract"]
    units = package["units_contract"]
    ontology = package["ontology_contract"]
    assert mapping["source_temperature_response"] == "Delta_Tq = Delta_u_ph / C_src"
    assert units["Delta_u_ph"] == "J m^-3"
    assert units["C_src"] == "J m^-3 K^-1"
    assert units["Delta_Tq"] == "K"
    assert ontology["C_src_is_uet_C"] is False
    assert mapping["base_Phi_identity"] == "NOT_ASSERTED"


def test_audit_closes_only_the_source_formula_lane() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert "ding_pbte_numeric_C_src_T_not_packaged" in audit["major_result"][
        "open_blockers"
    ]
    assert audit["checks"]["numeric_C_not_fabricated"] is True
    assert audit["checks"]["xie_holdout_not_accessed"] is True


def test_energy_branch_and_full_gate_keep_uet_mapping_open() -> None:
    energy = load(ENERGY)
    gate = load(GATE)
    source_anchor = energy["standard_pbte_source_anchor"]
    gate_anchor = gate["verification_status"]["alpha_Phi_K"][
        "named_energy_response_branch"
    ]["pbte_energy_temperature_source"]
    assert source_anchor["status"] == "PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN"
    assert source_anchor["base_Phi_identity"] == "not asserted"
    assert gate_anchor["numeric_C_src_status"] == "OPEN_NOT_PROVIDED"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert gate["verification_status"]["holdout_integrity"]["holdout_consumed"] is False


def test_major_result_register_contains_ding_mapping_without_unlocking_core() -> None:
    register = load(REGISTER)
    entries = {
        entry["major_result_id"]: entry for entry in register["entries"]
    }
    result = entries["T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING"]
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert "no base-Phi or downstream Core dependency is unlocked" in result[
        "dependency_unlocked"
    ]
    assert register["claim_promotion"] is False
    assert register["next_major_result"] == "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"
