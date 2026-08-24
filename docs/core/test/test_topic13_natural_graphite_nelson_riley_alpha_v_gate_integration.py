from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/artifacts/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_natural_graphite_alpha_v_lane_is_integrated_without_full_bridge_promotion() -> None:
    lane = load(LANE)
    full = load(FULL)
    projected = full["verification_status"]["source_package"][
        "natural_graphite_nelson_riley_alpha_v_comparator"
    ]
    assert projected["major_result_id"] == "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["data_role"] == "EXTERNAL_INPUT_STANDARD_THERMODYNAMIC_COMPARATOR_NOT_DING_TTG_GRADE"
    assert projected["derived_comparator"]["alpha_V_per_K"] == 2.408235e-5
    assert projected["derived_comparator"]["alpha_V_uncertainty_per_K"] is None
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "same_grade_alpha_V_and_K_T_missing" not in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert any(
        item["path"] == "docs/core/artifacts/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert lane["numeric_alpha_Phi_K_emitted"] is False
