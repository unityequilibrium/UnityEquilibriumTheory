"""Reconcile the funding-plan snapshot with this checkout without promoting G0."""

from __future__ import annotations

import hashlib
import json
from math import isclose
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PLAN_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json"
OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_baseline_lineage_audit.json"
J02_SOURCE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_svp_second_sound_response_source_package.json"
CORE_CALIBRATION = ROOT / "docs/core/07_artifacts/topic13/t13_he4_o2_response_calibration_audit.json"
CORE_SI = ROOT / "docs/core/07_artifacts/topic13/t13_he4_o2_si_beta_mapping_audit.json"
CORE_ETA = ROOT / "docs/core/07_artifacts/topic13/t13_he4_normal_viscosity_kubo_audit.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inspect(record: dict) -> dict:
    path = ROOT / record["path"]
    actual = _sha256(path) if path.is_file() else None
    return {
        "path": record["path"],
        "expected_sha256": record["sha256"],
        "current_sha256": actual,
        "state": "MISSING" if actual is None else "MATCH" if actual == record["sha256"] else "DRIFT",
    }


def _j02_review(protocol_path: Path, origin_commit: str) -> dict:
    source = json.loads(J02_SOURCE.read_text(encoding="utf-8"))
    calibration = json.loads(CORE_CALIBRATION.read_text(encoding="utf-8"))["record"]
    si = json.loads(CORE_SI.read_text(encoding="utf-8"))["record"]
    eta = json.loads(CORE_ETA.read_text(encoding="utf-8"))["record"]
    frozen = source["frozen_matching_constants"]
    rows = source["response_rows"]
    close = lambda left, right: isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)
    checks = {
        "protocol_and_package_present": protocol_path.is_file() and J02_SOURCE.is_file(),
        "origin_commit_matches_plan": source["origin_commit"] == origin_commit,
        "source_role_is_nonblind_candidate": (
            source["status"] == "RESPONSE_SOURCE_CANDIDATE_PROTOCOL_OPEN"
            and source["data_role"] == "SOURCE_ANCESTRY_OVERLAP_COMPARATOR_NOT_BLIND_HOLDOUT"
            and source["independence_and_holdout_policy"]["response_rows_examined_during_protocol_design"]
            and not source["independence_and_holdout_policy"]["blind_holdout"]
        ),
        "rows_have_locator_units_and_no_imputed_uncertainty": (
            len(rows) == 4
            and len({row["row_id"] for row in rows}) == 4
            and all(row["table"] == "4.3" and row["row_uncertainty"] is None for row in rows)
            and source["observable_contract"]["units"] == "m s^-1"
            and "Table 4.3" in source["main_reference_source"]["table_locators"][1]
        ),
        "finite_difference_is_only_protocol_diagnostic": (
            close((rows[2]["u2_m_s"] - rows[0]["u2_m_s"]) /
                  (rows[2]["temperature_T90_K"] - rows[0]["temperature_T90_K"]),
                  source["derived_diagnostic"]["value_m_s_per_K"])
            and "not a UET prediction" in source["derived_diagnostic"]["role"]
        ),
        "he4_alpha_and_normalization_match_current_core": (
            close(frozen["alpha_Phi_K"]["value"], calibration["alpha_Phi_K"])
            and close(frozen["alpha_Phi_K"]["uncertainty_bound"],
                      calibration["alpha_uncertainty_K_per_normalized_base_Phi"])
            and close(frozen["theta_T_K_per_natural_temperature"]["value"],
                      calibration["theta_T_K_per_natural_temperature"])
            and close(frozen["Z_Phi_normalized_per_natural_Phi"]["value"],
                      calibration["Z_Phi_normalized_per_natural_Phi"])
            and frozen["alpha_Phi_K"]["role"] == "He-4 frozen calibration interface, not graphite TTG derivation"
        ),
        "si_scale_and_external_shear_match_current_core": (
            close(frozen["e0_J_m3"]["value"], si["energy_density_scale_J_m3"])
            and close(frozen["eta_normal_component_Pa_s"]["value"], eta["value"])
            and frozen["eta_normal_component_Pa_s"]["data_role"] == "EXTERNAL_INPUT_NOT_UET_PREDICTION"
        ),
        "no_uet_two_fluid_operator_or_quantitative_threshold": (
            not source["topic10_interface_requirements"]["current_legacy_state_can_predict_second_sound"]
            and source["uncertainty_contract"]["quantitative_pass_threshold"]
            == "not set until a primary source row, state, frequency and uncertainty budget are locked"
        ),
        "locked_xie_holdout_not_used": not source["independence_and_holdout_policy"]["xie_2026_accessed_by_this_package"],
        "j02_source_ancestry_overlap_disclosed": (
            not source["independence_and_holdout_policy"]["direct_table_4_3_rows_used_to_construct_alpha_Z_theta_or_e0"]
            and source["independence_and_holdout_policy"]["upstream_second_sound_measurement_family_used_for_calibration_source"]
            and "not an independent He-II response test" in source["independence_and_holdout_policy"]["independence_class"]
        ),
    }
    paths = (protocol_path, J02_SOURCE, CORE_CALIBRATION, CORE_SI, CORE_ETA)
    return {
        "status": "PASS_SOURCE_PROTOCOL_CANDIDATE_ONLY" if all(checks.values()) else "REVIEW_REQUIRED",
        "origin_commit": origin_commit,
        "checks": checks,
        "response_row_count": len(rows),
        "row_uncertainty_status": source["uncertainty_contract"]["recommended_row_uncertainty_status"],
        "blind_holdout": False,
        "uet_two_fluid_operator_admitted": False,
        "evidence_artifacts": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)} for path in paths
        ],
        "claim_boundary": "Reviewed J02 source-overlap comparator in this checkout, not an independent/blind He-II test, UET second-sound prediction, primary frequency-matched response row or G0/Core validation.",
    }


