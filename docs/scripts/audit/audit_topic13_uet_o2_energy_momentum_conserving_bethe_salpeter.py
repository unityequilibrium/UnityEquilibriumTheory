"""Audit the finite-grid energy-momentum conserving BS/KMS interface lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from math import isfinite
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import (  # noqa: E402
    energy_momentum_conserving_bs_contract,
    energy_momentum_conserving_bs_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_energy_momentum_conserving_bethe_salpeter_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py"
MOMENTUM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_momentum_ladder_sk_kms.py"
COLLISION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_change(values: tuple[float, ...], reference: tuple[float, ...]) -> float:
    return max(
        abs(value - baseline) / max(abs(baseline), 1.0e-30)
        for value, baseline in zip(values, reference)
    )


def compact_state(state: object) -> dict[str, object]:
    payload = asdict(state)
    for key in (
        "conserved_invariants",
        "projector",
        "collision_operator",
        "source_vector",
        "projected_source_vector",
    ):
        payload.pop(key, None)
    payload["conserved_invariants_shape"] = [state.state_count, 5]
    payload["projector_shape"] = [state.state_count, state.state_count]
    payload["collision_operator_shape"] = [state.state_count, state.state_count]
    return payload


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    reference = energy_momentum_conserving_bs_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=28,
        collision_integration_order=48,
        angular_order=32,
        cutoff_factor=48.0,
    )
    refined = energy_momentum_conserving_bs_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=32,
        collision_integration_order=48,
        angular_order=32,
        cutoff_factor=48.0,
    )
    angular_refined = energy_momentum_conserving_bs_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=28,
        collision_integration_order=48,
        angular_order=40,
        cutoff_factor=48.0,
    )
    contract = energy_momentum_conserving_bs_contract()
    response_change = relative_change(
        refined.retarded_response_real,
        reference.retarded_response_real,
    )
    angular_response_change = relative_change(
        angular_refined.retarded_response_real,
        reference.retarded_response_real,
    )
    eigenvalues = reference.collision_operator_eigenvalues
    state_count = reference.state_count
    null_mode_count = sum(abs(value) <= 1.0e-12 for value in eigenvalues)
    positive_frequency_indices = tuple(
        index
        for index, ratio in enumerate(reference.retarded_frequency_over_rate)
        if ratio > 0.0
    )
    checks = {
        "six_direction_grid_is_explicit": reference.direction_count == 6,
        "two_species_and_momentum_count_are_consistent": (
            state_count == 2 * reference.radial_order * reference.direction_count
        ),
        "all_charge_energy_and_momentum_invariants_are_independent": (
            reference.invariant_rank == 5
        ),
        "five_conserved_zero_modes_are_present": (
            null_mode_count == 5
            and sum(value > 1.0e-12 for value in eigenvalues) == state_count - 5
        ),
        "projector_annihilates_conserved_subspace": (
            reference.invariant_projection_residual <= 1.0e-12
        ),
        "collision_operator_preserves_all_five_moments": (
            reference.collision_conservation_residual <= 1.0e-10
        ),
        "projected_operator_is_symmetric": reference.operator_symmetry_residual <= 1.0e-12,
        "projected_operator_is_positive_semidefinite": (
            reference.positive_semidefinite_min_eigenvalue >= -1.0e-12
        ),
        "momentum_widths_are_not_single_reference_width": (
            reference.collision_width_relative_spread > 0.1
        ),
        "projected_source_is_orthogonal_to_all_conserved_moments": (
            reference.source_constraint_residual <= 1.0e-12
        ),
        "retarded_real_response_is_positive": all(
            value >= 0.0 and isfinite(value)
            for value in reference.retarded_response_real
        ),
        "retarded_real_response_is_nonincreasing": all(
            later <= earlier + 1.0e-10
            for earlier, later in zip(
                reference.retarded_response_real,
                reference.retarded_response_real[1:],
            )
        ),
        "retarded_imaginary_response_has_declared_sign": all(
            reference.retarded_response_imag[index] > 0.0
            for index in positive_frequency_indices
        ),
        "state_grid_response_converges_at_fixed_cutoff": response_change <= 0.02,
        "angular_grid_response_is_stable_at_fixed_cutoff": angular_response_change <= 0.02,
        "cutoff_is_explicitly_fixed_for_this_lane": (
            reference.momentum_cutoff == refined.momentum_cutoff == angular_refined.momentum_cutoff
        ),
        "algebraic_bethe_salpeter_identity_is_resolved": (
            max(reference.bs_match_residuals) <= 1.0e-10
        ),
        "kms_spectral_density_is_positive": all(
            value > 0.0 and isfinite(value)
            for value in reference.kms_spectral_density
        ),
        "kms_greater_and_lesser_are_positive": all(
            greater > lesser > 0.0
            for greater, lesser in zip(
                reference.kms_greater,
                reference.kms_lesser,
            )
        ),
        "kms_ratio_matches_boltzmann_factor": all(
            abs(value - target) / target <= 1.0e-12
            for value, target in zip(
                reference.kms_ratio,
                reference.kms_target_ratio,
            )
        ),
        "fdt_noise_matches_coth_target": all(
            abs(value - target) / max(abs(target), 1.0e-30) <= 1.0e-12
            for value, target in zip(
                reference.kms_noise,
                reference.kms_noise_target,
            )
        ),
        "entropy_production_witness_is_positive": (
            reference.entropy_production_witness > 0.0
            and isfinite(reference.entropy_production_witness)
        ),
        "full_energy_momentum_constraint_flag_is_explicit": (
            reference.full_energy_momentum_constraints_included is True
        ),
        "microscopic_bethe_salpeter_match_not_claimed": (
            reference.microscopic_bethe_salpeter_match_completed is False
        ),
        "microscopic_sk_kms_match_not_claimed": (
            reference.microscopic_sk_kms_match_completed is False
        ),
        "physical_kubo_coefficient_not_emitted": (
            reference.physical_kubo_coefficient_emitted is False
        ),
        "numeric_alpha_not_emitted": reference.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": reference.parameter_fitting_performed is False,
        "no_target_or_holdout": (
            reference.target_data_used is False and reference.xie_2026_accessed is False
        ),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "finite_cutoff_boundary_is_declared": "finite-grid" in contract["claim_boundary"],
        "physical_scope_exclusions_are_explicit": (
            contract["excluded"]["microscopic_two_to_two_transition_kernel"] is True
            and contract["excluded"]["physical_kubo_coefficient"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_FULL_MOMENT_CONSERVING_BS_INTERFACE_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_FULL_MOMENT_CONSERVING_BS_INTERFACE_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_momentum_ladder_sk_kms.py", "sha256": sha256(MOMENTUM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(COLLISION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-energy-momentum-conserving-bs-v1",
        "artifact": "t13_uet_o2_energy_momentum_conserving_bethe_salpeter_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ENERGY_MOMENTUM_CONSERVING_BS_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "a six-direction finite momentum grid carries independent charge, energy, and three spatial-momentum invariant columns",
                "a positive semidefinite projected collision operator preserves all five declared conserved moments",
                "the momentum-current retarded response is stable under fixed-cutoff radial and angular refinement",
                "an algebraic Bethe-Salpeter resolvent identity is verified without claiming a microscopic vertex",
                "the same formal response is paired with algebraic KMS/FDT and entropy-positivity checks",
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
            "open_blockers": [
                "finite_cutoff_limit_missing",
                "microscopic_two_to_two_transition_kernel_missing",
                "microscopic_bethe_salpeter_vertex_match_missing",
                "microscopic_SK_action_and_KMS_match_missing",
                "full_entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "named finite-grid charge and four-momentum conserving response plus algebraic Bethe-Salpeter/KMS interface only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": compact_state(reference),
            "refined": compact_state(refined),
            "angular_refined": compact_state(angular_refined),
            "relative_response_change_refined_vs_reference": response_change,
            "relative_response_change_angular_refined_vs_reference": angular_response_change,
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_transition_kernel_and_vertex_SK_match_missing",
        "next_controller": "derive an action-derived two-to-two transition kernel with detailed balance and match its ladder vertex to the SK/KMS interface without consuming Xie 2026",
        "claim_promotion": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "state_count": state_count,
                "invariant_rank": reference.invariant_rank,
                "null_mode_count": null_mode_count,
                "relative_response_change": response_change,
                "angular_response_change": angular_response_change,
                "max_bs_match_residual": max(reference.bs_match_residuals),
                "entropy_production_witness": reference.entropy_production_witness,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
