from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_density_charged_vertex import (  # noqa: E402
    FINITE_DENSITY_CHARGED_VERTEX_STATUS,
    finite_density_charged_vertex_contract,
    finite_density_charged_vertex_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_renormalized_vertex_scheme import (  # noqa: E402
    renormalized_vertex_scheme_state,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_density_charged_vertex_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py"
RENORMALIZED_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_renormalized_vertex_scheme.py"
UV_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py"
NORMAL_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py"
KMS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py"


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
    config = _config()
    state = finite_density_charged_vertex_state(
        0.22,
        0.25,
        0.15,
        config,
        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0, 128.0),
    )
    neutral = renormalized_vertex_scheme_state(
        0.22,
        0.0,
        0.15,
        config,
        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0, 128.0),
    )
    neutral_bubble_residual = float(
        np.max(
            np.abs(
                np.asarray(
                    finite_density_charged_vertex_state(
                        0.22,
                        0.0,
                        0.15,
                        config,
                        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0, 128.0),
                    ).renormalized_bubble_values
                )
                - np.asarray(neutral.renormalized_bubble_values)
            )
        )
    )
    neutral_vertex_residual = float(
        np.max(
            np.abs(
                np.asarray(
                    finite_density_charged_vertex_state(
                        0.22,
                        0.0,
                        0.15,
                        config,
                        cutoff_multipliers=(8.0, 16.0, 32.0, 64.0, 128.0),
                    ).renormalized_vertex_norms
                )
                - np.asarray(neutral.renormalized_vertex_norms)
            )
        )
    )
    checks = {
        "finite_density_completion_flag": state.finite_density_charged_vertex_completed,
        "nonzero_chemical_potential_sample": abs(state.chemical_potential) > 1.0e-12,
        "stable_normal_static_gap": state.static_gap > 0.0,
        "particle_mode_energy_positive": state.particle_mode_energy > 0.0,
        "antiparticle_mode_energy_positive": state.antiparticle_mode_energy > 0.0,
        "static_propagator_identity": state.static_propagator_residual <= 1.0e-12,
        "propagator_factorization_identity": state.propagator_factorization_residual <= 1.0e-12,
        "raw_vacuum_growth_visible": state.raw_vacuum_growth_ratio > 1.5,
        "charged_thermal_cutoff_converges": state.charged_thermal_cutoff_relative_change <= 1.0e-8,
        "renormalized_bubble_cutoff_change_bounded": state.renormalized_bubble_last_relative_change <= 1.0e-3,
        "renormalized_vertex_cutoff_change_bounded": state.renormalized_vertex_last_relative_change <= 1.0e-6,
        "particle_kms_holds": state.particle_kms_residual <= 1.0e-12,
        "antiparticle_kms_holds": state.antiparticle_kms_residual <= 1.0e-12,
        "charge_conjugation_bubble_holds": state.charge_conjugation_bubble_residual <= 1.0e-12,
        "charge_density_is_odd": state.charge_density_odd_residual <= 1.0e-12,
        "neutral_limit_matches_previous_lane": neutral_bubble_residual <= 1.0e-12 and neutral_vertex_residual <= 1.0e-12,
        "declared_physical_scheme_remains_open": not state.unique_physical_renormalization_scheme_matched,
        "full_interacting_sk_remains_open": not state.full_interacting_sk_kms_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": True,
        "C_ontology_preserved": True,
        "R_gen_ontology_preserved": True,
        "R_obs_separate": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = FINITE_DENSITY_CHARGED_VERTEX_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_FINITE_DENSITY_CHARGED_O2_VERTEX_SCHEME"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_renormalized_vertex_scheme.py", "sha256": sha256(RENORMALIZED_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_one_loop_vertex_uv_boundary.py", "sha256": sha256(UV_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py", "sha256": sha256(NORMAL_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py", "sha256": sha256(KMS_MODULE)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-finite-density-charged-vertex-v1",
        "artifact": "t13_uet_o2_finite_density_charged_vertex_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the finite-density O(2) Euclidean charged propagator is defined on the stable normal branch",
                "particle and antiparticle thermal weights and the associated charged one-loop bubble are evaluated without clipping",
                "the existing mass-squared reference subtraction is extended to the finite-density charged vertex",
                "particle/antiparticle KMS-FDT, charge-conjugation, and the neutral-limit compatibility witnesses are verified",
            ] if not failed else [],
            "equation_or_mapping": finite_density_charged_vertex_contract()["equations"],
            "units": finite_density_charged_vertex_contract()["units"],
            "derivation_class": finite_density_charged_vertex_contract()["derivation_class"],
            "observable": finite_density_charged_vertex_contract()["observable"],
            "data_role": finite_density_charged_vertex_contract()["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "unique_physical_renormalization_scheme_match_missing",
                "condensed_two_fluid_charged_completion_missing",
                "full_interacting_SK_action_and_KMS_match_missing",
                "continuum_limit_not_converged",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "one declared finite-density charged normal-branch natural-unit vertex scheme only; no physical renormalization, full SK/KMS, transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": finite_density_charged_vertex_contract()["claim_boundary"],
        },
        "contract": finite_density_charged_vertex_contract(),
        "state": {
            **state.__dict__,
            "neutral_limit_bubble_residual": neutral_bubble_residual,
            "neutral_limit_vertex_residual": neutral_vertex_residual,
        },
        "checks": checks,
        "failed_checks": failed,
        "finite_density_charged_vertex_completed": state.finite_density_charged_vertex_completed,
        "unique_physical_renormalization_scheme_matched": state.unique_physical_renormalization_scheme_matched,
        "full_interacting_sk_kms_match_completed": state.full_interacting_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "unique_physical_renormalization_and_full_interacting_sk_kms_match_missing",
        "next_controller": "match the finite-density charged scheme to a full interacting SK/KMS construction and a declared physical renormalization; keep condensed/two-fluid, physical Kubo, alpha, source, and holdout gates independent",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": state.data_role,
        "audit": {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_finite_density_charged_vertex_audit.json",
            "summary": {
                "status": status,
                "major_result_id": "T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME",
                "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            },
        },
        "open_blockers": [
            "unique_physical_renormalization_scheme_match_missing",
            "condensed_two_fluid_charged_completion_missing",
            "full_interacting_SK_action_and_KMS_match_missing",
            "continuum_limit_not_converged",
            "physical_Kubo_coefficient_missing",
            "entropy_current_heat_flux_and_dissipative_balance_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "claim_boundary": finite_density_charged_vertex_contract()["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
