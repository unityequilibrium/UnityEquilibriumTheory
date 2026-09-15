"""Audit the scoped continuum-limit boundary of the Topic 13 collocation lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_continuum_limit_boundary import (  # noqa: E402
    CONTINUUM_LIMIT_BOUNDARY_STATUS,
    CONTINUUM_ACCEPTANCE_THRESHOLD,
    assess_continuum_limit,
    continuum_limit_boundary_contract,
)
from docs.core.uet_o2_continuum_collision_operator import (  # noqa: E402
    continuum_collision_operator_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_limit_boundary_audit.json"
SOURCE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_tree_level_bs_sk_match_audit.json"
MODULE = ROOT / "docs/core/uet_o2_continuum_limit_boundary.py"
SOURCE_MODULE = ROOT / "docs/core/uet_o2_tree_level_bs_sk_match.py"
COLLISION_MODULE = ROOT / "docs/core/uet_o2_continuum_collision_operator.py"

FIXED_CHANNEL_RADIAL_ORDERS = (14, 16, 18, 20)
FIXED_CHANNEL_COUNT = 256
FIXED_COLLISION_INTEGRATION_ORDER = 32
FIXED_ANGULAR_ORDER = 32
FIXED_CUTOFF_FACTOR = 48.0
FIXED_TRANSITION_QUADRATURE_ORDER = 32
FIXED_TRANSITION_INTERPOLATION_ORDER = 40


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_channel_diagnostic() -> dict[str, object]:
    """Recheck radial refinement while holding the transition channel count fixed."""

    config = FiniteTemperatureO2QuasiparticleConfig()
    states = []
    for radial_order in FIXED_CHANNEL_RADIAL_ORDERS:
        state = continuum_collision_operator_state(
            0.22,
            0.35,
            0.15,
            config,
            radial_order=radial_order,
            collision_integration_order=FIXED_COLLISION_INTEGRATION_ORDER,
            angular_order=FIXED_ANGULAR_ORDER,
            cutoff_factor=FIXED_CUTOFF_FACTOR,
            transition_quadrature_order=FIXED_TRANSITION_QUADRATURE_ORDER,
            transition_channel_count=FIXED_CHANNEL_COUNT,
            transition_interpolation_order=FIXED_TRANSITION_INTERPOLATION_ORDER,
        )
        states.append(
            {
                "radial_order": int(radial_order),
                "channel_count": int(state.transition_channel_count),
                "dc_response": float(state.dc_response),
                "state_count": int(state.state_count),
                "transition_state_count": int(state.transition_state_count),
            }
        )
    responses = tuple(float(item["dc_response"]) for item in states)
    relative_changes = tuple(
        abs(current - previous) / max(abs(previous), 1.0e-300)
        for previous, current in zip(responses, responses[1:])
    )
    return {
        "radial_orders": list(FIXED_CHANNEL_RADIAL_ORDERS),
        "channel_counts": [int(item["channel_count"]) for item in states],
        "dc_responses": list(responses),
        "relative_changes": list(relative_changes),
        "maximum_relative_change": max(relative_changes),
        "acceptance_threshold": CONTINUUM_ACCEPTANCE_THRESHOLD,
        "channel_count_held_constant": len(
            {int(item["channel_count"]) for item in states}
        )
        == 1,
        "configuration": {
            "temperature": 0.22,
            "chemical_potential": 0.35,
            "space_response": 0.15,
            "collision_integration_order": FIXED_COLLISION_INTEGRATION_ORDER,
            "angular_order": FIXED_ANGULAR_ORDER,
            "cutoff_factor": FIXED_CUTOFF_FACTOR,
            "transition_quadrature_order": FIXED_TRANSITION_QUADRATURE_ORDER,
            "transition_channel_count": FIXED_CHANNEL_COUNT,
            "transition_interpolation_order": FIXED_TRANSITION_INTERPOLATION_ORDER,
        },
    }


def main() -> int:
    source_path = ROOT / SOURCE_REL
    source = json.loads(source_path.read_text(encoding="utf-8-sig"))
    state = source["state"]
    contract = continuum_limit_boundary_contract()
    boundary = assess_continuum_limit(
        tuple(state["continuum_sequence_radial_orders"]),
        tuple(state["continuum_sequence_channel_counts"]),
        tuple(state["continuum_sequence_dc_responses"]),
        tuple(state["continuum_sequence_relative_changes"]),
    )
    fixed_channel = fixed_channel_diagnostic()
    fixed_channel_boundary = assess_continuum_limit(
        tuple(fixed_channel["radial_orders"]),
        tuple(fixed_channel["channel_counts"]),
        tuple(fixed_channel["dc_responses"]),
        tuple(fixed_channel["relative_changes"]),
    )
    source_checks = source.get("checks", {})
    checks = {
        "source_tree_level_lane_is_present": source.get("status")
        == "PASS_ACTION_DERIVED_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE",
        "resolution_sequence_has_four_points": len(boundary.dc_responses) == 4,
        "adjacent_change_count_is_three": len(boundary.relative_changes) == 3,
        "resolution_values_are_finite": all(
            value == value
            and abs(float(value)) != float("inf")
            for value in (*boundary.dc_responses, *boundary.relative_changes)
        ),
        "repository_threshold_is_unchanged": boundary.acceptance_threshold == 1.0e-2,
        "current_scheme_fails_continuum_acceptance": boundary.current_scheme_continuum_no_go,
        "fixed_channel_count_is_held_constant": fixed_channel["channel_count_held_constant"],
        "fixed_channel_sequence_has_four_points": len(fixed_channel["dc_responses"]) == 4,
        "fixed_channel_values_are_finite": all(
            value == value
            and abs(float(value)) != float("inf")
            for value in (*fixed_channel["dc_responses"], *fixed_channel["relative_changes"])
        ),
        "fixed_channel_threshold_is_unchanged": fixed_channel["acceptance_threshold"]
        == CONTINUUM_ACCEPTANCE_THRESHOLD,
        "fixed_channel_sequence_still_fails_acceptance": fixed_channel_boundary.current_scheme_continuum_no_go,
        "fixed_channel_has_no_extrapolation": fixed_channel_boundary.extrapolated_response_emitted is False,
        "existing_controller_is_visible": source_checks.get("continuum_controller_is_visible") is True,
        "existing_lane_does_not_claim_continuum": source_checks.get("continuum_limit_is_not_claimed") is True,
        "finite_cutoff_algebraic_lane_remains_pass": source.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE",
        "no_extrapolated_response_emitted": boundary.extrapolated_response_emitted is False,
        "no_parameter_fitting": boundary.parameter_fitting_performed is False,
        "no_target_data": boundary.target_data_used is False,
        "xie_holdout_is_unread": boundary.xie_2026_accessed is False,
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    status = CONTINUUM_LIMIT_BOUNDARY_STATUS if not failed else "BLOCKED_CONTINUUM_LIMIT_BOUNDARY_AUDIT"
    major_result = {
        "major_result_id": "T13_UET_O2_CONTINUUM_LIMIT_CURRENT_SCHEME_NO_GO",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
        "what_is_closed": [
            "the existing radial/channel resolution sequence is source-linked and machine-readable",
            "the repository continuum-controller threshold 1e-2 is applied without adjustment",
            "the declared current finite-cutoff discretization fails continuum promotion because the maximum adjacent response change is above threshold",
            "a fixed-channel radial refinement also fails continuum promotion, so channel-count growth is not the sole cause of the current no-go",
            "no extrapolated continuum response is emitted and the finite-cutoff lane remains separately bounded",
        ]
        if not failed
        else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/uet_o2_continuum_limit_boundary.py", "sha256": sha256(MODULE)},
            {"path": SOURCE_REL, "sha256": sha256(source_path)},
            {"path": "docs/core/uet_o2_tree_level_bs_sk_match.py", "sha256": sha256(SOURCE_MODULE)},
            {"path": "docs/core/uet_o2_continuum_collision_operator.py", "sha256": sha256(COLLISION_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "new_continuum_discretization_or_matched_extrapolation_missing",
            "loop_renormalized_microscopic_vertex_missing",
            "microscopic_SK_KMS_action_match_missing",
            "physical_Kubo_coefficient_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "dependency_unlocked": (
            "scoped no-go for continuum promotion of the current finite-cutoff scheme; "
            "finite-cutoff formal lane remains available, but no continuum, physical Kubo, SI, alpha, TTG, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-continuum-limit-boundary-v1",
        "artifact": "t13_uet_o2_continuum_limit_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "boundary": asdict(boundary),
        "fixed_channel_diagnostic": fixed_channel,
        "source": {
            "path": SOURCE_REL,
            "major_result_id": source.get("major_result", {}).get("major_result_id"),
            "source_status": source.get("status"),
            "source_sha256": sha256(source_path),
        },
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": False,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "claim_promotion": False,
        "full_core_unlock": False,
        "controlling_blocker": "new_continuum_discretization_or_matched_extrapolation_missing",
        "next_controller": (
            "replace or analytically control the current basis/cutoff dependence, then rerun the same 1e-2 convergence gate; "
            "do not call the present finite-cutoff response a continuum or physical Kubo result"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "max_relative_change": boundary.maximum_relative_change}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
