from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
AUDIT_REL = "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_candidate_reproduction_closes_only_the_numeric_lane() -> None:
    audit = load(AUDIT_REL)
    assert audit["status"] == "PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION"
    assert audit["major_result"]["major_result_id"] == "T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["acceptance_for_full_topic13"] is False
    assert audit["checks"]["latest_mesh_pair_preflight_pass"] is True
    assert audit["checks"]["material_state_match_to_ding"] is False
    assert audit["checks"]["source_grade_uncertainty_present"] is False
    assert audit["checks"]["fit_performed"] is False
    assert audit["checks"]["alpha_Phi_K_fit_performed"] is False
    assert audit["checks"]["holdout_accessed"] is False
    assert audit["reproduction"]["convergence"]["latest_pair"]["max_relative_change"] <= 0.01
    rows = audit["reproduction"]["c_src_rows_latest_mesh"]
    assert [row["temperature_K"] for row in rows] == [200.0, 250.0, 300.0]
    assert all(float(row["C_src_J_m^-3_K^-1"]) > 0 for row in rows)


def test_full_gate_and_register_preserve_non_promotion_boundary() -> None:
    audit = load(AUDIT_REL)
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    lane = full["verification_status"]["source_package"]["calorine_zenodo_nep_bte_numeric_reproduction"]
    assert lane["major_result_id"] == "T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == audit["status"]
    assert lane["audit"]["path"] == AUDIT_REL
    assert lane["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])
    assert any(
        item.get("major_result_id") == "T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION"
        for item in register["entries"]
    )
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in full["major_result"]["what_remains_open"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
