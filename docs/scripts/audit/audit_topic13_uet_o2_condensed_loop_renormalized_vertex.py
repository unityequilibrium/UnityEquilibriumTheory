"""Audit the loop-renormalized condensed contact-channel lane for Topic 13."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_condensed_loop_renormalized_vertex import (  # noqa: E402
    CONDENSED_LOOP_VERTEX_STATUS,
    LOOP_VERTEX_ACCEPTANCE_THRESHOLD,
    condensed_loop_renormalized_vertex_contract,
    condensed_loop_renormalized_vertex_state,
)


from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)

OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_loop_renormalized_vertex_audit.json"
MODULE = ROOT / "docs/core/uet_o2_condensed_loop_renormalized_vertex.py"
CONTINUUM = ROOT / "docs/core/uet_o2_continuum_relative_flow_kubo.py"
EOS = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(
                epsilon_nc=0.1,
                phi_equilibrium=0.0,
            ),
        ),
        quadrature_order=192,
        cutoff_factor=70.0,
    )

    state = condensed_loop_renormalized_vertex_state(
        0.20,
        1.28,
        0.15,
        config,
        reference_space_response=0.0,
        radial_orders=(24, 32, 40),
        angular_order=24,
        angular_refined_order=36,
        radial_scale_factor=1.0,
        refined_scale_factor=0.5,
    )
    contract = condensed_loop_renormalized_vertex_contract()
    numeric_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float))
    )
    target = state.target_bubble_matrix
    reference = state.reference_bubble_matrix
    subtracted = state.subtracted_bubble_matrix
    effective = state.effective_coupling_matrix
    checks = {
        "target_branch_is_condensed": state.branch == "condensed",
        "reference_branch_is_condensed": state.reference_branch == "condensed",
        "reference_and_target_are_distinct": abs(state.space_response - state.reference_space_response) > 1.0e-12,
        "loop_integrals_are_finite": state.loop_integrals_finite,
        "loop_convergence_passes": state.loop_renormalization_convergence_passes,
        "threshold_is_unchanged": (
            LOOP_VERTEX_ACCEPTANCE_THRESHOLD == 1.0e-2
            and state.numerical_uncertainty_bound <= 1.0e-2
            and state.loop_bubble_last_relative_change <= 1.0e-2
            and state.loop_coupling_relative_change <= 1.0e-2
        ),
        "reference_subtraction_condition_is_explicit": state.reference_subtraction_residual <= 1.0e-15,
        "target_and_reference_bubbles_are_positive": all(
            value > 0.0 for row in target + reference for value in row
        ),
        "subtracted_bubble_is_symmetric": abs(subtracted[0][1] - subtracted[1][0]) <= 1.0e-15,
        "effective_coupling_is_positive": all(
            value > 0.0 for row in effective for value in row
        ),
        "loop_changes_target_channel": max(abs(value) for row in subtracted for value in row) > 1.0e-12,
        "response_is_positive": state.dc_relative_response > 0.0,
        "collision_eigenvalues_are_nonnegative": min(state.collision_eigenvalues) >= -1.0e-12,
        "common_flow_is_conserved": state.common_flow_conservation_residual <= 1.0e-12,
        "kernel_is_symmetric": state.symmetric_kernel_residual <= 1.0e-12,
        "kms_is_closed": state.kms_residual <= 1.0e-12,
        "fdt_is_closed": state.fdt_residual <= 1.0e-12,
        "entropy_is_nonnegative": state.entropy_production_at_unit_force >= 0.0,
        "state_matched_retarded_response_is_closed": state.state_matched_retarded_response_completed,
        "physical_kubo_remains_open": state.physical_kubo_coefficient_emitted is False,
        "physical_anchor_remains_open": state.physical_anchor_supplied is False,
        "numeric_alpha_not_emitted": state.numeric_alpha_phi_k_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "holdout_is_unread": state.xie_2026_accessed is False,
        "state_values_are_finite": all(math.isfinite(float(value)) for value in numeric_values),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_is_derived": "not an independent state" in contract["unit_contract"]["R_gen"],
        "R_obs_is_separate": "observer record" in contract["unit_contract"]["R_obs"],
        "physical_kubo_required_fields_are_declared": len(
            contract["physical_kubo_admission"]["required_external_or_microscopic_fields"]
        ) == 11,
        "physical_kubo_is_not_admitted": contract["physical_kubo_admission"]["status"] == "OPEN_PHYSICAL_KUBO",
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = CONDENSED_LOOP_VERTEX_STATUS if not failed else (
        "BLOCKED_T13_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX"
    )
    evidence = [
        {"path": "docs/core/uet_o2_condensed_loop_renormalized_vertex.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_continuum_relative_flow_kubo.py", "sha256": sha256(CONTINUUM)},
        {"path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-loop-renormalized-vertex-v1",
        "artifact": "t13_uet_o2_condensed_loop_renormalized_vertex_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "finite thermal derivative-channel loop bubble for the declared condensed contact channel",
                "explicit reference-subtracted loop coupling with a positive denominator",
                "radial, angular, and compactification-scale convergence with numerical uncertainty bound",
                "state-matched natural-unit retarded relative-flow response with KMS/FDT checks",
                "symmetric positive semidefinite relative kernel with common-flow conservation",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_Kubo_coefficient_record_missing",
                "independent_physical_condensed_vertex_anchor_missing",
                "complete_condensed_1PI_vertex_and_scattering_channels_missing",
                "full_interacting_SK_KMS_match_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": (
                "loop-renormalized condensed contact-channel and state-matched natural-unit retarded lane only; "
                "physical Kubo, SI, alpha, complete transport, Core, Gravity, and external-validation dependencies remain blocked"
            ),
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": asdict(state),
            "state_matched_retarded_kubo_record": {
                "coefficient_name": "K_rel^natural(omega->0)",
                "value": state.dc_relative_response,
                "units": "natural-unit relative response coefficient; not SI conductivity",
                "hydrodynamic_frame": "declared relative-flow frame",
                "temperature": state.temperature,
                "chemical_potential": state.chemical_potential,
                "space_response": state.space_response,
                "correlator_formula_id": "uet.o2.thermal.condensed_loop_relative_flow_retarded_v1",
                "source_path_or_url": "docs/core/uet_o2_condensed_loop_renormalized_vertex.py",
                "source_hash": sha256(MODULE),
                "evidence_status": "INTERNAL_ACTION_DERIVED_NATURAL_RESPONSE_NOT_PHYSICAL_KUBO",
                "state_match": True,
                "uncertainty": state.numerical_uncertainty_bound,
                "uncertainty_class": "numerical quadrature bound only; source/systematic uncertainty absent",
                "physical_admission": "OPEN_PHYSICAL_KUBO",
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "loop_renormalized_vertex_completed": state.loop_renormalization_convergence_passes,
        "state_matched_retarded_response_completed": state.state_matched_retarded_response_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "physical_kubo_admission_status": "OPEN_PHYSICAL_KUBO",
        "physical_anchor_supplied": state.physical_anchor_supplied,
        "numeric_alpha_phi_k_emitted": state.numeric_alpha_phi_k_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "next_controller": (
            "source-lock or microscopically match one state-matched physical Kubo coefficient and independent condensed vertex anchor; "
            "retain this natural-unit response as non-physical until the admission fields and uncertainty are complete"
        ),
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
            "used_for_threshold_adjustment": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "failed_checks": failed,
        "closure_level": artifact["major_result"]["closure_level"],
        "dc_relative_response": state.dc_relative_response,
        "numerical_uncertainty_bound": state.numerical_uncertainty_bound,
        "loop_bubble_last_relative_change": state.loop_bubble_last_relative_change,
        "loop_coupling_relative_change": state.loop_coupling_relative_change,
        "physical_kubo_admission_status": "OPEN_PHYSICAL_KUBO",
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
