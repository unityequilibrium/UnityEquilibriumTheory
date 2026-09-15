from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_zenodo_hitrace_isotropic_graphite_cp_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "zenodo_hitrace_isotropic_graphite_cp_source_package.json"
)
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_hitrace_lane_closes_only_source_comparator_scope() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "zenodo_hitrace_isotropic_graphite_cp_comparator"
    ]
    assert lane["status"] == "PASS_SCOPED_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["derived_comparator"]["row_count"] == 27
    assert lane["derived_comparator"]["uncertainty_bearing_row_count"] == 16
    assert lane["derived_comparator"]["uncertainty_missing_row_count"] == 11
    assert lane["derived_comparator"]["quantity_is_Cp_not_Cv"] is True
    assert lane["derived_comparator"]["c_v_emitted"] is False
    assert package["source"]["local_raw_sha256"] == lane["source"]["local_hash_observed"]
    assert projected["major_result_id"] == "T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "c_v_source_uncertainty_not_closed" in full["major_result"][
        "what_remains_open"
    ]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"][
        "what_remains_open"
    ]
    assert any(
        item["major_result_id"] == "T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR"
        for item in register["entries"]
    )
