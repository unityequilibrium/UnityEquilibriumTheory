"""Audit the Topic 13 formal once-subtracted sunset dispersion lane."""

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

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_o2_sunset_dispersion_interface import (  # noqa: E402
    _cut_rates,
)
from docs.core.uet_o2_sunset_dispersion_interface_verified import (  # noqa: E402
    SUNSET_DISPERSION_STATUS,
    sunset_dispersion_interface_contract,
    sunset_dispersion_interface_verified_state,
)
from docs.core.uet_o2_finite_density_eos import effective_mass_sq  # noqa: E402


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_sunset_dispersion_interface_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface.py"
VERIFIED_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface_verified.py"
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
    reference = sunset_dispersion_interface_verified_state(
        0.22,
        0.0,
        0.15,
        config,
        radial_order=48,
        center_of_mass_order=40,
        frequency_order=12,
        cutoff_factor=24.0,
    )
    contract = sunset_dispersion_interface_contract()
    continuum = json.loads(CONTINUUM_ARTIFACT.read_text(encoding="utf-8-sig"))
    continuum_state = continuum["state"]["reference"]

    mass = math.sqrt(effective_mass_sq(0.15, config.eos))
    on_shell_greater, on_shell_lesser = _cut_rates(
        mass,
        0.22,
        mass,
        config.eos.matter.matter_quartic,
        48,
        40,
        24.0,
    )
    on_shell_spectral = 2.0 * mass * (on_shell_greater - on_shell_lesser)
    on_shell_match = {
        "effective_mass": _relative(reference.effective_mass, continuum_state["effective_mass"]),
        "greater_cut": _relative(on_shell_greater, continuum_state["greater_cut"]),
        "lesser_cut": _relative(on_shell_lesser, continuum_state["lesser_cut"]),
        "spectral_cut": _relative(on_shell_spectral, continuum_state["spectral_cut"]),
    }

    finite_response = all(
        math.isfinite(value)
        for values in (
            reference.retarded_raw_real,
            reference.retarded_raw_imaginary,
            reference.subtracted_real_response,
            reference.subtracted_imaginary_response,
        )
        for value in values
    )
    checks = {
        "formal_dispersion_interface_is_completed": reference.continuum_dispersion_interface_completed,
        "once_subtraction_interface_is_completed": reference.real_part_subtraction_interface_completed,
        "off_shell_matching_interface_is_completed": reference.off_shell_matching_interface_completed,
        "neutral_lane_is_explicit": reference.chemical_potential == 0.0,
        "kms_ratio_is_small": reference.kms_max_residual <= 1.0e-12,
        "spectral_density_is_positive": reference.spectral_positivity_witness,
        "retarded_imaginary_sign_is_consistent": reference.retarded_imaginary_sign_witness,
        "retarded_response_is_finite": finite_response,
        "reference_subtraction_is_exact": reference.reference_subtraction_residual <= 1.0e-24,
        "dispersion_convergence_is_within_declared_threshold": reference.convergence_passed,
        "on_shell_effective_mass_matches": on_shell_match["effective_mass"] <= 1.0e-12,
        "on_shell_greater_cut_matches": on_shell_match["greater_cut"] <= 1.0e-12,
        "on_shell_lesser_cut_matches": on_shell_match["lesser_cut"] <= 1.0e-12,
        "on_shell_spectral_cut_matches": on_shell_match["spectral_cut"] <= 1.0e-12,
        "continuum_artifact_is_passed": continuum["status"] == "PASS_ACTION_DERIVED_CONTINUUM_SUNSET_CUT_LANE",
        "full_1pi_self_energy_remains_open": not reference.full_1pi_retarded_self_energy_completed,
        "zero_eta_physical_limit_remains_open": not reference.physical_retarded_self_energy_completed,
        "unique_renormalization_remains_open": not reference.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not reference.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not reference.parameter_fitting_performed,
        "no_target_or_holdout": not reference.target_data_used and not reference.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "full_self_energy_boundary_is_explicit": contract["excluded"]["full_1PI_retarded_self_energy"],
        "physical_kubo_boundary_is_explicit": contract["excluded"]["physical_kubo_coefficient"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = SUNSET_DISPERSION_STATUS if not failed else "BLOCKED_ACTION_DERIVED_SUBTRACTED_SUNSET_DISPERSION_INTERFACE_LANE"

    open_blockers = [
        "full_1PI_retarded_self_energy_and_zero_eta_physical_limit_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "off_shell_microscopic_action_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_sunset_dispersion_interface_verified.py", "sha256": sha256(VERIFIED_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_sunset_cut_audit.json", "sha256": sha256(CONTINUUM_ARTIFACT)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-sunset-dispersion-interface-v1",
        "artifact": "t13_uet_o2_sunset_dispersion_interface_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_SUBTRACTED_SUNSET_DISPERSION_INTERFACE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "formal neutral off-shell rest-energy extension of the declared elastic sunset cut",
                "finite-regulator retarded dispersion representation with an explicit reference subtraction",
                "KMS ratio, spectral/noise positivity, retarded sign witness, and composite-quadrature convergence",
                "on-shell matching of the extended cut to the canonical continuum sunset artifact under identical controls",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "formal subtracted dispersion interface only; no physical self-energy, Kubo, entropy, SI mapping, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(reference)},
        "on_shell_match": on_shell_match,
        "checks": checks,
        "failed_checks": failed,
        "continuum_dispersion_interface_completed": reference.continuum_dispersion_interface_completed,
        "real_part_subtraction_interface_completed": reference.real_part_subtraction_interface_completed,
        "off_shell_matching_interface_completed": reference.off_shell_matching_interface_completed,
        "continuum_sunset_self_energy_completed": reference.continuum_sunset_self_energy_completed,
        "full_1pi_retarded_self_energy_completed": reference.full_1pi_retarded_self_energy_completed,
        "real_part_subtraction_completed": reference.real_part_subtraction_completed,
        "off_shell_matching_completed": reference.off_shell_matching_completed,
        "unique_physical_renormalization_scheme_match_completed": reference.unique_physical_renormalization_scheme_match_completed,
        "physical_retarded_self_energy_completed": reference.physical_retarded_self_energy_completed,
        "physical_transport_coefficients_emitted": reference.physical_kubo_coefficient_emitted,
        "numeric_alpha_Phi_K_emitted": reference.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": reference.parameter_fitting_performed,
        "target_data_used": reference.target_data_used,
        "xie_2026_accessed": reference.xie_2026_accessed,
        "controlling_blocker": "full_1PI_retarded_self_energy_and_zero_eta_physical_limit_missing",
        "next_controller": "derive the full 1PI retarded self-energy and its physical regulator/renormalization match before treating the formal dispersion interface as physical transport",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_SUBTRACTED_SUNSET_DISPERSION_INTERFACE_LANE",
        "closure_level": closure_level,
        "data_role": reference.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
