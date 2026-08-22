from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
BASELINE_AUDIT_REL = "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
VARIANT_AUDIT_REL = "docs/core/artifacts/t13_calorine_legacy_nep2_pbte_reproduction_audit.json"
BASELINE_PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "t13_calorine_zenodo_nep_bte_reproduction_source_package.json"
)
VARIANT_PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_legacy_nep2_pbte_reproduction_source_package.json"
)
OUT_REL = "docs/core/artifacts/t13_calorine_model_form_state_spread_comparison_audit.json"
COMMON_MESH = [10, 10, 5]
COMMON_TEMPERATURES = [200.0, 300.0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(rel_path: str) -> tuple[Path, dict[str, Any]]:
    path = ROOT / rel_path
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return path, value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def latest_mesh(audit: dict[str, Any], label: str) -> dict[str, Any]:
    runs = audit.get("reproduction", {}).get("mesh_runs", [])
    matches = [run for run in runs if run.get("mesh") == COMMON_MESH]
    require(len(matches) == 1, f"{label} must contain exactly one {COMMON_MESH} mesh run")
    return matches[0]


def rows_by_temperature(mesh_run: dict[str, Any], label: str) -> dict[float, float]:
    rows = mesh_run.get("c_src_rows", [])
    result: dict[float, float] = {}
    for row in rows:
        temperature = float(row["temperature_K"])
        value = float(row["C_src_J_m^-3_K^-1"])
        require(value > 0.0, f"{label} C_src must be positive at {temperature} K")
        require(temperature not in result, f"{label} has duplicate temperature {temperature}")
        result[temperature] = value
    return result


def source_input_records(package: dict[str, Any], label: str) -> list[dict[str, Any]]:
    records = package.get("source", {}).get("inputs", [])
    require(records, f"{label} source package has no input records")
    checked: list[dict[str, Any]] = []
    for record in records:
        path = ROOT / record["path"]
        require(path.is_file(), f"{label} source input is missing: {record['path']}")
        actual = sha256(path)
        require(actual == record["sha256"], f"{label} source input hash mismatch: {record['path']}")
        checked.append(
            {
                "path": record["path"],
                "size_bytes": record.get("size_bytes"),
                "sha256": actual,
                "locator": record.get("locator"),
            }
        )
    return checked


def model_header(package: dict[str, Any], label: str) -> str:
    records = package.get("source", {}).get("inputs", [])
    potential = records[-1]
    first_line = (ROOT / potential["path"]).read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
    require(first_line, f"{label} potential input has no model header")
    return first_line


def run_flags(audit: dict[str, Any], label: str) -> dict[str, bool]:
    runs = audit.get("reproduction", {}).get("mesh_runs", [])
    require(runs, f"{label} has no mesh runs")
    checks = {
        "fit_performed": all(run.get("fit_performed") is False for run in runs),
        "target_curve_used": all(run.get("target_curve_used") is False for run in runs),
        "alpha_Phi_K_fit_performed": all(
            run.get("alpha_Phi_K_fit_performed") is False for run in runs
        ),
        "holdout_accessed": all(run.get("holdout_accessed") is False for run in runs),
    }
    require(all(checks.values()), f"{label} contains a fit, target, alpha, or holdout flag")
    return checks


def evidence(rel_path: str, role: str, summary: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / rel_path
    require(path.is_file(), f"missing evidence artifact: {rel_path}")
    return {
        "path": rel_path,
        "sha256": sha256(path),
        "role": role,
        "summary": summary,
    }


def main() -> int:
    baseline_audit_path, baseline = load(BASELINE_AUDIT_REL)
    variant_audit_path, variant = load(VARIANT_AUDIT_REL)
    baseline_package_path, baseline_package = load(BASELINE_PACKAGE_REL)
    variant_package_path, variant_package = load(VARIANT_PACKAGE_REL)

    require(
        baseline.get("status") == "PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION",
        "unexpected baseline Calorine status",
    )
    require(
        variant.get("status") == "PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION",
        "unexpected C-CX legacy status",
    )
    baseline_mesh = latest_mesh(baseline, "baseline")
    variant_mesh = latest_mesh(variant, "C-CX legacy")
    baseline_rows = rows_by_temperature(baseline_mesh, "baseline")
    variant_rows = rows_by_temperature(variant_mesh, "C-CX legacy")
    common_temperatures = sorted(set(baseline_rows) & set(variant_rows))
    require(common_temperatures == COMMON_TEMPERATURES, "latest mesh temperature intersection changed")

    baseline_inputs = source_input_records(baseline_package, "baseline")
    variant_inputs = source_input_records(variant_package, "C-CX legacy")
    baseline_package_hash = sha256(baseline_package_path)
    variant_package_hash = sha256(variant_package_path)
    require(
        baseline_package_hash == baseline.get("source_package", {}).get("sha256"),
        "baseline source package hash does not match its audit",
    )
    require(
        variant_package_hash == variant.get("source_package", {}).get("sha256"),
        "C-CX source package hash does not match its audit",
    )

    baseline_flags = run_flags(baseline, "baseline")
    variant_flags = run_flags(variant, "C-CX legacy")
    rows: list[dict[str, float]] = []
    for temperature in common_temperatures:
        baseline_value = baseline_rows[temperature]
        variant_value = variant_rows[temperature]
        absolute_spread = variant_value - baseline_value
        rows.append(
            {
                "temperature_K": temperature,
                "baseline_C_src_J_m^-3_K^-1": baseline_value,
                "variant_C_src_J_m^-3_K^-1": variant_value,
                "absolute_spread_J_m^-3_K^-1": absolute_spread,
                "relative_spread_to_baseline": absolute_spread / baseline_value,
            }
        )

    baseline_volume = float(baseline_mesh["primitive_volume_A3"])
    variant_volume = float(variant_mesh["primitive_volume_A3"])
    volume_delta = variant_volume - baseline_volume
    baseline_header = model_header(baseline_package, "baseline")
    variant_header = model_header(variant_package, "C-CX legacy")
    baseline_backend = baseline_package.get("reproduction", {}).get("software", {}).get("calorine")
    variant_backend = variant_package.get("source", {}).get("backend", {})
    require(baseline_backend and variant_backend.get("commit"), "backend identity is incomplete")
    require(variant_package.get("source", {}).get("model_header") == variant_header, "variant model header drift")

    baseline_evidence = evidence(
        BASELINE_AUDIT_REL,
        "archived baseline audit",
        {"status": baseline.get("status"), "mesh": COMMON_MESH},
    )
    variant_evidence = evidence(
        VARIANT_AUDIT_REL,
        "archived C-CX legacy audit",
        {"status": variant.get("status"), "mesh": COMMON_MESH},
    )
    baseline_package_evidence = evidence(
        BASELINE_PACKAGE_REL,
        "baseline source and reproduction manifest",
        {"sha256_recorded_by_audit": baseline.get("source_package", {}).get("sha256")},
    )
    variant_package_evidence = evidence(
        VARIANT_PACKAGE_REL,
        "C-CX source, legacy backend, and reproduction manifest",
        {"sha256_recorded_by_audit": variant.get("source_package", {}).get("sha256")},
    )
    evidence_artifacts = [
        baseline_evidence,
        variant_evidence,
        baseline_package_evidence,
        variant_package_evidence,
    ]

    major_result = {
        "major_result_id": "T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "The archived baseline and C-CX legacy candidate rows are compared on the common 10x10x5 q mesh at 200 K and 300 K.",
            "The comparison derives absolute and baseline-relative C_src spread from source-locked artifact rows rather than hand-entered values.",
            "The C-CX result is confirmed as a legacy-backend model/state comparison; backend, model-header, and primitive-volume differences are explicit.",
        ],
        "equation_or_mapping": {
            "candidate_observable": "C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]",
            "comparison": "relative_spread(T) = [C_src_C-CX(T) - C_src_baseline(T)] / C_src_baseline(T)",
            "temperature_response_contract": "Delta_Tq = Delta_u_ph / C_src(T); candidate source response only",
            "ttg_measurement": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
        },
        "units": {
            "C_src": "J m^-3 K^-1",
            "temperature": "K",
            "primitive_volume": "A^3",
            "absolute_spread": "J m^-3 K^-1",
            "relative_spread": "dimensionless",
        },
        "derivation_class": "EXTERNAL_CANDIDATE_MODEL_FORM_STATE_COMPARISON_NO_UET_DERIVATION",
        "observable": "candidate graphite volumetric phonon heat-capacity model/state spread",
        "data_role": "EXTERNAL_COMPARATOR_COMPARISON_NOT_UNCERTAINTY",
        "evidence_artifacts": evidence_artifacts,
        "verification_status": "PASS_SCOPED_CALORINE_MODEL_FORM_STATE_SPREAD",
        "open_blockers": [
            "calorine_route_source_grade_uncertainty_missing",
            "calorine_route_material_regime_mapping_to_ding_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "dependency_unlocked": "Calorine comparator spread lane only; no Ding C_src acceptance, alpha calibration, full Topic 13, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This is not a Ding numeric source, not source-grade uncertainty, not a pure model-form error because state and backend differ, not an alpha_Phi_K calibration, not a Phi prediction, and not Full Topic 13 closure.",
    }

    checks = {
        "baseline_status_valid": True,
        "variant_status_valid": True,
        "baseline_source_package_hash_matches": baseline_package_hash
        == baseline.get("source_package", {}).get("sha256"),
        "variant_source_package_hash_matches": variant_package_hash
        == variant.get("source_package", {}).get("sha256"),
        "source_input_hashes_match": True,
        "common_mesh_is_10x10x5": True,
        "common_temperature_set_is_200_300_K": True,
        "baseline_latest_mesh_preflight_pass": baseline.get("checks", {}).get("latest_mesh_pair_preflight_pass") is True,
        "variant_latest_mesh_preflight_pass": variant.get("checks", {}).get("mesh_pair_preflight_pass") is True,
        "c_src_units_are_j_m^-3_K^-1": True,
        "volume_difference_recorded": baseline_volume != variant_volume,
        "model_headers_recorded": bool(baseline_header and variant_header),
        "baseline_no_fit_target_alpha_or_holdout": all(baseline_flags.values()),
        "variant_no_fit_target_alpha_or_holdout": all(variant_flags.values()),
        "xie_2026_holdout_accessed": False,
        "comparison_is_not_source_grade_uncertainty": True,
        "comparison_is_not_pure_model_form_error": True,
        "numeric_alpha_Phi_K_emitted": False,
        "ding_csrc_accepted": False,
        "claim_promotion": False,
    }
    positive_check_keys = (
        "baseline_status_valid",
        "variant_status_valid",
        "baseline_source_package_hash_matches",
        "variant_source_package_hash_matches",
        "source_input_hashes_match",
        "common_mesh_is_10x10x5",
        "common_temperature_set_is_200_300_K",
        "baseline_latest_mesh_preflight_pass",
        "variant_latest_mesh_preflight_pass",
        "c_src_units_are_j_m^-3_K^-1",
        "volume_difference_recorded",
        "model_headers_recorded",
        "baseline_no_fit_target_alpha_or_holdout",
        "variant_no_fit_target_alpha_or_holdout",
        "comparison_is_not_source_grade_uncertainty",
        "comparison_is_not_pure_model_form_error",
    )
    require(all(checks[key] for key in positive_check_keys), "one or more comparison checks failed")

    artifact = {
        "schema_version": "t13-calorine-model-form-state-spread-comparison-v1",
        "artifact": "t13_calorine_model_form_state_spread_comparison_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_CALORINE_MODEL_FORM_STATE_SPREAD",
        "claim_promotion": False,
        "major_result": major_result,
        "comparison": {
            "mesh": COMMON_MESH,
            "temperatures_K": common_temperatures,
            "rows": rows,
            "baseline": {
                "audit": baseline_evidence,
                "source_package": baseline_package_evidence,
                "model_header": baseline_header,
                "calorine_backend": baseline_backend,
                "primitive_volume_A3": baseline_volume,
                "material_state": baseline_package.get("source", {}).get("source_state"),
                "source_inputs": baseline_inputs,
            },
            "variant": {
                "audit": variant_evidence,
                "source_package": variant_package_evidence,
                "model_header": variant_header,
                "calorine_backend": {
                    "tag": variant_backend.get("tag"),
                    "commit": variant_backend.get("commit"),
                    "source_locator": variant_backend.get("source_locator"),
                },
                "primitive_volume_A3": variant_volume,
                "material_state": variant_package.get("source", {}).get("state"),
                "source_inputs": variant_inputs,
            },
            "primitive_volume_difference_A3": volume_delta,
            "primitive_volume_relative_difference": volume_delta / baseline_volume,
            "spread_summary": {
                "max_absolute_relative_spread": max(abs(row["relative_spread_to_baseline"]) for row in rows),
                "min_absolute_relative_spread": min(abs(row["relative_spread_to_baseline"]) for row in rows),
            },
        },
        "uncertainty": {
            "status": "OPEN_SOURCE_GRADE_UNCERTAINTY",
            "model_form_state_spread_is_reported": True,
            "source_grade_statistical_or_systematic_uncertainty_present": False,
            "ding_material_state_mapping_closed": False,
            "density_uncertainty_closed": False,
            "c_v_source_uncertainty_closed": False,
        },
        "checks": checks,
        "evidence_artifacts": evidence_artifacts,
        "numeric_candidate_rows_compared": True,
        "numeric_C_src_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "acceptance_for_full_topic13": False,
        "controlling_blocker": "calorine_model_form_state_spread_is_comparator_only_until_material_mapping_and_source_grade_uncertainty_close",
        "next_controller": "Obtain an authorized Ding numeric C_src package or accepted same-regime independent reproduction with source-grade uncertainty; keep this comparison outside alpha_Phi_K calibration and holdout paths.",
        "claim_boundary": major_result["claim_boundary"],
        "report": {
            "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
            "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
            "WHAT_REMAINS_OPEN": major_result["open_blockers"],
            "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
            "STATUS": "PASS_SCOPED_CALORINE_MODEL_FORM_STATE_SPREAD",
            "WHAT_CHANGED": "Added a hash-backed comparison of archived baseline and C-CX legacy Calorine candidate C_src rows on the common 10x10x5 mesh; no new model run, fit, calibration, synthetic data, threshold change, or holdout access was used.",
            "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
            "VERIFICATION": "Source package hashes and local input hashes match; both latest mesh preflights pass; model headers, backend identity, primitive-volume difference, and common-temperature rows are recorded.",
            "CONTROLLING_BLOCKER": "Ding-compatible source-grade C_src and independent alpha_Phi_K remain missing; the comparison is not uncertainty closure.",
            "NEXT_ACTION": artifact_next_action_placeholder(),
            "CLAIM_BOUNDARY": major_result["claim_boundary"],
        },
    }
    OUT_PATH = ROOT / OUT_REL
    OUT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "path": OUT_REL, "rows": rows}, indent=2))
    return 0


def artifact_next_action_placeholder() -> str:
    return "Source-lock an authorized Ding numeric C_src package or accepted same-regime independent reproduction; do not use this comparator for alpha_Phi_K or holdout prediction."


if __name__ == "__main__":
    raise SystemExit(main())
