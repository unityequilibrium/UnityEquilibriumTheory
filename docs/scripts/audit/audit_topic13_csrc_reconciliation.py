"""Reconcile Topic 13 C_src routes without accepting unmatched candidates."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/artifacts/t13_csrc_reconciliation_audit.json"
EVIDENCE = {
    "ding_oa": ROOT / "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json",
    "ding_request": ROOT / "docs/core/artifacts/t13_ding_pbte_author_request_audit.json",
    "public_screening": ROOT / "docs/core/artifacts/t13_public_phonon_route_screening_audit.json",
    "huberman": ROOT / "docs/core/artifacts/t13_huberman_2019_public_pbte_boundary_audit.json",
    "calorine_boundary": ROOT / "docs/core/artifacts/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json",
    "calorine_numeric": ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_nep_bte_reproduction_source_package.json",
    "mp48_spectral": ROOT / "docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json",
    "mp48_mapping": ROOT / "docs/core/artifacts/t13_mp48_ding_csrc_response_mapping_audit.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(key: str, role: str) -> dict:
    path = EVIDENCE[key]
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "role": role,
    }


def candidate(
    candidate_id: str,
    key: str,
    role: str,
    candidate_class: str,
    numeric_csrc: bool,
    source_grade_uncertainty: bool,
    ding_material_match: bool,
    accepted: bool,
    reason: str,
    blocker: str,
    **extra: object,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "artifact": ref(key, role),
        "candidate_class": candidate_class,
        "numeric_csrc_present": numeric_csrc,
        "source_grade_uncertainty_present": source_grade_uncertainty,
        "ding_material_state_match": ding_material_match,
        "accepted_for_independent_csrc": accepted,
        "eligible_for_full_topic13": accepted,
        "reason": reason,
        "controlling_blocker": blocker,
        **extra,
    }


def main() -> int:
    sources = {key: load(path) for key, path in EVIDENCE.items()}
    ding_oa = sources["ding_oa"]
    ding_request = sources["ding_request"]
    public = sources["public_screening"]
    huberman = sources["huberman"]
    calorine_boundary = sources["calorine_boundary"]
    calorine = sources["calorine_numeric"]
    mp48_spectral = sources["mp48_spectral"]
    mp48_mapping = sources["mp48_mapping"]

    candidates = [
        candidate(
            "ding_official_oa_inventory", "ding_oa", "official Ding OA payload availability boundary",
            "DING_PUBLIC_NO_PAYLOAD", False, False, False, False,
            "The captured official OA distribution contains article/supplementary objects but no mode-resolved C_src payload.",
            "ding_pbte_author_data_or_independent_reproduction_package_missing",
            author_request_route=ding_oa.get("checks", {}).get("data_availability_is_author_request"),
        ),
        candidate(
            "ding_author_request_not_received", "ding_request", "bounded corresponding-author acquisition package",
            "DING_REQUEST_SPECIFICATION", False, False, False, False,
            "The request schema is complete, but no permissioned response or numeric payload has been received.",
            "author_data_or_independent_reproduction_payload_not_received",
            request_executed=not ding_request.get("checks", {}).get("manifest_not_sent", True),
        ),
        candidate(
            "public_phonon_route_screening", "public_screening", "public phonon route screening boundary",
            "PUBLIC_ROUTE_NO_CORE_PAYLOAD", False, False, False, False,
            "Materials Project, LCBOPII, and Dryad routes provide metadata or method context only; no accepted C_src payload was imported.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            route_count=3,
        ),
        candidate(
            "huberman_public_pbte", "huberman", "Huberman public PBTE formula/setup boundary",
            "PUBLIC_FORMULA_ONLY", False, False, False, False,
            "The public route provides PBTE equations and setup, but no machine-readable mode C_src, force constants, or uncertainty rows.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ),
        candidate(
            "calorine_candidate_route_boundary", "calorine_boundary", "Calorine public candidate-route boundary",
            "CANDIDATE_ROUTE_NO_DEPOSITED_ROWS", False, False, False, False,
            "The tutorial route identifies inputs and an RTA workflow but does not deposit accepted mode-resolved C_src rows or source-grade uncertainty.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ),
        candidate(
            "calorine_numeric_reproduction", "calorine_numeric", "Calorine/Zenodo numeric PBTE candidate reproduction",
            "NUMERIC_INDEPENDENT_CANDIDATE", True, False, False, False,
            "Numeric volumetric C_src rows and mesh convergence exist, but the periodic NEP/RTA graphite state is not Ding-equivalent and has no source-grade uncertainty.",
            "calorine_route_material_regime_mapping_to_ding_missing",
            latest_mesh_pair_pass=calorine.get("checks", {}).get("latest_mesh_pair_preflight_pass"),
            acceptance_for_full_topic13=calorine.get("acceptance_for_full_topic13"),
        ),
        candidate(
            "mp48_spectral_csrc", "mp48_spectral", "MP48 harmonic spectral C_src-like reproduction",
            "NUMERIC_HARMONIC_COMPARATOR", True, False, False, False,
            "The DOS integration reproduces harmonic heat capacity in volumetric units, but it is not Ding PBTE and lacks source-grade uncertainty/material equivalence.",
            "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing",
            cross_file_reproduction=mp48_spectral.get("checks", {}).get("cross_file_reproduction_rows_present"),
        ),
        candidate(
            "mp48_ding_mode_sum_mapping", "mp48_mapping", "MP48-to-Ding standard mode-sum response mapping",
            "NUMERIC_STANDARD_MAPPING_COMPARATOR", True, False, False, False,
            "The mode-sum identity and unit conversion are explicit, but the route remains a standard harmonic comparator rather than Ding PBTE acceptance.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            mapping_scope=mp48_mapping.get("major_result", {}).get("claim_boundary"),
        ),
    ]

    checks = {
        "all_evidence_files_present": all(path.is_file() for path in EVIDENCE.values()),
        "ding_oa_no_payload": ding_oa.get("checks", {}).get("no_reproduction_payload_candidate_in_oa_prefix") is True
        and ding_oa.get("checks", {}).get("xie_holdout_not_consumed") is True,
        "ding_request_not_received": ding_request.get("checks", {}).get("manifest_not_sent") is True
        and ding_request.get("checks", {}).get("no_numeric_alpha_claim") is True,
        "public_screening_no_core_payload": public.get("checks", {}).get("no_core_payload_imported") is True
        and public.get("checks", {}).get("no_numeric_C_src_emitted") is True,
        "huberman_no_numeric_payload": huberman.get("checks", {}).get("no_machine_readable_mode_resolved_csrc_or_force_constant_payload") is True,
        "calorine_boundary_not_promoted": calorine_boundary.get("checks", {}).get("deposited_csrc_payload_present") is False
        and calorine_boundary.get("checks", {}).get("material_regime_mapping_present") is False,
        "calorine_numeric_candidate_not_accepted": calorine.get("acceptance_for_full_topic13") is False
        and calorine.get("checks", {}).get("source_grade_uncertainty_present") is False
        and calorine.get("checks", {}).get("material_state_match_to_ding") is False,
        "mp48_spectral_not_ding_promoted": mp48_spectral.get("checks", {}).get("holdout_not_accessed") is True
        and mp48_spectral.get("checks", {}).get("alpha_fit_not_performed") is True,
        "mp48_mapping_not_ding_promoted": mp48_mapping.get("checks", {}).get("route_wide_convergence_is_not_silently_promoted") is True
        and mp48_mapping.get("checks", {}).get("numeric_alpha_Phi_K_not_emitted") is True,
        "no_accepted_csrc_candidate": all(
            not item["accepted_for_independent_csrc"]
            and not item["eligible_for_full_topic13"]
            for item in candidates
        ),
        "holdout_is_clean": all(
            not source.get("holdout_accessed", False)
            and not source.get("xie_2026_accessed", False)
            for source in sources.values()
        ),
    }
    summary = {
        "route_count": len(candidates),
        "numeric_csrc_candidate_count": sum(item["numeric_csrc_present"] for item in candidates),
        "source_grade_uncertainty_count": sum(item["source_grade_uncertainty_present"] for item in candidates),
        "ding_material_state_match_count": sum(item["ding_material_state_match"] for item in candidates),
        "ding_author_payload_count": 0,
        "accepted_independent_reproduction_count": sum(item["accepted_for_independent_csrc"] for item in candidates),
        "accepted_ding_csrc_count": 0,
        "accepted_for_full_topic13_count": sum(item["eligible_for_full_topic13"] for item in candidates),
    }
    passed = all(checks.values()) and summary["accepted_for_full_topic13_count"] == 0
    status = "PASS_SCOPED_CSRC_RECONCILIATION_OPEN" if passed else "FAIL_T13_CSRC_RECONCILIATION"
    artifact = {
        "schema_version": "t13-csrc-reconciliation-v1",
        "artifact": "t13_csrc_reconciliation_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CSRC_SOURCE_RECONCILIATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "Ding official OA, author-request, public phonon, Huberman, Calorine, and MP48 C_src routes are classified by payload and acceptance state",
                "numeric C_src-like candidates are separated from Ding-compatible accepted C_src",
                "material-state equivalence and source-grade uncertainty are explicit acceptance fields",
                "no synthetic route, comparator, or holdout value is promoted",
            ],
            "what_remains_open": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "c_v_source_uncertainty_not_closed",
                "author_data_or_independent_reproduction_payload_not_received",
            ],
            "dependency_unlocked": "C_src source-route reconciliation only; no Ding C_src, EOS, alpha, transport, or Full Topic 13 unlock",
            "equation_or_mapping": {
                "mode_sum": "C_src(T) = sum_mu c_mu(T)",
                "thermal_response": "Delta_Tq = Delta_u_ph / C_src(T)",
                "acceptance": "numeric rows + units + material/state match + source-grade uncertainty + convergence/provenance",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "Delta_Tq": "K",
                "source_route_metadata": "not a calibration quantity",
            },
            "derivation_class": "source-route reconciliation; external candidate reproduction and standard mapping kept separate from Ding acceptance",
            "observable": "mode-resolved or equivalent C_src(T) source acceptance state",
            "data_role": "INTERNAL_CSRC_SOURCE_RECONCILIATION_NOT_CALIBRATION",
            "evidence_artifacts": [item["artifact"] for item in candidates],
            "verification_status": status,
            "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "claim_boundary": "This closes a C_src route boundary only. Numeric Calorine/MP48 candidates are not Ding-equivalent, are not accepted source uncertainty, and cannot calibrate alpha_Phi_K or close Full Topic 13.",
        },
        "summary": summary,
        "candidates": candidates,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "alpha_Phi_K_fit_used": False,
            "fit_performed": False,
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE" if passed else "OPEN",
            "WHAT_IS_ACTUALLY_CLOSED": "Eight C_src routes are reconciled: five have no accepted numeric payload and three have numeric candidate outputs, but zero satisfy Ding/material/uncertainty acceptance.",
            "WHAT_REMAINS_OPEN": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing; material mapping; source-grade uncertainty; author response.",
            "DEPENDENCY_UNLOCKED": "None beyond C_src route visibility.",
            "STATUS": status,
            "WHAT_CHANGED": "Added a fail-closed reconciliation of eight C_src source routes; no C_src, alpha, source uncertainty, threshold, equation, or holdout role was promoted.",
            "EQUATION_OR_MAPPING": "C_src(T)=sum_mu c_mu(T) and Delta_Tq=Delta_u_ph/C_src(T) remain standard response mappings until an accepted Ding-compatible source is received.",
            "VERIFICATION": "All route artifacts are present and hashed; numeric candidate count is 3, source-grade uncertainty count is 0, Ding material match count is 0, and accepted count is 0.",
            "CONTROLLING_BLOCKER": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "NEXT_ACTION": "Send the prepared Ding author request only with project authorization, or complete an independent same-regime reproduction with source-grade uncertainty and material mapping; do not promote Calorine/MP48 values.",
            "CLAIM_BOUNDARY": "C_src reconciliation is closed for lane only. Full Topic 13 and global claim promotion remain blocked.",
        },
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "route_count": summary["route_count"],
        "numeric_csrc_candidate_count": summary["numeric_csrc_candidate_count"],
        "source_grade_uncertainty_count": summary["source_grade_uncertainty_count"],
        "ding_material_state_match_count": summary["ding_material_state_match_count"],
        "accepted_independent_reproduction_count": summary["accepted_independent_reproduction_count"],
        "accepted_for_full_topic13_count": summary["accepted_for_full_topic13_count"],
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