def audit() -> dict:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    historical = [_inspect(item) for item in plan["baseline"]["evidence"]]
    pre_sprint = [_inspect(item) for item in plan["pre_sprint_evidence"]["results"]]
    route = _inspect(plan["source_route_screen"])
    protocol = plan["baseline"]["existing_protocol"]
    protocol_path = ROOT / protocol["path"]
    protocol_present = protocol_path.is_file()
    j02 = _j02_review(protocol_path, protocol["commit"]) if protocol_present and J02_SOURCE.is_file() else None
    counts = {state: sum(row["state"] == state for row in historical) for state in ("MATCH", "DRIFT", "MISSING")}
    pre_sprint_reproduced = bool(pre_sprint) and all(row["state"] == "MATCH" for row in pre_sprint)
    source_route_current = route["state"] == "MATCH"
    clean_baseline_revalidated = bool(plan["baseline"]["clean_reproduction_completed"])
    # This screen cannot promote G0; a separate clean Core verifier must do that.
    g0_ready = False
    blockers = []
    if counts["DRIFT"] or counts["MISSING"]:
        blockers.append("historical_dirty_branch_evidence_requires_clean_equivalent_selection")
    if not clean_baseline_revalidated:
        blockers.append("full_clean_core_baseline_not_revalidated")
    if j02 is None or j02["status"] != "PASS_SOURCE_PROTOCOL_CANDIDATE_ONLY":
        blockers.append("j02_protocol_not_present_in_clean_checkout")
    return {
        "schema_version": "t13-funding-baseline-lineage-v1",
        "major_result_id": "T13_FUNDING_CLEAN_BASELINE_LINEAGE_SCREEN",
        "topic": "0.13",
        "closure_level": "PARTIAL",
        "what_is_closed": "Historical versus current-checkout identity is classified for each planned baseline input; saved pre-sprint evidence and the imported J02 source/protocol candidate are reviewed separately",
        "equation_or_mapping": "source identity is path plus SHA-256; a passing local audit is not a physical mapping",
        "units": "not applicable to source identity",
        "derivation_class": "deterministic file-identity reconciliation",
        "observable": "reproducibility of the proposed funding baseline in this checkout",
        "data_role": "PROVENANCE_AUDIT_NOT_PHYSICAL_VALIDATION",
        "historical_snapshot": {"branch": plan["baseline"]["branch"], "head": plan["baseline"]["head"],
                                "dirty_worktree": plan["baseline"]["dirty_worktree"],
                                "evidence": historical, "counts": counts,
                                "hashes_are_historical_not_required_to_equal_selected_clean_equivalents": True},
        "pre_sprint_saved_evidence": {"records": pre_sprint, "all_match": pre_sprint_reproduced},
        "source_route_screen": {"record": route, "numeric_rows_admitted": plan["source_route_screen"]["numeric_response_rows_admitted"],
                                 "current": source_route_current},
        "referenced_j02_protocol": {"commit": protocol["commit"], "path": protocol["path"],
                                    "present_in_this_checkout": protocol_present},
        "j02_dependency_review": j02,
        "clean_core_baseline_revalidated": clean_baseline_revalidated,
        "g0_evaluation_authority": "separate hash-backed clean Core baseline verifier; not this identity screen, J02 source review or a planning Boolean",
        "g0_baseline_ready": g0_ready,
        "g0_status": "BLOCKED_LINEAGE_RECONCILIATION",
        "verification_status": "PASS_IDENTITY_SCREEN_WITH_OPEN_G0" if pre_sprint_reproduced and source_route_current else "REVIEW_REQUIRED",
        "evidence_artifacts": [
            {"path": PLAN_PATH.relative_to(ROOT).as_posix(), "sha256": _sha256(PLAN_PATH)},
            {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": _sha256(Path(__file__).resolve())},
            {"path": Path(__file__).with_name("test_t13_funding_baseline_lineage.py").relative_to(ROOT).as_posix(),
             "sha256": _sha256(Path(__file__).with_name("test_t13_funding_baseline_lineage.py"))},
        ],
        "open_blockers": blockers,
        "controlling_blocker": "full_clean_core_baseline_not_revalidated",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "Five pre-sprint saved artifacts and the reviewed J02 source/protocol candidate do not establish clean reproduction of the older Core baseline or an admitted two-fluid operator. G0 remains open; no Xie 2026 access, physical prediction, external validation or Full Topic 13 closure is asserted.",
    }


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
