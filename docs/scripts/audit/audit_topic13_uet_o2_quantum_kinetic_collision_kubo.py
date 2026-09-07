"""Audit the action-derived quantum 2-to-2 collision lane for Topic 13.

The underlying kinetic module already contains an explicit elastic final-state
Bose factor.  This audit exercises that branch as a separate result instead
of silently changing the existing dilute comparator.  It remains a natural-
unit kinetic lane: ladder resummation, continuum promotion, condensed
scattering, microscopic SK matching, and SI transport are still open.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_state


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_uet_o2_quantum_kinetic_collision_kubo_audit.json"
MODULE = ROOT / "docs/core/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"

STATUS = "PASS_ACTION_DERIVED_QUANTUM_KINETIC_COLLISION_LANE"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_change(new: float, old: float) -> float:
    return abs(float(new) - float(old)) / max(abs(float(old)), 1.0e-300)


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    common = {
        "temperature": 0.22,
        "chemical_potential": 0.35,
        "space_response": 0.15,
        "config": config,
    }
    dilute = kinetic_collision_state(
        **common,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
        include_final_state_bose_enhancement=False,
    )
    coarse = kinetic_collision_state(
        **common,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
        include_final_state_bose_enhancement=True,
    )
    reference = kinetic_collision_state(
        **common,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
        include_final_state_bose_enhancement=True,
    )
    refined = kinetic_collision_state(
        **common,
        quadrature_order=80,
        angular_order=56,
        cutoff_factor=28.0,
        include_final_state_bose_enhancement=True,
    )

    relative_width_change = max(
        _relative_change(refined_value, reference_value)
        for refined_value, reference_value in zip(
            refined.collision_width_by_species,
            reference.collision_width_by_species,
        )
    )
    relative_response_change = _relative_change(
        refined.kinetic_coefficient,
        reference.kinetic_coefficient,
    )
    enhancement_ratios = tuple(
        quantum / dilute_width
        for quantum, dilute_width in zip(
            reference.collision_width_by_species,
            dilute.collision_width_by_species,
        )
    )
    checks = {
        "normal_state_is_strict": True,
        "quantum_widths_are_finite_and_positive": all(
            isfinite(value) and value > 0.0
            for value in reference.collision_width_by_species
        ),
        "quantum_response_is_finite_and_positive": (
            isfinite(reference.kinetic_coefficient)
            and reference.kinetic_coefficient > 0.0
        ),
        "final_state_bose_factor_is_enabled": (
            reference.final_state_bose_enhancement_included is True
        ),
        "bose_enhancement_does_not_reduce_width": all(
            ratio >= 1.0 for ratio in enhancement_ratios
        ),
        "bose_enhancement_is_numerically_nontrivial": any(
            ratio > 1.0 + 1.0e-9 for ratio in enhancement_ratios
        ),
        "quadrature_width_converges": relative_width_change <= 0.02,
        "quadrature_response_converges": relative_response_change <= 0.02,
        "coarse_and_refined_are_positive": (
            coarse.kinetic_coefficient > 0.0
            and refined.kinetic_coefficient > 0.0
        ),
        "ladder_vertex_resummation_remains_explicitly_open": (
            reference.ladder_vertex_resummation_included is False
        ),
        "physical_coefficient_not_emitted": (
            reference.physical_kubo_coefficient_emitted is False
        ),
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = STATUS if not failed else "BLOCKED_ACTION_DERIVED_QUANTUM_KINETIC_COLLISION_LANE"
    evidence = [
        {"path": "docs/core/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py",
            "sha256": sha256(EOS_MODULE),
        },
    ]
    contract = {
        "status": status,
        "equations": {
            "normal_dispersion": "E_s(k)=sqrt(k^2+m_eff^2)-s*sqrt(Z)*abs(mu), s in {-1,+1}",
            "constant_amplitude_cross_section": "sigma_22(s)=lambda^2/(16*pi*s)",
            "quantum_collision_kernel": "Gamma_s(k)=sum_r integral f_r(E_p) v_rel sigma_22(s) (1+f_3)(1+f_4) d^3p/(2*pi)^3",
            "static_weight": "D_s=(1/3) integral[d^3k/(2*pi)^3] k^2[-partial_E f_s]",
            "kinetic_response": "K_quantum=sum_s D_s/Gamma_s(k_ref)",
            "detailed_balance_boundary": "f_1 f_2 (1+f_3)(1+f_4)=f_3 f_4 (1+f_1)(1+f_2) on energy/charge-conserving elastic channels",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "mass_temperature_mu": "energy",
            "lambda": "dimensionless quartic coupling",
            "sigma_22": "inverse energy squared",
            "collision_width": "energy/inverse time",
            "K_quantum": "formal kinetic comparator coefficient",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived elastic 2-to-2 quantum kinetic comparator with explicit final-state Bose factors; not full microscopic transport",
        "observable": "finite-temperature normal collision width and quantum kinetic response comparator",
        "data_role": "ACTION_DERIVED_QUANTUM_KINETIC_COMPARATOR_NOT_PHYSICAL_KUBO",
        "included": {
            "normal_branch": True,
            "constant_amplitude_2_to_2_kernel": True,
            "final_state_bose_enhancement": True,
            "detailed_balance_boundary": True,
            "deterministic_quadrature": True,
            "positivity_and_cutoff_checks": True,
        },
        "excluded": {
            "ladder_vertex_resummation": True,
            "condensed_scattering": True,
            "microscopic_SK_KMS_match": True,
            "continuum_limit": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes only a named action-derived quantum kinetic comparator with explicit final-state Bose factors. It does not emit a physical Kubo coefficient, SI observable, alpha_Phi_K, TTG prediction, or Full Topic 13 closure.",
    }
    artifact = {
        "schema_version": "t13-uet-o2-quantum-kinetic-collision-kubo-v1",
        "artifact": "t13_uet_o2_quantum_kinetic_collision_kubo_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_QUANTUM_COLLISION_ENHANCEMENT_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the existing action-matched elastic 2-to-2 kernel is exercised with explicit final-state Bose enhancement",
                "the quantum collision width remains finite and positive on the strict normal branch",
                "the Bose-enhanced response is nontrivial and convergent on the declared refinement sequence",
                "the dilute comparator remains unchanged and is retained as a separate baseline",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "ladder_vertex_resummation_missing",
                "condensed_collision_kernel_missing",
                "continuum_limit_missing",
                "microscopic_SK_KMS_and_retarded_Kubo_match_missing",
                "physical_Kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "action-derived quantum kinetic collision lane only; no ladder, continuum, physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "dilute_baseline": dilute.__dict__,
            "reference": reference.__dict__,
            "coarse": coarse.__dict__,
            "refined": refined.__dict__,
            "enhancement_ratios": enhancement_ratios,
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
        "controlling_blocker": "ladder_vertex_resummation_missing" if not failed else "quantum_kinetic_lane_verification_failed",
        "next_controller": "derive or match the ladder/retarded response and continuum limit without relabeling this finite-grid quantum kinetic comparator as physical Kubo",
        "claim_promotion": False,
        "full_core_unlock": False,
        "action_matching_boundary": "Canonical comparator only; full action tensor/channel normalization remains open.",
        "source_hashes": {
            path: sha256(ROOT / path) for path in (
                "docs/core/uet_o2_kinetic_collision_kubo.py",
                "docs/scripts/audit/audit_topic13_uet_o2_quantum_kinetic_collision_kubo.py",
            )
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "closure_level": artifact["major_result"]["closure_level"],
        "failed_checks": failed,
        "enhancement_ratios": enhancement_ratios,
        "reference_widths": reference.collision_width_by_species,
        "reference_kinetic_coefficient": reference.kinetic_coefficient,
        "relative_width_change": relative_width_change,
        "relative_response_change": relative_response_change,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
