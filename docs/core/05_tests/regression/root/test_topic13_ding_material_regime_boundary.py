from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_ding_material_regime_boundary_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ding_material_regime_boundary_rejects_silent_comparator_substitution() -> None:
    lane = load(LANE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "ding_material_regime_boundary"
    ]
    assert lane["status"] == "PASS_SCOPED_DING_MATERIAL_REGIME_BOUNDARY_NO_GO"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["mapping_contract"]["equivalence_result"] is False
    assert len(lane["source"]["comparators"]) == 8
    assert all(
        item["equivalence_status"] == "NOT_ESTABLISHED"
        for item in lane["source"]["comparators"]
    )
    calorine = lane["source"]["calorine_admission_boundary"]
    assert calorine["primitive_cell_atoms"] == 4
    assert calorine["primitive_volume_A3"] > 0.0
    assert calorine["crystallographic_density_kg_per_m3"] > 0.0
    assert calorine["accepted_as_ding_csrc"] is False
    assert calorine["source_grade_uncertainty_present"] is False
    assert projected["major_result_id"] == "T13_DING_MATERIAL_REGIME_BOUNDARY"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert any(
        item["major_result_id"] == "T13_DING_MATERIAL_REGIME_BOUNDARY"
        for item in register["entries"]
    )
