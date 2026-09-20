"""Audit the declared finite-temperature sunset cut composition."""

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

from docs.core.uet_o2_finite_temperature_full_sunset_sk_kms import (  # noqa: E402
    FINITE_T_FULL_SUNSET_CONVERGENCE_THRESHOLD,
    FINITE_T_FULL_SUNSET_SK_KMS_STATUS,
    finite_temperature_full_sunset_sk_kms_contract,
    finite_temperature_full_sunset_sk_kms_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_full_sunset_sk_kms_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_full_sunset_sk_kms.py"
ONE_TO_THREE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py"
TWO_TO_TWO = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_full_sunset_sk_kms_state(0.35, 0.5, 0.8)
    contract = finite_temperature_full_sunset_sk_kms_contract()
    finite_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key not in {"species_count"}
    )
    finite_state = all(math.isfinite(float(value)) for value in finite_values)
    threshold = FINITE_T_FULL_SUNSET_CONVERGENCE_THRESHOLD
    checks = {
        "declared_timelike_order_lambda2_cut_partition_completed": state.declared_timelike_order_lambda2_cut_partition_completed,
        "one_to_three_channel_completed": state.one_to_three_channel_completed,
        "two_to_two_channel_completed": state.two_to_two_channel_completed,
        "matched_invariant_and_normalization": state.same_invariant_and_normalization_witness,
        "combined_greater_measure_is_positive": state.combined_greater_measure > 0.0,
        "combined_lesser_measure_is_positive": state.combined_lesser_measure > 0.0,
        "combined_spectral_difference_is_positive": state.combined_spectral_measure > 0.0,
        "combined_retarded_i0_is_completed": state.combined_retarded_i0_completed,
        "combined_retarded_imaginary_part_has_negative_sign": state.combined_retarded_imaginary_part < 0.0,
        "combined_channel_sk_kms_match_is_completed": state.combined_channel_sk_kms_match_completed,
        "combined_kms_log_ratio_matches_beta_energy": state.combined_kms_log_ratio_residual <= threshold,
        "combined_fdt_relation_is_closed": state.combined_fdt_residual <= threshold,
        "combined_principal_value_is_completed": state.combined_pole_subtracted_real_part_completed,
        "combined_principal_value_is_nonzero": state.combined_principal_value_real_part != 0.0,
        "one_to_three_pv_converges": max(
            state.one_to_three_pv_inner_convergence_residual,
            state.one_to_three_pv_outer_convergence_residual,
        ) <= threshold,
        "two_to_two_pv_converges": max(
            state.two_to_two_pv_inner_convergence_residual,
            state.two_to_two_pv_outer_convergence_residual,
        ) <= threshold,
        "combined_pv_inner_converges": state.combined_pv_inner_convergence_residual <= threshold,
        "combined_pv_outer_converges": state.combined_pv_outer_convergence_residual <= threshold,
        "aggregate_pv_witness_is_conservative": state.aggregate_pv_convergence_is_conservative_bound,
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
        "declared_partition_is_included": contract["included"]["declared_timelike_order_lambda2_cut_partition"],
        "complete_1pi_boundary_is_explicit": contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        FINITE_T_FULL_SUNSET_SK_KMS_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE"
    )
    open_blockers = [
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_full_sunset_sk_kms.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py", "sha256": sha256(ONE_TO_THREE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py", "sha256": sha256(TWO_TO_TWO)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-declared-full-sunset-sk-kms-v1",
        "artifact": "t13_uet_o2_finite_temperature_full_sunset_sk_kms_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "declared timelike equal-mass order-lambda^2 sunset thermal-cut partition into 1<->3 and labeled 2<->2 channels",
                "matched action normalization and common invariant composition of the two channel states",
                "summed greater, lesser, spectral, and retarded i0 quantities",
                "combined channel KMS log-ratio and FDT noise relation",
                "compositional pole-subtracted real part with conservative component convergence bound",
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
            "dependency_unlocked": "declared finite-temperature sunset cut composition and summed SK/KMS/FDT/PV interface only; no complete 1PI, physical renormalization, transport, entropy, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "declared_timelike_order_lambda2_cut_partition_completed": state.declared_timelike_order_lambda2_cut_partition_completed,
        "combined_channel_sk_kms_match_completed": state.combined_channel_sk_kms_match_completed,
        "combined_retarded_i0_completed": state.combined_retarded_i0_completed,
        "combined_pole_subtracted_real_part_completed": state.combined_pole_subtracted_real_part_completed,
        "combined_principal_value_real_part": state.combined_principal_value_real_part,
        "combined_kms_log_ratio_residual": state.combined_kms_log_ratio_residual,
        "combined_fdt_residual": state.combined_fdt_residual,
        "combined_pv_inner_convergence_residual": state.combined_pv_inner_convergence_residual,
        "combined_pv_outer_convergence_residual": state.combined_pv_outer_convergence_residual,
        "full_finite_temperature_1pi_self_energy_completed": state.full_finite_temperature_1pi_self_energy_completed,
        "all_finite_temperature_sunset_channels_completed": state.all_finite_temperature_sunset_channels_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "complete_off_shell_finite_temperature_1pi_and_unique_physical_renormalization_missing",
        "next_controller": "derive the complete off-shell retarded/advanced/Keldysh 1PI object and a physical renormalization scheme before transport and entropy closure",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE",
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
                "combined_greater_measure": state.combined_greater_measure,
                "combined_lesser_measure": state.combined_lesser_measure,
                "combined_spectral_measure": state.combined_spectral_measure,
                "combined_retarded_imaginary_part": state.combined_retarded_imaginary_part,
                "combined_principal_value_real_part": state.combined_principal_value_real_part,
                "combined_kms_log_ratio_residual": state.combined_kms_log_ratio_residual,
                "combined_fdt_residual": state.combined_fdt_residual,
                "combined_pv_inner_convergence_residual": state.combined_pv_inner_convergence_residual,
                "combined_pv_outer_convergence_residual": state.combined_pv_outer_convergence_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
