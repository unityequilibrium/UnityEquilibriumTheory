"""Audit the regulated Euclidean off-shell O(2) sunset interface."""

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
    EUCLIDEAN_1PI_SUNSET_STATUS,
    euclidean_1pi_sunset_contract,
    euclidean_1pi_sunset_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_1pi_sunset_euclidean_audit.json"
MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_euclidean.py"
TENSOR_MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_tensor.py"
ZERO_ETA_MODULE = ROOT / "docs/core/uet_o2_action_sunset_zero_eta.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = euclidean_1pi_sunset_state(0.5, 0.8)
    contract = euclidean_1pi_sunset_contract()
    finite_state = all(
        math.isfinite(value)
        for values in (
            state.loop_integral_values_at_last_cutoff,
            state.raw_self_energy_values_at_last_cutoff,
            state.twice_subtracted_self_energy_values,
        )
        for value in values
    ) and all(
        math.isfinite(value)
        for value in (
            state.sunset_tensor_prefactor,
            state.loop_integral_derivative_at_reference,
            state.cutoff_convergence_residual,
            state.quadrature_convergence_residual,
        )
    )
    checks = {
        "euclidean_loop_integral_completed": state.euclidean_loop_integral_completed,
        "proper_time_regulator_is_declared": contract["included"][
            "proper_time_regulator"
        ]
        and "alpha_i>=Lambda^-2" in contract["equations"][
            "euclidean_sunset_integral"
        ],
        "o2_sunset_prefactor_matches": abs(
            state.sunset_tensor_prefactor - 5.12
        )
        <= 1.0e-12,
        "reference_subtraction_condition_passes": state.reference_subtraction_residual
        <= 1.0e-30,
        "reference_derivative_condition_passes": state.reference_derivative_residual
        <= 1.0e-30
        and state.twice_subtracted_derivative_at_reference <= 1.0e-30,
        "subtracted_response_is_nonzero_off_reference": state.nonzero_subtracted_response_witness,
        "cutoff_sequence_converges": state.cutoff_convergence_passed,
        "quadrature_sequence_converges": state.quadrature_convergence_passed,
        "state_is_finite": finite_state,
        "retarded_continuation_remains_open": not state.retarded_continuation_completed
        and not state.full_1pi_retarded_self_energy_completed,
        "unique_renormalization_remains_open": not state.unique_physical_renormalization_scheme_match_completed,
        "finite_temperature_completion_remains_open": not state.finite_temperature_completion_completed,
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
        "retarded_boundary_is_explicit": contract["excluded"][
            "retarded_analytic_continuation"
        ],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        EUCLIDEAN_1PI_SUNSET_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_EUCLIDEAN_1PI_SUNSET_REGULATED_SUBTRACTION_LANE"
    )
    open_blockers = [
        "retarded_i0_analytic_continuation_missing",
        "full_retarded_1PI_self_energy_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "finite_temperature_self_energy_and_SK_KMS_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/uet_o2_action_1pi_sunset_euclidean.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_tensor.py", "sha256": sha256(TENSOR_MODULE)},
        {"path": "docs/core/uet_o2_action_sunset_zero_eta.py", "sha256": sha256(ZERO_ETA_MODULE)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-action-1pi-sunset-euclidean-v1",
        "artifact": "t13_uet_o2_action_1pi_sunset_euclidean_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_EUCLIDEAN_1PI_SUNSET_REGULATED_SUBTRACTION_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "finite proper-time regulated equal-mass Euclidean off-shell sunset loop",
                "explicit Schwinger determinant and three-parameter integrand",
                "twice-subtracted invariant BPHZ conditions at the declared reference s_*",
                "cutoff-sequence convergence and refined log-quadrature convergence",
                "nonzero off-reference Euclidean self-energy response",
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
            "dependency_unlocked": "regulated Euclidean off-shell 1PI sunset and invariant subtraction only; no retarded, physical renormalization, finite-T SK/KMS, transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "euclidean_loop_integral_completed": state.euclidean_loop_integral_completed,
        "invariant_bphz_subtraction_completed": state.invariant_bphz_subtraction_completed,
        "full_1pi_retarded_self_energy_completed": state.full_1pi_retarded_self_energy_completed,
        "retarded_continuation_completed": state.retarded_continuation_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "finite_temperature_completion_completed": state.finite_temperature_completion_completed,
        "microscopic_sk_kms_match_completed": state.microscopic_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "retarded_i0_analytic_continuation_and_unique_physical_renormalization_missing",
        "next_controller": "derive the retarded analytic continuation of the regulated Euclidean sunset, compare its discontinuity with the action-matched zero-eta cut, and then perform the finite-temperature SK/KMS match",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_EUCLIDEAN_1PI_SUNSET_REGULATED_SUBTRACTION_LANE",
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
                "cutoff_convergence_residual": state.cutoff_convergence_residual,
                "quadrature_convergence_residual": state.quadrature_convergence_residual,
                "reference_subtraction_residual": state.reference_subtraction_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
