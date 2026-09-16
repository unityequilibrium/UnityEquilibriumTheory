"""Audit the finite-channel formal entropy balance lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_channel_entropy_balance import (  # noqa: E402
    FINITE_CHANNEL_ENTROPY_BALANCE_STATUS,
    finite_channel_entropy_balance_contract,
    finite_channel_entropy_balance_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_channel_entropy_balance_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_channel_entropy_balance.py"
TRANSITION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py"
SUNSET_ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_two_loop_sunset_cut_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig()
    reference = finite_channel_entropy_balance_state(
        0.22,
        0.25,
        0.15,
        config,
        quadrature_order=24,
        channel_count=12,
        cutoff_factor=20.0,
        affinity_scale=0.05,
    )
    enriched = finite_channel_entropy_balance_state(
        0.22,
        0.25,
        0.15,
        config,
        quadrature_order=24,
        channel_count=16,
        cutoff_factor=20.0,
        affinity_scale=0.05,
    )
    contract = finite_channel_entropy_balance_contract()
    sunset = json.loads(SUNSET_ARTIFACT.read_text(encoding="utf-8-sig"))
    checks = {
        "channel_affinities_are_positive": reference.positive_affinity_witness,
        "channel_entropy_production_is_nonnegative": reference.minimum_channel_entropy_production >= -1.0e-30,
        "perturbed_entropy_production_is_positive": reference.perturbed_entropy_production > 0.0,
        "entropy_balance_identity_closes": reference.entropy_balance_residual <= 1.0e-30,
        "equilibrium_entropy_is_nonnegative": reference.equilibrium_entropy_production >= -1.0e-30,
        "enriched_entropy_production_is_positive": enriched.perturbed_entropy_production > 0.0,
        "detailed_balance_source_is_small": reference.detailed_balance_max_residual <= 1.0e-10,
        "conservation_source_is_small": reference.collision_conservation_residual <= 1.0e-10,
        "inherited_kms_is_small": reference.response_kms_max_residual <= 1.0e-12,
        "inherited_fdt_is_small": reference.response_fdt_max_residual <= 1.0e-12,
        "sunset_lane_is_passing": sunset["status"] == "PASS_ACTION_DERIVED_TWO_LOOP_SUNSET_CUT_LANE",
        "covariant_entropy_current_remains_open": not reference.physical_entropy_current_completed,
        "physical_heat_flux_remains_open": not reference.physical_heat_flux_balance_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used and not reference.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "physical_boundary_is_explicit": contract["excluded"]["covariant_entropy_current"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = FINITE_CHANNEL_ENTROPY_BALANCE_STATUS if not failed else "BLOCKED_ACTION_DERIVED_FINITE_CHANNEL_ENTROPY_BALANCE_LANE"
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_finite_channel_entropy_balance.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(TRANSITION_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_two_loop_sunset_cut_audit.json", "sha256": sha256(SUNSET_ARTIFACT)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-finite-channel-entropy-balance-v1",
        "artifact": "t13_uet_o2_finite_channel_entropy_balance_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the formal finite-channel entropy affinity and H-theorem identity",
                "nonnegative channel entropy production under the declared internal affinity witness",
                "the discrete entropy-balance divergence identity and zero-equilibrium-affinity boundary",
                "inheritance of action-derived detailed balance, conservation, and KMS/FDT controls",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "covariant_continuum_entropy_current_missing",
                "physical_heat_flux_and_dissipative_balance_missing",
                "physical_Kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "finite-channel formal entropy balance only; no covariant entropy current, heat flux, physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": reference.__dict__, "channel_enriched": enriched.__dict__},
        "checks": checks,
        "failed_checks": failed,
        "physical_entropy_current_completed": reference.physical_entropy_current_completed,
        "physical_heat_flux_balance_completed": reference.physical_heat_flux_balance_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "covariant_continuum_entropy_current_and_heat_flux_balance_missing",
        "next_controller": "derive the covariant entropy current and heat-flux balance from the continuum retarded/KMS kernel; retain this finite-channel H-theorem as a formal lane",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": reference.data_role,
        "open_blockers": [
            "covariant_continuum_entropy_current_missing",
            "physical_heat_flux_and_dissipative_balance_missing",
            "physical_Kubo_coefficient_missing",
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
