"""Audit the Topic 13 neutral continuum on-shell sunset-cut lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_continuum_sunset_cut import (  # noqa: E402
    CONTINUUM_SUNSET_CUT_STATUS,
    continuum_sunset_cut_contract,
    continuum_sunset_cut_state,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_sunset_cut_audit.json"
MODULE = ROOT / "docs/core/uet_o2_continuum_sunset_cut.py"
FINITE_SUNSET_ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_two_loop_sunset_cut_audit.json"


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
    reference = continuum_sunset_cut_state(
        0.22,
        0.0,
        0.15,
        config,
        radial_order=48,
        center_of_mass_order=40,
        cutoff_factor=24.0,
    )
    enriched = continuum_sunset_cut_state(
        0.22,
        0.0,
        0.15,
        config,
        radial_order=64,
        center_of_mass_order=48,
        cutoff_factor=28.0,
    )
    contract = continuum_sunset_cut_contract()
    finite_sunset = json.loads(
        FINITE_SUNSET_ARTIFACT.read_text(encoding="utf-8-sig")
    )
    checks = {
        "continuum_on_shell_cut_is_completed": reference.continuum_sunset_cut_completed,
        "neutral_lane_is_explicit": reference.chemical_potential == 0.0,
        "greater_cut_is_positive": reference.greater_cut > 0.0,
        "lesser_cut_is_positive": reference.lesser_cut > 0.0,
        "spectral_cut_is_positive": reference.positive_spectral_cut,
        "noise_cut_is_positive": reference.noise_cut > 0.0,
        "kms_ratio_is_small": reference.kms_residual <= 1.0e-12,
        "radial_convergence_is_small": (
            reference.radial_convergence_residual <= reference.convergence_threshold
        ),
        "angular_convergence_is_small": (
            reference.angular_convergence_residual <= reference.convergence_threshold
        ),
        "cutoff_convergence_is_small": (
            reference.cutoff_convergence_residual <= reference.convergence_threshold
        ),
        "convergence_contract_passes": reference.convergence_passed,
        "enriched_lane_remains_positive": enriched.positive_spectral_cut,
        "finite_channel_sunset_is_preserved": (
            finite_sunset["status"] == "PASS_ACTION_DERIVED_TWO_LOOP_SUNSET_CUT_LANE"
        ),
        "full_1pi_self_energy_remains_open": not reference.full_1pi_retarded_self_energy_completed,
        "real_part_subtraction_remains_open": not reference.real_part_subtraction_completed,
        "off_shell_matching_remains_open": not reference.off_shell_matching_completed,
        "physical_retarded_self_energy_remains_open": not reference.physical_retarded_self_energy_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used and not reference.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "full_self_energy_boundary_is_explicit": contract["excluded"]["full_1PI_retarded_self_energy"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        CONTINUUM_SUNSET_CUT_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_CONTINUUM_SUNSET_CUT_LANE"
    )
    evidence = [
        {"path": "docs/core/uet_o2_continuum_sunset_cut.py", "sha256": sha256(MODULE)},
        {
            "path": "docs/core/07_artifacts/topic13/t13_uet_o2_two_loop_sunset_cut_audit.json",
            "sha256": sha256(FINITE_SUNSET_ARTIFACT),
        },
    ]
    open_blockers = [
        "full_1PI_retarded_self_energy_real_part_subtraction_and_off_shell_match_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    artifact = {
        "schema_version": "t13-uet-o2-continuum-sunset-cut-v1",
        "artifact": "t13_uet_o2_continuum_sunset_cut_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONTINUUM_SUNSET_CUT_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the neutral p=0 continuum on-shell 2-to-2 sunset-cut phase-space integral in the declared natural-unit convention",
                "radial quadrature, center-of-mass angular quadrature, and cutoff refinements are separately checked",
                "greater/lesser cut weights satisfy the KMS ratio implied by four-momentum conservation",
                "the spectral-cut and noise-cut quantities are positive on the declared normal-state lane",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "neutral continuum on-shell cut lane only; no full retarded self-energy, physical Kubo, covariant entropy current, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {
            "reference": asdict(reference),
            "enriched": asdict(enriched),
        },
        "checks": checks,
        "failed_checks": failed,
        "continuum_sunset_cut_completed": reference.continuum_sunset_cut_completed,
        "continuum_sunset_self_energy_completed": reference.continuum_sunset_self_energy_completed,
        "full_1pi_retarded_self_energy_completed": reference.full_1pi_retarded_self_energy_completed,
        "real_part_subtraction_completed": reference.real_part_subtraction_completed,
        "off_shell_matching_completed": reference.off_shell_matching_completed,
        "physical_retarded_self_energy_completed": reference.physical_retarded_self_energy_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "full_1PI_retarded_self_energy_real_part_subtraction_and_off_shell_match_missing",
        "next_controller": "derive the real and imaginary parts of the full 1PI retarded self-energy with a declared regulator/subtraction and off-shell matching, then connect the KMS kernel to a covariant entropy/heat-flux balance",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_CONTINUUM_SUNSET_CUT_LANE",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "data_role": reference.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))},
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
