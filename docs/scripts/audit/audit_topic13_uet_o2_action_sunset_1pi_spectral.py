"""Audit the action-normalized O(2) sunset spectral interface lane."""

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

from docs.core.uet_o2_action_sunset_1pi_spectral import (  # noqa: E402
    ACTION_SUNSET_STATUS,
    action_matrix_element_squared,
    action_sunset_spectral_contract,
    action_sunset_spectral_state,
    action_vertex_component,
)
from docs.core.uet_o2_finite_density_eos import (  # noqa: E402
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_sunset_dispersion_interface import (  # noqa: E402
    _cut_rates as comparator_cut_rates,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_sunset_1pi_spectral_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_sunset_1pi_spectral.py"
COMPARATOR_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface.py"
CONTINUUM_ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_sunset_cut_audit.json"


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


def _relative(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def main() -> int:
    config = _config()
    reference = action_sunset_spectral_state(
        0.22,
        0.0,
        0.15,
        config,
        external_species=0,
        radial_order=40,
        center_of_mass_order=32,
        frequency_order=10,
        cutoff_factor=24.0,
        frequency_cutoff_factor=6.0,
    )
    contract = action_sunset_spectral_contract()
    continuum = json.loads(CONTINUUM_ARTIFACT.read_text(encoding="utf-8-sig"))
    continuum_state = continuum["state"]["reference"]
    mass = math.sqrt(effective_mass_sq(0.15, config.eos))
    comparator_greater, comparator_lesser = comparator_cut_rates(
        mass,
        0.22,
        mass,
        config.eos.matter.matter_quartic,
        40,
        32,
        24.0,
    )
    comparator_spectral = 2.0 * mass * (
        comparator_greater - comparator_lesser
    )
    on_shell_mapping = {
        "greater_action_to_comparator": _relative(
            reference.on_shell_greater_cut,
            comparator_greater * 28.0,
        ),
        "lesser_action_to_comparator": _relative(
            reference.on_shell_lesser_cut,
            comparator_lesser * 28.0,
        ),
        "spectral_action_to_comparator": _relative(
            reference.on_shell_spectral_cut,
            comparator_spectral * 28.0,
        ),
        "expected_matrix_element_ratio": reference.action_to_comparator_matrix_element_ratio,
    }
    vertex_checks = {
        "vertex_0000": action_vertex_component(0, 0, 0, 0, 0.8),
        "vertex_0011": action_vertex_component(0, 0, 1, 1, 0.8),
        "vertex_0101": action_vertex_component(0, 1, 0, 1, 0.8),
        "vertex_0110": action_vertex_component(0, 1, 1, 0, 0.8),
        "matrix_squared_external_0": action_matrix_element_squared(0.8, 0),
        "matrix_squared_external_1": action_matrix_element_squared(0.8, 1),
    }
    finite_response = all(
        math.isfinite(value)
        for values in (
            reference.raw_real_response,
            reference.raw_imaginary_response,
            reference.twice_subtracted_real_response,
            reference.twice_subtracted_imaginary_response,
        )
        for value in values
    )
    checks = {
        "action_vertex_tensor_is_explicit": abs(
            vertex_checks["vertex_0000"] - 4.8
        )
        <= 1.0e-12,
        "action_vertex_crossed_components_are_explicit": (
            vertex_checks["vertex_0011"] == 1.6
            and vertex_checks["vertex_0101"] == 1.6
            and vertex_checks["vertex_0110"] == 1.6
        ),
        "final_state_symmetry_factor_is_included": (
            abs(vertex_checks["matrix_squared_external_0"] - 17.92) <= 1.0e-12
        ),
        "external_species_orthogonal_lane_matches": (
            abs(
                vertex_checks["matrix_squared_external_0"]
                - vertex_checks["matrix_squared_external_1"]
            )
            <= 1.0e-12
        ),
        "action_to_comparator_ratio_is_28": abs(
            reference.action_to_comparator_matrix_element_ratio - 28.0
        )
        <= 1.0e-12,
        "action_on_shell_mapping_is_not_silent": all(
            value <= 1.0e-12
            for key, value in on_shell_mapping.items()
            if key != "expected_matrix_element_ratio"
        ),
        "canonical_effective_mass_is_preserved": _relative(
            reference.effective_mass, continuum_state["effective_mass"]
        )
        <= 1.0e-12,
        "neutral_lane_is_explicit": reference.chemical_potential == 0.0,
        "kms_ratio_is_small": reference.kms_max_residual <= 1.0e-12,
        "spectral_density_is_positive": reference.spectral_positivity_witness,
        "retarded_imaginary_sign_is_consistent": reference.retarded_imaginary_sign_witness,
        "retarded_response_is_finite": finite_response,
        "twice_subtraction_is_exact_at_reference": reference.reference_subtraction_residual
        <= 1.0e-24,
        "twice_subtraction_first_s_derivative_is_small": reference.reference_first_s_derivative_residual
        <= 5.0e-3,
        "dispersion_convergence_is_within_declared_threshold": reference.convergence_passed,
        "continuum_artifact_is_passed": continuum[
            "status"
        ]
        == "PASS_ACTION_DERIVED_CONTINUUM_SUNSET_CUT_LANE",
        "full_1pi_self_energy_remains_open": not reference.full_1pi_retarded_self_energy_completed,
        "zero_eta_physical_limit_remains_open": not reference.zero_eta_physical_limit_completed,
        "unique_renormalization_remains_open": not reference.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_match_remains_open": not reference.microscopic_sk_kms_match_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used
        and not reference.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "full_1pi_boundary_is_explicit": contract["excluded"]["full_1PI_retarded_self_energy"],
        "physical_transport_boundary_is_explicit": contract["excluded"]["physical_kubo_coefficient"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        ACTION_SUNSET_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_O2_SUNSET_1PI_SPECTRAL_INTERFACE_LANE"
    )
    open_blockers = [
        "full_1PI_retarded_self_energy_and_zero_eta_physical_limit_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "microscopic_SK_KMS_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_action_sunset_1pi_spectral.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface.py",
            "sha256": sha256(COMPARATOR_MODULE),
        },
        {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_sunset_cut_audit.json",
            "sha256": sha256(CONTINUUM_ARTIFACT),
        },
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-action-sunset-1pi-spectral-v1",
        "artifact": "t13_uet_o2_action_sunset_1pi_spectral_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ACTION_NORMALIZED_SUNSET_SPECTRAL_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "O(2) action four-point tensor under the declared lambda*(chi^2)^2/4 convention",
                "explicit bath/final species sum with identical-final-state symmetry factor",
                "action-normalized neutral continuum sunset cut and on-shell mapping to the old comparator",
                "finite-regulator retarded dispersion interface with two subtractions in omega^2",
                "KMS ratio, spectral/noise positivity, retarded sign, subtraction, and quadrature controls",
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
            "dependency_unlocked": "action-normalized sunset spectral interface only; no physical 1PI, Kubo, entropy, SI mapping, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(reference)},
        "vertex_checks": vertex_checks,
        "on_shell_mapping": on_shell_mapping,
        "checks": checks,
        "failed_checks": failed,
        "action_vertex_normalization_completed": reference.action_vertex_normalization_completed,
        "action_continuum_cut_completed": reference.action_continuum_cut_completed,
        "twice_subtracted_dispersion_interface_completed": reference.twice_subtracted_dispersion_interface_completed,
        "full_1pi_retarded_self_energy_completed": reference.full_1pi_retarded_self_energy_completed,
        "zero_eta_physical_limit_completed": reference.zero_eta_physical_limit_completed,
        "unique_physical_renormalization_scheme_match_completed": reference.unique_physical_renormalization_scheme_match_completed,
        "microscopic_sk_kms_match_completed": reference.microscopic_sk_kms_match_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "full_1PI_retarded_self_energy_and_zero_eta_physical_limit_missing",
        "next_controller": "match the finite-regulator action branch to a complete microscopic 1PI renormalization and physical zero-eta limit before calling it physical thermal transport",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_ACTION_NORMALIZED_SUNSET_SPECTRAL_INTERFACE_LANE",
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
                "action_matrix_element_squared": reference.action_matrix_element_squared,
                "action_to_comparator_ratio": reference.action_to_comparator_matrix_element_ratio,
                "dispersion_convergence_residual": reference.dispersion_convergence_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
