"""Compare existing Topic 13 candidate sources with the Core input contracts.

This is a read-only compatibility diagnostic. It does not promote a candidate,
derive a missing scale, read Xie 2026, or replace the canonical closure gate.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_candidate_core_compatibility_audit.json"


CANDIDATES: dict[str, dict[str, str]] = {
    "calorine_zenodo_nep_bte": {
        "source": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_nep_bte_reproduction_source_package.json",
        "audit": "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json",
    },
    "mp48_independent_graphite_cv": {
        "source": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json",
        "audit": "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json",
    },
    "qh15_graphite_specific_c": {
        "source": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/qh15_graphite_transport_source_package.json",
        "audit": "docs/core/artifacts/t13_qh15_graphite_transport_boundary_audit.json",
    },
    "gatech_gen3csp_graphite": {
        "source": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/gatech_gen3csp_graphite_source_package.json",
        "audit": "docs/core/artifacts/t13_gatech_graphite_source_audit.json",
    },
    "kim_2018_graphite_green_kubo": {
        "source": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/kim_2018_graphite_green_kubo_source_package.json",
        "audit": "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json",
    },
}


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def path_value(value: Any, path: str, default: Any = None) -> Any:
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def present(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def field(
    field_id: str,
    label: str,
    is_present: bool,
    evidence: str,
    note: str,
    blocker: str | None = None,
) -> dict[str, Any]:
    result = {
        "field_id": field_id,
        "label": label,
        "present_in_candidate": bool(is_present),
        "evidence": evidence,
        "note": note,
    }
    if blocker:
        result["controlling_blocker_if_missing"] = blocker
    return result


def source_ref(candidate_id: str, role: str) -> dict[str, Any]:
    rel = CANDIDATES[candidate_id]["source"]
    package = load(rel)
    return {
        "path": rel,
        "sha256": digest(rel),
        "role": role,
        "status": package.get("status"),
        "claim_boundary": package.get("claim_boundary")
        or package.get("major_result", {}).get("claim_boundary"),
    }


def audit_ref(candidate_id: str) -> dict[str, Any]:
    rel = CANDIDATES[candidate_id]["audit"]
    audit = load(rel)
    return {
        "path": rel,
        "sha256": digest(rel),
        "status": audit.get("status"),
    }


def holdout_clean(package: dict[str, Any]) -> bool:
    policy = package.get("holdout_policy", {})
    return (
        policy.get("xie_2026_accessed") is False
        and policy.get("xie_2026_source_data_consumed") is not True
        and policy.get("target_curve_used") is not True
        and policy.get("fit_performed") is not True
        and policy.get("alpha_fit_used") is not True
        and policy.get("alpha_Phi_K_fit_used") is not True
    )


def ding_candidate(candidate_id: str) -> dict[str, Any]:
    package = load(CANDIDATES[candidate_id]["source"])
    checks = package.get("checks", {})
    reproduction = package.get("reproduction", {})
    source = package.get("source", {})
    rows = reproduction.get("c_src_rows_latest_mesh", [])
    mode_rows = reproduction.get("mode_resolved_rows", [])
    is_calorine = candidate_id == "calorine_zenodo_nep_bte"
    fields = [
        field(
            "numeric_mode_resolved_C_src",
            "Mode-resolved C_src(T) rows",
            present(mode_rows),
            "reproduction.mode_resolved_rows",
            "The candidate has aggregate rows but no mode-resolved payload under the accepted field contract.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ),
        field(
            "numeric_aggregate_C_src",
            "Aggregate C_src(T) rows",
            present(rows),
            "reproduction.c_src_rows_latest_mesh",
            "Numeric equilibrium heat-capacity rows are candidate evidence only until state equivalence is accepted.",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ),
        field(
            "material_state_match_to_Ding",
            "Ding material/morphology/state match",
            checks.get("material_state_match_to_ding", False),
            "checks.material_state_match_to_ding",
            "The candidate is not admitted as Ding-equivalent in its current package.",
            "material_regime_mapping_to_TTG_not_closed",
        ),
        field(
            "TTG_response_state_contract",
            "TTG response and state contract",
            False,
            "candidate compatibility rule",
            "A formula or normalized response equation is not a same-state TTG numeric response package.",
            "material_regime_mapping_to_TTG_not_closed",
        ),
        field(
            "source_provenance_and_hash",
            "Locator, provenance, preprocessing, and hash",
            checks.get("source_locators_present", False)
            and checks.get("source_hashes_recorded", False),
            "checks.source_locators_present + checks.source_hashes_recorded",
            "Source identity is archived and hash-linked for this candidate route.",
        ),
        field(
            "PBTE_convergence",
            "PBTE convergence record",
            checks.get("latest_mesh_pair_preflight_pass", False),
            "checks.latest_mesh_pair_preflight_pass",
            "The candidate mesh check is useful lane evidence but does not establish Ding equivalence.",
        ),
        field(
            "source_grade_uncertainty",
            "Source-grade statistical/systematic uncertainty",
            checks.get("source_grade_uncertainty_present", False),
            "checks.source_grade_uncertainty_present",
            "A numerical mesh envelope is not source-grade uncertainty.",
            "c_v_source_uncertainty_not_closed",
        ),
        field(
            "same_grade_thermodynamic_pair",
            "Same-grade alpha_V/K_T or justified c_v conversion",
            False,
            "candidate compatibility rule",
            "No accepted same-grade temperature-resolved correction pair is attached to this candidate.",
            "c_v_source_uncertainty_not_closed",
        ),
        field(
            "holdout_clean",
            "Holdout and target-fit isolation",
            holdout_clean(package),
            "holdout_policy",
            "The candidate route does not consume Xie 2026 or fit the target curve.",
        ),
    ]
    return {
        "candidate_id": candidate_id,
        "contract_id": "T13_INPUT_DING_TTG_SOURCE",
        "route_role": "numeric_C_src_candidate_route",
        "source_artifact": source_ref(candidate_id, "candidate source package"),
        "audit_artifact": audit_ref(candidate_id),
        "field_checks": fields,
        "accepted_for_core": False,
        "closure_level": package.get("major_result", {}).get("closure_level"),
        "lane_value": "numeric candidate only" if present(rows) else "no accepted numeric C_src",
        "missing_core_fields": [
            item["field_id"] for item in fields if not item["present_in_candidate"]
        ],
        "controlling_blockers": sorted(
            {
                item["controlling_blocker_if_missing"]
                for item in fields
                if not item["present_in_candidate"]
                and item.get("controlling_blocker_if_missing")
            }
        ),
        "candidate_specific_note": (
            "Calorine is the strongest numeric candidate route but remains a public "
            "C-CX/NEP PBTE lane, not Ding-equivalent."
            if is_calorine
            else "This source is retained as comparator or source-boundary evidence, not a Ding Core package."
        ),
    }


def base_phi_candidate(candidate_id: str) -> dict[str, Any]:
    package = load(CANDIDATES[candidate_id]["source"])
    fields = [
        field(
            "base_Phi_amplitude",
            "Base-Phi amplitude and normalization",
            False,
            "candidate inventory",
            "No candidate package contains a paired physical base-Phi amplitude and normalization record.",
            "dimensional_phi_to_thermal_observable_map_missing",
        ),
        field(
            "dimensionful_energy_anchor_e0",
            "Dimensionful energy anchor e0",
            False,
            "candidate inventory",
            "A standard heat-capacity or transport source does not identify the UET energy scale e0.",
            "normalized_beta_and_SI_scale_correspondence_missing",
        ),
        field(
            "paired_Phi_SI_response",
            "Paired Delta_Phi to SI response rows",
            False,
            "candidate inventory",
            "No candidate contains paired Delta_Phi and Delta_Tq/Delta_u rows with independent provenance.",
            "alpha_Phi_K_independent_calibration_missing",
        ),
        field(
            "independent_alpha_Phi_K",
            "Independent alpha_Phi_K record",
            False,
            "candidate inventory",
            "No numeric alpha is emitted from a source that lacks the paired Phi/SI response.",
            "alpha_Phi_K_independent_calibration_missing",
        ),
        field(
            "non_Landauer_beta_derivation",
            "Beta derivation independent of Landauer",
            False,
            "candidate inventory",
            "None of these external comparator packages derives the UET beta symbol.",
            "normalized_beta_and_SI_scale_correspondence_missing",
        ),
        field(
            "holdout_clean",
            "Holdout and target-fit isolation",
            holdout_clean(package),
            "holdout_policy",
            "The inventory route remains clean, but cleanliness alone cannot create the missing calibration.",
        ),
    ]
    return {
        "candidate_id": candidate_id,
        "contract_id": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "route_role": "external_comparator_without_UET_Phi_scale",
        "source_artifact": source_ref(candidate_id, "candidate source package"),
        "audit_artifact": audit_ref(candidate_id),
        "field_checks": fields,
        "accepted_for_core": False,
        "closure_level": package.get("major_result", {}).get("closure_level"),
        "missing_core_fields": [
            item["field_id"] for item in fields if not item["present_in_candidate"]
        ],
        "controlling_blockers": sorted(
            {
                item["controlling_blocker_if_missing"]
                for item in fields
                if not item["present_in_candidate"]
                and item.get("controlling_blocker_if_missing")
            }
        ),
    }


def transport_candidate() -> dict[str, Any]:
    candidate_id = "kim_2018_graphite_green_kubo"
    package = load(CANDIDATES[candidate_id]["source"])
    payload = package.get("source_payload", {})
    contract = package.get("transport_record_contract", {})
    acceptance = package.get("acceptance", {})
    rows = payload.get("coefficient_rows", [])
    fields = [
        field(
            "physical_transport_coefficient",
            "Numeric SI transport coefficient",
            present(rows),
            "source_payload.coefficient_rows",
            "A source-locked standard-physics coefficient is present.",
            "physical_Kubo_coefficient_record_missing",
        ),
        field(
            "state_and_units",
            "Temperature, frame, direction, and SI units",
            contract.get("value_units") == "W m^-1 K^-1"
            and present(contract.get("temperature"))
            and present(contract.get("space_response")),
            "transport_record_contract",
            "The comparator state and coefficient units are recorded.",
        ),
        field(
            "UET_Phi_state_and_anchor",
            "UET Phi state and base-Phi anchor",
            acceptance.get("uet_space_response_state_present", False)
            and acceptance.get("base_Phi_amplitude_present", False),
            "acceptance.uet_space_response_state_present + acceptance.base_Phi_amplitude_present",
            "The external Green-Kubo model has no UET Phi state or base-Phi amplitude.",
            "dimensional_phi_to_thermal_observable_map_missing",
        ),
        field(
            "retarded_correlator_or_KMS_match",
            "Retarded correlator and KMS/FDT matching",
            False,
            "candidate compatibility rule",
            "A normalized Green-Kubo autocorrelation formula is not a matched UET SK/KMS record.",
            "physical_Kubo_coefficient_record_missing",
        ),
        field(
            "source_grade_correlator_payload",
            "Source-grade raw correlator payload",
            package.get("convergence_evidence", {}).get(
                "raw_correlator_payload_archived", False
            ),
            "source_payload.convergence_evidence.raw_correlator_payload_archived",
            "Only the limited numeric transcription is archived; raw correlator data are absent.",
            "physical_Kubo_coefficient_record_missing",
        ),
        field(
            "entropy_production_mapping",
            "Same-state heat-flux and entropy-production map",
            False,
            "candidate compatibility rule",
            "No UET entropy-current or uncertainty propagation is supplied by this comparator.",
            "physical_Kubo_coefficient_record_missing",
        ),
        field(
            "accepted_for_UET_physical_Kubo",
            "Accepted UET physical Kubo status",
            acceptance.get("accepted_for_uet_physical_kubo_coefficient", False),
            "acceptance.accepted_for_uet_physical_kubo_coefficient",
            "The package explicitly remains an external standard-physics comparator.",
            "physical_Kubo_coefficient_record_missing",
        ),
        field(
            "holdout_clean",
            "Holdout and target-fit isolation",
            holdout_clean(package),
            "holdout_policy",
            "This is marked clean only when explicit metadata supports it; missing holdout metadata remains false.",
        ),
    ]
    return {
        "candidate_id": candidate_id,
        "contract_id": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "route_role": "standard_physics_Green_Kubo_comparator",
        "source_artifact": source_ref(candidate_id, "candidate source package"),
        "audit_artifact": audit_ref(candidate_id),
        "field_checks": fields,
        "accepted_for_core": False,
        "closure_level": "CLOSED_FOR_LANE",
        "missing_core_fields": [
            item["field_id"] for item in fields if not item["present_in_candidate"]
        ],
        "controlling_blockers": sorted(
            {
                item["controlling_blocker_if_missing"]
                for item in fields
                if not item["present_in_candidate"]
                and item.get("controlling_blocker_if_missing")
            }
        ),
    }


def main() -> int:
    ding_ids = [
        "calorine_zenodo_nep_bte",
        "mp48_independent_graphite_cv",
        "qh15_graphite_specific_c",
        "gatech_gen3csp_graphite",
    ]
    base_ids = list(CANDIDATES)
    records = [*(ding_candidate(item) for item in ding_ids)]
    records.extend(base_phi_candidate(item) for item in base_ids)
    records.append(transport_candidate())

    by_contract: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_contract.setdefault(record["contract_id"], []).append(record)

    contract_summary = []
    for contract_id, contract_records in by_contract.items():
        field_records = [
            item for record in contract_records for item in record["field_checks"]
        ]
        contract_summary.append(
            {
                "contract_id": contract_id,
                "candidate_route_count": len(contract_records),
                "core_accepted_route_count": sum(
                    item["accepted_for_core"] for item in contract_records
                ),
                "candidate_routes_with_any_positive_field": sum(
                    any(field_item["present_in_candidate"] for field_item in item["field_checks"])
                    for item in contract_records
                ),
                "positive_field_observations": sum(
                    field_item["present_in_candidate"] for field_item in field_records
                ),
                "field_observation_count": len(field_records),
                "remaining_blockers": sorted(
                    {
                        blocker
                        for item in contract_records
                        for blocker in item["controlling_blockers"]
                    }
                ),
            }
        )

    all_clean = all(
        all(item["present_in_candidate"] for item in record["field_checks"] if item["field_id"] == "holdout_clean")
        for record in records
    )
    report = {
        "schema_version": "t13-candidate-core-compatibility-audit-v1",
        "artifact": "t13_candidate_core_compatibility_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN",
        "major_result": {
            "major_result_id": "T13_CANDIDATE_CORE_COMPATIBILITY_DIAGNOSTIC",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "PARTIAL",
            "what_is_closed": [
                "The strongest local source candidates are compared field-by-field with the three Core input contracts.",
                "Candidate numeric rows, standard-physics comparators, and missing UET mappings are separated.",
                "No candidate is accepted for Core merely because its lane artifact is PASS.",
                "No target-fit violation is emitted; holdout verification remains fail-closed when candidate metadata is incomplete.",
            ],
            "what_remains_open": sorted(
                {
                    blocker
                    for record in records
                    for blocker in record["controlling_blockers"]
                }
            ),
            "dependency_unlocked": "None; this diagnostic only narrows evidence acquisition.",
            "equation_or_mapping": {
                "TTG": "C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)",
                "UET_measurement": "y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)",
                "dimensional_bridge": "Delta_Tq=alpha_Phi_K*Delta_Phi",
                "transport": "KuboRecord -> physical coefficient only after matched Phi/SK/KMS/entropy provenance",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "alpha_Phi_K": "K per normalized Phi",
                "thermal_conductivity": "W m^-1 K^-1",
            },
            "derivation_class": "candidate compatibility and provenance audit; no new physical derivation",
            "observable": "Core input-package coverage and remaining closure distance",
            "data_role": "INTERNAL_AUDIT_NOT_CALIBRATION",
            "evidence_artifacts": [
                source_ref(item, "candidate source package") for item in CANDIDATES
            ],
            "verification_status": "PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN",
            "controlling_blocker": "three grouped input packages remain unaccepted",
            "claim_boundary": "This diagnostic does not close Full Topic 13, derive alpha_Phi_K, turn a comparator into UET transport, or unlock Core/Gravity.",
        },
        "contract_summary": contract_summary,
        "candidate_records": records,
        "summary": {
            "candidate_source_package_count": len(CANDIDATES),
            "evaluated_route_record_count": len(records),
            "core_accepted_route_count": sum(item["accepted_for_core"] for item in records),
            "lane_only_or_boundary_route_count": sum(
                item["closure_level"] == "CLOSED_FOR_LANE" for item in records
            ),
            "holdout_clean_for_all_routes": all_clean,
            "new_core_subresults_closed": 0,
            "canonical_full_topic13_unlocked": False,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_fit_performed": False,
            "calibration_path_may_read_holdout": False,
        },
        "report": {
            "MAJOR_RESULT_CLOSURE": "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": "Candidate-to-contract compatibility is now explicit; no candidate is Core-accepted.",
            "WHAT_REMAINS_OPEN": "Ding-equivalent numeric C_src/material uncertainty, base-Phi SI/alpha/beta scale, and physical UET Kubo/SK/KMS/entropy mapping.",
            "DEPENDENCY_UNLOCKED": "None.",
            "STATUS": "PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN",
            "WHAT_CHANGED": "Added a deterministic field-level comparison of five existing source packages against the three Topic 13 Core input contracts.",
            "EQUATION_OR_MAPPING": "No equation, threshold, source role, or holdout policy was changed.",
            "VERIFICATION": "All candidate source and audit hashes are recorded; every route remains non-Core, while incomplete holdout metadata stays false.",
            "CONTROLLING_BLOCKER": "No admissible Core input package has arrived.",
            "NEXT_ACTION": "Acquire one accepted Ding-compatible C_src package, one paired base-Phi/SI alpha-beta package, and one state-matched physical Kubo/SK/KMS/entropy package.",
            "CLAIM_BOUNDARY": "Compatibility diagnostic only; not Full Topic 13 closure, external validation, prediction, or global UET closure.",
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "candidate_source_package_count": len(CANDIDATES),
                "evaluated_route_record_count": len(records),
                "core_accepted_route_count": 0,
                "holdout_clean_for_all_routes": all_clean,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
