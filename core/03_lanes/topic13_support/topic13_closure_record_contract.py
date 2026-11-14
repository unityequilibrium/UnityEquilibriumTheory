"""Fail-closed record contracts for Topic 13 Core closure inputs.

These validators do not create scientific evidence.  They only decide whether
an incoming source package contains the fields needed by the existing Topic 13
closure gate.  Missing or synthetic values remain blocked.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any


SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-fA-F]{64}$")
ALPHA_EVIDENCE = frozenset({"SOURCE_LOCKED", "EXTERNALLY_MATCHED", "DERIVED_INDEPENDENT"})
TRANSPORT_EVIDENCE = frozenset({"KUBO_MATCHED", "SOURCE_LOCKED", "EXTERNALLY_MATCHED"})


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value.strip()))


def _required(record: dict[str, Any], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if name not in record]


def _holdout_clean(record: dict[str, Any]) -> bool:
    policy = record.get("holdout_policy")
    if not isinstance(policy, dict):
        return False
    return all(
        policy.get(key) is False
        for key in ("xie_2026_accessed", "target_curve_used", "fit_or_tuning_used")
    )


def validate_base_phi_alpha_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate one independent base-Phi/SI response record."""

    required = (
        "record_id",
        "record_kind",
        "data_role",
        "alpha_Phi_K",
        "alpha_uncertainty_K_per_normalized_base_Phi",
        "delta_phi_base",
        "delta_phi_uncertainty",
        "delta_Tq_K",
        "delta_Tq_uncertainty_K",
        "alpha_units",
        "phi_units",
        "temperature_K",
        "material_state_id",
        "source_locator",
        "source_hash",
        "preprocessing",
        "row_identity",
        "independence_statement",
        "evidence_status",
        "holdout_policy",
    )
    missing = _required(record, required)
    checks: dict[str, bool] = {
        "required_fields_present": not missing,
        "record_kind_is_admissible": record.get("record_kind") in {"EXTERNAL_INPUT", "DERIVED"},
        "data_role_is_calibration": record.get("data_role") == "CALIBRATION",
        "alpha_units_are_declared": record.get("alpha_units") == "K per normalized base Phi",
        "phi_units_are_declared": record.get("phi_units") == "normalized base Phi",
        "alpha_is_finite": _finite(record.get("alpha_Phi_K")),
        "alpha_uncertainty_is_nonnegative": _finite(record.get("alpha_uncertainty_K_per_normalized_base_Phi"))
        and float(record.get("alpha_uncertainty_K_per_normalized_base_Phi")) >= 0.0,
        "paired_phi_is_nonzero": _finite(record.get("delta_phi_base"))
        and abs(float(record.get("delta_phi_base"))) > 0.0,
        "paired_uncertainties_are_nonnegative": all(
            _finite(record.get(name)) and float(record.get(name)) >= 0.0
            for name in ("delta_phi_uncertainty", "delta_Tq_uncertainty_K")
        ),
        "thermal_response_is_finite": _finite(record.get("delta_Tq_K")),
        "temperature_is_positive": _finite(record.get("temperature_K"))
        and float(record.get("temperature_K")) > 0.0,
        "material_state_is_declared": _nonempty(record.get("material_state_id")),
        "provenance_is_complete": all(
            (
                _nonempty(record.get("source_locator")),
                _hash(record.get("source_hash")),
                _nonempty(record.get("preprocessing")),
                _nonempty(record.get("row_identity")),
                _nonempty(record.get("independence_statement")),
            )
        ),
        "evidence_status_is_admissible": record.get("evidence_status") in ALPHA_EVIDENCE,
        "holdout_is_clean": _holdout_clean(record),
        "source_does_not_name_locked_holdout": "xie" not in str(record.get("source_locator", "")).lower(),
    }
    if checks["paired_phi_is_nonzero"] and checks["thermal_response_is_finite"]:
        expected = float(record["delta_Tq_K"]) / float(record["delta_phi_base"])
        checks["alpha_matches_paired_response"] = math.isclose(
            expected,
            float(record["alpha_Phi_K"]),
            rel_tol=1.0e-9,
            abs_tol=1.0e-12,
        )
    else:
        checks["alpha_matches_paired_response"] = False
    return {
        "status": "PASS_BASE_PHI_ALPHA_RECORD" if all(checks.values()) else "BLOCKED_BASE_PHI_ALPHA_RECORD",
        "missing_fields": missing,
        "checks": checks,
        "claim_boundary": "Record validation only; no value is accepted until this contract and the Topic 13 gate both pass.",
    }


