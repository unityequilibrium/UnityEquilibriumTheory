from __future__ import annotations

from docs.core.topic13_closure_record_contract import (
    topic13_closure_record_schema,
    validate_base_phi_alpha_record,
    validate_ding_csrc_payload,
    validate_physical_transport_record,
)


def _holdout() -> dict[str, bool]:
    return {
        "xie_2026_accessed": False,
        "target_curve_used": False,
        "fit_or_tuning_used": False,
    }


def test_schema_contains_three_fail_closed_packages() -> None:
    schema = topic13_closure_record_schema()
    assert schema["status"] == "SCHEMA_ONLY_NO_EVIDENCE"
    assert len(schema["packages"]) == 3
    assert len(schema["forbidden_shortcuts"]) >= 5


def test_base_phi_alpha_record_requires_independent_paired_response() -> None:
    record = {
        "record_id": "test-alpha-001",
        "record_kind": "EXTERNAL_INPUT",
        "data_role": "CALIBRATION",
        "alpha_Phi_K": 4.0,
        "alpha_uncertainty_K_per_normalized_base_Phi": 0.2,
        "delta_phi_base": 0.25,
        "delta_phi_uncertainty": 0.01,
        "delta_Tq_K": 1.0,
        "delta_Tq_uncertainty_K": 0.05,
        "alpha_units": "K per normalized base Phi",
        "phi_units": "normalized base Phi",
        "temperature_K": 300.0,
        "material_state_id": "independent-material-state",
        "source_locator": "https://example.invalid/independent-record",
        "source_hash": "a" * 64,
        "preprocessing": "none",
        "row_identity": "row-001",
        "independence_statement": "locked before target comparison; not selected from TTG curve",
        "evidence_status": "SOURCE_LOCKED",
        "holdout_policy": _holdout(),
    }
    result = validate_base_phi_alpha_record(record)
    assert result["status"] == "PASS_BASE_PHI_ALPHA_RECORD"
    record["holdout_policy"]["target_curve_used"] = True
    assert validate_base_phi_alpha_record(record)["status"] == "BLOCKED_BASE_PHI_ALPHA_RECORD"


def test_ding_payload_recomputes_aggregate_c_src_from_mode_rows() -> None:
    payload = {
        "package_id": "test-ding-001",
        "data_role": "DERIVED",
        "source_locator": "https://example.invalid/ding-payload",
        "source_hash": "b" * 64,
        "permission_or_terms": "permissioned research use",
        "preprocessing": "none",
        "material_state": {
            "material_identity": "natural graphite",
            "morphology": "bulk TTG specimen",
            "isotope_state": "natural isotope mix",
            "defect_state": "declared source state",
            "temperature_state": "300 K",
        },
        "response_contract": {
            "observable": "Delta_Tq",
            "equation": "Delta_Tq=Delta_u_ph/C_src",
        },
        "convergence": {"status": "PASS"},
        "mode_rows": [
            {"row_id": "m1", "mode_id": "m1", "temperature_K": 300.0, "c_mu_J_m3_K": 2.0, "weight": 1.0, "units": "J m^-3 K^-1"},
            {"row_id": "m2", "mode_id": "m2", "temperature_K": 300.0, "c_mu_J_m3_K": 3.0, "weight": 1.0, "units": "J m^-3 K^-1"},
        ],
        "c_src_rows": [
            {"row_id": "c300", "temperature_K": 300.0, "C_src_J_m3_K": 5.0, "uncertainty_J_m3_K": 0.1, "uncertainty_status": "SOURCE_GRADE", "units": "J m^-3 K^-1"},
        ],
        "holdout_policy": _holdout(),
    }
    assert validate_ding_csrc_payload(payload)["status"] == "PASS_DING_CSRC_PAYLOAD"
    payload["c_src_rows"][0]["C_src_J_m3_K"] = 5.5
    assert validate_ding_csrc_payload(payload)["status"] == "BLOCKED_DING_CSRC_PAYLOAD"


def test_transport_record_rejects_synthetic_evidence() -> None:
    record = {
        "coefficient_name": "kappa",
        "value": 1.0,
        "uncertainty": 0.1,
        "units": "W m^-1 K^-1",
        "unit_lane": "SI",
        "hydrodynamic_frame": "Landau",
        "state": {"temperature_K": 300.0, "chemical_potential": 0.0, "space_response": 0.1},
        "correlator_formula_id": "retarded-001",
        "correlator_locator": "https://example.invalid/correlator",
        "source_locator": "https://example.invalid/transport",
        "source_hash": "c" * 64,
        "evidence_status": "SYNTHETIC_CONTROL",
        "kms_fdt": {"status": "PASS"},
        "entropy_mapping": {"status": "PASS"},
        "holdout_policy": _holdout(),
    }
    assert validate_physical_transport_record(record)["status"] == "BLOCKED_PHYSICAL_TRANSPORT_RECORD"
