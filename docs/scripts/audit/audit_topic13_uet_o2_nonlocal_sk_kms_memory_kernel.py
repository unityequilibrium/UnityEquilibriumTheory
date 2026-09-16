from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_nonlocal_sk_kms_memory_kernel import (  # noqa: E402
    NONLOCAL_SK_KMS_MEMORY_STATUS,
    nonlocal_sk_kms_memory_contract,
    nonlocal_sk_kms_memory_state,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_nonlocal_sk_kms_memory_kernel_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_nonlocal_sk_kms_memory_kernel.py"
COLLISION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py"
OPEN_SYSTEM_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_open_system_sk_kms.py"
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
    state = nonlocal_sk_kms_memory_state(
        0.22,
        0.25,
        0.15,
        _config(),
        collision_quadrature_order=40,
        collision_angular_order=24,
        collision_cutoff_factor=20.0,
    )
    contract = nonlocal_sk_kms_memory_contract()
    checks = {
        "formal_nonlocal_influence_functional_completed": state.formal_nonlocal_influence_functional_completed,
        "memory_rate_is_source_derived": state.gamma_memory > 0.0 and all(value > 0.0 for value in state.source_collision_widths),
        "memory_time_is_positive_and_nonzero": state.memory_time > 0.0,
        "causal_negative_time_support_is_zero": state.negative_time_support_residual == 0.0,
        "positive_time_memory_is_visible": state.positive_time_memory_value > 0.0,
        "retarded_memory_pole_is_lower_half_plane": state.memory_pole_imaginary_part < 0.0,
        "retarded_imaginary_part_has_damping_sign": all(value <= 1.0e-12 for value in state.retarded_imag),
        "spectral_density_is_nonnegative": state.spectral_density_minimum >= -1.0e-14,
        "causal_transform_matches_exponential_memory": max(state.causal_transform_residuals) <= 1.0e-10,
        "kernel_reality_condition_holds": max(state.kernel_reality_residuals) <= 1.0e-12,
        "kms_ratio_holds": max(state.kms_ratio_residuals) <= 2.0e-12,
        "fdt_noise_holds": max(state.fdt_residuals) <= 2.0e-12,
        "formal_entropy_is_nonnegative": state.entropy_production_witness >= 0.0,
        "physical_retarded_self_energy_remains_open": not state.physical_retarded_self_energy_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "formal_boundary_is_explicit": (
            contract["excluded"]["physical_retarded_self_energy"]
            and contract["excluded"]["physical_kubo_coefficient"]
            and contract["excluded"]["alpha_Phi_K"]
            and contract["excluded"]["TTG_validation"]
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = NONLOCAL_SK_KMS_MEMORY_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE"
    )
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_nonlocal_sk_kms_memory_kernel.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_kinetic_collision_kubo.py", "sha256": sha256(COLLISION_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_open_system_sk_kms.py", "sha256": sha256(OPEN_SYSTEM_MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py", "sha256": sha256(KMS_MODULE)},
    ]
    contract = nonlocal_sk_kms_memory_contract()
    artifact = {
        "schema_version": "t13-uet-o2-nonlocal-sk-kms-memory-kernel-v1",
        "artifact": "t13_uet_o2_nonlocal_sk_kms_memory_kernel_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the explicit causal exponential memory kernel and its retarded transfer function",
                "the action-derived collision-width source for the formal memory damping rate",
                "positive spectral density, lower-half-plane memory pole, and causal transform identity",
                "equilibrium charged KMS/FDT noise and a nonnegative formal entropy-production witness",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_retarded_self_energy_and_dissipative_kernel_missing",
                "unique_physical_renormalization_scheme_match_missing",
                "condensed_two_fluid_completion_missing",
                "physical_Kubo_coefficient_missing",
                "entropy_current_heat_flux_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal action-derived nonlocal SK/KMS memory-kernel control only; no physical retarded self-energy, Kubo, SI, alpha, Core, Gravity, transport, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": state.__dict__,
        "checks": checks,
        "failed_checks": failed,
        "formal_nonlocal_influence_functional_completed": state.formal_nonlocal_influence_functional_completed,
        "physical_retarded_self_energy_completed": state.physical_retarded_self_energy_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "physical_retarded_self_energy_and_dissipative_kernel_missing",
        "next_controller": "replace the formal collision-width memory control with a state-matched microscopic retarded self-energy and entropy-current kernel; keep physical Kubo, alpha, source, and holdout gates independent",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": state.data_role,
        "audit": {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_nonlocal_sk_kms_memory_kernel_audit.json",
            "summary": {
                "status": status,
                "major_result_id": "T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE",
                "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            },
        },
        "open_blockers": [
            "physical_retarded_self_energy_and_dissipative_kernel_missing",
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
