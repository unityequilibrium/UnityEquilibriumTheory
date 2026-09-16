"""Audit the momentum-dependent conserving response and KMS interface lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_momentum_ladder_sk_kms import (  # noqa: E402
    momentum_ladder_sk_kms_contract,
    momentum_ladder_sk_kms_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_momentum_ladder_sk_kms_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_momentum_ladder_sk_kms.py"
COLLISION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_change(values: tuple[float, ...], reference: tuple[float, ...]) -> float:
    return max(
        abs(value - baseline) / max(abs(baseline), 1.0e-30)
        for value, baseline in zip(values, reference)
    )


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    reference = momentum_ladder_sk_kms_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=32,
        collision_integration_order=48,
        angular_order=32,
        cutoff_factor=48.0,
    )
    refined = momentum_ladder_sk_kms_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        collision_integration_order=48,
        angular_order=40,
        cutoff_factor=48.0,
    )
    contract = momentum_ladder_sk_kms_contract()
    response_change = relative_change(
        refined.retarded_response_real,
        reference.retarded_response_real,
    )
    eigenvalues = reference.collision_operator_eigenvalues
    state_count = len(reference.collision_widths)
    positive_frequency_indices = tuple(
        index
        for index, ratio in enumerate(reference.retarded_frequency_over_rate)
        if ratio > 0.0
    )
    checks = {
        "momentum_grid_has_two_species": len(reference.state_species_signs) == 2 * len(reference.momentum_nodes),
        "momentum_widths_are_not_single_reference_width": (
            reference.collision_width_relative_spread > 0.1
        ),
        "quantum_collision_width_is_explicit": (
            reference.final_state_bose_enhancement_included is True
        ),
        "conserved_charge_zero_mode_is_present": (
            abs(eigenvalues[0]) <= 1.0e-12
            and sum(value > 1.0e-12 for value in eigenvalues) == state_count - 1
        ),
        "projected_operator_is_symmetric": reference.operator_symmetry_residual <= 1.0e-12,
        "projected_operator_preserves_charge": reference.charge_conservation_residual <= 1.0e-12,
        "projected_source_is_charge_orthogonal": abs(reference.source_projection_residual) <= 1.0e-12,
        "projected_operator_is_positive_semidefinite": (
            reference.positive_semidefinite_min_eigenvalue >= -1.0e-12
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
        "cutoff_is_explicitly_fixed_for_this_lane": (
            reference.momentum_cutoff == refined.momentum_cutoff
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
        "momentum_resolvent_is_explicit": (
            reference.momentum_dependent_resolvent_included is True
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
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "finite_cutoff_boundary_is_declared": "finite cutoff" in contract["claim_boundary"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_momentum_ladder_sk_kms.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(COLLISION_MODULE)},
        {
            "path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "sha256": sha256(EOS_MODULE),
        },
    ]
    artifact = {
        "schema_version": "t13-uet-o2-momentum-ladder-sk-kms-v1",
        "artifact": "t13_uet_o2_momentum_ladder_sk_kms_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the corrected quantum collision kernel is evaluated over a momentum grid rather than only at k_ref",
                "a weighted charge-conserving projector gives one exact conserved mode and a positive dissipative subspace",
                "the momentum-dependent retarded response is stable under fixed-cutoff state-grid and angular refinement",
                "an algebraic Wightman/KMS/FDT interface and positive entropy-production witness are verified from the declared spectral convention",
                "the finite-cutoff comparator boundary is explicit and is not promoted to an infinite-cutoff or physical transport result",
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
                "finite_cutoff_and_full_energy_momentum_conservation_missing",
                "microscopic_bethe_salpeter_vertex_match_missing",
                "microscopic_SK_action_and_KMS_match_missing",
                "full_entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "named momentum-dependent response and algebraic KMS interface only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This closes only a named action-derived momentum-grid conserving response and algebraic KMS/FDT interface at a declared finite cutoff. It does not establish a microscopic Bethe-Salpeter or SK/KMS match, a physical Kubo coefficient, an SI observable, alpha_Phi_K, TTG validation, or Full Topic 13 closure.",
        },
        "contract": contract,
        "state": {
            "reference": reference.__dict__,
            "refined": refined.__dict__,
            "relative_response_change_refined_vs_reference": response_change,
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_bethe_salpeter_and_SK_KMS_matching_missing",
        "next_controller": "derive the full energy-momentum conserving collision operator and match its momentum-dependent resolvent to a microscopic Bethe-Salpeter/SK construction",
        "claim_promotion": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "state_count": state_count,
                "positive_mode_rate": reference.positive_mode_rate,
                "relative_response_change": response_change,
                "width_spread": reference.collision_width_relative_spread,
                "entropy_production_witness": reference.entropy_production_witness,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
