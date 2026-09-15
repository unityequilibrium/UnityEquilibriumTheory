from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

from docs.core.uet_o2_interacting_sk_kms_action import (  # noqa: E402
    INTERACTING_SK_KMS_ACTION_STATUS,
    interacting_sk_kms_action_contract,
    interacting_sk_kms_action_state,
)
from docs.core.uet_o2_finite_density_charged_vertex import (  # noqa: E402
    finite_density_charged_vertex_contract,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_interacting_sk_kms_action_audit.json"
MODULE = ROOT / "docs/core/uet_o2_interacting_sk_kms_action.py"
CHARGED_MODULE = ROOT / "docs/core/uet_o2_finite_density_charged_vertex.py"
TRANSITION_MODULE = ROOT / "docs/core/uet_o2_action_derived_transition_kernel.py"
KMS_MODULE = ROOT / "docs/core/uet_o2_equilibrium_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    state = interacting_sk_kms_action_state(0.22, 0.25, 0.15, _config())
    contract = interacting_sk_kms_action_contract()
    checks = {
        "local_interacting_action_completed": state.local_interacting_sk_action_completed,
        "contour_action_is_finite": abs(state.contour_action_difference) < 10.0,
        "ra_expansion_is_exact": state.contour_ra_expansion_residual <= 1.0e-12,
        "contour_unitarity_holds": state.contour_unitarity_residual <= 1.0e-14,
        "contour_reality_holds": state.contour_reality_residual <= 1.0e-12,
        "no_pure_r_interaction": state.no_pure_r_interaction_residual <= 1.0e-14,
        "r3a_vertex_is_present": abs(state.ra_interaction_r3a_weight) > 1.0e-8,
        "ra3_vertex_is_present": abs(state.ra_interaction_ra3_weight) > 1.0e-8,
        "charged_particle_kms_holds": state.charged_particle_kms_residual <= 1.0e-12,
        "charged_antiparticle_kms_holds": state.charged_antiparticle_kms_residual <= 1.0e-12,
        "charged_collision_detailed_balance_holds": state.charged_collision_detailed_balance_residual <= 1.0e-10,
        "charged_collision_kms_holds": state.charged_collision_kms_residual <= 1.0e-12,
        "charged_collision_fdt_holds": state.charged_collision_fdt_residual <= 1.0e-12,
        "formal_entropy_witness_is_nonnegative": state.formal_entropy_witness >= 0.0,
        "nonlocal_influence_functional_remains_open": not state.nonlocal_influence_functional_completed,
        "microscopic_retarded_self_energy_remains_open": not state.microscopic_retarded_self_energy_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "external_boundaries_are_explicit": (
            contract["excluded"]["nonlocal_influence_functional"]
            and contract["excluded"]["microscopic_retarded_self_energy"]
            and contract["excluded"]["physical_kubo_coefficient"]
            and contract["excluded"]["alpha_Phi_K"]
            and contract["excluded"]["TTG_validation"]
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = INTERACTING_SK_KMS_ACTION_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_INTERACTING_SK_KMS_LOCAL_ACTION_INTERFACE"
    )
    evidence = [
        {"path": "docs/core/uet_o2_interacting_sk_kms_action.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_finite_density_charged_vertex.py", "sha256": sha256(CHARGED_MODULE)},
        {"path": "docs/core/uet_o2_action_derived_transition_kernel.py", "sha256": sha256(TRANSITION_MODULE)},
        {"path": "docs/core/uet_o2_equilibrium_kms.py", "sha256": sha256(KMS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-interacting-sk-kms-local-action-v1",
        "artifact": "t13_uet_o2_interacting_sk_kms_action_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the exact local O(2) contour action difference S[plus]-S[minus] in r/a variables",
                "the absence of pure-r interactions and the explicit r^3 a and r a^3 interaction content",
                "the charged particle/antiparticle equilibrium KMS-FDT interface",
                "the action-derived charged two-to-two detailed-balance interface and formal nonnegative entropy witness",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "nonlocal_interacting_SK_influence_functional_missing",
                "microscopic_retarded_self_energy_and_physical_dissipation_missing",
                "unique_physical_renormalization_scheme_match_missing",
                "condensed_two_fluid_completion_missing",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "local interacting SK contour and charged equilibrium KMS/detailed-balance interface only; no nonlocal influence-functional, physical dissipation, Kubo, SI, alpha, Core, Gravity, transport, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": state.__dict__,
        "checks": checks,
        "failed_checks": failed,
        "local_interacting_sk_action_completed": state.local_interacting_sk_action_completed,
        "formal_charged_kms_match_completed": state.formal_charged_kms_match_completed,
        "nonlocal_influence_functional_completed": state.nonlocal_influence_functional_completed,
        "microscopic_retarded_self_energy_completed": state.microscopic_retarded_self_energy_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "nonlocal_interacting_sk_influence_functional_and_physical_retarded_kernel_missing",
        "next_controller": "derive the nonlocal interacting SK influence functional and physical retarded self-energy/entropy kernel; keep physical Kubo, condensed/two-fluid, alpha, source, and holdout gates independent",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": state.data_role,
        "audit": {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_interacting_sk_kms_action_audit.json",
            "summary": {
                "status": status,
                "major_result_id": "T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE",
                "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            },
        },
        "open_blockers": [
            "nonlocal_interacting_SK_influence_functional_missing",
            "microscopic_retarded_self_energy_and_physical_dissipation_missing",
            "unique_physical_renormalization_scheme_match_missing",
            "condensed_two_fluid_completion_missing",
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
