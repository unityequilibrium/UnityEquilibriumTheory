"""Audit whether alternate public routes satisfy the Ding C_src contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_ding_alternate_public_dataset_discovery_package.json"
OUT = ROOT / "docs/core/artifacts/t13_ding_alternate_public_dataset_discovery_boundary_audit.json"
DING_AVAILABILITY = ROOT / "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json"
DING_SUPPLEMENTARY = ROOT / "docs/core/artifacts/t13_ding_public_supplementary_payload_boundary_audit.json"
ACCEPTANCE = ROOT / "docs/core/artifacts/t13_independent_csrc_acceptance_contract.json"
HOLDOUT = ROOT / "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def holdout_unconsumed(value: dict) -> bool:
    audit = value.get("audit", {})
    return (
        value.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"
        and audit.get("numeric_payload_consumed") is False
        and audit.get("numeric_rows_consumed") is False
        and audit.get("source_data_payload_observed") is False
        and audit.get("audit_path_read_source_data") is False
        and audit.get("used_for_fit") is False
        and audit.get("used_for_tuning") is False
        and audit.get("used_for_calibration") is False
        and audit.get("used_for_threshold_adjustment") is False
        and audit.get("locked_holdout_remains_unconsumed") is True
    )


def main() -> int:
    package = load(PACKAGE)
    ding_availability = load(DING_AVAILABILITY)
    ding_supplementary = load(DING_SUPPLEMENTARY)
    acceptance = load(ACCEPTANCE)
    holdout = load(HOLDOUT)
    candidates = package.get("candidates", [])
    by_id = {item.get("candidate_id"): item for item in candidates}
    stfc = by_id.get("stfc_isis_99714235", {})
    caltech = by_id.get("caltech_c_axis_graphite_mfp_2016", {})
    nims = by_id.get("nims_mdr_huang_2023_graphite_poiseuille", {})
    stfc_identity = stfc.get("source_identity", {})
    stfc_access = stfc.get("access_route", {})
    stfc_compat = stfc.get("compatibility", {})
    caltech_identity = caltech.get("source_identity", {})
    caltech_access = caltech.get("access_route", {})
    caltech_compat = caltech.get("compatibility", {})
    nims_identity = nims.get("source_identity", {})
    nims_access = nims.get("access_route", {})
    nims_compat = nims.get("compatibility", {})
    import_policy = package.get("import_policy", {})
    registry_search = package.get("repository_registry_search", {})
    registry_queries = registry_search.get("queries", [])
    registry_by_name = {item.get("registry"): item for item in registry_queries}

    checks = {
        "candidate_count_is_three": len(candidates) == 3,
        "stfc_identity_is_public_isis_dataset": (
            stfc_identity.get("doi") == "10.5286/ISIS.E.99714235"
            and stfc_identity.get("license") == "CC-BY-4.0"
            and stfc_access.get("format") == "RAW/Nexus"
        ),
        "stfc_is_nanocomposite_pdos": (
            "Bi2Te3/Graphite nanocomposites" in stfc_identity.get("title", "")
            and stfc_compat.get("observable_matches_mode_resolved_C_src") is False
        ),
        "caltech_identity_is_graphite_mfp_route": (
            caltech_identity.get("doi") == "10.1021/acs.nanolett.5b04499"
            and "Mean Free Path" in caltech_identity.get("title", "")
        ),
        "caltech_is_not_C_src_route": (
            caltech_compat.get("observable_matches_mode_resolved_C_src") is False
            and caltech_compat.get("regime_matches_Ding_TTG_PBTE") is False
        ),
        "nims_identity_is_public_mdr_graphite_route": (
            nims_identity.get("doi") == "10.1038/s41467-023-37380-5"
            and nims_identity.get("repository_locator")
            == "https://mdr.nims.go.jp/datasets/bf141c90-3911-4b2c-9fbc-274dad05d5d0"
            and nims_identity.get("license") == "CC-BY-4.0"
        ),
        "nims_public_record_is_pdf_only_author_request": (
            nims_access.get("format") == "ARTICLE_PDF_ONLY"
            and nims_access.get("data_availability_route")
            == "corresponding authors upon reasonable request"
            and nims_access.get("local_payload_imported") is False
        ),
        "nims_is_not_Ding_C_src_route": (
            nims_compat.get("material_matches_ding_natural_graphite") is False
            and nims_compat.get("observable_matches_mode_resolved_C_src") is False
            and nims_compat.get("regime_matches_Ding_TTG_PBTE") is False
            and nims_compat.get("unitful_C_src_present") is False
        ),
        "all_candidates_fail_C_src_acceptance": all(
            item.get("decision") == "REJECTED_AS_DING_C_SRC_ROUTE"
            and item.get("compatibility", {}).get("mode_resolved_c_src_present") is False
            and item.get("compatibility", {}).get("Ding_mapping_closed") is False
            for item in candidates
        ),
        "no_candidate_payload_imported": all(
            item.get("access_route", {}).get("local_payload_imported") is False
            for item in candidates
        ),
        "no_numeric_rows_imported": import_policy.get("numeric_rows_imported") is False,
        "no_synthetic_replacement_created": import_policy.get("synthetic_replacement_created") is False,
        "no_alpha_fit_performed": import_policy.get("alpha_Phi_K_fit_performed") is False,
        "no_target_curve_fit_performed": import_policy.get("target_curve_fit_performed") is False,
        "ding_public_numeric_input_remains_open": ding_availability.get("controlling_blocker")
        == "ding_pbte_author_data_or_independent_reproduction_package_missing",
        "ding_supplementary_boundary_remains_open": ding_supplementary.get("controlling_blocker")
        == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "acceptance_contract_still_rejects_current_route": acceptance.get("acceptance", {}).get("accepted_for_full_topic13") is False,
        "holdout_is_unconsumed": holdout_unconsumed(holdout),
        "package_holdout_policy_is_locked": all(
            package.get("holdout_policy", {}).get(key) is False
            for key in (
                "xie_2026_accessed",
                "xie_2026_source_data_consumed",
                "used_for_fit",
                "used_for_tuning",
                "used_for_calibration",
                "used_for_threshold_adjustment",
            )
        ),
        "registry_search_has_target_identity": (
            registry_search.get("target_doi") == "10.1038/s41467-021-27907-z"
            and registry_search.get("target_title") == "Observation of second sound in graphite over 200 K"
            and registry_search.get("xie_2026_consumed") is False
        ),
        "datacite_exact_match_is_zero": (
            registry_by_name.get("DataCite", {}).get("exact_target_matches") == 0
            and registry_by_name.get("DataCite", {}).get("result") == "NO_EXACT_DATASET_RECORD"
        ),
        "crossref_has_no_dataset_relation": (
            registry_by_name.get("Crossref", {}).get("article_record_found") is True
            and registry_by_name.get("Crossref", {}).get("dataset_relation_present") is False
        ),
        "zenodo_exact_page_match_is_zero": (
            registry_by_name.get("Zenodo", {}).get("exact_target_matches_in_returned_page") == 0
            and registry_by_name.get("Zenodo", {}).get("scope_note")
        ),
        "figshare_exact_page_match_is_zero": (
            registry_by_name.get("Figshare", {}).get("exact_target_matches_in_returned_page") == 0
        ),
        "dryad_exact_page_match_is_zero": (
            registry_by_name.get("Dryad", {}).get("exact_target_matches_in_returned_page") == 0
        ),
        "registry_search_does_not_overclaim": (
            "author-held data do not exist" in registry_search.get("not_proven", [])
            and "all third-party repositories are empty" in registry_search.get("not_proven", [])
        ),
    }
    status = (
        "PASS_SCOPED_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_NO_GO"
        if all(checks.values())
        else "FAIL_DING_ALTERNATE_PUBLIC_DATASET_BOUNDARY_AUDIT"
    )
    evidence = [
        {"role": "candidate_package", "path": PACKAGE.relative_to(ROOT).as_posix(), "sha256": sha256(PACKAGE)},
        {"role": "ding_numeric_availability", "path": DING_AVAILABILITY.relative_to(ROOT).as_posix(), "sha256": sha256(DING_AVAILABILITY)},
        {"role": "ding_public_supplementary", "path": DING_SUPPLEMENTARY.relative_to(ROOT).as_posix(), "sha256": sha256(DING_SUPPLEMENTARY)},
        {"role": "independent_csrc_acceptance", "path": ACCEPTANCE.relative_to(ROOT).as_posix(), "sha256": sha256(ACCEPTANCE)},
        {"role": "locked_holdout_audit", "path": HOLDOUT.relative_to(ROOT).as_posix(), "sha256": sha256(HOLDOUT)},
        {
            "role": "repository_registry_search_boundary",
            "path": PACKAGE.relative_to(ROOT).as_posix(),
            "sha256": sha256(PACKAGE),
            "summary": package.get("repository_registry_search"),
        },
    ]
    report = {
        "schema_version": "t13-ding-alternate-public-dataset-discovery-boundary-v3",
        "artifact": "t13_ding_alternate_public_dataset_discovery_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": (
                "The current three-route public inventory is bounded: the ISIS route is a "
                "Bi2Te3/Graphite nanocomposite PDOS dataset and the Caltech route is a "
                "graphite c-axis mean-free-path dataset; the NIMS/MDR route is an "
                "article/PDF-only graphite-ribbon record whose numeric BTE inputs remain "
                "available from the corresponding authors. None satisfies the Ding "
                "mode-resolved volumetric C_src(T) acceptance contract."
            ),
            "equation_or_mapping": {
                "required_Ding_bridge": "C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)",
                "measurement_mapping": "y_TTG=Delta_Tq(t)/Delta_Tq(0); y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "Delta_u_ph": "J m^-3",
                "Delta_Tq": "K",
                "normalized_TTG": "dimensionless",
            },
            "derivation_class": "public-source compatibility and availability boundary; no UET derivation",
            "observable": "Ding-compatible mode-resolved volumetric C_src(T)",
            "data_role": "SOURCE_DISCOVERY_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "dependency_unlocked": (
                "Alternate public-route inventory boundary only; no numeric C_src, "
                "alpha_Phi_K, TTG prediction, Full Topic 13, Core, Gravity, or "
                "constitutive transport unlock."
            ),
            "claim_boundary": (
                "This closes only the current source-discovery boundary. It does not "
                "claim that no future source exists, does not import or synthesize "
                "numeric data, and is not Ding validation or Full Topic 13 closure."
            ),
        },
        "candidate_observations": [
            {
                "candidate_id": item.get("candidate_id"),
                "source_identity": item.get("source_identity"),
                "access_route": {
                    "format": item.get("access_route", {}).get("format"),
                    "data_availability_route": item.get("access_route", {}).get("data_availability_route"),
                    "local_payload_imported": item.get("access_route", {}).get("local_payload_imported"),
                },
                "decision": item.get("decision"),
                "compatibility": item.get("compatibility"),
                "local_payload_imported": item.get("access_route", {}).get("local_payload_imported"),
                "remote_payload_hash": item.get("access_route", {}).get("remote_payload_hash"),
            }
            for item in candidates
        ],
        "checks": checks,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": (
            "Obtain an authorized Ding numeric package or a permitted same-regime "
            "PBTE reproduction with mode-resolved C_src(T), SI units, uncertainty, "
            "convergence, and material-state mapping. Keep current public routes as "
            "comparison-only and do not fit alpha_Phi_K."
        ),
        "claim_boundary": (
            "No numeric C_src, alpha_Phi_K, TTG prediction, external validation, "
            "or Full Topic 13 closure is emitted."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT.relative_to(ROOT).as_posix(), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
