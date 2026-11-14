from __future__ import annotations

import copy
import json
from pathlib import Path

from docs.scripts.audit.audit_topic13_ding_pbte_payload import audit_payload


def _payload() -> dict:
    return {
        "schema_version": "t13-ding-pbte-numeric-payload-v1",
        "data_role": "INDEPENDENT_REPRODUCTION_INPUT",
        "source_identity": {"source_id": "authorized-test-fixture"},
        "source_locator_or_author_file_name": "authorized_payload.zip::csrc.json",
        "material_state_and_geometry": {"state": "declared graphite state"},
        "quantity_definition": {"c_mu": "mode heat capacity", "C_src": "weighted mode sum"},
        "units": {"c_mu": "J m^-3 K^-1", "C_src": "J m^-3 K^-1"},
        "temperature_grid_K": [200.0, 250.0],
        "mode_rows": [
            {"row_id": "200-0", "temperature_K": 200.0, "mode_index": 0, "c_mu_J_per_m3_K": 2.0, "weight": 1.0},
            {"row_id": "200-1", "temperature_K": 200.0, "mode_index": 1, "c_mu_J_per_m3_K": 3.0, "weight": 2.0},
            {"row_id": "250-0", "temperature_K": 250.0, "mode_index": 0, "c_mu_J_per_m3_K": 4.0, "weight": 1.0},
            {"row_id": "250-1", "temperature_K": 250.0, "mode_index": 1, "c_mu_J_per_m3_K": 5.0, "weight": 2.0},
        ],
        "c_src_rows": [
            {"row_id": "csrc-200", "temperature_K": 200.0, "C_src_J_per_m3_K": 8.0, "uncertainty_standard_J_per_m3_K": 0.1},
            {"row_id": "csrc-250", "temperature_K": 250.0, "C_src_J_per_m3_K": 14.0, "uncertainty_standard_J_per_m3_K": 0.2},
        ],
        "preprocessing": "none; source rows retained with stable identities",
        "uncertainty_or_convergence": {"accepted": True, "method": "source standard uncertainty", "source_standard_uncertainty": "reported per C_src row"},
        "source_hashes": [{"path": "authorized_payload.zip", "sha256": "a" * 64}],
        "permission_or_terms": "authorized research reuse",
        "independence_statement": {"independent_of_target": True},
        "holdout_non_access_statement": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
            "parameter_fitting_performed": False,
            "post_inspection_tuning": False,
        },
    }


def test_missing_payload_stays_blocked(tmp_path: Path) -> None:
    report = audit_payload(tmp_path / "missing.json")
    assert report["status"] == "BLOCKED_DING_PBTE_PAYLOAD_NOT_RECEIVED"
    assert report["payload_present"] is False


def test_valid_payload_recomputes_c_src_without_emitting_alpha(tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(_payload()), encoding="utf-8")
    report = audit_payload(payload_path)
    assert report["status"] == "PASS_DING_PBTE_PAYLOAD_ACCEPTANCE"
    assert report["row_summary"]["recomputed_C_src_J_per_m3_K"] == {"200": 8.0, "250": 14.0}
    assert report["numeric_C_src_accepted"] is True
    assert report["numeric_alpha_Phi_K_emitted"] is False
    assert report["holdout_accessed"] is False


def test_c_src_mismatch_fails_without_partial_acceptance(tmp_path: Path) -> None:
    payload = copy.deepcopy(_payload())
    payload["c_src_rows"][1]["C_src_J_per_m3_K"] = 99.0
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    report = audit_payload(payload_path)
    assert report["status"] == "FAIL_DING_PBTE_PAYLOAD_ACCEPTANCE"
    assert "c_src_recompute_mismatch_250K" in report["row_failures"]
    assert report["numeric_C_src_accepted"] is False


def test_holdout_access_fails_the_payload_contract(tmp_path: Path) -> None:
    payload = copy.deepcopy(_payload())
    payload["holdout_non_access_statement"]["xie_2026_accessed"] = True
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    report = audit_payload(payload_path)
    assert report["status"] == "FAIL_DING_PBTE_PAYLOAD_ACCEPTANCE"
    assert report["checks"]["holdout_policy_pass"] is False
    assert report["holdout_accessed"] is True

def test_malformed_numeric_row_fails_without_exception(tmp_path: Path) -> None:
    payload = copy.deepcopy(_payload())
    payload["mode_rows"][0]["c_mu_J_per_m3_K"] = None
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    report = audit_payload(payload_path)
    assert report["status"] == "FAIL_DING_PBTE_PAYLOAD_ACCEPTANCE"
    assert "mode_heat_capacity_not_nonnegative_finite" in report["row_failures"]
