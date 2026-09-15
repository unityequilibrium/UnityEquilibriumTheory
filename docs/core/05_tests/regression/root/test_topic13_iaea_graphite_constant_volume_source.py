from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_iaea_graphite_constant_volume_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_graphite_handbook_constant_volume_source_package.json"
)
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_iaea_table_cv_lane_is_integrated_without_volumetric_or_topic13_promotion() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "iaea_graphite_table_cv_comparator"
    ]
    assert lane["status"] == "PASS_SCOPED_IAEA_TABLE_CV_COMPARATOR_UNCERTAINTY_OPEN"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["source_row"]["cv_cal_per_g_K"] == 0.17152
    assert lane["derived_comparator"]["cv_mass_J_per_kg_K"] == 717.63968
    assert lane["derived_comparator"]["cv_volumetric_emitted"] is False
    assert lane["source_row"]["source_uncertainty_boundary"]["cv_standard_uncertainty"] is None
    assert package["source"]["local_raw_sha256"] == lane["source"]["local_hash_observed"]
    assert projected["major_result_id"] == "T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "c_v_source_uncertainty_not_closed" in full["major_result"]["what_remains_open"]
    assert "direct_volumetric_c_v_or_same_state_Cp_source_missing" not in full["major_result"]["what_remains_open"]
    assert any(
        item["path"] == "docs/core/artifacts/t13_iaea_graphite_constant_volume_source_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert any(
        item["major_result_id"] == "T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR"
        for item in register["entries"]
    )
