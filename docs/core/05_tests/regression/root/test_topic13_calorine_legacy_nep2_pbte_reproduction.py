from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_legacy_nep2_pbte_reproduction_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_legacy_nep2_pbte_reproduction_source_package.json"
)


def test_legacy_nep2_pbte_reproduction_is_candidate_only() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"
    assert audit["major_result"]["major_result_id"] == (
        "T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["checks"]["same_force_constant_state_across_meshes"] is True
    assert audit["checks"]["displacement_contract_valid"] is True
    assert audit["checks"]["mesh_pair_preflight_pass"] is True
    assert audit["checks"]["no_fit_target_or_holdout"] is True
    assert audit["uncertainty"]["status"] == "OPEN_SOURCE_GRADE_UNCERTAINTY"
    assert audit["acceptance_for_full_topic13"] is False
    assert audit["claim_promotion"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert package["source"]["backend"]["commit"] == (
        "eedb2ac9f49cb60a64512e987b98993d3a44e186"
    )
    assert package["source"]["inputs"][1]["sha256"] == (
        "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
    )
    assert package["reproduction"]["c_src_rows_latest_mesh"] == [
        {"temperature_K": 200.0, "C_src_J_m^-3_K^-1": 993760.2797173061},
        {"temperature_K": 300.0, "C_src_J_m^-3_K^-1": 1689859.0705455516},
    ]
