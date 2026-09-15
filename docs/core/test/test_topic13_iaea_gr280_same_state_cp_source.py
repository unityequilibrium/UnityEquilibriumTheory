from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/artifacts/t13_iaea_gr280_same_state_cp_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_gr280_same_state_cp_source_package.json"
)
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_iaea_gr280_same_state_cp_lane_closes_only_the_availability_subblocker() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "iaea_gr280_same_state_cp_comparator"
    ]
    assert lane["status"] == "PASS_SCOPED_IAEA_GR280_SAME_STATE_CP_COMPARATOR"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["same_state_cp_and_density_rows"] is True
    assert lane["derived_comparator"]["cp_volumetric_J_per_m3_K"] == 2386800.0
    assert lane["derived_comparator"][
        "cp_volumetric_standard_uncertainty_J_per_m3_K"
    ] is None
    assert package["source"]["local_raw_sha256"] == lane["source"]["local_hash_observed"]
    assert projected["major_result_id"] == "T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "direct_volumetric_c_v_or_same_state_Cp_source_missing" not in full[
        "major_result"
    ]["what_remains_open"]
    assert "c_v_source_uncertainty_not_closed" in full["major_result"][
        "what_remains_open"
    ]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"][
        "what_remains_open"
    ]
    assert any(
        item["major_result_id"] == "T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR"
        for item in register["entries"]
    )
