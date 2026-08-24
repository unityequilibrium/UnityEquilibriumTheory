"""Reconcile Topic 13 base-Phi/SI/alpha evidence without emitting alpha."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json"
EVIDENCE = {
    "alpha_search": ROOT / "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json",
    "phi_e": ROOT / "docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json",
    "formula": ROOT / "docs/core/artifacts/t13_dimensional_bridge_contract_audit.json",
    "public": ROOT / "docs/core/artifacts/t13_phi_si_anchor_public_source_boundary_audit.json",
    "action": ROOT / "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json",
    "field_no_go": ROOT / "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json",
    "normalized_no_go": ROOT / "docs/core/artifacts/t13_alpha_phi_k_identifiability_audit.json",
    "calibration": ROOT / "docs/core/artifacts/thermal_dimensional_calibration_contract.json",
    "observable": ROOT / "docs/core/artifacts/uet_dimensional_observable_closure_audit.json",
    "protocol": ROOT / "docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json",
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
    formal: bool,
    source_boundary: bool,
    named_phi_e: bool,
    independent_base_phi_si: bool,
    reason: str,
    blocker: str,
    **extra: object,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "artifact": ref(key, role),
        "candidate_class": candidate_class,
        "formal_or_structural_lane": formal,
        "source_boundary": source_boundary,
        "named_phi_e_comparator": named_phi_e,
        "independent_base_phi_si_record": independent_base_phi_si,
        "eligible_for_full_topic13": independent_base_phi_si,
        "reason": reason,
        "controlling_blocker": blocker,
        **extra,
    }


def main() -> int:
    sources = {key: load(path) for key, path in EVIDENCE.items()}
    alpha = sources["alpha_search"]
    phi_e = sources["phi_e"]
    formula = sources["formula"]
    public = sources["public"]
    action = sources["action"]
    field_no_go = sources["field_no_go"]
    normalized_no_go = sources["normalized_no_go"]
    calibration = sources["calibration"]
    observable = sources["observable"]
    protocol = sources["protocol"]

    candidates = [
        candidate(
            "paired_base_phi_si_search", "alpha_search", "74-record paired base-Phi/SI search",
            "SOURCE_SEARCH_BOUNDARY", False, True, False, False,
            "The repository-wide search found candidates but no paired base-Phi amplitude and independent SI response record.",
            "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            candidate_count=alpha.get("candidate_count"), eligible_candidate_count=alpha.get("eligible_candidate_count"),
        ),
        candidate(
            "mp48_named_phi_e_comparator", "phi_e", "named Phi_E harmonic dimensional comparator",
            "NAMED_PHI_E_COMPARATOR", False, False, True, False,
            "MP48 supplies conditional alpha_Phi_E, but the base-Phi-to-Phi_E map remains open.",
            "base_Phi_to_Phi_E_mapping_missing",
            numeric_named_alpha_present=phi_e.get("numeric_alpha_Phi_E_K_emitted"),
            base_phi_mapping_present=not phi_e.get("checks", {}).get("base_phi_to_phi_e_mapping_remains_open", False),
        ),
        candidate(
            "conditional_dimensional_alpha_formula", "formula", "conditional alpha formula and SI unit contract",
            "CONDITIONAL_FORMULA_LANE", True, False, False, False,
            "The formula and units are implemented, but a_Phi(T), e0, and the equilibrium branch are not source-locked.",
            "conditional_alpha_inputs_a_Phi_T_e0_and_equilibrium_reference_not_source_locked",
            numeric_alpha_witness_present=formula.get("witness", {}).get("alpha_K_per_normalized_phi") is not None,
            source_locked_e0=formula.get("conditional_inputs", {}).get("e0", {}).get("status") == "SOURCE_LOCKED",
        ),
        candidate(
            "normalized_phi_scale_no_go", "normalized_no_go", "normalized Phi scale identifiability no-go",
            "NORMALIZED_SCALE_NO_GO", True, False, False, False,
            "Normalized dynamics cannot identify an absolute K per Phi scale under compensating field rescaling.",
            "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
        ),
        candidate(
            "public_ding_paired_record_boundary", "public", "official public source and author-request boundary",
            "PUBLIC_SOURCE_BOUNDARY", False, True, False, False,
            "The captured public Ding route has no paired base-Phi/SI record and the author request has not been received.",
            "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            public_paired_record_present=public.get("source_availability", {}).get("public_numeric_paired_record_present"),
            author_route_executed=public.get("source_availability", {}).get("author_request_state") == "RECEIVED",
        ),
        candidate(
            "covariant_natural_unit_si_route", "action", "covariant action natural-unit route and SI boundary",
            "NATURAL_UNIT_ACTION_ROUTE", True, False, False, False,
            "The action route is identified, but its implementation is natural-unit only and does not supply Phi normalization or e0.",
            "system_specific_SI_contract_and_covariant_Phi_to_normalized_Phi_map_missing",
            si_mapping_present=not action.get("checks", {}).get("formula_si_gate_open", False),
        ),
        candidate(
            "covariant_field_rescaling_no_go", "field_no_go", "covariant field normalization identifiability no-go",
            "COVARIANT_FIELD_SCALE_NO_GO", True, False, False, False,
            "The natural-unit covariant scalar has a field-rescaling redundancy; canonicalization does not provide physical SI amplitude.",
            "physical_field_normalization_observable_and_SI_coefficient_provenance_missing",
        ),
        candidate(
            "thermal_calibration_contract", "calibration", "anti-fitting dimensional calibration contract",
            "ANTI_FITTING_CALIBRATION_CONTRACT", True, False, False, False,
            "The scale-degeneracy contract is explicit, but the open record has no value, uncertainty, or source locator.",
            "normalized_phi_has_no_absolute_kelvin_scale",
            numeric_alpha_present=False,
        ),
        candidate(
            "normalized_observable_closure", "observable", "normalized TTG operator and observable audit",
            "NORMALIZED_OBSERVABLE_ONLY", True, False, False, False,
            "The normalized TTG operator is defined, but Kelvin, heat-flux, and entropy observables remain downstream of alpha/SI closure.",
            "dimensional_phi_to_thermal_observable_map_missing",
            alpha_open=observable.get("measurement_operator", {}).get("alpha_Phi_K_status") == "OPEN_CALIBRATION_DEPENDENT",
        ),
        candidate(
            "independent_calibration_protocol", "protocol", "independent base-Phi calibration acceptance protocol",
            "PROTOCOL_NOT_EVIDENCE", True, False, False, False,
            "The acceptance protocol is complete, but no permitted paired source row has been received and no numeric alpha is emitted.",
            "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            record_received=protocol.get("source_rows_consumed", False),
        ),
    ]

    checks = {
        "all_evidence_files_present": all(path.is_file() for path in EVIDENCE.values()),
        "alpha_search_is_zero_eligible": alpha.get("candidate_count") == 74
        and alpha.get("eligible_candidate_count") == 0
        and alpha.get("numeric_alpha_Phi_K_emitted") is False,
        "named_phi_e_is_not_base_phi": phi_e.get("numeric_alpha_Phi_E_K_emitted") is True
        and phi_e.get("checks", {}).get("base_phi_to_phi_e_mapping_remains_open") is True
        and phi_e.get("checks", {}).get("numeric_alpha_Phi_K_not_emitted") is True,
        "conditional_formula_inputs_remain_open": formula.get("conditional_inputs", {}).get("e0", {}).get("status") != "SOURCE_LOCKED"
        and formula.get("checks", {}).get("no_numeric_alpha_emitted") is True,
        "public_paired_record_is_absent": public.get("source_availability", {}).get("public_numeric_paired_record_present") is False
        and public.get("checks", {}).get("author_request_not_claimed_sent") is True,
        "natural_action_route_remains_non_si": action.get("checks", {}).get("formula_si_gate_open") is True
        and action.get("checks", {}).get("no_numeric_anchor_emitted") is True,
        "field_rescaling_no_go_is_preserved": field_no_go.get("checks", {}).get("scalar_rescaling_witness_passes") is True
        and field_no_go.get("checks", {}).get("normalized_energy_no_go_is_present") is True,
        "normalized_no_go_is_preserved": normalized_no_go.get("checks", {}).get("absolute_alpha_not_identifiable_from_normalized_lane") is True,
        "calibration_contract_is_open": calibration.get("gates", {}).get("physical_mapping_requires_independent_record") is True
        and calibration.get("open_calibration_record", {}).get("temperature_scale_K_per_phi") is None,
        "normalized_observable_is_not_kelvin": observable.get("measurement_operator", {}).get("alpha_Phi_K_status") == "OPEN_CALIBRATION_DEPENDENT"
        and observable.get("checks", {}).get("heat_flux_observable") is False,
        "protocol_has_no_received_rows": protocol.get("source_rows_consumed") is False
        and protocol.get("numeric_alpha_Phi_K_emitted") is False,
        "holdout_is_clean": alpha.get("holdout_accessed") is False
        and public.get("checks", {}).get("xie_2026_accessed") is False
        and normalized_no_go.get("checks", {}).get("xie_2026_not_accessed") is True,
        "no_target_fit_or_calibration": alpha.get("target_fit_performed") is False
        and alpha.get("numeric_alpha_Phi_K_emitted") is False
        and phi_e.get("alpha_Phi_K_fit_performed") is False,
    }
    summary = {
        "candidate_count": len(candidates),
        "paired_alpha_search_candidate_count": alpha.get("candidate_count"),
        "eligible_paired_alpha_record_count": alpha.get("eligible_candidate_count"),
        "formal_or_structural_lane_count": sum(item["formal_or_structural_lane"] for item in candidates),
        "source_boundary_count": sum(item["source_boundary"] for item in candidates),
        "named_phi_e_comparator_count": sum(item["named_phi_e_comparator"] for item in candidates),
        "independent_base_phi_si_record_count": sum(item["independent_base_phi_si_record"] for item in candidates),
        "accepted_for_full_topic13_count": sum(item["eligible_for_full_topic13"] for item in candidates),
    }
    passed = all(checks.values()) and summary["independent_base_phi_si_record_count"] == 0
    status = "PASS_SCOPED_BASE_PHI_RECONCILIATION_OPEN" if passed else "FAIL_T13_BASE_PHI_RECONCILIATION"
    artifact = {
        "schema_version": "t13-base-phi-si-reconciliation-v1",
        "artifact": "t13_base_phi_si_reconciliation_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_BASE_PHI_SI_RECONCILIATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the 74-record paired base-Phi/SI candidate search is reconciled with zero eligible records",
                "the named Phi_E comparator is separated from the base UET Phi lane",
                "conditional formula, natural-unit action, and field-rescaling no-go boundaries are source-linked",
                "the independent calibration protocol is separated from received evidence",
            ],
            "what_remains_open": [
                "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
                "base_Phi_to_Phi_E_mapping_missing",
                "dimensional_free_energy_density_scale_e0_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "base-Phi evidence reconciliation only; no SI anchor, alpha, beta, EOS, transport, or Full Topic 13 unlock",
            "equation_or_mapping": {
                "measurement": "Delta_Tq = alpha_Phi_K * Delta_Phi_base",
                "named_comparator": "Delta_Tq = (e0(T0)/c_v(T0)) Phi_E",
                "coordinate_map": "Phi_E = s_material * Phi_base",
                "identifiability": "Delta_Phi_prime = s Delta_Phi; alpha_Phi_K_prime = alpha_Phi_K/s",
            },
            "units": {
                "base_Phi": "dimensionless normalized response; SI scale open",
                "Phi_E": "dimensionless named energy-response comparator",
                "e0": "J m^-3; not source-locked",
                "c_v": "J m^-3 K^-1",
                "alpha_Phi_K": "K per normalized base Phi; no numeric value emitted",
            },
            "derivation_class": "source-search reconciliation, conditional formula audit, and identifiability boundary; no numerical base-Phi calibration",
            "observable": "paired base-Phi amplitude and SI thermal-response acceptance state",
            "data_role": "INTERNAL_BASE_PHI_RECONCILIATION_NOT_CALIBRATION",
            "evidence_artifacts": [item["artifact"] for item in candidates],
            "verification_status": status,
            "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            "claim_boundary": "This closes the base-Phi evidence boundary for lane only. It does not convert Phi_E into base Phi, emit alpha_Phi_K, or close the dimensional thermal bridge.",
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
            "WHAT_IS_ACTUALLY_CLOSED": "The 74-record search, Phi_E comparator, conditional formula, natural-unit action route, no-go boundaries, and calibration protocol are reconciled; no base-Phi/SI pair is accepted.",
            "WHAT_REMAINS_OPEN": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing; base-Phi to Phi_E map; e0; independent alpha_Phi_K.",
            "DEPENDENCY_UNLOCKED": "None beyond base-Phi evidence visibility.",
            "STATUS": status,
            "WHAT_CHANGED": "Added a fail-closed reconciliation of ten base-Phi/SI evidence classes; no alpha, e0, source row, threshold, equation, or holdout role was promoted.",
            "EQUATION_OR_MAPPING": "Delta_Tq=alpha_Phi_K*Delta_Phi_base remains distinct from the conditional Phi_E comparator; the scale transformation remains non-identifiable.",
            "VERIFICATION": "All evidence artifacts are present and hashed; candidate search is 74/0; Phi_E is not relabelled as base Phi; no numeric alpha or holdout access occurred.",
            "CONTROLLING_BLOCKER": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            "NEXT_ACTION": "Obtain an authorized paired base-Phi/SI record or derive a source-provenance-backed action-to-SI map; do not use Phi_E, TTG residuals, or Xie 2026 as base-Phi calibration.",
            "CLAIM_BOUNDARY": "Base-Phi reconciliation is closed for lane only. Full Topic 13 and global claim promotion remain blocked.",
        },
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "candidate_count": summary["candidate_count"],
        "paired_alpha_search_candidate_count": summary["paired_alpha_search_candidate_count"],
        "eligible_paired_alpha_record_count": summary["eligible_paired_alpha_record_count"],
        "named_phi_e_comparator_count": summary["named_phi_e_comparator_count"],
        "independent_base_phi_si_record_count": summary["independent_base_phi_si_record_count"],
        "accepted_for_full_topic13_count": summary["accepted_for_full_topic13_count"],
        "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
