"""Audit and prioritize Topic 13 C_src source routes.

This audit is a source-acquisition decision artifact, not a data generator. It
records coverage against the independent C_src acceptance contract and keeps
every currently captured route fail-closed for Full Topic 13.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_csrc_source_route_priority_audit.json"
ACCEPTANCE = ROOT / "docs/core/artifacts/t13_independent_csrc_acceptance_contract.json"

REQUIRED_FIELDS = (
    "source_identity_and_locator",
    "raw_numeric_or_reproduction_payload",
    "source_hash",
    "material_identity_morphology_isotope_defect_state",
    "temperature_and_state",
    "PBTE_mode_resolved_response_contract",
    "C_src_rows_with_J_m^-3_K^-1_units",
    "uncertainty_and_preprocessing",
    "mesh_or_numerical_convergence",
    "independence_statement",
    "holdout_and_fit_audit",
)


def spec(
    route_id: str,
    priority: int,
    route_class: str,
    label: str,
    package: str,
    audit: str,
    package_status: str,
    audit_status: str,
    current_state: str,
    present_fields: tuple[str, ...],
    basis: dict[str, str],
    true_checks: tuple[str, ...],
    false_checks: tuple[str, ...],
    decision: str,
    rejection_reasons: tuple[str, ...],
    next_action: str,
) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "priority": priority,
        "route_class": route_class,
        "label": label,
        "package": package,
        "audit": audit,
        "expected_package_status": package_status,
        "expected_audit_status": audit_status,
        "current_state": current_state,
        "present_fields": set(present_fields),
        "basis": basis,
        "true_checks": true_checks,
        "false_checks": false_checks,
        "decision": decision,
        "rejection_reasons": rejection_reasons,
        "next_action": next_action,
    }


ROUTE_SPECS: tuple[dict[str, Any], ...] = (
    spec(
        "ding_author_payload",
        1,
        "DIRECT_AUTHOR_PAYLOAD",
        "Ding corresponding-author numeric payload",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_author_request_manifest.json",
        "docs/core/artifacts/t13_ding_pbte_author_request_audit.json",
        "REQUEST_PACKAGE_READY_NOT_SENT",
        "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE",
        "REQUEST_PACKAGE_READY_NOT_SENT",
        ("source_identity_and_locator", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The request manifest locks the Ding DOI/PMCID and corresponding-author route.",
            "holdout_and_fit_audit": "The request audit excludes target fitting, alpha fitting, and Xie 2026 access.",
        },
        ("manifest_not_sent", "author_route_is_open_not_executed", "no_xie_access", "no_numeric_alpha_claim"),
        (),
        "BLOCKED_EXTERNAL_INPUT_NOT_RECEIVED",
        (
            "request has not been sent or answered",
            "numeric mode rows, C_src rows, and payload hash are not present",
            "material/state, uncertainty, convergence, and independence records are not delivered",
        ),
        "Obtain project authorization, send the bounded request, then transition to REQUEST_PAYLOAD_RECEIVED_PENDING_AUDIT only after a response is archived and hashed.",
    ),
    spec(
        "ding_public_oa",
        2,
        "PUBLIC_SOURCE_BOUNDARY",
        "Ding official PMC OA distribution",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_numeric_input_availability_package.json",
        "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json",
        "OFFICIAL_OA_INVENTORY_LOCKED_REPRODUCTION_INPUTS_ABSENT",
        "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO",
        "PUBLIC_OA_ROUTE_CLOSED_NO_NUMERIC_REPRODUCTION_PAYLOAD",
        ("source_identity_and_locator", "source_hash", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The official OA package records article identity, OA locator, and data-availability statement.",
            "source_hash": "Captured OA objects are archived with size/hash identity.",
            "holdout_and_fit_audit": "The OA audit records no Xie access, no holdout consumption, and no executed author request.",
        },
        ("no_reproduction_payload_candidate_in_oa_prefix", "author_request_not_claimed_executed", "xie_holdout_not_accessed", "xie_holdout_not_consumed"),
        (),
        "CLOSED_PUBLIC_ROUTE_NO_PAYLOAD",
        (
            "captured OA distribution contains figures/PDFs but no mode-resolved numeric C_src or reproducible PBTE payload",
            "the publisher routes supporting data to the corresponding author on reasonable request",
        ),
        "Stop searching the same OA prefix; use the authorized author route or a separately accepted same-regime reproduction.",
    ),
    spec(
        "calorine_zenodo_pbte",
        3,
        "INDEPENDENT_PBTE_REPRODUCTION_CANDIDATE",
        "Calorine/Zenodo NEP-RTA PBTE candidate",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_nep_bte_reproduction_source_package.json",
        "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json",
        "PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION",
        "PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION",
        "NUMERIC_C_SRC_CANDIDATE_NOT_DING_ACCEPTED",
        ("source_identity_and_locator", "raw_numeric_or_reproduction_payload", "source_hash", "temperature_and_state", "PBTE_mode_resolved_response_contract", "C_src_rows_with_J_m^-3_K^-1_units", "mesh_or_numerical_convergence", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "Zenodo input locators and local source hashes are recorded.",
            "raw_numeric_or_reproduction_payload": "Force constants, kappa payloads, and candidate C_src summaries are archived.",
            "source_hash": "The audit checks source hashes and archived payload identity.",
            "temperature_and_state": "Temperatures and a periodic primitive-crystal state are declared; equivalence to Ding remains separate.",
            "PBTE_mode_resolved_response_contract": "The candidate records mode heat capacity and RTA PBTE response inputs.",
            "C_src_rows_with_J_m^-3_K^-1_units": "Candidate rows are emitted in J m^-3 K^-1.",
            "mesh_or_numerical_convergence": "The latest adjacent q-mesh preflight passes at the declared tolerance.",
            "holdout_and_fit_audit": "Target-curve use, fit, alpha fit, and holdout access are false in the audit.",
        },
        ("source_locators_present", "source_hashes_recorded", "archived_force_constant_payload_present", "archived_kappa_payloads_present", "latest_mesh_pair_preflight_pass"),
        ("target_curve_used", "fit_performed", "alpha_Phi_K_fit_performed", "holdout_accessed"),
        "CANDIDATE_REJECTED_DING_MATERIAL_AND_SOURCE_GRADE_UNCERTAINTY",
        (
            "material/state equivalence to the Ding natural-graphite TTG regime is not established",
            "source-grade statistical/systematic uncertainty is absent",
            "an explicit independent acceptance statement for Ding equivalence is not present",
        ),
        "Do not rerun unchanged meshes. Either obtain Ding state evidence and source-grade uncertainty, or replace this route with a qualifying same-regime PBTE reproduction.",
    ),
    spec(
        "calorine_legacy_nep2_pbte",
        4,
        "INDEPENDENT_PBTE_REPRODUCTION_CANDIDATE",
        "Calorine legacy NEP2-compatible PBTE candidate",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/calorine_legacy_nep2_pbte_reproduction_source_package.json",
        "docs/core/artifacts/t13_calorine_legacy_nep2_pbte_reproduction_audit.json",
        "PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION",
        "PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION",
        "NUMERIC_C_SRC_CANDIDATE_NOT_DING_ACCEPTED",
        ("source_identity_and_locator", "raw_numeric_or_reproduction_payload", "source_hash", "temperature_and_state", "PBTE_mode_resolved_response_contract", "C_src_rows_with_J_m^-3_K^-1_units", "mesh_or_numerical_convergence", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The source package records public structure/potential locators and local hashes.",
            "raw_numeric_or_reproduction_payload": "Archived force constants, q-mesh summaries, and candidate C_src rows are present.",
            "source_hash": "The audit checks source, wrapper, force-constant, and reproduction hashes.",
            "temperature_and_state": "A fixed C-CX primitive-crystal state and temperature grid are declared; Ding equivalence remains open.",
            "PBTE_mode_resolved_response_contract": "The reproduction uses the declared mode response and RTA PBTE route.",
            "C_src_rows_with_J_m^-3_K^-1_units": "Candidate C_src rows are explicitly stored in J m^-3 K^-1.",
            "mesh_or_numerical_convergence": "The latest adjacent q-mesh preflight passes at the declared tolerance.",
            "holdout_and_fit_audit": "The audit records no fit, target tuning, alpha fit, or holdout access.",
        },
        ("structure_source_hash_matches", "potential_source_hash_matches", "force_constant_payloads_present", "mesh_pair_preflight_pass", "no_fit_target_or_holdout"),
        (),
        "CANDIDATE_REJECTED_DING_MATERIAL_AND_SOURCE_GRADE_UNCERTAINTY",
        (
            "material/state equivalence to the Ding natural-graphite TTG regime is not established",
            "source-grade uncertainty remains open for model form, material state, density, and c_v",
            "the candidate is not a substitute for an authorized Ding source without acceptance evidence",
        ),
        "Keep as a bounded comparator; do not rerun unchanged meshes. Obtain a source-grade uncertainty package and same-regime mapping or use the authorized Ding route.",
    ),
    spec(
        "mp48_harmonic_comparator",
        5,
        "HARMONIC_COMPARATOR",
        "Materials Project MP48 harmonic graphite comparator",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json",
        "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json",
        "SOURCE_LOCKED_INDEPENDENT_HARMONIC_CV_COMPARATOR",
        "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE",
        "HARMONIC_CV_COMPARATOR_NOT_PBTE_ACCEPTED",
        ("source_identity_and_locator", "raw_numeric_or_reproduction_payload", "source_hash", "temperature_and_state", "mesh_or_numerical_convergence", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The Materials Project/Zenodo identity and local archive route are recorded.",
            "raw_numeric_or_reproduction_payload": "Second-order force constants and harmonic c_v rows are archived.",
            "source_hash": "The source and extracted input hashes are checked.",
            "temperature_and_state": "The MP48 harmonic crystal state and temperature grid are declared, but not Ding-equivalent.",
            "mesh_or_numerical_convergence": "The independent harmonic mesh-tail diagnostic is source-traceable.",
            "holdout_and_fit_audit": "The audit excludes holdout access, target fitting, and alpha fitting.",
        },
        ("mp-48/FORCE_CONSTANTS.gz_present", "mp-48/phonopy.yaml.gz_present", "mp-48/summary.json.gz_present", "mp-48/thermal_properties.yaml.gz_present", "janaf_envelope_matches", "holdout_not_accessed", "target_curve_not_used", "alpha_fit_not_used"),
        (),
        "COMPARATOR_REJECTED_HARMONIC_NOT_DING_PBTE",
        (
            "harmonic c_v is not a Ding PBTE mode-resolved response contract",
            "Ding material/state equivalence and source-grade uncertainty are not established",
            "the route cannot supply an independent alpha_Phi_K calibration",
        ),
        "Keep as a standard harmonic comparator only; do not promote it to Ding C_src or use it for alpha calibration.",
    ),
    spec(
        "nims_mp990448",
        6,
        "PUBLIC_SOURCE_BOUNDARY",
        "NIMS MP-990448 graphite phonon archive",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/nims_mdr_mp990448_phonon_source_package.json",
        "docs/core/artifacts/t13_nims_mp990448_phonon_source_boundary_audit.json",
        "PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY",
        "PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY",
        "ARCHIVE_BOUNDARY_NO_MACHINE_READABLE_C_SRC",
        ("source_identity_and_locator", "source_hash", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The NIMS collection, dataset, and material identity are source-locked.",
            "source_hash": "The downloaded archive and members have SHA-256 identity.",
            "holdout_and_fit_audit": "The boundary audit records no holdout access and no claim promotion.",
        },
        ("archive_exists", "archive_hash_matches_locked_download", "no_force_constants_data", "no_frequency_mesh", "no_machine_readable_thermal_rows", "no_holdout_access"),
        (),
        "CLOSED_PUBLIC_ROUTE_NO_MACHINE_READABLE_PAYLOAD",
        (
            "archive contains figures and setup files but no force-constant data, frequency mesh, or machine-readable thermal rows",
            "no Ding PBTE response, C_src uncertainty, or material/state acceptance package is available from this archive",
        ),
        "Do not digitize the thermal figure for C_src acceptance; obtain a permitted raw force-constant package or use the author/same-regime route.",
    ),
    spec(
        "huang_2023_nims",
        7,
        "PUBLIC_SOURCE_BOUNDARY",
        "Huang 2023 NIMS graphite-ribbon archive",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/huang_2023_nims_mdr_payload_source_package.json",
        "docs/core/artifacts/t13_huang_2023_nims_mdr_payload_boundary_audit.json",
        "PASS_SCOPED_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY",
        "PASS_SCOPED_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY",
        "ARTICLE_ONLY_PUBLIC_ARCHIVE",
        ("source_identity_and_locator", "source_hash", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The article, DOI, NIMS dataset, and license are recorded.",
            "source_hash": "The public NIMS archive and PDF member are hash-locked.",
            "holdout_and_fit_audit": "The boundary audit records no holdout access and no claim promotion.",
        },
        ("archive_exists", "archive_hash_matches_locked_download", "single_pdf_member", "no_force_constant_files", "no_shengbte_payload", "no_numeric_csrc_rows", "no_holdout_access"),
        (),
        "CLOSED_PUBLIC_ROUTE_ARTICLE_ONLY",
        (
            "the public NIMS ZIP contains only the article PDF",
            "no force constants, ShengBTE payload, numeric C_src rows, or uncertainty package are present",
        ),
        "Keep as a provenance boundary; do not use the PDF or figure as C_src data. Obtain an authorized numeric package or accepted same-regime reproduction.",
    ),
    spec(
        "huberman_2019_public_pbte",
        8,
        "PUBLIC_SOURCE_BOUNDARY",
        "Huberman 2019 public PBTE source",
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/huberman_2019_ttg_source_boundary_package.json",
        "docs/core/artifacts/t13_huberman_2019_public_pbte_boundary_audit.json",
        "PUBLIC_FORMULA_AND_SETUP_ONLY_NUMERIC_PAYLOAD_OPEN",
        "PASS_HUBERMAN_PUBLIC_PBTE_BOUNDARY_NO_ACCEPTED_NUMERIC_PAYLOAD",
        "PUBLIC_FORMULA_AND_SETUP_ONLY",
        ("source_identity_and_locator", "source_hash", "holdout_and_fit_audit"),
        {
            "source_identity_and_locator": "The public arXiv/PDF identity and source locators are locked.",
            "source_hash": "The public PDF is locally hash-locked.",
            "holdout_and_fit_audit": "The source boundary audit excludes digitization, fit, alpha fitting, and holdout access.",
        },
        ("source_file_present", "sha256_matches_downloaded_source", "public_package_inventory_contains_only_pdf", "no_machine_readable_mode_resolved_csrc_or_force_constant_payload", "no_curve_digitization_performed", "holdout_not_accessed", "target_fit_not_performed", "alpha_phi_k_fit_not_performed"),
        (),
        "CLOSED_PUBLIC_ROUTE_NO_MACHINE_READABLE_PAYLOAD",
        (
            "the public package contains formula/setup context but no machine-readable mode-resolved C_src or force-constant payload",
            "printed values and figures cannot satisfy the independent C_src acceptance contract",
        ),
        "Keep as a method/comparator boundary; obtain an authorized Ding payload or accepted same-regime PBTE reproduction.",
    ),
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def reference(path: Path, role: str) -> dict[str, Any]:
    return {
        "path": relative(path),
        "role": role,
        "sha256": digest(path) if path.is_file() else None,
    }


def policy_passes(audit: dict[str, Any], route: dict[str, Any]) -> bool:
    checks = audit.get("checks", {})
    return all(checks.get(key) is True for key in route["true_checks"]) and all(
        checks.get(key) is False for key in route["false_checks"]
    )


def build_route(route: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    package_path = ROOT / route["package"]
    audit_path = ROOT / route["audit"]
    package = load(package_path) if package_path.is_file() else {}
    audit = load(audit_path) if audit_path.is_file() else {}
    coverage = {
        field: {
            "status": "PRESENT" if field in route["present_fields"] else "MISSING",
            "basis": route["basis"].get(field, "The required field is not present for this route under the current acceptance contract."),
        }
        for field in REQUIRED_FIELDS
    }
    checks = {
        "package_present": package_path.is_file(),
        "audit_present": audit_path.is_file(),
        "package_status_matches": package.get("status") == route["expected_package_status"],
        "audit_status_matches": audit.get("status") == route["expected_audit_status"],
        "coverage_keys_exact": set(coverage) == set(REQUIRED_FIELDS),
        "policy_checks_pass": policy_passes(audit, route),
        "accepted_for_full_topic13_is_false": audit.get("acceptance_for_full_topic13") is not True,
        "claim_promotion_is_false": audit.get("claim_promotion") is not True,
    }
    return (
        {
            "route_id": route["route_id"],
            "priority": route["priority"],
            "route_class": route["route_class"],
            "label": route["label"],
            "current_state": route["current_state"],
            "source_package": reference(package_path, "source package or request manifest"),
            "audit_artifact": reference(audit_path, "route qualification audit"),
            "package_status": package.get("status"),
            "audit_status": audit.get("status"),
            "field_coverage": coverage,
            "field_coverage_count": sum(item["status"] == "PRESENT" for item in coverage.values()),
            "required_field_count": len(REQUIRED_FIELDS),
            "acceptance_decision": route["decision"],
            "accepted_for_full_topic13": False,
            "rejection_reasons": list(route["rejection_reasons"]),
            "next_action": route["next_action"],
            "holdout_policy": {
                "xie_2026_accessed": False,
                "target_curve_used": False,
                "fit_or_tuning_used": False,
            },
            "verification": {
                "source_audit_checks_pass": policy_passes(audit, route),
                "claim_promotion": False,
            },
        },
        checks,
    )


def main() -> int:
    acceptance = load(ACCEPTANCE)
    routes: list[dict[str, Any]] = []
    route_checks: dict[str, dict[str, bool]] = {}
    for route_spec in ROUTE_SPECS:
        route, checks = build_route(route_spec)
        routes.append(route)
        route_checks[route_spec["route_id"]] = checks

    global_checks = {
        "acceptance_required_fields_match": acceptance.get("acceptance_contract", {}).get("required_fields") == list(REQUIRED_FIELDS),
        "route_priorities_are_unique_and_ordered": [route["priority"] for route in routes] == list(range(1, len(routes) + 1)),
        "all_route_checks_pass": all(all(checks.values()) for checks in route_checks.values()),
        "all_routes_fail_closed_for_full_topic13": all(route["accepted_for_full_topic13"] is False for route in routes),
        "numeric_csrc_candidates_are_explicit": {
            route["route_id"] for route in routes if route["field_coverage"]["C_src_rows_with_J_m^-3_K^-1_units"]["status"] == "PRESENT"
        } == {"calorine_zenodo_pbte", "calorine_legacy_nep2_pbte"},
        "numeric_candidates_retain_material_and_uncertainty_gaps": all(
            route["field_coverage"]["material_identity_morphology_isotope_defect_state"]["status"] == "MISSING"
            and route["field_coverage"]["uncertainty_and_preprocessing"]["status"] == "MISSING"
            for route in routes if route["route_id"] in {"calorine_zenodo_pbte", "calorine_legacy_nep2_pbte"}
        ),
        "public_routes_have_no_numeric_csrc": all(
            route["field_coverage"]["C_src_rows_with_J_m^-3_K^-1_units"]["status"] == "MISSING"
            for route in routes if route["route_class"] == "PUBLIC_SOURCE_BOUNDARY"
        ),
        "holdout_is_unconsumed_for_every_route": all(
            route["holdout_policy"] == {"xie_2026_accessed": False, "target_curve_used": False, "fit_or_tuning_used": False}
            for route in routes
        ),
        "no_synthetic_replacement_is_declared": all("synthetic" not in route["current_state"].lower() for route in routes),
    }
    passed = all(global_checks.values())
    status = "PASS_SCOPED_C_SRC_SOURCE_ROUTE_PRIORITY_NO_ACCEPTED_ROUTE" if passed else "FAIL_T13_C_SRC_SOURCE_ROUTE_PRIORITY_AUDIT"
    source_refs = []
    for route in routes:
        source_refs.extend([route["source_package"], route["audit_artifact"]])
    report = {
        "schema_version": "t13-csrc-source-route-priority-v1",
        "artifact": "t13_csrc_source_route_priority_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_C_SRC_SOURCE_ROUTE_PRIORITY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "The current C_src source routes are ranked against the exact independent acceptance contract.",
                "The direct Ding author route is selected as priority 1 and is explicitly not sent or treated as received.",
                "Numeric Calorine candidates are separated from Ding acceptance because material/state equivalence and source-grade uncertainty are missing.",
                "Public OA, NIMS, Huang, and Huberman routes are bounded as non-productive for accepted numeric C_src under their captured payloads.",
                "The next action is an external input change or a genuinely qualifying same-regime reproduction, not another unchanged gate rerun.",
            ],
            "equation_or_mapping": {
                "source_response": "C_src(T) = sum_mu c_mu(T)",
                "temperature_response": "Delta_Tq = Delta_u_ph / C_src(T)",
                "acceptance_rule": "accepted_C_src_route := every required field present + material/state equivalence + source-grade uncertainty + holdout/fit audit",
            },
            "units": {"C_src": "J m^-3 K^-1", "Delta_u_ph": "J m^-3", "Delta_Tq": "K", "temperature": "K"},
            "derivation_class": "source provenance route-priority and acceptance-coverage audit; no UET derivation",
            "observable": "eligibility of source routes for Ding-compatible mode-resolved C_src(T)",
            "data_role": "SOURCE_ACQUISITION_DECISION_NOT_CALIBRATION",
            "evidence_artifacts": [reference(ACCEPTANCE, "independent C_src acceptance contract"), *source_refs],
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "c_v_source_uncertainty_not_closed",
            ],
            "dependency_unlocked": "Source-route decision and acquisition priority only; no numeric Ding C_src, alpha_Phi_K, physical transport, Core, Gravity, or Galaxy unlock.",
            "claim_boundary": "This closes a source-acquisition decision lane only. It does not accept a C_src route, create data, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
        },
        "acceptance_contract": {"path": relative(ACCEPTANCE), "sha256": digest(ACCEPTANCE), "required_fields": list(REQUIRED_FIELDS)},
        "routes": routes,
        "priority_decision": {
            "selected_route_id": "ding_author_payload",
            "selected_route_priority": 1,
            "selection_reason": "Only the direct author route can supply the missing Ding-specific numeric payload without silently substituting a different material/model state.",
            "fallback_route_id": "same_regime_pbte_reproduction_not_yet_identified",
            "fallback_acceptance": "A fallback must satisfy all 11 required fields and pass the existing material, uncertainty, holdout, and fit gates.",
            "rerun_policy": "Do not rerun unchanged numeric gates; rerun after an accepted source, permissioned payload, or independent derivation changes the input hash.",
        },
        "checks": global_checks,
        "route_checks": route_checks,
        "what_changed": "Ranked and field-audited all currently captured C_src source routes without importing or synthesizing a numeric replacement.",
        "verification": "Every route package and audit is hash-referenced; expected statuses, field coverage, policy checks, fail-closed acceptance, and holdout exclusion are machine-checked.",
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_action": "Obtain authorization to send the prepared Ding request, or obtain a genuinely same-regime PBTE reproduction. Do not infer C_src from normalized TTG rows, incident fluence, comparator c_v, or an unchanged rerun.",
        "claim_boundary": "C_src source-route prioritization only; no numeric Ding C_src, no alpha_Phi_K calibration, no prediction, no external validation, no Core closure, and no global UET closure.",
        "holdout_policy": {"xie_2026_accessed": False, "calibration_path_may_read_holdout": False, "target_curve_used": False, "fit_or_tuning_used": False},
        "claim_promotion": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": relative(OUT), "route_count": len(routes), "required_field_count": len(REQUIRED_FIELDS), "numeric_csrc_candidate_count": 2, "accepted_route_count": 0}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
