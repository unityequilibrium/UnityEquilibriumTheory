"""Decide whether the frozen He-4 calibration has an admitted second-sound domain."""

from __future__ import annotations

import hashlib
import json
from math import isclose
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
INPUTS = {
    "frozen_branch": TOPIC / "Result/artifacts/t13_he4_frozen_branch_compatibility.json",
    "condensed_selection": TOPIC / "Result/artifacts/t13_he4_condensed_state_identifiability.json",
    "gaussian_no_go": TOPIC / "Result/artifacts/t13_he4_phi_amplitude_compatibility.json",
    "formal_auxiliary": TOPIC / "Result/artifacts/t13_he4_formal_auxiliary_phi_joint_root.json",
    "source_route": TOPIC / "Result/artifacts/t13_he4_independent_measurement_route_screen.json",
}
OUTPUT = TOPIC / "Result/artifacts/t13_funding_heii_operator_domain_decision.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    frozen = records["frozen_branch"]
    candidates = records["condensed_selection"]
    gaussian = records["gaussian_no_go"]
    formal = records["formal_auxiliary"]
    source = records["source_route"]
    state = frozen["frozen_natural_state"]
    reference = formal["reference_config"]
    q_from_frozen_equation = state["matter_kinetic"] * state["chemical_potential"] ** 2 - state["effective_mass_sq"]
    checks = {
        "frozen_reference_is_normal_by_declared_tree_equation": (
            state["branch"] == "normal"
            and state["condensate_amplitude"] == 0.0
            and q_from_frozen_equation < 0.0
            and isclose(q_from_frozen_equation, state["condensate_control"], abs_tol=1e-12)
        ),
        "heii_anchor_has_nonzero_superfluid_fraction": (
            frozen["physical_anchor"]["phase"] == "He II"
            and frozen["physical_anchor"]["superfluid_fraction"] > 0.0
        ),
        "tree_condensed_witnesses_are_not_material_admitted": (
            len(candidates["witnesses"]) >= 2
            and all(row["tree_branch"] == "condensed" and not row["physical_HeII_state_admitted"]
                    for row in candidates["witnesses"])
            and candidates["checks"]["source_fractions_have_no_declared_absolute_O2_order_parameter_map"]
        ),
        "gaussian_phi_only_point_has_scoped_amplitude_no_go": (
            gaussian["closure_level"] == "CLOSED_AS_NO_GO"
            and gaussian["checks"]["proof_domain_contains_partial_root"]
            and gaussian["root_state"]["tree_condensate_control_q"] > 0.0
        ),
        "formal_auxiliary_changes_prescription_and_is_not_physical": (
            reference["Z_auxiliary"] != reference["Z_prior_normalized"]
            and formal["checks"]["original_normalized_action_is_outside_auxiliary_domain"]
            and formal["full_core_unlock"] is False
        ),
        "static_and_source_interfaces_do_not_supply_physical_operator": (
            frozen["checks"]["static_and_collision_lanes_exclude_complete_two_fluid_transport"]
            and source["numeric_response_rows_admitted"] == 0
            and source["independent_heii_validation_admitted"] is False
        ),
    }
    evidence = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}
        for path in INPUTS.values()
    ]
    return {
        "schema_version": "t13-funding-heii-operator-domain-decision-v1",
        "major_result_id": "T13_FROZEN_HEII_OPERATOR_DOMAIN_BOUNDARY",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "The presently frozen normal-branch He-4 calibration cannot be treated as an admitted condensed He-II second-sound prediction; the nearest condensed alternatives are unadmitted, class-incompatible, or formal-only.",
        "equation_or_mapping": "q=Z*mu^2-m_eff(Phi)^2; q_frozen<0 while the physical anchor has rho_s/rho>0. The calibration map g exists locally, but an admitted h(p; protocol)=u2_UET does not yet exist on this frozen model domain.",
        "units": "q and mu use the natural action lane; rho_s/rho is dimensionless; u2 requires m s^-1 and an independent SI state/response map",
        "derivation_class": "cross-artifact logical domain check using an exact frozen tree-branch equation and scoped candidate admissibility results",
        "observable": "He-II second-sound phase velocity under a matched saturated-vapor-pressure resonance protocol",
        "data_role": "STRUCTURAL_MODEL_ADMISSION_DECISION_NOT_EMPIRICAL_SCORE",
        "frozen_branch": {
            "T_natural": state["temperature"],
            "mu_natural": state["chemical_potential"],
            "Phi_natural": state["space_response"],
            "q_recomputed": q_from_frozen_equation,
            "q_recorded": state["condensate_control"],
            "heii_anchor_T_K": frozen["physical_anchor"]["temperature_K"],
            "heii_anchor_superfluid_fraction": frozen["physical_anchor"]["superfluid_fraction"],
        },
        "candidate_dispositions": [
            {"candidate": "frozen_normal_calibration", "decision": "NOT_A_CONDENSED_HEII_LINEARIZATION"},
            {"candidate": "tree_condensed_witnesses", "decision": "INTERNAL_NOT_MATERIAL_ADMITTED"},
            {"candidate": "thermal_only_gaussian_phi_root", "decision": "CLOSED_AS_NO_GO_IN_DECLARED_CLASS"},
            {"candidate": "formal_auxiliary_joint_root", "decision": "FORMAL_ONLY_DIFFERENT_Z_PRESCRIPTION"},
        ],
        "checks": checks,
        "g1_physical_protocol_status": "BLOCKED_NO_ADMITTED_CONDENSED_STATE_AND_LONGITUDINAL_OPERATOR",
        "g2_scientific_disposition": "UNRESOLVED_OPERATOR_COMPLETION_BOUNDARY_NOT_NONIDENTIFIABILITY_PROOF",
        "why_no_rank_claim": "An h map is not defined on the frozen physical model domain; no Jacobian or same-calibration different-response proof can be claimed until a named admissible completion supplies h.",
        "next_research_route": "Specify one fixed, Ward-consistent condensed finite-temperature model and independent material state map; then derive the longitudinal source-to-detector operator or prove a same-calibration different-response family within that named class.",
        "verification_status": "PASS_SCOPED_OPERATOR_DOMAIN_BOUNDARY" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": evidence,
        "open_blockers": [
            "microscopic_ward_consistent_condensed_completion_not_selected",
            "absolute_charge_or_stiffness_to_heii_density_map_not_admitted",
            "longitudinal_two_fluid_source_to_detector_operator_not_admitted",
            "independent_response_source_and_g0_clean_baseline_open",
        ],
        "controlling_blocker": "named_admissible_condensed_model_to_observable_operator_missing",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "xie_2026_accessed": False,
        "claim_boundary": "This excludes only a physical second-sound inference from the frozen bundle. It is not a theorem against future UET completions, a proof of structural nonidentifiability, a He-II prediction, an external validation or Full Topic 13 closure.",
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(audit(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(OUTPUT)
