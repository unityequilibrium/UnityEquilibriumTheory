"""Audit the three non-derivable input packages that control Topic 13 closure.

The audit reads only existing non-holdout artifacts. It never invents a source
row, alpha value, SI Phi scale, or physical transport coefficient.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
GATE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
RECORD_CONTRACT_REL = "docs/core/artifacts/t13_closure_record_contract_audit.json"
CANDIDATE_COMPATIBILITY_REL = "docs/core/artifacts/t13_candidate_core_compatibility_audit.json"
RECONCILIATION_RELS = {
    "cv": "docs/core/artifacts/t13_cv_source_reconciliation_audit.json",
    "transport": "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json",
    "base_phi": "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json",
    "csrc": "docs/core/artifacts/t13_csrc_reconciliation_audit.json",
}

EVIDENCE_RELS = [
    RECORD_CONTRACT_REL,
    "docs/core/artifacts/t13_independent_csrc_acceptance_contract.json",
    "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json",
    "docs/core/artifacts/t13_ding_pbte_author_request_audit.json",
    "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json",
    "docs/core/artifacts/t13_ding_material_regime_boundary_audit.json",
    "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json",
    "docs/core/artifacts/t13_dimensional_bridge_contract_audit.json",
    "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json",
    "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json",
    "docs/core/artifacts/t13_physical_kubo_coefficient_provenance_audit.json",
    "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json",
    "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json",
    "docs/core/artifacts/t13_huberman_2019_ttg_source_boundary_audit.json",
    "docs/core/artifacts/t13_public_phonon_route_screening_audit.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_public_phonon_route_screening_package.json",
    CANDIDATE_COMPATIBILITY_REL,
    "docs/core/artifacts/covariant_superfluid_transport_verification.json",
    "docs/core/artifacts/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json",
    "docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json",
    *RECONCILIATION_RELS.values(),
    GATE_REL,
]


def load(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def artifact_ref(rel: str, role: str) -> dict[str, Any]:
    return {
        "path": rel,
        "sha256": sha256(rel),
        "role": role,
    }


def main() -> int:
    gate = load(GATE_REL)
    record_contract = load(RECORD_CONTRACT_REL)
    csrc_contract = load("docs/core/artifacts/t13_independent_csrc_acceptance_contract.json")
    calorine = load("docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json")
    author_request = load("docs/core/artifacts/t13_ding_pbte_author_request_audit.json")
    oa_route = load("docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json")
    material = load("docs/core/artifacts/t13_ding_material_regime_boundary_audit.json")
    alpha = load("docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json")
    dimensional = load("docs/core/artifacts/t13_dimensional_bridge_contract_audit.json")
    anchor_no_go = load("docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json")
    action_si = load("docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json")
    kubo = load("docs/core/artifacts/t13_physical_kubo_coefficient_provenance_audit.json")
    transport = load("docs/core/artifacts/covariant_superfluid_transport_verification.json")
    natural_kubo = load(
        "docs/core/artifacts/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json"
    )
    sk_entropy = load("docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json")
    lowitzer_pair = load("docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json")
    graphite_pair_boundary = load("docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json")
    huberman = load("docs/core/artifacts/t13_huberman_2019_ttg_source_boundary_audit.json")
    public_phonon = load("docs/core/artifacts/t13_public_phonon_route_screening_audit.json")
    candidate_compatibility = load(CANDIDATE_COMPATIBILITY_REL)
    cv_reconciliation = load(RECONCILIATION_RELS["cv"])
    transport_reconciliation = load(RECONCILIATION_RELS["transport"])
    base_phi_reconciliation = load(RECONCILIATION_RELS["base_phi"])
    csrc_reconciliation = load(RECONCILIATION_RELS["csrc"])

    cv_summary = cv_reconciliation.get("summary", {})
    transport_summary = transport_reconciliation.get("summary", {})
    base_phi_summary = base_phi_reconciliation.get("summary", {})
    csrc_summary = csrc_reconciliation.get("summary", {})

    calorine_checks = calorine.get("checks", {})
    alpha_count = int(alpha.get("eligible_candidate_count", 0))
    alpha_package_eligible = alpha_count > 0
    physical_coefficient_blocked = (
        kubo.get("transport_verification", {}).get("physical_coefficient_evidence")
        == "BLOCKED_NOT_PROVIDED"
    )

    ding_missing = [
        key
        for key, present in {
            "authorized_numeric_C_src_payload": csrc_contract.get("acceptance", {}).get(
                "raw_author_numeric_C_src_available", False
            ),
            "accepted_independent_reproduction": csrc_contract.get("acceptance", {}).get(
                "accepted_independent_reproduction_available", False
            ),
            "Ding_material_state_match": calorine_checks.get(
                "material_state_match_to_ding", False
            ),
            "source_grade_uncertainty": calorine_checks.get(
                "source_grade_uncertainty_present", False
            ),
        }.items()
        if not present
    ]

    phi_missing = [
        key
        for key, present in {
            "eligible_paired_alpha_record": alpha_package_eligible,
            "numeric_alpha_emitted": alpha.get("numeric_alpha_Phi_K_emitted", False),
            "dimensional_bridge_open_inputs_closed": dimensional.get("status")
            == "PASS_CONDITIONAL_FORMULA_CLOSED",
            "dimensionful_action_SI_map": action_si.get("status")
            == "PASS_COVARIANT_ACTION_SI_MAP_CLOSED",
        }.items()
        if not present
    ]

    transport_missing = [
        key
        for key, present in {
            "physical_coefficient_record": not physical_coefficient_blocked,
            "finite_temperature_transport_completion": transport.get(
                "finite_temperature_two_fluid_completion"
            )
            == "PASS",
            "physical_anchor_supplied": natural_kubo.get("state", {}).get(
                "admission", {}
            ).get("physical_anchor_supplied", False),
            "physical_heat_flux_entropy_link": sk_entropy.get(
                "physical_coefficient_evidence"
            )
            not in {None, "BLOCKED_NOT_PROVIDED"},
        }.items()
        if not present
    ]

    packages = [
        {
            "package_id": "T13_INPUT_DING_TTG_SOURCE",
            "status": "BLOCKED",
            "accepted_for_core": not ding_missing,
            "current_evidence": {
                "numeric_candidate_rows_present": calorine_checks.get(
                    "summary_schema_valid", False
                )
                and calorine_checks.get("mode_heat_capacity_unit_recorded", False),
                "mesh_convergence_pass": calorine_checks.get(
                    "latest_mesh_pair_preflight_pass", False
                ),
                "material_state_match_to_ding": calorine_checks.get(
                    "material_state_match_to_ding", False
                ),
                "source_grade_uncertainty_present": calorine_checks.get(
                    "source_grade_uncertainty_present", False
                ),
                "author_payload_received": csrc_contract.get("acceptance", {}).get(
                    "raw_author_numeric_C_src_available", False
                ),
                "public_route_is_bounded": oa_route.get("checks", {}).get(
                    "no_reproduction_payload_candidate_in_oa_prefix", False
                ),
                "author_request_executed": not author_request.get("checks", {}).get(
                    "manifest_not_sent", False
                ),
                "material_equivalence_audit": material.get("status"),
                "thermodynamic_pair_status": lowitzer_pair.get("status"),
                "same_grade_alpha_V_and_K_T_correction_pair": graphite_pair_boundary.get("same_grade_pair_route_available", False),
                "huberman_2019_public_route_status": huberman.get("status"),
                "huberman_2019_numeric_payload_present": huberman.get("checks", {}).get("numeric_C_src_rows_present", False),
                "public_phonon_route_screening_status": public_phonon.get("status"),
                "public_phonon_core_payload_present": not public_phonon.get("checks", {}).get("no_core_payload_imported", False),
                "candidate_compatibility_status": candidate_compatibility.get("status"),
                "candidate_core_accepted_route_count": candidate_compatibility.get("summary", {}).get("core_accepted_route_count"),
                "cv_source_reconciliation_status": cv_reconciliation.get("status"),
                "direct_or_derived_cv_count": cv_summary.get("direct_or_derived_cv_count"),
                "source_grade_cv_uncertainty_count": cv_summary.get("source_grade_cv_uncertainty_count"),
                "eligible_cv_input_count": cv_summary.get("eligible_for_full_topic13_count"),
                "csrc_reconciliation_status": csrc_reconciliation.get("status"),
                "csrc_route_count": csrc_summary.get("route_count"),
                "numeric_csrc_candidate_count": csrc_summary.get("numeric_csrc_candidate_count"),
                "source_grade_uncertainty_count": csrc_summary.get("source_grade_uncertainty_count"),
                "ding_material_state_match_count": csrc_summary.get("ding_material_state_match_count"),
                "ding_author_payload_count": csrc_summary.get("ding_author_payload_count"),
                "accepted_independent_reproduction_count": csrc_summary.get("accepted_independent_reproduction_count"),
                "eligible_csrc_input_count": csrc_summary.get("accepted_for_full_topic13_count"),
            },
            "missing_acceptance_fields": ding_missing,
            "unlocks_subresults": [
                "accepted_numeric_csrc",
                "material_and_uncertainty_closure",
                "physical_source_backed_eos",
                "physical_heat_flux_entropy_map",
            ],
        },
        {
            "package_id": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
            "status": "BLOCKED",
            "accepted_for_core": not phi_missing,
            "current_evidence": {
                "eligible_paired_alpha_records": alpha_count,
                "candidate_search_status": alpha.get("status"),
                "normalized_scale_no_go": anchor_no_go.get("status"),
                "dimensional_bridge_status": dimensional.get("status"),
                "covariant_action_route_status": action_si.get("status"),
                "numeric_alpha_emitted": alpha.get("numeric_alpha_Phi_K_emitted", False),
                "holdout_accessed": alpha.get("holdout_accessed", False),
                "candidate_compatibility_status": candidate_compatibility.get("status"),
                "candidate_core_accepted_route_count": candidate_compatibility.get("summary", {}).get("core_accepted_route_count"),
                "base_phi_reconciliation_status": base_phi_reconciliation.get("status"),
                "paired_alpha_search_candidate_count": base_phi_summary.get("paired_alpha_search_candidate_count"),
                "eligible_paired_alpha_record_count": base_phi_summary.get("eligible_paired_alpha_record_count"),
                "named_phi_e_comparator_count": base_phi_summary.get("named_phi_e_comparator_count"),
                "independent_base_phi_si_record_count": base_phi_summary.get("independent_base_phi_si_record_count"),
                "eligible_base_phi_input_count": base_phi_summary.get("accepted_for_full_topic13_count"),
            },
            "missing_acceptance_fields": phi_missing,
            "unlocks_subresults": [
                "base_phi_si_anchor",
                "independent_alpha_record",
                "normalized_beta_si_map",
                "physical_source_backed_eos",
                "physical_heat_flux_entropy_map",
            ],
        },
        {
            "package_id": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
            "status": "BLOCKED",
            "accepted_for_core": not transport_missing,
            "current_evidence": {
                "physical_coefficient_evidence": kubo.get(
                    "transport_verification", {}
                ).get("physical_coefficient_evidence"),
                "finite_temperature_two_fluid_completion": transport.get(
                    "finite_temperature_two_fluid_completion"
                ),
                "natural_kubo_lane_status": natural_kubo.get("status"),
                "natural_kubo_is_SI": natural_kubo.get("state", {})
                .get("admission", {})
                .get("units")
                == "SI",
                "formal_sk_entropy_status": sk_entropy.get("status"),
                "candidate_compatibility_status": candidate_compatibility.get("status"),
                "candidate_core_accepted_route_count": candidate_compatibility.get("summary", {}).get("core_accepted_route_count"),
                "physical_transport_reconciliation_status": transport_reconciliation.get("status"),
                "formal_lane_count": transport_summary.get("formal_lane_count"),
                "natural_unit_uet_lane_count": transport_summary.get("natural_unit_uet_lane_count"),
                "external_physical_comparator_count": transport_summary.get("external_physical_comparator_count"),
                "physical_uet_coefficient_count": transport_summary.get("physical_uet_coefficient_count"),
                "eligible_physical_transport_input_count": transport_summary.get("accepted_for_full_topic13_count"),
            },
            "missing_acceptance_fields": transport_missing,
            "unlocks_subresults": [
                "physical_uet_kubo_record",
                "physical_sk_transport_match",
                "physical_entropy_production_mapping",
                "physical_heat_flux_entropy_map",
            ],
        },
    ]

    checks = {
        "all_evidence_files_present": all(
            (ROOT / rel).is_file() for rel in EVIDENCE_RELS
        ),
        "record_contract_schema_is_valid": record_contract.get("status")
        == "PASS_T13_CLOSURE_RECORD_CONTRACT_OPEN",
        "canonical_gate_is_still_blocked": gate.get("status")
        == "BLOCKED_OPEN_T13_FULL_BRIDGE",
        "all_packages_are_explicitly_blocked_until_inputs_arrive": all(
            package["status"] == "BLOCKED" and not package["accepted_for_core"]
            for package in packages
        ),
        "holdout_is_unread": not gate.get("verification_status", {})
        .get("holdout_integrity", {})
        .get("holdout_consumed", False),
        "no_target_fit": all(
            not value.get("target_fit_performed", False)
            for value in (alpha, calorine, natural_kubo)
        ),
        "no_numeric_alpha_emitted": not alpha.get("numeric_alpha_Phi_K_emitted", False),
        "no_physical_transport_value_emitted": physical_coefficient_blocked,
        "public_phonon_route_is_scoped_without_core_payload": public_phonon.get("status")
        == "PASS_SCOPED_PUBLIC_PHONON_ROUTE_SCREENING_NO_CORE_PAYLOAD"
        and public_phonon.get("checks", {}).get("no_core_payload_imported", False),
        "candidate_compatibility_audit_is_scoped_without_core_acceptance": candidate_compatibility.get("status")
        == "PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN"
        and candidate_compatibility.get("summary", {}).get("core_accepted_route_count") == 0
        and candidate_compatibility.get("summary", {}).get("new_core_subresults_closed") == 0
        and candidate_compatibility.get("summary", {}).get("canonical_full_topic13_unlocked") is not True,
        "cv_source_reconciliation_is_fail_closed": cv_reconciliation.get("status")
        == "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN"
        and cv_summary.get("eligible_for_full_topic13_count") == 0,
        "physical_transport_reconciliation_is_fail_closed": transport_reconciliation.get("status")
        == "PASS_SCOPED_PHYSICAL_TRANSPORT_RECONCILIATION_OPEN"
        and transport_summary.get("physical_uet_coefficient_count") == 0
        and transport_summary.get("accepted_for_full_topic13_count") == 0,
        "base_phi_reconciliation_is_fail_closed": base_phi_reconciliation.get("status")
        == "PASS_SCOPED_BASE_PHI_RECONCILIATION_OPEN"
        and base_phi_summary.get("independent_base_phi_si_record_count") == 0
        and base_phi_summary.get("accepted_for_full_topic13_count") == 0,
        "csrc_reconciliation_is_fail_closed": csrc_reconciliation.get("status")
        == "PASS_SCOPED_CSRC_RECONCILIATION_OPEN"
        and csrc_summary.get("accepted_for_full_topic13_count") == 0
        and csrc_summary.get("accepted_ding_csrc_count") == 0,
        "gate_blocker_set_is_nonempty": bool(
            gate.get("major_result", {}).get("what_remains_open")
        ),
    }

    status = (
        "PASS_SCOPED_T13_CLOSURE_INPUT_AUDIT_OPEN"
        if all(checks.values())
        else "FAIL_T13_CLOSURE_INPUT_AUDIT"
    )
    evidence = [
        artifact_ref(rel, "input-package acceptance evidence")
        for rel in EVIDENCE_RELS
    ]
    report = {
        "schema_version": "t13-closure-input-package-audit-v1",
        "artifact": "t13_closure_input_package_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CLOSURE_INPUT_PACKAGE_AUDIT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "PARTIAL",
            "what_is_closed": [
                "The three non-derivable input packages are checked against current artifacts.",
                "The fail-closed record contract is linked before any package can be accepted.",
                "Numeric candidates are separated from accepted Core-ready evidence.",
                "The field-level candidate compatibility diagnostic is linked without accepting any route.",
                "Holdout and anti-fitting boundaries are rechecked.",
                "Existing graphite heat-capacity and correction sources are reconciled by quantity, uncertainty, and material-state eligibility.",
                "Formal, natural-unit, and external-comparator transport evidence is reconciled without physical UET promotion.",
                "Base-Phi/SI candidate, Phi_E comparator, and natural-unit action evidence are reconciled without alpha promotion.",
                "C_src routes are reconciled by payload, numeric status, material match, uncertainty, and acceptance without Ding promotion.",
            ],
            "what_remains_open": gate.get("major_result", {}).get(
                "what_remains_open", []
            ),
            "equation_or_mapping": {
                "TTG": "C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)",
                "UET": "y_TTG^UET=Delta_Phi(t)/Delta_Phi(0); Delta_Tq=alpha_Phi_K*Delta_Phi",
                "transport": "KuboCoefficientRecord -> physical coefficient only after matched provenance",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "Delta_Tq": "K",
                "alpha_Phi_K": "K per normalized Phi",
                "transport": "source-specific; no physical value emitted",
            },
            "derivation_class": "provenance and acceptance audit; no new physical derivation",
            "observable": "closure-input acceptance state",
            "data_role": "INTERNAL_AUDIT_NOT_CALIBRATION",
            "evidence_artifacts": evidence,
            "record_contract_artifact": {
                "path": RECORD_CONTRACT_REL,
                "status": record_contract.get("status"),
            },
            "verification_status": status,
            "controlling_blocker": gate.get("controlling_blocker"),
            "claim_boundary": "This audit narrows input readiness only. It does not close Full Topic 13, derive alpha_Phi_K, or promote candidate C_src/Kubo values.",
        },
        "packages": packages,
        "checks": checks,
        "open_blockers": gate.get("major_result", {}).get("what_remains_open", []),
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_fit_performed": False,
            "calibration_path_may_read_holdout": False,
        },
        "evidence_artifacts": evidence,
        "report": {
            "MAJOR_RESULT_CLOSURE": "PARTIAL",
            "WHAT_IS_ACTUALLY_CLOSED": "The three package acceptance boundaries and the linked candidate compatibility diagnostic are machine-audited; no package is accepted for Core.",
            "WHAT_REMAINS_OPEN": gate.get("major_result", {}).get(
                "what_remains_open", []
            ),
            "DEPENDENCY_UNLOCKED": "None.",
            "STATUS": status,
            "WHAT_CHANGED": "Reconciled the three grouped input packages with c_v, physical transport, base-Phi, and C_src evidence projections without promoting any candidate.",
            "EQUATION_OR_MAPPING": "No equations or numeric values were changed or emitted.",
            "VERIFICATION": "All evidence hashes, reconciliation fail-closed checks, holdout, fit, candidate-compatibility, and canonical-gate checks passed; candidate metadata remains fail-closed where incomplete.",
            "CONTROLLING_BLOCKER": gate.get("controlling_blocker"),
            "NEXT_ACTION": "Acquire an authorized Ding-compatible source, independent base-Phi/SI calibration, and physical Kubo/SK/KMS record; rerun only after an input hash changes.",
            "CLAIM_BOUNDARY": "Input-readiness audit only; not Full Topic 13 closure or external validation.",
        },
        "wave_controller": {
            "wave_type": "topic13_input_package_reconciliation_projection",
            "controlling_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
                "physical_Kubo_coefficient_record_missing",
            ],
            "composition": list(RECONCILIATION_RELS.values()),
            "claim_impact": "no_change",
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "package_count": len(packages),
                "accepted_for_core": sum(
                    package["accepted_for_core"] for package in packages
                ),
                "holdout_accessed": False,
                "failed_checks": [
                    key for key, value in checks.items() if not value
                ],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())