def validate_ding_csrc_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a mode-resolved, uncertainty-bearing Ding-compatible C_src payload."""

    required = (
        "package_id",
        "data_role",
        "source_locator",
        "source_hash",
        "permission_or_terms",
        "preprocessing",
        "material_state",
        "response_contract",
        "convergence",
        "mode_rows",
        "c_src_rows",
        "holdout_policy",
    )
    missing = _required(payload, required)
    material = payload.get("material_state")
    material_fields = ("material_identity", "morphology", "isotope_state", "defect_state", "temperature_state")
    rows = payload.get("c_src_rows")
    modes = payload.get("mode_rows")
    checks: dict[str, bool] = {
        "required_fields_present": not missing,
        "data_role_is_not_holdout": payload.get("data_role") != "HOLDOUT",
        "source_hash_is_sha256": _hash(payload.get("source_hash")),
        "source_provenance_is_complete": all(
            _nonempty(payload.get(name))
            for name in ("source_locator", "permission_or_terms", "preprocessing")
        ),
        "material_state_is_complete": isinstance(material, dict)
        and all(_nonempty(material.get(name)) for name in material_fields),
        "response_contract_is_declared": isinstance(payload.get("response_contract"), dict)
        and all(
            _nonempty(payload["response_contract"].get(name))
            for name in ("observable", "equation")
        ),
        "convergence_is_passed": isinstance(payload.get("convergence"), dict)
        and payload["convergence"].get("status") in {"PASS", "ACCEPTED"},
        "mode_rows_are_nonempty": isinstance(modes, list) and bool(modes),
        "c_src_rows_are_nonempty": isinstance(rows, list) and bool(rows),
        "holdout_is_clean": _holdout_clean(payload),
        "source_does_not_name_locked_holdout": "xie" not in str(payload.get("source_locator", "")).lower(),
    }
    row_ids: list[str] = []
    mode_ids: list[str] = []
    mode_by_temperature: dict[float, float] = defaultdict(float)
    if isinstance(modes, list):
        for row in modes:
            if not isinstance(row, dict):
                continue
            row_ids.append(str(row.get("row_id", "")))
            mode_ids.append(str(row.get("mode_id", "")))
            if all(
                _finite(row.get(name))
                for name in ("temperature_K", "c_mu_J_m3_K", "weight")
            ):
                mode_by_temperature[float(row["temperature_K"])] += float(row["c_mu_J_m3_K"]) * float(row["weight"])
    checks["mode_row_identity_is_unique"] = bool(mode_ids) and len(mode_ids) == len(set(mode_ids))
    checks["mode_units_are_declared"] = bool(modes) and all(
        isinstance(row, dict) and row.get("units") == "J m^-3 K^-1"
        for row in modes
    )
    row_by_temperature: dict[float, dict[str, Any]] = {}
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_ids.append(str(row.get("row_id", "")))
            if _finite(row.get("temperature_K")):
                row_by_temperature[float(row["temperature_K"])] = row
    checks["c_src_row_identity_is_unique"] = bool(row_by_temperature) and len(row_ids) == len(set(row_ids))
    checks["c_src_units_are_declared"] = bool(rows) and all(
        isinstance(row, dict) and row.get("units") == "J m^-3 K^-1"
        for row in rows
    )
    checks["uncertainty_is_source_grade"] = bool(rows) and all(
        isinstance(row, dict)
        and (_finite(row.get("uncertainty_J_m3_K")) or _finite(row.get("relative_uncertainty")))
        and row.get("uncertainty_status") == "SOURCE_GRADE"
        for row in rows
    )
    recompute_residuals: dict[str, float] = {}
    for temperature, row in row_by_temperature.items():
        reported = row.get("C_src_J_m3_K")
        calculated = mode_by_temperature.get(temperature)
        if not (_finite(reported) and _finite(calculated)):
            continue
        recompute_residuals[str(temperature)] = abs(float(reported) - calculated) / max(abs(float(reported)), 1.0e-30)
    checks["mode_sum_reproduces_C_src"] = bool(recompute_residuals) and max(recompute_residuals.values()) <= 1.0e-8
    return {
        "status": "PASS_DING_CSRC_PAYLOAD" if all(checks.values()) else "BLOCKED_DING_CSRC_PAYLOAD",
        "missing_fields": missing,
        "checks": checks,
        "max_mode_sum_relative_residual": max(recompute_residuals.values()) if recompute_residuals else None,
        "claim_boundary": "Payload validation only; material equivalence and Topic 13 promotion still require the canonical gate.",
    }


def validate_physical_transport_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate one state-matched physical transport/KMS/entropy record."""

    required = (
        "coefficient_name",
        "value",
        "uncertainty",
        "units",
        "unit_lane",
        "hydrodynamic_frame",
        "state",
        "correlator_formula_id",
        "correlator_locator",
        "source_locator",
        "source_hash",
        "evidence_status",
        "kms_fdt",
        "entropy_mapping",
        "holdout_policy",
    )
    missing = _required(record, required)
    state = record.get("state")
    checks: dict[str, bool] = {
        "required_fields_present": not missing,
        "coefficient_is_finite": _finite(record.get("value")),
        "uncertainty_is_nonnegative": _finite(record.get("uncertainty"))
        and float(record.get("uncertainty")) >= 0.0,
        "SI_units_are_declared": record.get("unit_lane") == "SI" and _nonempty(record.get("units")),
        "frame_is_declared": _nonempty(record.get("hydrodynamic_frame")),
        "state_is_complete": isinstance(state, dict)
        and all(_finite(state.get(name)) for name in ("temperature_K", "chemical_potential", "space_response")),
        "correlator_provenance_is_complete": all(
            _nonempty(record.get(name))
            for name in ("correlator_formula_id", "correlator_locator", "source_locator")
        )
        and _hash(record.get("source_hash")),
        "evidence_status_is_physical": record.get("evidence_status") in TRANSPORT_EVIDENCE,
        "kms_fdt_is_passed": isinstance(record.get("kms_fdt"), dict)
        and record["kms_fdt"].get("status") == "PASS",
        "entropy_mapping_is_passed": isinstance(record.get("entropy_mapping"), dict)
        and record["entropy_mapping"].get("status") == "PASS",
        "holdout_is_clean": _holdout_clean(record),
        "source_does_not_name_locked_holdout": "xie" not in str(record.get("source_locator", "")).lower(),
    }
    return {
        "status": "PASS_PHYSICAL_TRANSPORT_RECORD" if all(checks.values()) else "BLOCKED_PHYSICAL_TRANSPORT_RECORD",
        "missing_fields": missing,
        "checks": checks,
        "claim_boundary": "Record validation only; physical transport is not promoted until the canonical Topic 13 gate passes.",
    }


