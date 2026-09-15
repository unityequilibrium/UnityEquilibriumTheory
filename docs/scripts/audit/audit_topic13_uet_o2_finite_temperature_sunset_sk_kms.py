"""Audit the finite-temperature action-derived 1<->3 sunset SK/KMS lane."""

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

from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (  # noqa: E402
    FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
    FINITE_T_SUNSET_SK_KMS_STATUS,
    finite_temperature_sunset_sk_kms_contract,
    finite_temperature_sunset_sk_kms_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_sk_kms_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_sunset_sk_kms.py"
RETARDED_MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_retarded.py"
TENSOR_MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_tensor.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_sunset_sk_kms_state(0.35, 0.5, 0.8)
    contract = finite_temperature_sunset_sk_kms_contract()
    finite_state = all(
        math.isfinite(float(value))
        for value in (
            state.vacuum_spectral_measure,
            state.thermal_greater_measure,
            state.thermal_lesser_measure,
            state.thermal_spectral_measure,
            state.thermal_retarded_spectral_density,
            state.retarded_imaginary_part,
            state.thermal_noise_measure,
            state.finite_temperature_principal_value_real_part,
            state.vacuum_phase_space_normalization_residual,
            state.thermal_pv_inner_convergence_residual,
            state.thermal_pv_outer_convergence_residual,
            state.kms_log_ratio_residual,
            state.fdt_residual,
            state.inner_quadrature_convergence_residual,
            state.outer_quadrature_convergence_residual,
            state.thermal_enhancement_ratio,
        )
    )
    checks = {
        "finite_temperature_three_body_cut_completed": state.finite_temperature_three_body_cut_completed,
        "threshold_is_nine_mass_squared": abs(state.three_body_threshold_s - 4.5) <= 1.0e-12,
        "greater_measure_is_positive": state.greater_is_positive,
        "lesser_measure_is_positive": state.lesser_is_positive,
        "spectral_difference_is_positive": state.spectral_difference_is_positive,
        "retarded_i0_channel_is_completed": state.thermal_retarded_i0_channel_completed,
        "retarded_imaginary_part_has_negative_sign": state.retarded_imaginary_sign_witness,
        "channel_sk_kms_match_is_completed": state.three_body_channel_sk_kms_match_completed,
        "kms_log_ratio_matches_beta_energy": state.kms_log_ratio_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "fdt_relation_is_closed": state.fdt_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "vacuum_phase_space_normalization_is_closed": state.vacuum_phase_space_normalization_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "inner_quadrature_converges": state.inner_quadrature_convergence_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "outer_quadrature_converges": state.outer_quadrature_convergence_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "finite_temperature_principal_value_is_completed": state.finite_temperature_principal_value_completed,
        "finite_temperature_principal_value_is_nonzero": state.finite_temperature_principal_value_real_part != 0.0,
        "finite_temperature_pv_inner_converges": state.thermal_pv_inner_convergence_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "finite_temperature_pv_outer_converges": state.thermal_pv_outer_convergence_residual <= FINITE_T_SUNSET_CONVERGENCE_THRESHOLD,
        "state_is_finite": finite_state,
        "full_finite_temperature_1pi_remains_open": not state.full_finite_temperature_1pi_self_energy_completed,
        "all_finite_temperature_sunset_channels_remain_open": not state.all_finite_temperature_sunset_channels_completed,
        "unique_renormalization_remains_open": not state.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "covariant_entropy_remains_open": not state.covariant_entropy_current_completed,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "channel_boundary_is_explicit": contract["included"]["channel_level_sk_kms_match"],
        "thermal_real_part_boundary_is_explicit": contract["included"]["finite_temperature_principal_value_real_part"],
        "full_1pi_boundary_is_explicit": contract["excluded"]["full_finite_temperature_1pi_self_energy"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        FINITE_T_SUNSET_SK_KMS_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE"
    )
    open_blockers = [
        "all_finite_temperature_sunset_channels_missing",
        "full_finite_temperature_1pi_self_energy_missing",
        "full_finite_temperature_all_channel_real_part_and_subtraction_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/uet_o2_finite_temperature_sunset_sk_kms.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_retarded.py", "sha256": sha256(RETARDED_MODULE)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_tensor.py", "sha256": sha256(TENSOR_MODULE)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-sunset-sk-kms-v2",
        "artifact": "t13_uet_o2_finite_temperature_sunset_sk_kms_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "action-derived equal-mass O(2) finite-temperature 1<->3 sunset channel",
                "Bose-weighted greater and lesser channel measures on the same three-body phase space",
                "channel-level KMS log-ratio and FDT noise relation",
                "channel retarded i0 imaginary-part sign and vacuum phase-space normalization",
                "channel pole-subtracted principal-value retarded real part",
                "inner and outer quadrature convergence controls",
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
            "dependency_unlocked": "finite-temperature 1<->3 channel SK/KMS/FDT/PV-real-part and retarded-sign interface only; no full finite-temperature 1PI, physical renormalization, transport, entropy, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "finite_temperature_three_body_cut_completed": state.finite_temperature_three_body_cut_completed,
        "three_body_channel_sk_kms_match_completed": state.three_body_channel_sk_kms_match_completed,
        "thermal_retarded_i0_channel_completed": state.thermal_retarded_i0_channel_completed,
        "finite_temperature_principal_value_completed": state.finite_temperature_principal_value_completed,
        "finite_temperature_principal_value_real_part": state.finite_temperature_principal_value_real_part,
        "thermal_pv_inner_convergence_residual": state.thermal_pv_inner_convergence_residual,
        "thermal_pv_outer_convergence_residual": state.thermal_pv_outer_convergence_residual,
        "full_finite_temperature_1pi_self_energy_completed": state.full_finite_temperature_1pi_self_energy_completed,
        "all_finite_temperature_sunset_channels_completed": state.all_finite_temperature_sunset_channels_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "full_finite_temperature_1pi_all_channels_and_unique_physical_renormalization_missing",
        "next_controller": "extend the action-derived thermal sunset from the named 1<->3 channel to all finite-temperature cuts, then match the complete retarded/advanced/Keldysh 1PI object and its physical subtraction scheme",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE",
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
                "thermal_greater_measure": state.thermal_greater_measure,
                "thermal_lesser_measure": state.thermal_lesser_measure,
                "kms_log_ratio_residual": state.kms_log_ratio_residual,
                "fdt_residual": state.fdt_residual,
                "retarded_imaginary_part": state.retarded_imaginary_part,
                "finite_temperature_principal_value_real_part": state.finite_temperature_principal_value_real_part,
                "thermal_pv_inner_convergence_residual": state.thermal_pv_inner_convergence_residual,
                "thermal_pv_outer_convergence_residual": state.thermal_pv_outer_convergence_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
