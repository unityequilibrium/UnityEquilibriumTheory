"""Audit the action-derived O(2) 1PI sunset tensor interface."""

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

from docs.core.uet_o2_action_1pi_sunset_tensor import (  # noqa: E402
    ACTION_1PI_SUNSET_TENSOR_STATUS,
    action_1pi_sunset_tensor_contract,
    action_1pi_sunset_tensor_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_1pi_sunset_tensor_audit.json"
MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_tensor.py"
ACTION_MODULE = ROOT / "docs/core/uet_o2_action_sunset_1pi_spectral.py"
ZERO_ETA_MODULE = ROOT / "docs/core/uet_o2_action_sunset_zero_eta.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = action_1pi_sunset_tensor_state(
        0.8,
        species_count=2,
        external_species=0,
        reference_invariant_s=0.5,
        probe_invariants_s=(0.36, 0.64, 0.81, 1.21),
    )
    contract = action_1pi_sunset_tensor_contract()
    expected_prefactor = 5.12
    expected_contraction = 30.72
    expected_scattering = 17.92
    expected_ratio = 2.0 / 7.0
    finite_state = all(
        math.isfinite(value)
        for value in (
            state.vertex_tensor_norm,
            state.vertex_contraction_diagonal,
            state.vertex_contraction_off_diagonal_maximum,
            state.sunset_tensor_prefactor,
            state.expected_sunset_tensor_prefactor,
            state.tensor_contraction_residual,
            state.action_scattering_matrix_element_squared,
            state.sunset_to_scattering_prefactor_ratio,
        )
    )
    checks = {
        "action_vertex_tensor_is_completed": state.action_vertex_tensor_completed,
        "sunset_vertex_contraction_is_diagonal": state.vertex_contraction_off_diagonal_maximum
        <= 1.0e-12,
        "o2_raw_vertex_contraction_matches": abs(
            state.vertex_contraction_diagonal - expected_contraction
        )
        <= 1.0e-12,
        "sunset_symmetry_factor_is_one_sixth": abs(
            state.sunset_symmetry_factor - 1.0 / 6.0
        )
        <= 1.0e-15,
        "o2_1pi_sunset_prefactor_matches": abs(
            state.sunset_tensor_prefactor - expected_prefactor
        )
        <= 1.0e-12,
        "tensor_contraction_residual_is_small": state.tensor_contraction_residual
        <= 1.0e-12,
        "action_scattering_comparator_is_independent": abs(
            state.action_scattering_matrix_element_squared - expected_scattering
        )
        <= 1.0e-12,
        "sunset_to_scattering_ratio_is_reported_not_identified": abs(
            state.sunset_to_scattering_prefactor_ratio - expected_ratio
        )
        <= 1.0e-12,
        "local_two_point_counterterm_basis_is_present": set(
            state.two_point_counterterm_basis
        )
        == {"delta_m2", "delta_Z"},
        "action_subdivergence_basis_is_separate": set(
            state.action_subdivergence_counterterm_basis
        )
        == {"delta_m2", "delta_Z", "delta_lambda"},
        "invariant_subtraction_interface_is_matched": state.invariant_subtraction_interface_matched
        and "Sigma_R,ab(s_*)=0" in state.invariant_subtraction_conditions,
        "natural_unit_contract_is_present": contract["unit_contract"][
            "self_energy_and_delta_m2"
        ]
        == "energy squared",
        "state_is_finite": finite_state,
        "full_loop_integral_remains_open": not state.loop_integral_evaluated
        and not state.full_1pi_retarded_self_energy_completed,
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
        "full_off_shell_boundary_is_explicit": contract["excluded"][
            "full_off_shell_loop_integral"
        ],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        ACTION_1PI_SUNSET_TENSOR_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_1PI_SUNSET_TENSOR_INTERFACE_LANE"
    )
    open_blockers = [
        "full_off_shell_1PI_loop_integral_and_retarded_continuation_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "microscopic_SK_KMS_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/uet_o2_action_1pi_sunset_tensor.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/uet_o2_action_sunset_1pi_spectral.py",
            "sha256": sha256(ACTION_MODULE),
        },
        {
            "path": "docs/core/uet_o2_action_sunset_zero_eta.py",
            "sha256": sha256(ZERO_ETA_MODULE),
        },
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-action-1pi-sunset-tensor-v1",
        "artifact": "t13_uet_o2_action_1pi_sunset_tensor_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ACTION_1PI_SUNSET_TENSOR_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "action-derived O(N) four-point tensor and O(2) specialization",
                "three-internal-line sunset vertex contraction",
                "sunset symmetry factor 1/6 and diagonal O(2) 1PI tensor prefactor 8*lambda^2",
                "two-point local counterterm basis delta_m2 and delta_Z, with delta_lambda kept as an action subdivergence requirement",
                "invariant subtraction variable match s=p^2=omega^2 for the declared rest-energy lane",
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
            "dependency_unlocked": "action-derived 1PI sunset tensor and counterterm interface only; no full loop, physical renormalization, SK/KMS, transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "action_vertex_tensor_completed": state.action_vertex_tensor_completed,
        "one_pi_sunset_tensor_completed": state.one_pi_sunset_tensor_completed,
        "local_counterterm_basis_completed": state.local_counterterm_basis_completed,
        "invariant_subtraction_interface_matched": state.invariant_subtraction_interface_matched,
        "full_1pi_retarded_self_energy_completed": state.full_1pi_retarded_self_energy_completed,
        "loop_integral_evaluated": state.loop_integral_evaluated,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_match_completed": state.microscopic_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "full_off_shell_1PI_loop_integral_and_unique_physical_renormalization_missing",
        "next_controller": "evaluate the action-derived off-shell sunset loop with a declared regulator, prove its subtraction/continuation against the zero-eta interface, then match the finite-temperature result to SK/KMS",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_ACTION_1PI_SUNSET_TENSOR_INTERFACE_LANE",
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
                "sunset_tensor_prefactor": state.sunset_tensor_prefactor,
                "tensor_contraction_residual": state.tensor_contraction_residual,
                "action_scattering_matrix_element_squared": state.action_scattering_matrix_element_squared,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
