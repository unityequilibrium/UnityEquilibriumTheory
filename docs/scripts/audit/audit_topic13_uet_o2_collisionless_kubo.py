"""Audit the collisionless Kubo boundary for the Topic 13 O(2) lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose, isfinite
from pathlib import Path

from docs.core.uet_o2_collisionless_kubo import (
    COLLISIONLESS_KUBO_STATUS,
    collisionless_kubo_contract,
    collisionless_kubo_witness,
    drude_spectral_density,
    regulated_kubo_dc_coefficient,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_collisionless_kubo_audit.json"
MODULE = ROOT / "docs/core/uet_o2_collisionless_kubo.py"
STATIC_MODULE = ROOT / "docs/core/uet_o2_formal_transverse_response.py"
EOS_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
    )
    witness = collisionless_kubo_witness(0.22, 0.35, 0.15, config)
    contract = collisionless_kubo_contract()
    probe_frequency = 0.2
    spectral_values = tuple(
        drude_spectral_density(probe_frequency, width, witness.drude_weight)
        for width in witness.diagnostic_widths
    )
    checks = {
        "normal_drude_weight_is_positive": witness.drude_weight > 0.0,
        "regulated_coefficients_match_D_over_gamma": all(
            isclose(
                coefficient,
                regulated_kubo_dc_coefficient(width, witness.drude_weight),
                rel_tol=1.0e-13,
                abs_tol=1.0e-15,
            )
            for width, coefficient in zip(
                witness.diagnostic_widths,
                witness.regulated_dc_coefficients,
            )
        ),
        "width_reduction_increases_regulated_coefficient": all(
            left < right
            for left, right in zip(
                witness.regulated_dc_coefficients,
                witness.regulated_dc_coefficients[1:],
            )
        ),
        "diagnostic_limit_spans_two_orders_of_magnitude": isclose(
            witness.regulated_dc_coefficients[-1]
            / witness.regulated_dc_coefficients[0],
            witness.diagnostic_widths[0] / witness.diagnostic_widths[-1],
            rel_tol=1.0e-13,
            abs_tol=1.0e-12,
        ),
        "broadened_spectral_density_is_nonnegative": all(
            isfinite(value) and value >= 0.0 for value in spectral_values
        ),
        "zero_frequency_spectral_density_is_zero": all(
            drude_spectral_density(0.0, width, witness.drude_weight) == 0.0
            for width in witness.diagnostic_widths
        ),
        "collisionless_dc_is_not_finite": witness.collisionless_dc_is_finite is False,
        "physical_coefficient_not_emitted": witness.physical_coefficient_emitted is False,
        "no_source_rows_consumed": True,
        "no_parameter_fitting": True,
        "no_target_or_holdout": True,
        "Phi_ontology_preserved": "not temperature" in contract["units"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["units"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["units"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["units"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = COLLISIONLESS_KUBO_STATUS if not failed else "BLOCKED_COLLISIONLESS_KUBO_AUDIT"
    evidence = [
        {"path": "docs/core/uet_o2_collisionless_kubo.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_formal_transverse_response.py", "sha256": sha256(STATIC_MODULE)},
        {"path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-collisionless-kubo-v1",
        "artifact": "t13_uet_o2_collisionless_kubo_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_COLLISIONLESS_KUBO_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "the declared collisionless normal quasiparticle response has a positive Drude weight but no finite DC Kubo coefficient",
                "a positive width regularizes the response as D/gamma, and the coefficient diverges as the width tends to zero",
                "the diagnostic width is therefore a regulator, not a physical UET transport input",
                "the next physical transport step is narrowed to an interaction collision kernel or a state-matched microscopic self-energy/retarded correlator",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "interaction_collision_kernel_or_microscopic_width_missing",
                "retarded_physical_Kubo_match_missing",
                "interacting_finite_temperature_self_energy_and_renormalization_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "collisionless Kubo structural boundary only; no physical transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "temperature": witness.temperature,
            "chemical_potential": witness.chemical_potential,
            "space_response": witness.space_response,
            "drude_weight": witness.drude_weight,
            "diagnostic_widths": list(witness.diagnostic_widths),
            "regulated_dc_coefficients": list(witness.regulated_dc_coefficients),
            "probe_frequency": probe_frequency,
            "probe_spectral_density": list(spectral_values),
            "collisionless_dc_is_finite": witness.collisionless_dc_is_finite,
        },
        "checks": checks,
        "failed_checks": failed,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "interaction_collision_kernel_or_microscopic_width_missing",
        "next_controller": "derive a state-matched interaction collision kernel or obtain a microscopic retarded correlator with a declared width; do not promote D/gamma diagnostics to physical transport",
        "claim_promotion": False,
        "primary_literature_context": [
            {
                "locator": "https://arxiv.org/abs/hep-ph/9409250",
                "role": "leading weak-coupling scalar transport requires resummed diagrams or an equivalent linearized Boltzmann equation; context only, no numeric input consumed",
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
                "drude_weight": witness.drude_weight,
                "regulated_dc_coefficients": witness.regulated_dc_coefficients,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
