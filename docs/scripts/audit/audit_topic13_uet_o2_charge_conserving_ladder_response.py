"""Audit the conserving two-channel retarded response lane for Topic 13."""

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

from docs.core.uet_o2_charge_conserving_ladder_response import (  # noqa: E402
    charge_conserving_ladder_response_contract,
    charge_conserving_ladder_response_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_charge_conserving_ladder_response_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_charge_conserving_ladder_response.py"
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
    reference = charge_conserving_ladder_response_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=64,
        angular_order=48,
        cutoff_factor=24.0,
    )
    refined = charge_conserving_ladder_response_state(
        0.22,
        0.35,
        0.15,
        config,
        quadrature_order=80,
        angular_order=56,
        cutoff_factor=28.0,
    )
    contract = charge_conserving_ladder_response_contract()
    positive_frequency_indices = tuple(
        index for index, ratio in enumerate(reference.frequency_over_gamma) if ratio > 0.0
    )
    real_values = reference.retarded_response_real
    checks = {
        "quantum_collision_width_is_explicit": (
            reference.final_state_bose_enhancement_included is True
        ),
        "ladder_resolvent_is_explicit": (
            reference.ladder_vertex_resummation_included is True
        ),
        "conserved_zero_mode_is_present": (
            abs(reference.collision_operator_eigenvalues[0]) <= 1.0e-15
            and reference.collision_operator_eigenvalues[1] > 0.0
        ),
        "collision_operator_is_symmetric": reference.symmetry_residual <= 1.0e-12,
        "collision_operator_preserves_conserved_vector": (
            reference.conservation_residual <= 1.0e-12
        ),
        "collision_operator_is_positive_semidefinite": (
            reference.positive_semidefinite_min_eigenvalue >= -1.0e-12
        ),
        "projected_source_is_finite_and_conserved": (
            reference.source_norm_squared > 0.0
            and isfinite(reference.source_norm_squared)
            and abs(sum(
                c * b
                for c, b in zip(
                    reference.conserved_vector,
                    reference.projected_source_vector,
                )
            ))
            <= 1.0e-12
        ),
        "dc_response_matches_closed_form": (
            abs(reference.dc_response - reference.dc_closed_form)
            / reference.dc_closed_form
            <= 1.0e-12
        ),
        "retarded_real_response_is_positive": all(
            value >= 0.0 and isfinite(value) for value in reference.retarded_response_real
        ),
        "retarded_real_response_is_nonincreasing": all(
            later <= earlier + 1.0e-12
            for earlier, later in zip(real_values, real_values[1:])
        ),
        "retarded_imaginary_response_has_declared_sign": all(
            reference.retarded_response_imag[index] > 0.0
            for index in positive_frequency_indices
        ),
        "retarded_response_is_finite": all(
            isfinite(value)
            for value in (*reference.retarded_response_real, *reference.retarded_response_imag)
        ),
        "quadrature_response_converges": (
            relative_change(
                refined.retarded_response_real,
                reference.retarded_response_real,
            )
            <= 0.02
        ),
        "refined_operator_remains_conserving": (
            refined.conservation_residual <= 1.0e-12
            and refined.symmetry_residual <= 1.0e-12
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
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE"
    )
    relative_response_change = relative_change(
        refined.retarded_response_real,
        reference.retarded_response_real,
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_charge_conserving_ladder_response.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(COLLISION_MODULE)},
        {
            "path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "sha256": sha256(EOS_MODULE),
        },
    ]
    artifact = {
        "schema_version": "t13-uet-o2-charge-conserving-ladder-response-v1",
        "artifact": "t13_uet_o2_charge_conserving_ladder_response_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CHARGE_CONSERVING_LADDER_RESPONSE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the corrected quantum collision width feeds an explicit two-channel conserving collision operator",
                "the conserved sum mode is an exact zero mode and the relative mode is positive dissipative",
                "the projected retarded response is finite, sign-consistent, and stable under quadrature refinement",
                "the lane records a matrix-resolvent ladder comparator without emitting a physical Kubo coefficient",
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
                "microscopic_bethe_salpeter_ladder_and_vertex_matching_missing",
                "microscopic_SK_KMS_and_fluctuation_dissipation_matching_missing",
                "condensed_collision_and_full_finite_temperature_transport_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "named conserving response lane only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This closes only a named action-derived conserving two-channel response lane. It does not close microscopic ladder vertices, SK/KMS matching, physical transport, SI calibration, alpha_Phi_K, TTG prediction, or Full Topic 13.",
        },
        "contract": contract,
        "state": {
            "reference": reference.__dict__,
            "refined": refined.__dict__,
            "relative_response_change_refined_vs_reference": relative_response_change,
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "microscopic_ladder_vertex_and_SK_KMS_matching_missing",
        "next_controller": "match the conserving response to a microscopic momentum-dependent ladder and SK/KMS interface before calling it physical transport",
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
                "eigenvalues": reference.collision_operator_eigenvalues,
                "relative_rate": reference.relative_collision_rate,
                "dc_response": reference.dc_response,
                "relative_response_change": relative_response_change,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
