"""Audit the finite-channel action-derived two-loop sunset-cut lane."""

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

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_two_loop_sunset_cut import (  # noqa: E402
    TWO_LOOP_SUNSET_CUT_STATUS,
    two_loop_sunset_cut_contract,
    two_loop_sunset_cut_state,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_two_loop_sunset_cut_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_two_loop_sunset_cut.py"
TRANSITION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"
TRANSITION_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_derived_transition_kernel_audit.json"
ONE_LOOP_NO_GO = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_retarded_self_energy_no_go_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(state: object) -> dict[str, object]:
    payload = asdict(state)
    payload["channel_rate_count"] = len(payload.pop("channel_forward_rates"))
    payload.pop("channel_reverse_rates", None)
    payload.pop("channel_cut_rates", None)
    return payload


def _config() -> FiniteTemperatureO2QuasiparticleConfig:
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=0.5,
                matter_quartic=0.8,
                response_coupling=0.3,
            ),
            response=CovariantResponseConfig(epsilon_nc=0.1),
        )
    )


def main() -> int:
    config = _config()
    reference = two_loop_sunset_cut_state(
        0.22,
        0.25,
        0.15,
        config,
        quadrature_order=24,
        channel_count=12,
        cutoff_factor=20.0,
    )
    enriched = two_loop_sunset_cut_state(
        0.22,
        0.25,
        0.15,
        config,
        quadrature_order=24,
        channel_count=16,
        cutoff_factor=20.0,
    )
    contract = two_loop_sunset_cut_contract()
    one_loop_no_go = json.loads(ONE_LOOP_NO_GO.read_text(encoding="utf-8-sig"))
    checks = {
        "finite_channel_sunset_cut_is_completed": reference.finite_channel_sunset_cut_completed,
        "forward_reverse_channel_counts_match": (
            len(reference.channel_forward_rates) == len(reference.channel_reverse_rates) == reference.channel_count
        ),
        "forward_rates_are_positive": all(value > 0.0 for value in reference.channel_forward_rates),
        "reverse_rates_are_positive": all(value > 0.0 for value in reference.channel_reverse_rates),
        "symmetric_cut_is_positive": reference.symmetric_cut_total > 0.0,
        "every_channel_has_nonzero_cut": reference.nonzero_cut_channel_count == reference.channel_count,
        "detailed_balance_is_small": reference.detailed_balance_max_residual <= 1.0e-10,
        "cut_forward_reverse_totals_match": (
            abs(reference.forward_cut_total - reference.reverse_cut_total)
            / max(reference.symmetric_cut_total, 1.0e-300)
            <= 1.0e-10
        ),
        "inherited_collision_operator_is_positive": reference.positive_semidefinite_min_eigenvalue >= -1.0e-12,
        "inherited_conservation_is_small": reference.collision_conservation_residual <= 1.0e-10,
        "inherited_entropy_witness_is_positive": reference.entropy_production_witness > 0.0,
        "inherited_response_kms_is_small": reference.response_kms_max_residual <= 1.0e-12,
        "inherited_response_fdt_is_small": reference.response_fdt_max_residual <= 1.0e-12,
        "enriched_channel_cut_remains_positive": enriched.symmetric_cut_total > 0.0,
        "action_order_is_explicit": "order lambda^2" in contract["equations"]["action_order"],
        "full_1pi_sunset_remains_open": not reference.continuum_sunset_self_energy_completed,
        "physical_retarded_self_energy_remains_open": not reference.physical_retarded_self_energy_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used and not reference.xie_2026_accessed,
        "one_loop_no_go_is_preserved": (
            one_loop_no_go["status"] == "PASS_ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO"
        ),
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "self_energy_boundary_is_explicit": contract["excluded"]["full_1PI_sunset_self_energy"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = TWO_LOOP_SUNSET_CUT_STATUS if not failed else "BLOCKED_ACTION_DERIVED_TWO_LOOP_SUNSET_CUT_LANE"
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_two_loop_sunset_cut.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(TRANSITION_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_action_derived_transition_kernel_audit.json", "sha256": sha256(TRANSITION_AUDIT)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_retarded_self_energy_no_go_audit.json", "sha256": sha256(ONE_LOOP_NO_GO)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-two-loop-sunset-cut-v1",
        "artifact": "t13_uet_o2_two_loop_sunset_cut_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_TWO_LOOP_SUNSET_CUT_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the first nonzero action-derived order-lambda^2 finite-channel elastic phase-space cut after the one-loop tadpole no-go",
                "forward and reverse Bose-weighted cut rates are evaluated separately and satisfy channel detailed balance",
                "the symmetric cut is positive on every declared active finite channel",
                "the inherited conserved collision, response KMS/FDT, and entropy witnesses remain valid",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "continuum_sunset_integral_and_regulator_matching_missing",
                "full_1PI_retarded_self_energy_missing",
                "unique_physical_renormalization_scheme_match_missing",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "finite-channel two-loop phase-space cut interface only; no full retarded self-energy, physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": compact(reference), "channel_enriched": compact(enriched)},
        "checks": checks,
        "failed_checks": failed,
        "continuum_sunset_self_energy_completed": reference.continuum_sunset_self_energy_completed,
        "physical_retarded_self_energy_completed": reference.physical_retarded_self_energy_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "continuum_sunset_integral_and_full_retarded_self_energy_missing",
        "next_controller": "derive and verify the continuum 1PI sunset retarded self-energy with an explicit regulator/subtraction and then match its KMS/entropy kernel; keep the finite-channel cut as a non-promoted lane",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_TWO_LOOP_SUNSET_CUT_LANE",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": reference.data_role,
        "open_blockers": [
            "continuum_sunset_integral_and_regulator_matching_missing",
            "full_1PI_retarded_self_energy_missing",
            "unique_physical_renormalization_scheme_match_missing",
            "physical_Kubo_coefficient_missing",
            "entropy_current_heat_flux_and_dissipative_balance_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
