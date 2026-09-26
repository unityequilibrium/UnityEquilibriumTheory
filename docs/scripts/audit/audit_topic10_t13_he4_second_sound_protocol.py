#!/usr/bin/env python3
"""Audit the Topic 10–13 He-4 second-sound protocol candidate.

This checks frozen input identity and the declared source/uncertainty boundary.
It does not solve a UET mode, validate a physical prediction, or promote a gate.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = Path("docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_svp_second_sound_response_source_package.json")
CARD_PATH = Path("docs/topics/0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md")
SCRIPT_PATH = Path("docs/scripts/audit/audit_topic10_t13_he4_second_sound_protocol.py")
ALPHA_PATH = Path("docs/core/07_artifacts/topic13/t13_he4_o2_response_calibration_audit.json")
BETA_PATH = Path("docs/core/07_artifacts/topic13/t13_he4_o2_si_beta_mapping_audit.json")
ETA_PATH = Path("docs/core/07_artifacts/topic13/t13_he4_normal_viscosity_kubo_audit.json")
MATCH_PATH = Path("docs/core/07_artifacts/topic13/t13_he4_matching_independence_audit.json")
T10_PATH = Path("docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_state_velocity_representability_audit.json")
OUT_PATH = Path("docs/core/07_artifacts/topic13/t13_he4_second_sound_response_protocol_audit.json")


def load_json(relative_path: Path) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def sha256(relative_path: Path) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def close(actual: float, expected: float) -> bool:
    return math.isfinite(float(actual)) and math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=1e-12)


package = load_json(PACKAGE_PATH)
alpha = load_json(ALPHA_PATH)
beta = load_json(BETA_PATH)
eta = load_json(ETA_PATH)
matching = load_json(MATCH_PATH)
t10 = load_json(T10_PATH)
card_text = (ROOT / CARD_PATH).read_text(encoding="utf-8")

frozen = package["frozen_matching_constants"]
alpha_record = alpha["record"]
beta_record = beta["record"]
eta_record = eta["record"]
rows = package["response_rows"]
row_map = {round(float(row["temperature_T90_K"]), 3): row for row in rows}

expected_rows = {1.65: 20.37, 1.70: 20.33, 1.75: 20.18, 1.80: 19.90}
rows_match = all(
    temperature in row_map and close(row_map[temperature]["u2_m_s"], speed)
    for temperature, speed in expected_rows.items()
)
slope = (row_map[1.75]["u2_m_s"] - row_map[1.65]["u2_m_s"]) / (1.75 - 1.65) if rows_match else math.nan

checks = {
    "source_package_schema_and_id_valid": package.get("schema_version") == "t13-he4-second-sound-response-source-v1" and package.get("package_id") == "T13_HE4_SVP_SECOND_SOUND_RESPONSE",
    "human_protocol_card_matches_machine_source_scope": "20.33 m s^-1" in card_text and "blind holdout" in card_text and "Core F0" in card_text and "F0–F8" in card_text,
    "svP_t90_heii_state_explicit": package["material_state"].get("phase") == "He II" and package["material_state"].get("pressure_path") == "saturated vapour pressure" and package["material_state"].get("temperature_scale") == "T90",
    "recommended_second_sound_rows_match_table_4_3": rows_match,
    "local_slope_recomputes_from_rounded_rows": close(slope, -1.9) and close(package["derived_diagnostic"]["value_m_s_per_K"], slope),
    "alpha_theta_and_z_frozen_to_existing_audit": close(frozen["alpha_Phi_K"]["value"], alpha_record["alpha_Phi_K"]) and close(frozen["theta_T_K_per_natural_temperature"]["value"], alpha_record["theta_T_K_per_natural_temperature"]) and close(frozen["Z_Phi_normalized_per_natural_Phi"]["value"], alpha_record["Z_Phi_normalized_per_natural_Phi"]),
    "e0_frozen_to_existing_si_audit": close(frozen["e0_J_m3"]["value"], beta_record["energy_density_scale_J_m3"]),
    "eta_retained_as_external_shear_input": close(frozen["eta_normal_component_Pa_s"]["value"], eta_record["value"]) and frozen["eta_normal_component_Pa_s"]["data_role"] == "EXTERNAL_INPUT_NOT_UET_PREDICTION",
    "independent_observable_not_used_for_matching": package["independence_and_holdout_policy"]["observable_used_to_construct_alpha_Z_theta_or_e0"] is False and package["independence_and_holdout_policy"]["no_rematching_on_response_rows"] is True,
    "source_overlap_and_covariance_limits_are_explicit": "statistical/source independence is not claimed" in package["independence_and_holdout_policy"]["independence_class"] and package["uncertainty_contract"]["covariance"] == "unavailable",
    "row_uncertainty_and_frequency_gap_are_visible": package["uncertainty_contract"]["recommended_row_uncertainty_status"] == "NOT_REPORTED_PER_ROW" and "not specified" in package["observable_contract"]["frequency_or_timescale"],
    "prior_source_exposure_not_mislabeled_blind": package["independence_and_holdout_policy"]["response_rows_examined_during_protocol_design"] is True and package["independence_and_holdout_policy"]["blind_holdout"] is False,
    "no_uet_prediction_or_core_unlock_claimed": package["topic10_interface_requirements"]["current_legacy_state_can_predict_second_sound"] is False and "uet_two_fluid_second_sound_operator_not_admitted" in package["open_blockers"],
    "topic10_j01_scope_remains_a_scoped_no_go": t10.get("status") == "PASS_SCOPED_NO_GO_FOR_LEGACY_ROTATIONAL_FLOW",
    "matching_identity_audit_still_blocks_independent_validation": matching.get("full_core_unlock") is False and matching.get("claim_promotion") is False,
}

input_paths = [PACKAGE_PATH, CARD_PATH, SCRIPT_PATH, ALPHA_PATH, BETA_PATH, ETA_PATH, MATCH_PATH, T10_PATH]
all_passed = all(checks.values())
result = {
    "schema_version": "t13-he4-second-sound-protocol-audit-v1",
    "artifact": "t13_he4_second_sound_response_protocol_audit",
    "generated_on": date.today().isoformat(),
    "status": "PASS_SOURCE_PROTOCOL_CANDIDATE_ONLY" if all_passed else "FAIL_SOURCE_PROTOCOL_CONTRACT",
    "topic": "0.13_Thermodynamic_Bridge",
    "joint_work_package": "J02",
    "closure_level": "PARTIAL",
    "observable": "He-II second-sound phase velocity along the SVP reference path",
    "data_role": package["data_role"],
    "controlling_blocker": package["open_blockers"][0],
    "constants_frozen": True,
    "source_rows_used_for_fit_or_parameter_tuning": False,
    "source_rows_are_blind_holdout": False,
    "uet_dynamic_prediction_emitted": False,
    "recorded_core_status_changed": False,
    "dependency_unlocked": False,
    "claim_promotion": False,
    "derived_diagnostic": {"u2_slope_m_s_per_K": slope, "derived_from_rounded_recommended_rows": True},
    "checks": checks,
    "evidence_hashes": {str(path).replace("\\", "/"): sha256(path) for path in input_paths},
    "open_blockers": package["open_blockers"],
    "next_controller": "Lock a primary resonance row with matching T90/SVP state, frequency, mode geometry and uncertainty; then derive and admit the coupled two-fluid thermal eigenmode under Core F0-F8 before any UET comparison.",
    "claim_boundary": "A source/protocol candidate is checked, not a UET prediction or independent action-to-material validation. The 1998 compilation and prior protocol exposure prevent a blind-holdout claim; no gate or dependency was promoted.",
}

out_path = ROOT / OUT_PATH
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open("w", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
print(json.dumps({"status": result["status"], "passed": sum(checks.values()), "total": len(checks), "artifact": str(OUT_PATH).replace("\\", "/")}, indent=2))
if not all_passed:
    raise SystemExit(1)