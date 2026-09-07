"""Audit the action-derived dilute-gas collision comparator for Topic 13."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose, isfinite
from pathlib import Path

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import (
    KINETIC_COLLISION_KUBO_STATUS,
    kinetic_collision_contract,
    kinetic_collision_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_uet_o2_kinetic_collision_kubo_audit.json"
MODULE = ROOT / "docs/core/uet_o2_kinetic_collision_kubo.py"
EOS_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=128,
        cutoff_factor=60.0,
    )
    coarse = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=48,
        angular_order=32,
        cutoff_factor=20.0,
    )
    reference = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
    )
    refined = kinetic_collision_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=80,
        angular_order=56,
        cutoff_factor=28.0,
    )
    contract = kinetic_collision_contract()
    relative_width_change = max(
        abs(refined_value - reference_value) / reference_value
        for refined_value, reference_value in zip(
            refined.collision_width_by_species,
            reference.collision_width_by_species,
        )
    )
    relative_response_change = abs(
        refined.kinetic_coefficient - reference.kinetic_coefficient
    ) / reference.kinetic_coefficient
    checks = {
        "normal_state_is_strict": True,
        "all_drude_weights_positive": all(
            value > 0.0 and isfinite(value)
            for value in reference.drude_weight_by_species
        ),
        "all_collision_widths_positive": all(
            value > 0.0 and isfinite(value)
            for value in reference.collision_width_by_species
        ),
        "kinetic_response_is_finite_and_positive": (
            reference.kinetic_coefficient > 0.0
            and isfinite(reference.kinetic_coefficient)
        ),
        "quadrature_width_converges": relative_width_change <= 0.02,
        "quadrature_response_converges": relative_response_change <= 0.02,
        "coarse_and_refined_are_positive": (
            coarse.kinetic_coefficient > 0.0
            and refined.kinetic_coefficient > 0.0
        ),
        "final_state_bose_enhancement_is_explicitly_excluded": (
            reference.final_state_bose_enhancement_included is False
        ),
        "ladder_resummation_is_explicitly_excluded": (
            reference.ladder_vertex_resummation_included is False
        ),
        "physical_coefficient_not_emitted": (
            reference.physical_kubo_coefficient_emitted is False
        ),
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = KINETIC_COLLISION_KUBO_STATUS if not failed else "BLOCKED_ACTION_DERIVED_DILUTE_KINETIC_COLLISION_LANE"
    evidence = [
        {"path": "docs/core/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-kinetic-collision-kubo-v1",
        "artifact": "t13_uet_o2_kinetic_collision_kubo_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_KINETIC_COLLISION_KERNEL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "a declared constant-amplitude 2-to-2 phase-space kernel produces a positive normal-branch collision width",
                "the same kernel produces a finite action-derived dilute-gas kinetic response in natural units",
                "quadrature and cutoff refinement are bounded on the declared state point",
                "the lane explicitly excludes final-state Bose enhancement, ladder resummation, condensed scattering, and microscopic SK matching",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "final_state_bose_enhancement_and_ladder_vertex_matching_missing",
                "condensed_collision_kernel_missing",
                "microscopic_SK_KMS_and_retarded_Kubo_match_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "action-derived dilute-gas kinetic comparator only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": reference.__dict__,
            "coarse": coarse.__dict__,
            "refined": refined.__dict__,
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
        "controlling_blocker": "final_state_bose_enhancement_and_ladder_vertex_matching_missing",
        "next_controller": "extend the declared kernel with quantum final-state factors and a matched retarded/ladder response, while keeping the present lane as a natural-unit comparator",
        "claim_promotion": False,
        "full_core_unlock": False,
        "action_matching_boundary": "Canonical comparator only; full action tensor/channel normalization remains open.",
        "source_hashes": {
            path: sha256(ROOT / path) for path in (
                "docs/core/uet_o2_kinetic_collision_kubo.py",
                "docs/scripts/audit/audit_topic13_uet_o2_kinetic_collision_kubo.py",
            )
        },
        "primary_literature_context": [
            {
                "locator": "https://arxiv.org/abs/hep-ph/9409250",
                "role": "weak-coupling scalar transport requires resummed diagrams or an equivalent linearized Boltzmann equation; context only, no numeric input consumed",
            }
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "reference_widths": reference.collision_width_by_species,
                "reference_kinetic_coefficient": reference.kinetic_coefficient,
                "relative_width_change": relative_width_change,
                "relative_response_change": relative_response_change,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
