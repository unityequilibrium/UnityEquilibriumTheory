from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_graphite_elastic_bulk_lane_is_integrated_without_k_t_or_topic13_promotion() -> None:
    lane = load(LANE)
    full = load(FULL)
    projected = full["verification_status"]["source_package"][
        "graphite_elastic_bulk_modulus_source"
    ]
    assert projected["major_result_id"] == "T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["data_role"] == "INTERNAL_SOURCE_COMPARATOR_NOT_DING_TTG_GRADE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "same_grade_alpha_V_and_K_T_missing" not in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert any(
        item["path"] == "docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert lane["isothermal_boundary"]["K_T_emitted"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
