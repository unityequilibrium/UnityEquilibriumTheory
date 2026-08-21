from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_nist_srm_3600_heat_capacity_boundary_audit.json"
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nist_srm_3600_glassy_carbon_heat_capacity.pdf"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_srm_3600_boundary_is_source_locked_and_comparator_only() -> None:
    result = load(ARTIFACT)
    assert result["status"] == "PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY"
    assert result["major_result"]["major_result_id"] == "T13_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["source"]["local_sha256"] == "5bbbd0e3949a1e38cbb7ec00bbfc1a75a9d4708f6a0656e5e49c8d44d32ba5da"
    assert result["source"]["local_bytes"] == 758635
    assert result["source"]["page_count"] == 6
    assert result["source"]["material_identity"]["ding_ttg_hopg_match"] is False


def test_srm_3600_preserves_uncertainty_boundary_without_emitting_rows() -> None:
    result = load(ARTIFACT)
    uncertainty = result["source"]["uncertainty_boundary"]
    assert uncertainty["reported_relative_magnitude"] == 0.02
    assert uncertainty["confidence_level"] == 0.90
    assert uncertainty["is_row_level_standard_uncertainty"] is False
    assert result["acceptance"]["numeric_rows_emitted"] == 0
    assert result["acceptance"]["figure_only_payload"] is True
    assert result["acceptance"]["accepted_for_full_topic13"] is False
    assert result["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
    assert result["acceptance"]["accepted_as_alpha_phi_k_calibration"] is False


def test_srm_3600_raw_hash_matches_artifact_and_holdout_is_untouched() -> None:
    result = load(ARTIFACT)
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == result["source"]["local_sha256"]
    assert result["checks"]["holdout_accessed"] is False
    assert result["acceptance"]["holdout_accessed"] is False
    assert result["acceptance"]["target_fit_performed"] is False
    assert result["acceptance"]["alpha_fit_performed"] is False


def test_full_gate_exposes_srm_3600_without_unlocking_topic13() -> None:
    gate = load(FULL_GATE)
    lane = gate["verification_status"]["source_package"]["nist_srm_3600_heat_capacity_comparator_boundary"]
    assert lane["major_result_id"] == "T13_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == "PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY"
    assert lane["controlling_blocker"] == "figure_only_numeric_payload_and_Ding_material_mapping_missing"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
