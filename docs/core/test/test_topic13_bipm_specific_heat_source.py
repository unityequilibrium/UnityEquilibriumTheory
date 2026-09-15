from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_bipm_specific_heat_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "bipm_2006_01_graphite_specific_heat_source_package.json"
)
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_bipm_cp_lane_is_source_locked_without_cv_or_topic13_promotion() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "bipm_specific_heat_cp_comparator"
    ]
    assert lane["status"] == "PASS_SCOPED_BIPM_CP_COMPARATOR_CV_OPEN"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["derived_comparator"]["cv_emitted"] is False
    assert lane["derived_comparator"]["volumetric_cp_J_per_m3_K"] == 1264868.0
    assert lane["derived_comparator"]["volumetric_cp_standard_uncertainty_J_per_m3_K"] > 0.0
    assert package["source"]["local_raw_sha256"] == lane["source"]["local_hash_observed"]
    assert projected["major_result_id"] == "T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "c_v_source_uncertainty_not_closed" in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert any(
        item["path"] == "docs/core/artifacts/t13_bipm_specific_heat_source_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert any(
        item["major_result_id"] == "T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR"
        for item in register["entries"]
    )
