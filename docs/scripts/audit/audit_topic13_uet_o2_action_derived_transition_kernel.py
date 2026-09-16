"""Audit the exact-kinematic action-derived two-to-two transition lane."""

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

from docs.core.uet_o2_action_derived_transition_kernel import (  # noqa: E402
    action_derived_transition_kernel_contract,
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_derived_transition_kernel_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"
MOMENTUM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py"
COLLISION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_state(state: object) -> dict[str, object]:
    payload = asdict(state)
    for key in (
        "transition_vectors",
        "collision_operator",
        "source_vector",
        "active_source_vector",
    ):
        payload.pop(key, None)
    payload["transition_vector_shape"] = [state.channel_count, state.state_count]
    payload["collision_operator_shape"] = [state.state_count, state.state_count]
    return payload


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    reference = action_derived_transition_kernel_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=24,
        channel_count=12,
        cutoff_factor=36.0,
    )
    enriched = action_derived_transition_kernel_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=24,
        channel_count=16,
        cutoff_factor=36.0,
    )
    contract = action_derived_transition_kernel_contract()
    eigenvalues = reference.collision_operator_eigenvalues
    positive_frequency_indices = tuple(
        index
        for index, ratio in enumerate(reference.retarded_frequency_over_rate)
        if ratio > 0.0
    )
    checks = {
        "exact_kinematic_channel_boundary_is_explicit": (
            reference.exact_kinematics_declared is True
        ),
        "channel_count_and_state_count_are_consistent": (
            reference.state_count == 4 * reference.channel_count
        ),
        "all_channels_have_positive_rates": all(value > 0.0 for value in reference.channel_rates),
        "channel_energy_momentum_residuals_are_small": all(
            max(abs(value) for value in residual) <= 1.0e-10
            for residual in reference.channel_invariant_residuals
        ),
        "forward_reverse_detailed_balance_holds": (
            reference.detailed_balance_checked is True
            and max(reference.channel_detailed_balance_residuals) <= 1.0e-10
        ),
        "charge_energy_momentum_invariant_rank_is_five": (
            reference.invariant_matrix_rank == 5
        ),
        "collision_operator_preserves_invariants": (
            reference.collision_conservation_residual <= 1.0e-10
        ),
        "collision_operator_is_symmetric": reference.operator_symmetry_residual <= 1.0e-12,
        "collision_operator_is_positive_semidefinite": (
            reference.positive_semidefinite_min_eigenvalue >= -1.0e-12
        ),
        "positive_channel_modes_are_present": (
            sum(value > 0.0 for value in eigenvalues) >= reference.channel_count
        ),
        "finite_channel_nullspace_is_declared": reference.null_mode_count >= 5,
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
            abs(value - target) / max(abs(target), 1.0e-300) <= 1.0e-12
            for value, target in zip(
                reference.kms_noise,
                reference.kms_noise_target,
            )
        ),
        "entropy_production_witness_is_positive": (
            reference.entropy_production_witness > 0.0
            and isfinite(reference.entropy_production_witness)
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
        "finite_channel_boundary_is_declared": "finite exact-kinematic" in contract["claim_boundary"],
        "microscopic_scope_exclusions_are_explicit": (
            contract["excluded"]["microscopic_bethe_salpeter_vertex"] is True
            and contract["excluded"]["microscopic_sk_action_match"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py", "sha256": sha256(MOMENTUM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(COLLISION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-action-derived-transition-kernel-v1",
        "artifact": "t13_uet_o2_action_derived_transition_kernel_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "elastic two-to-two channels are generated by exact center-of-mass kinematics and boosts",
                "action-derived constant-amplitude cross sections and final-state Bose weights are explicit",
                "forward and reverse equilibrium weights satisfy detailed balance channel by channel",
                "the finite channel outer-product operator is symmetric positive semidefinite and preserves charge and four-momentum",
                "the active retarded response, algebraic Bethe-Salpeter identity, KMS/FDT interface, and entropy witness are verified",
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
                "connected_continuum_collision_operator_missing",
                "finite_channel_limit_missing",
                "microscopic_bethe_salpeter_vertex_match_missing",
                "microscopic_SK_action_and_KMS_match_missing",
                "full_entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "named finite exact-kinematic transition-kernel and detailed-balance response interface only; no microscopic vertex, physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": compact_state(reference),
            "channel_enriched": compact_state(enriched),
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "connected_continuum_collision_operator_and_microscopic_vertex_missing",
        "next_controller": "connect the exact-kinematic channels into a continuum collision operator and match its vertex to the microscopic SK/KMS construction without consuming Xie 2026",
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
                "channel_count": reference.channel_count,
                "state_count": reference.state_count,
                "invariant_rank": reference.invariant_matrix_rank,
                "null_mode_count": reference.null_mode_count,
                "max_kinematic_residual": max(max(abs(value) for value in residual) for residual in reference.channel_invariant_residuals),
                "max_detailed_balance_residual": max(reference.channel_detailed_balance_residuals),
                "max_bs_match_residual": max(reference.bs_match_residuals),
                "entropy_production_witness": reference.entropy_production_witness,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
