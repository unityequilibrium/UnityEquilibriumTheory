from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_gatech_source_audit_closes_source_row_only() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SOURCE_CP_95CI_CV_OPEN"
    assert all(audit["checks"].values())
    assert audit["row_identity"]["temperature_K"] == 573.15
    assert audit["reported_values"]["uncertainty_confidence"] == "95%"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert "source_quantity_is_c_p_not_volumetric_c_v" in audit["major_result"]["open_blockers"]


def test_gatech_raw_identity_is_archived_and_not_holdout() -> None:
    package = load(PACKAGE)
    source = package["source"]
    if RAW.is_file():
        assert RAW.stat().st_size == source["local_raw_bytes"]
    else:
        # Public checkout keeps the source package, not the raw workbook.
        assert source["local_raw_path"].endswith("Data/03_Research/raw/gen3csp_graphite.xlsx")
        assert len(source["local_raw_sha256"]) == 64
        assert source["local_raw_bytes"] > 0
    assert package["holdout_policy"]["xie_2026_accessed"] is False
    assert source["source_data_role"].endswith("not consumed by target fitting")


def test_topic13_gate_records_source_anchor_without_promoting_alpha() -> None:
    gate = load(GATE)
    branch = gate["verification_status"]["alpha_Phi_K"]["named_energy_response_branch"]
    assert branch["source_anchor"]["status"] == "PASS_SOURCE_CP_95CI_CV_OPEN"
    assert branch["source_anchor"]["c_v_status"] == "OPEN"
    assert branch["source_anchor"]["consumed_for_calibration"] is False
    assert gate["verification_status"]["alpha_Phi_K"]["independent_calibration_or_derivation"] is False
    assert gate["claim_promotion"] is False
