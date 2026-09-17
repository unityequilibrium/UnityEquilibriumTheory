"""Audit the vacuum retarded discontinuity interface for the O(2) sunset."""

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

from docs.core.uet_o2_action_1pi_sunset_euclidean import (  # noqa: E402
    euclidean_1pi_sunset_state,
)
from docs.core.uet_o2_action_1pi_sunset_retarded import (  # noqa: E402
    RETARDED_1PI_SUNSET_STATUS,
    retarded_vacuum_sunset_contract,
    retarded_vacuum_sunset_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_1pi_sunset_retarded_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_retarded.py"
EUCLIDEAN_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_euclidean.py"
TENSOR_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_tensor.py"
ZERO_ETA_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_sunset_zero_eta.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    euclidean = euclidean_1pi_sunset_state(0.5, 0.8)
    state = retarded_vacuum_sunset_state(
        0.5,
        0.8,
        euclidean.twice_subtracted_self_energy_values,
    )
    contract = retarded_vacuum_sunset_contract()
    finite_state = all(
        math.isfinite(value)
        for values in (
            state.spacelike_dispersion_response,
            state.euclidean_reference_response,
        )
        for value in values
    ) and all(
        math.isfinite(value)
        for value in (
            state.three_body_threshold_s,
            state.phase_space_at_timelike_probe,
            state.spectral_measure_at_timelike_probe,
            state.retarded_spectral_density_at_timelike_probe,
            state.retarded_imaginary_part_at_timelike_probe,
            state.above_threshold_principal_value_real_part,
            state.euclidean_dispersion_match_residual,
            state.inner_phase_space_convergence_residual,
            state.outer_dispersion_convergence_residual,
            state.above_threshold_pv_inner_convergence_residual,
            state.above_threshold_pv_outer_convergence_residual,
        )
    )
    checks = {
        "vacuum_three_body_cut_completed": state.vacuum_three_body_cut_completed,
        "threshold_is_nine_mass_squared": abs(
            state.three_body_threshold_s - 4.5
        )
        <= 1.0e-12,
        "below_threshold_support_is_zero": state.below_threshold_zero_witness
        and state.phase_space_below_threshold <= 1.0e-30,
        "above_threshold_support_is_nonzero": state.above_threshold_nonzero_witness,
        "retarded_i0_discontinuity_is_completed": state.retarded_i0_discontinuity_completed,
        "retarded_imaginary_part_has_negative_sign": state.retarded_imaginary_sign_witness,
        "retarded_spectral_density_matches_imaginary_convention": abs(
            state.retarded_spectral_density_at_timelike_probe
            + state.retarded_imaginary_part_at_timelike_probe
        )
        <= 1.0e-30,
        "spacelike_dispersion_is_completed": state.spacelike_dispersion_completed,
        "euclidean_dispersion_match_is_small": state.euclidean_dispersion_match_residual
        <= 2.0e-2,
        "inner_phase_space_converges": state.inner_phase_space_convergence_residual
        <= 2.0e-2,
        "outer_dispersion_converges": state.outer_dispersion_convergence_residual
        <= 2.0e-2,
        "state_is_finite": finite_state,
        "above_threshold_principal_value_is_completed": state.above_threshold_principal_value_real_part_completed,
        "above_threshold_principal_value_is_nonzero": state.above_threshold_principal_value_real_part != 0.0,
        "above_threshold_pv_inner_converges": state.above_threshold_pv_inner_convergence_residual <= 2.0e-2,
        "above_threshold_pv_outer_converges": state.above_threshold_pv_outer_convergence_residual <= 2.0e-2,
        "full_retarded_1pi_remains_open": not state.full_1pi_retarded_self_energy_completed,
        "finite_temperature_remains_open": not state.finite_temperature_completion_completed,
        "unique_renormalization_remains_open": not state.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_remains_open": not state.microscopic_sk_kms_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used
        and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"][
            "Phi"
        ],
        "C_ontology_preserved": "not mass or charge"
        in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace"
        in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "principal_value_boundary_is_explicit": contract["included"][
            "above_threshold_principal_value_real_part"
        ],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        RETARDED_1PI_SUNSET_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE"
    )
    open_blockers = [
        "full_above_threshold_retarded_1pi_completion_missing",
        "full_retarded_1PI_self_energy_missing",
        "finite_temperature_self_energy_and_SK_KMS_match_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_retarded.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_euclidean.py", "sha256": sha256(EUCLIDEAN_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_tensor.py", "sha256": sha256(TENSOR_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_sunset_zero_eta.py", "sha256": sha256(ZERO_ETA_MODULE)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-action-1pi-sunset-retarded-v2",
        "artifact": "t13_uet_o2_action_1pi_sunset_retarded_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "equal-mass O(2) vacuum three-body sunset cut with threshold s_th=9*m^2",
                "declared retarded i0 discontinuity and negative imaginary-part convention",
                "below-threshold zero support and above-threshold nonzero support",
                "twice-subtracted spacelike dispersion from the vacuum spectral measure",
                "numerical match of the spacelike dispersion to the regulated Euclidean loop",
                "analytic above-threshold principal-value real part with pole subtraction",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "vacuum three-body cut, retarded discontinuity, spacelike dispersion match, and above-threshold PV real-part interface only; no finite-T SK/KMS, physical renormalization, transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "vacuum_three_body_cut_completed": state.vacuum_three_body_cut_completed,
        "spacelike_dispersion_completed": state.spacelike_dispersion_completed,
        "retarded_i0_discontinuity_completed": state.retarded_i0_discontinuity_completed,
        "above_threshold_principal_value_real_part_completed": state.above_threshold_principal_value_real_part_completed,
        "full_1pi_retarded_self_energy_completed": state.full_1pi_retarded_self_energy_completed,
        "finite_temperature_completion_completed": state.finite_temperature_completion_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_match_completed": state.microscopic_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "full_finite_temperature_retarded_1PI_SK_KMS_and_unique_physical_renormalization_missing",
        "next_controller": "extend the vacuum cut and pole-subtracted dispersion to finite temperature, then match the retarded/advanced/Keldysh components to SK/KMS before emitting physical transport coefficients",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE",
        "closure_level": closure_level,
        "data_role": state.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed,
                "artifact": str(OUT.relative_to(ROOT)),
                "three_body_threshold_s": state.three_body_threshold_s,
                "euclidean_dispersion_match_residual": state.euclidean_dispersion_match_residual,
                "retarded_imaginary_part_at_timelike_probe": state.retarded_imaginary_part_at_timelike_probe,
                "above_threshold_principal_value_real_part": state.above_threshold_principal_value_real_part,
                "above_threshold_pv_inner_convergence_residual": state.above_threshold_pv_inner_convergence_residual,
                "above_threshold_pv_outer_convergence_residual": state.above_threshold_pv_outer_convergence_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
