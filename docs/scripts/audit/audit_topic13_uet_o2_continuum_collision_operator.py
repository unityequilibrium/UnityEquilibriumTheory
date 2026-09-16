"""Audit the conservative continuum-collocation collision lane."""

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

from docs.core.uet_o2_continuum_collision_operator import (  # noqa: E402
    continuum_collision_operator_contract,
    continuum_collision_operator_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_collision_operator_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py"
TRANSITION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"
MOMENTUM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_state(state: object) -> dict[str, object]:
    payload = asdict(state)
    for key in (
        "state_momenta",
        "state_energies",
        "susceptibility_weights",
        "collision_widths",
        "continuum_operator",
        "action_width_operator",
        "transition_vertex_operator",
        "source_vector",
        "projected_source_vector",
    ):
        payload.pop(key, None)
    payload["continuum_operator_shape"] = [state.state_count, state.state_count]
    payload["transition_vertex_operator_shape"] = [state.state_count, state.state_count]
    return payload


def _max_residual(values: tuple[tuple[float, ...], ...]) -> float:
    return max(max(abs(value) for value in row) for row in values)


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    reference = continuum_collision_operator_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=8,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=48.0,
        transition_quadrature_order=24,
        transition_channel_count=64,
        transition_interpolation_order=40,
    )
    refined = continuum_collision_operator_state(
        0.22,
        0.35,
        0.15,
        config,
        radial_order=10,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=48.0,
        transition_quadrature_order=24,
        transition_channel_count=96,
        transition_interpolation_order=40,
    )
    contract = continuum_collision_operator_contract()
    eigenvalues = reference.collision_operator_eigenvalues
    positive_frequency_indices = tuple(
        index
        for index, ratio in enumerate(reference.retarded_frequency_over_rate)
        if ratio > 0.0
    )
    refinement_response_change = abs(refined.dc_response - reference.dc_response) / max(
        abs(reference.dc_response), 1.0e-300
    )
    checks = {
        "shared_continuum_basis_is_present": reference.state_count >= 48,
        "exact_transition_channels_are_present": reference.transition_channel_count >= 8,
        "interpolation_columns_are_normalized": (
            reference.interpolation_column_sum_residual <= 1.0e-12
        ),
        "transition_support_is_connected": reference.transition_support_connected,
        "all_basis_states_are_covered": reference.basis_coverage_count == reference.state_count,
        "exact_channel_kinematics_are_conserved": (
            _max_residual(reference.exact_channel_invariant_residuals) <= 1.0e-10
        ),
        "exact_channel_detailed_balance_holds": (
            max(reference.exact_channel_detailed_balance_residuals) <= 1.0e-10
        ),
        "conservative_projection_removes_mapped_invariant_residual": (
            reference.projected_mapped_invariant_residual <= 1.0e-10
            and reference.raw_mapped_invariant_residual > 1.0e-8
        ),
        "charge_energy_momentum_invariant_rank_is_five": reference.invariant_rank == 5,
        "collision_operator_preserves_invariants": (
            reference.collision_conservation_residual <= 1.0e-10
        ),
        "collision_operator_is_symmetric": reference.operator_symmetry_residual <= 1.0e-12,
        "collision_operator_is_positive_semidefinite": (
            reference.positive_semidefinite_min_eigenvalue >= -1.0e-12
        ),
        "physical_zero_mode_count_is_five": reference.null_mode_count == 5,
        "all_nonconserved_modes_are_present": (
            sum(value > 1.0e-12 for value in eigenvalues)
            >= reference.state_count - reference.invariant_rank
        ),
        "transition_vertex_correction_is_present": (
            reference.transition_vertex_trace_ratio > 0.0
        ),
        "vertex_decomposition_is_exact": reference.vertex_decomposition_residual <= 1.0e-12,
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
        "fixed_cutoff_refinement_is_recorded": (
            refined.state_count > reference.state_count
            and refined.transition_channel_count > reference.transition_channel_count
            and isfinite(refinement_response_change)
        ),
        "continuum_limit_is_not_claimed": reference.continuum_limit_completed is False,
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
        "finite_cutoff_boundary_is_declared": reference.finite_cutoff_boundary_declared,
        "microscopic_scope_exclusions_are_explicit": (
            contract["excluded"]["microscopic_bethe_salpeter_vertex"] is True
            and contract["excluded"]["microscopic_sk_action_match"] is True
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(TRANSITION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py", "sha256": sha256(MOMENTUM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-conservative-continuum-collocation-v1",
        "artifact": "t13_uet_o2_continuum_collision_operator_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "a shared finite-temperature momentum basis is connected by an explicit transition-support graph",
                "exact action-derived two-to-two channel samples are mapped into the basis by a normalized interpolation matrix",
                "a Gram projection removes the mapped charge and four-momentum residual without changing the declared conserved moments",
                "the action-derived width operator plus projected transition vertex forms a symmetric positive semidefinite finite-cutoff operator with five physical zero modes",
                "the conservative operator decomposition, retarded response, algebraic Bethe-Salpeter identity, KMS/FDT interface, and entropy witness are verified",
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
                "continuum_limit_missing",
                "microscopic_bethe_salpeter_vertex_match_missing",
                "microscopic_SK_action_and_KMS_match_missing",
                "full_entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "named finite-cutoff conservative continuum-collocation operator and algebraic vertex/KMS interface only; no continuum-limit, microscopic, physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": compact_state(reference),
            "refined": compact_state(refined),
            "fixed_cutoff_refinement_response_change": refinement_response_change,
        },
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": False,
        "microscopic_bethe_salpeter_match_completed": False,
        "microscopic_sk_kms_match_completed": False,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_bethe_salpeter_vertex_and_SK_action_match_missing",
        "next_controller": "derive a microscopic vertex and SK/KMS action match on top of the connected finite-cutoff operator; keep continuum-limit, entropy-current, dimensional, source, and alpha gates independent",
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
                "reference": {
                    "state_count": reference.state_count,
                    "channel_count": reference.transition_channel_count,
                    "support_components": reference.transition_support_component_count,
                    "basis_coverage": reference.basis_coverage_count,
                    "invariant_rank": reference.invariant_rank,
                    "null_mode_count": reference.null_mode_count,
                    "projected_invariant_residual": reference.projected_mapped_invariant_residual,
                    "raw_invariant_residual": reference.raw_mapped_invariant_residual,
                    "response": reference.dc_response,
                    "vertex_trace_ratio": reference.transition_vertex_trace_ratio,
                    "max_bs_residual": max(reference.bs_match_residuals),
                    "entropy_production_witness": reference.entropy_production_witness,
                },
                "refinement_response_change": refinement_response_change,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
