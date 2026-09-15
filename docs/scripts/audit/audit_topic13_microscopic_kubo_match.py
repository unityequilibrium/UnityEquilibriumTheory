"""Audit the finite-cutoff microscopic Kubo matching lane for Topic 13."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from docs.core.uet_o2_microscopic_kubo_match import (
    MATCH_TOLERANCE,
    MICROSCOPIC_KUBO_MATCH_STATUS,
    microscopic_kubo_match_contract,
    microscopic_kubo_match_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_microscopic_finite_cutoff_kubo_match_audit.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def main() -> int:
    state = microscopic_kubo_match_state(
        0.35,
        0.10,
        0.80,
        radial_order=8,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=48.0,
        transition_quadrature_order=24,
        transition_channel_count=64,
        transition_interpolation_order=40,
    )
    checks = {
        "microscopic_bethe_salpeter_match": state.microscopic_bethe_salpeter_match_completed,
        "microscopic_sk_kms_match": state.microscopic_sk_kms_match_completed,
        "contact_vertex_match_is_below_threshold": state.contact_cross_section_match_residual <= MATCH_TOLERANCE,
        "transition_rates_are_same_action_object": state.transition_rate_match_residual <= MATCH_TOLERANCE,
        "kubo_identity_is_resolved_on_declared_lane": state.bethe_salpeter_match_residual <= MATCH_TOLERANCE,
        "kms_and_fdt_are_resolved": state.kms_ratio_residual <= MATCH_TOLERANCE and state.fdt_residual <= MATCH_TOLERANCE,
        "ward_projection_is_conservative": state.ward_projection_residual <= MATCH_TOLERANCE,
        "collision_operator_conserves_invariants": state.collision_conservation_residual <= MATCH_TOLERANCE,
        "entropy_production_is_nonnegative": state.entropy_production_witness >= 0.0,
        "operator_is_positive_semidefinite": state.positive_semidefinite_min_eigenvalue >= -MATCH_TOLERANCE,
        "finite_cutoff_is_declared": state.finite_cutoff_boundary_declared and state.finite_cutoff > 0.0,
        "continuum_limit_is_not_claimed": state.continuum_limit_completed is False,
        "physical_kubo_is_not_emitted": state.physical_kubo_coefficient_emitted is False,
        "numeric_alpha_is_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "holdout_is_unread": state.xie_2026_accessed is False,
    }
    status = MICROSCOPIC_KUBO_MATCH_STATUS if all(checks.values()) else "FAIL_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH"
    contract = microscopic_kubo_match_contract()
    major_result = {
        "major_result_id": "T13_UET_O2_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "OPEN",
        "what_is_closed": [
            "the contact-SK quartic vertex and exact two-to-two transition kernel are matched at one state",
            "the mapped finite-cutoff collision operator preserves charge and four-momentum zero modes",
            "the finite-cutoff retarded current response, KMS/FDT ratios, and entropy witness are evaluated from the same operator",
            "the finite-cutoff and natural-unit boundary is explicit, so the response is not promoted to SI transport",
        ] if status.startswith("PASS_") else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            evidence("docs/core/uet_o2_microscopic_kubo_match.py", {"role": "matching implementation"}),
            evidence("docs/core/uet_o2_continuum_collision_operator.py", {"role": "finite-cutoff conservative operator"}),
            evidence("docs/core/uet_o2_contact_sk_transition_vertex_match.py", {"role": "contact-SK normalization"}),
            evidence("docs/core/uet_o2_charged_current_correlator.py", {"role": "retarded charged-current interface"}),
        ],
        "verification_status": status,
        "open_blockers": [
            "continuum_limit_missing",
            "loop_renormalized_off_shell_self_energy_missing",
            "physical_Kubo_coefficient_record_missing",
            "finite_temperature_two_fluid_completion_missing",
            "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "dependency_unlocked": "finite-cutoff microscopic current/KMS matching lane only; no physical SI transport, Full Topic 13, Core, Gravity, or external-validation unlock",
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-microscopic-finite-cutoff-kubo-match-v1",
        "artifact": "t13_uet_o2_microscopic_finite_cutoff_kubo_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "physical_closure_status": "BLOCKED",
        "controlling_blocker": "continuum_limit_and_physical_kubo_promotion_missing",
        "next_controller": "Complete the continuum and renormalized retarded self-energy match, then provide a dimensional Phi map and independent calibration before any physical Kubo promotion.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
    }
    (ROOT / OUT_REL).write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "major_result_id": major_result["major_result_id"], "controlling_blocker": artifact["controlling_blocker"], "artifact": OUT_REL}, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
