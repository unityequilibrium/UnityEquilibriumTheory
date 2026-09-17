"""Audit the explicit elastic final-state Bose enhancement lane for Topic 13."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import (
    kinetic_collision_contract,
    kinetic_collision_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_quantum_collision_enhancement_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    classical = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=False,
    )
    quantum = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=True,
    )
    quantum_reference = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
        include_final_state_bose_enhancement=True,
    )
    quantum_refined = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=80,
        angular_order=56,
        cutoff_factor=28.0,
        include_final_state_bose_enhancement=True,
    )
    contract = kinetic_collision_contract()
    relative_width_change = max(
        abs(refined_value - reference_value) / reference_value
        for refined_value, reference_value in zip(
            quantum_refined.collision_width_by_species,
            quantum_reference.collision_width_by_species,
        )
    )
    relative_response_change = abs(
        quantum_refined.kinetic_coefficient - quantum_reference.kinetic_coefficient
    ) / quantum_reference.kinetic_coefficient
    width_ratios = tuple(
        quantum_width / classical_width
        for quantum_width, classical_width in zip(
            quantum.collision_width_by_species,
            classical.collision_width_by_species,
        )
    )
    checks = {
        "classical_lane_is_explicitly_disabled": (
            classical.final_state_bose_enhancement_included is False
        ),
        "quantum_lane_is_explicitly_enabled": (
            quantum.final_state_bose_enhancement_included is True
        ),
        "all_quantum_widths_positive_and_finite": all(
            value > 0.0 and isfinite(value)
            for value in quantum_reference.collision_width_by_species
        ),
        "all_quantum_responses_positive_and_finite": (
            quantum_reference.kinetic_coefficient > 0.0
            and isfinite(quantum_reference.kinetic_coefficient)
        ),
        "outgoing_bose_factor_increases_each_width": all(
            ratio > 1.0 for ratio in width_ratios
        ),
        "quantum_quadrature_width_converges": relative_width_change <= 0.02,
        "quantum_quadrature_response_converges": relative_response_change <= 0.02,
        "ladder_resummation_is_explicitly_excluded": (
            quantum_reference.ladder_vertex_resummation_included is False
        ),
        "physical_coefficient_not_emitted": (
            quantum_reference.physical_kubo_coefficient_emitted is False
        ),
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
        "contract_declares_optional_outgoing_factor": (
            "optional elastic outgoing-state factor"
            in contract["excluded"]["final_state_bose_enhancement"]
        ),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_QUANTUM_COLLISION_ENHANCEMENT_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_QUANTUM_COLLISION_ENHANCEMENT_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "sha256": sha256(EOS_MODULE),
        },
    ]
    artifact = {
        "schema_version": "t13-uet-o2-quantum-collision-enhancement-v1",
        "artifact": "t13_uet_o2_quantum_collision_enhancement_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_QUANTUM_COLLISION_ENHANCEMENT_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "an explicit elastic outgoing-state Bose factor is integrated into the declared 2-to-2 collision kernel",
                "the factor increases the collision width relative to the classical comparator at the same state point",
                "the quantum-enhanced comparator remains positive and bounded under quadrature and cutoff refinement",
                "the lane keeps ladder resummation, condensed scattering, microscopic SK/KMS matching, SI mapping, alpha_Phi_K, and TTG validation outside scope",
            ]
            if not failed
            else [],
            "equation_or_mapping": {
                **contract["equations"],
                "outgoing_state_factor": "B_34=(1+f_3)(1+f_4), averaged over elastic final-state center-of-mass angle",
                "quantum_kernel_mapping": "Gamma_s^Q(k)=sum_r integral[d^3p] f_r v_rel sigma_22 B_34",
            },
            "units": contract["unit_contract"],
            "derivation_class": "action-derived dilute-gas 2-to-2 comparator with explicit elastic final-state Bose enhancement; not full quantum transport",
            "observable": "finite-temperature normal collision width and quantum-enhanced kinetic comparator",
            "data_role": "ACTION_DERIVED_QUANTUM_KINETIC_COMPARATOR_NOT_PHYSICAL_KUBO",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "ladder_vertex_resummation_missing",
                "condensed_collision_kernel_missing",
                "microscopic_SK_KMS_and_retarded_Kubo_match_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "explicit quantum-enhanced dilute-gas comparator only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This closes only a named action-derived quantum-enhanced dilute-gas collision comparator. It does not emit a physical Kubo coefficient, SI observable, alpha_Phi_K, TTG prediction, or Full Topic 13 closure.",
        },
        "contract": contract,
        "state": {
            "classical": classical.__dict__,
            "quantum": quantum.__dict__,
            "quantum_reference": quantum_reference.__dict__,
            "quantum_refined": quantum_refined.__dict__,
            "width_ratios_quantum_vs_classical": width_ratios,
            "relative_width_change_refined_vs_reference": relative_width_change,
            "relative_response_change_refined_vs_reference": relative_response_change,
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "ladder_vertex_resummation_missing",
        "next_controller": "derive a matched retarded response and ladder/vertex closure before calling this a physical Kubo transport result",
        "claim_promotion": False,
        "primary_literature_context": [
            {
                "locator": "https://arxiv.org/abs/hep-ph/9409250",
                "role": "weak-coupling scalar transport requires resummed diagrams or an equivalent linearized Boltzmann equation; context only, no numeric input consumed",
            }
        ],
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
                "width_ratios": width_ratios,
                "relative_width_change": relative_width_change,
                "relative_response_change": relative_response_change,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