def topic13_closure_record_schema() -> dict[str, Any]:
    """Return the machine-readable schemas without any scientific values."""

    return {
        "schema_version": "t13-closure-record-contract-v1",
        "status": "SCHEMA_ONLY_NO_EVIDENCE",
        "packages": {
            "T13_INPUT_BASE_PHI_SI_ALPHA_BETA": {
                "validator": "validate_base_phi_alpha_record",
                "required_closure_fields": [
                    "paired base-Phi and SI response amplitudes",
                    "alpha_Phi_K and uncertainty",
                    "source locator, SHA-256, preprocessing, row identity",
                    "independence statement and clean holdout policy",
                ],
            },
            "T13_INPUT_DING_TTG_SOURCE": {
                "validator": "validate_ding_csrc_payload",
                "required_closure_fields": [
                    "mode-resolved c_mu rows and aggregate C_src rows",
                    "mode-sum recomputation residual <= 1e-8",
                    "material/morphology/isotope/defect/temperature state",
                    "source-grade uncertainty, convergence, provenance, and permission",
                ],
            },
            "T13_INPUT_PHYSICAL_TRANSPORT_MATCH": {
                "validator": "validate_physical_transport_record",
                "required_closure_fields": [
                    "SI coefficient value and uncertainty tied to one state",
                    "retarded-correlator and source provenance",
                    "KMS/FDT and entropy mapping status PASS",
                    "non-synthetic evidence status and clean holdout policy",
                ],
            },
        },
        "forbidden_shortcuts": [
            "normalized curve as alpha_Phi_K",
            "Landauer identity as beta derivation",
            "comparator as Ding C_src",
            "SYNTHETIC_CONTROL as physical transport",
            "Xie 2026 holdout in calibration, fitting, tuning, or threshold selection",
        ],
    }


__all__ = [
    "validate_base_phi_alpha_record",
    "validate_ding_csrc_payload",
    "validate_physical_transport_record",
    "topic13_closure_record_schema",
]
