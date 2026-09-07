"""Reconcile Topic 13 transport evidence without promoting comparators.

This audit separates formal transport contracts, a declared natural-unit UET
channel, and an external graphite Green-Kubo comparator from the physical UET
coefficient required by the Full Topic 13 gate.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json"

EVIDENCE = {
    "physical_kubo_provenance": ROOT / "docs/core/artifacts/t13_physical_kubo_coefficient_provenance_audit.json",
    "transport_kms_entropy": ROOT / "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json",
    "uet_natural_kubo": ROOT / "docs/core/artifacts/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json",
    "uet_sk_kms": ROOT / "docs/core/artifacts/t13_uet_o2_condensed_sk_kms_kubo_match_audit.json",
    "kim_external_green_kubo": ROOT / "docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json",
    "flat_components": ROOT / "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
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


def main() -> int:
    sources = {key: load(path) for key, path in EVIDENCE.items()}
    physical_gate = sources["physical_kubo_provenance"]
    transport_boundary = sources["transport_kms_entropy"]
    natural_kubo = sources["uet_natural_kubo"]
    sk_kms = sources["uet_sk_kms"]
    kim = sources["kim_external_green_kubo"]
    flat = sources["flat_components"]

    candidates = [
        {
            "candidate_id": "physical_kubo_provenance_gate",
            "artifact": ref(
                "physical_kubo_provenance",
                "physical coefficient acceptance schema and fail-closed gate",
            ),
            "candidate_class": "PROVENANCE_GATE_NO_COEFFICIENT",
            "closure_level": physical_gate.get("major_result", {}).get("closure_level"),
            "formal_lane": True,
            "natural_unit_uet_lane": False,
            "external_physical_comparator": False,
            "physical_uet_coefficient": False,
            "full_topic13_eligible": False,
            "reason": "The acceptance schema is closed, but the verifier still reports no physical coefficient value.",
            "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        },
        {
            "candidate_id": "formal_sk_kms_entropy_boundary",
            "artifact": ref(
                "transport_kms_entropy",
                "formal SK/KMS, entropy, and heat-flux status boundary",
            ),
            "candidate_class": "FORMAL_SK_KMS_ENTROPY_INTERFACE",
            "closure_level": transport_boundary.get("major_result", {}).get("closure_level"),
            "formal_lane": True,
            "natural_unit_uet_lane": True,
            "external_physical_comparator": False,
            "physical_uet_coefficient": False,
            "full_topic13_eligible": False,
            "reason": "Formal KMS/entropy and natural-unit balance are verified, while physical coefficient and finite-temperature normal sector remain blocked.",
            "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        },
        {
            "candidate_id": "uet_condensed_relative_flow_natural_kubo",
            "artifact": ref(
                "uet_natural_kubo",
                "declared action-derived UET natural-unit Kubo channel",
            ),
            "candidate_class": "UET_NATURAL_UNIT_KUBO_CHANNEL",
            "closure_level": natural_kubo.get("major_result", {}).get("closure_level"),
            "formal_lane": False,
            "natural_unit_uet_lane": True,
            "external_physical_comparator": False,
            "physical_uet_coefficient": False,
            "full_topic13_eligible": False,
            "numeric_coefficient_present": True,
            "si_units": False,
            "physical_anchor_supplied": natural_kubo.get("physical_anchor_supplied", False),
            "reason": "A state-matched action-derived coefficient exists only in a declared natural-unit channel and has no physical Phi/SI anchor.",
            "controlling_blocker": "independent_physical_condensed_vertex_anchor_missing",
        },
        {
            "candidate_id": "kim_2018_external_graphite_green_kubo",
            "artifact": ref(
                "kim_external_green_kubo",
                "source-locked external standard-physics comparator",
            ),
            "candidate_class": "EXTERNAL_STANDARD_PHYSICS_COMPARATOR",
            "closure_level": kim.get("major_result", {}).get("closure_level"),
            "formal_lane": False,
            "natural_unit_uet_lane": False,
            "external_physical_comparator": True,
            "physical_uet_coefficient": False,
            "full_topic13_eligible": False,
            "external_input_accepted": kim.get("acceptance", {}).get("accepted_for_external_transport_input", False),
            "uet_mapping_present": kim.get("acceptance", {}).get("uet_space_response_state_present", False),
            "reason": "Kim 2018 supplies source-locked SI graphite conductivity rows, but not a UET Phi response or Ding TTG state match.",
            "controlling_blocker": "UET_space_response_and_base_Phi_mapping_missing",
        },
        {
            "candidate_id": "flat_formal_bridge_with_external_inputs",
            "artifact": ref(
                "flat_components",
                "formal flat thermodynamic bridge component gate",
            ),
            "candidate_class": "FORMAL_BRIDGE_WITH_EXTERNAL_INPUTS",
            "closure_level": flat.get("major_result", {}).get("closure_level"),
            "formal_lane": True,
            "natural_unit_uet_lane": True,
            "external_physical_comparator": False,
            "physical_uet_coefficient": False,
            "full_topic13_eligible": False,
            "reason": "Flat bridge components pass with declared external inputs, not with a physical UET transport coefficient or SI Phi calibration.",
            "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        },
    ]

    checks = {
        "all_evidence_files_present": all(path.is_file() for path in EVIDENCE.values()),
        "physical_kubo_gate_reports_no_value": physical_gate.get("transport_verification", {}).get(
            "physical_coefficient_evidence"
        )
        == "BLOCKED_NOT_PROVIDED",
        "formal_sk_kms_entropy_lane_passes": transport_boundary.get("checks", {}).get(
            "formal_sk_kms_entropy_interface_passes"
        )
        and transport_boundary.get("checks", {}).get("natural_covariant_entropy_balance_lane_passes"),
        "natural_kubo_is_explicitly_not_si": natural_kubo.get("checks", {}).get(
            "units_are_explicitly_natural_not_si"
        )
        and natural_kubo.get("physical_anchor_supplied") is False,
        "kim_external_comparator_not_uet_relabelled": kim.get("checks", {}).get(
            "external_input_not_uet_relabelled"
        )
        and kim.get("acceptance", {}).get("accepted_for_uet_physical_kubo_coefficient") is False,
        "flat_components_remain_lane_scoped": flat.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE",
        "no_physical_uet_candidate_is_accepted": all(
            not candidate["physical_uet_coefficient"]
            and not candidate["full_topic13_eligible"]
            for candidate in candidates
        ),
        "holdout_is_clean": all(
            not source.get("holdout_policy", {}).get("xie_2026_accessed", False)
            for source in sources.values()
        ),
        "no_alpha_fit_or_tuning": all(
            not source.get("holdout_policy", {}).get("alpha_Phi_K_fit_used", False)
            and not source.get("holdout_policy", {}).get("fit_performed", False)
            for source in sources.values()
        ),
    }

    summary = {
        "candidate_count": len(candidates),
        "formal_lane_count": sum(candidate["formal_lane"] for candidate in candidates),
        "natural_unit_uet_lane_count": sum(
            candidate["natural_unit_uet_lane"] for candidate in candidates
        ),
        "external_physical_comparator_count": sum(
            candidate["external_physical_comparator"] for candidate in candidates
        ),
        "physical_uet_coefficient_count": sum(
            candidate["physical_uet_coefficient"] for candidate in candidates
        ),
        "accepted_for_full_topic13_count": sum(
            candidate["full_topic13_eligible"] for candidate in candidates
        ),
    }

    passed = all(checks.values()) and summary["physical_uet_coefficient_count"] == 0
    status = (
        "PASS_SCOPED_PHYSICAL_TRANSPORT_RECONCILIATION_OPEN"
        if passed
        else "FAIL_T13_PHYSICAL_TRANSPORT_RECONCILIATION"
    )
    artifact = {
        "schema_version": "t13-physical-transport-reconciliation-v1",
        "artifact": "t13_physical_transport_reconciliation_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_PHYSICAL_TRANSPORT_RECONCILIATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "formal SK/KMS/entropy and natural-unit transport evidence is separated from physical SI evidence",
                "the declared UET natural-unit Kubo channel is retained without SI or Full Topic 13 promotion",
                "the Kim 2018 graphite Green-Kubo rows are retained as an external comparator only",
                "the physical UET coefficient acceptance boundary is machine-readable and fail-closed",
            ],
            "what_remains_open": [
                "physical_Kubo_coefficient_record_missing",
                "finite_temperature_normal_component_not_derived",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "transport evidence reconciliation only; no physical transport, Full Topic 13, Core, Gravity, alpha, or external-validation unlock",
            "equation_or_mapping": {
                "formal_entropy": "nabla_mu J_S^mu = X_A L^(AB) X_B >= 0",
                "natural_uet_channel": "K_rel^natural = lim_(omega->0) Re G_R^rel(omega)",
                "external_comparator": "kappa_i = V/(k_B*T^2) * integral <J_i(s)J_i(0)> ds",
                "admission": "physical UET coefficient requires matched Phi/SI state, correlator, source identity, hash, and uncertainty",
            },
            "units": {
                "formal_lane": "declared natural units with local interface",
                "natural_uet_channel": "natural-unit relative-flow response; not SI conductivity",
                "external_comparator": "W m^-1 K^-1",
                "physical_uet_requirement": "coefficient-specific SI units plus Phi response mapping",
            },
            "derivation_class": "transport evidence reconciliation; formal/action-derived/comparator classes kept separate",
            "observable": "transport coefficient and thermal-response evidence acceptance state",
            "data_role": "INTERNAL_TRANSPORT_RECONCILIATION_NOT_UET_CALIBRATION",
            "evidence_artifacts": [candidate["artifact"] for candidate in candidates],
            "verification_status": status,
            "controlling_blocker": "physical_Kubo_coefficient_record_missing",
            "claim_boundary": "This closes a transport evidence boundary only. It does not identify a natural-unit channel or external graphite conductivity with a physical UET Phi coefficient, does not close SI mapping, and does not close Full Topic 13.",
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
            "WHAT_IS_ACTUALLY_CLOSED": "Formal SK/KMS/entropy, one declared natural-unit UET Kubo channel, and one external graphite comparator are separated and source-linked; no physical UET coefficient is admitted.",
            "WHAT_REMAINS_OPEN": "physical_Kubo_coefficient_record_missing; finite-temperature normal transport; Phi-to-SI mapping; independent alpha_Phi_K calibration.",
            "DEPENDENCY_UNLOCKED": "None beyond transport evidence reconciliation visibility.",
            "STATUS": status,
            "WHAT_CHANGED": "Added a fail-closed reconciliation of five transport evidence classes; no coefficient, alpha, threshold, equation, or holdout role was promoted.",
            "EQUATION_OR_MAPPING": "Formal entropy and KMS lanes, natural-unit K_rel, and external Green-Kubo kappa remain distinct; physical admission requires a matched Phi/SI record.",
            "VERIFICATION": "All source artifacts are present and hashed; formal lanes pass their scoped checks; Kim is external-only; natural Kubo is non-SI; accepted physical UET coefficient count is zero.",
            "CONTROLLING_BLOCKER": "physical_Kubo_coefficient_record_missing",
            "NEXT_ACTION": "Obtain or microscopically derive one state-matched physical UET transport record with Phi/SI mapping, correlator locator, source identity, uncertainty, and finite-temperature scope; do not relabel Kim or the natural-unit channel.",
            "CLAIM_BOUNDARY": "Transport reconciliation is closed for lane only. Full Topic 13 remains blocked and global claim promotion remains false.",
        },
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "candidate_count": summary["candidate_count"],
        "formal_lane_count": summary["formal_lane_count"],
        "external_physical_comparator_count": summary["external_physical_comparator_count"],
        "physical_uet_coefficient_count": summary["physical_uet_coefficient_count"],
        "accepted_for_full_topic13_count": summary["accepted_for_full_topic13_count"],
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
