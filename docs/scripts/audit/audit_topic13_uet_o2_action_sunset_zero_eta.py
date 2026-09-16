"""Audit the action-matched zero-eta sunset subtraction interface."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_sunset_zero_eta import (  # noqa: E402
    ZERO_ETA_SUNSET_STATUS,
    zero_eta_sunset_contract,
    zero_eta_sunset_state,
)
from docs.core.uet_o2_finite_density_eos import (  # noqa: E402
    O2FiniteDensityEOSConfig,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_sunset_zero_eta_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_sunset_zero_eta.py"
ACTION_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_sunset_1pi_spectral.py"


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
    reference = zero_eta_sunset_state(
        0.22,
        0.0,
        0.15,
        config,
        external_species=0,
        radial_order=24,
        center_of_mass_order=24,
        frequency_order=16,
        cutoff_factor=24.0,
        frequency_cutoff_factor=6.0,
    )
    contract = zero_eta_sunset_contract()
    finite_response = all(
        math.isfinite(value)
        for values in (
            reference.physical_real_response,
            reference.physical_imaginary_response,
        )
        for value in values
    )
    checks = {
        "action_vertex_normalization_is_present": abs(
            reference.action_matrix_element_squared - 17.92
        )
        <= 1.0e-12,
        "declared_zero_eta_distribution_is_present": reference.zero_eta_distributional_interface_completed,
        "declared_bphz_subtraction_is_present": reference.declared_bphz_subtraction_interface_completed,
        "reference_invariant_is_zero": reference.reference_invariant_s == 0.0,
        "subtraction_value_condition_is_exact": reference.subtraction_at_reference_residual
        <= 1.0e-24,
        "subtraction_derivative_condition_is_exact": reference.subtraction_derivative_at_reference_residual
        <= 1.0e-24,
        "imaginary_distribution_matches_cut": reference.imaginary_distribution_match_residual
        <= 1.0e-24,
        "imaginary_response_is_dissipative_sign": all(
            value <= 1.0e-30 for value in reference.physical_imaginary_response
        ),
        "spectral_density_is_positive": all(
            value >= -1.0e-30 for value in reference.spectral_density
        ),
        "kms_ratio_is_small": reference.kms_max_residual <= 1.0e-12,
        "physical_response_is_finite": finite_response,
        "principal_value_convergence_is_within_threshold": reference.convergence_passed,
        "full_microscopic_1pi_remains_open": not reference.full_1pi_retarded_self_energy_completed,
        "unique_renormalization_remains_open": not reference.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_remains_open": not reference.microscopic_sk_kms_match_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used
        and not reference.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "full_1pi_boundary_is_explicit": contract["excluded"]["full_microscopic_1PI_action_derivation"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        ZERO_ETA_SUNSET_STATUS
        if not failed
        else "BLOCKED_ACTION_MATCHED_O2_SUNSET_ZERO_ETA_SUBTRACTION_INTERFACE_LANE"
    )
    open_blockers = [
        "full_microscopic_1PI_action_derivation_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "microscopic_SK_KMS_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_action_sunset_zero_eta.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/02_equations/o2/uet_o2_action_sunset_1pi_spectral.py",
            "sha256": sha256(ACTION_MODULE),
        },
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-action-sunset-zero-eta-v1",
        "artifact": "t13_uet_o2_action_sunset_zero_eta_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ACTION_MATCHED_ZERO_ETA_SUNSET_SUBTRACTION_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "distributional zero-eta retarded prescription for the action-normalized sunset cut",
                "analytic principal-value evaluation of the real twice-subtracted response",
                "declared invariant BPHZ-like conditions Sigma_R(0)=0 and dSigma_R/ds(0)=0",
                "KMS ratio, spectral positivity, dissipative imaginary sign, and quadrature convergence",
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
            "open_blockers": open_blockers,
            "dependency_unlocked": "zero-eta distributional and declared subtraction interface only; no full microscopic 1PI, unique renormalization, Kubo, entropy, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(reference)},
        "checks": checks,
        "failed_checks": failed,
        "action_vertex_normalization_completed": reference.action_vertex_normalization_completed,
        "continuum_cut_completed": reference.continuum_cut_completed,
        "zero_eta_distributional_interface_completed": reference.zero_eta_distributional_interface_completed,
        "declared_bphz_subtraction_interface_completed": reference.declared_bphz_subtraction_interface_completed,
        "full_1pi_retarded_self_energy_completed": reference.full_1pi_retarded_self_energy_completed,
        "unique_physical_renormalization_scheme_match_completed": reference.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_match_completed": reference.microscopic_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "full_microscopic_1PI_action_derivation_and_unique_physical_renormalization_missing",
        "next_controller": "derive the complete off-shell microscopic 1PI action self-energy and match its declared subtraction to the finite-temperature SK/KMS construction before physical transport claims",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_ACTION_MATCHED_ZERO_ETA_SUNSET_SUBTRACTION_INTERFACE_LANE",
        "closure_level": closure_level,
        "data_role": reference.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed,
                "artifact": str(OUT.relative_to(ROOT)),
                "principal_value_convergence_residual": reference.principal_value_convergence_residual,
                "kms_max_residual": reference.kms_max_residual,
                "imaginary_distribution_match_residual": reference.imaginary_distribution_match_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
