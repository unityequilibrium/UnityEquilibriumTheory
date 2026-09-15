"""Audit the low-temperature finite-T to vacuum sunset match."""

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

from docs.core.uet_o2_finite_temperature_sunset_vacuum_match import (  # noqa: E402
    FINITE_T_VACUUM_MATCH_STATUS,
    FINITE_T_VACUUM_MATCH_THRESHOLD,
    finite_temperature_sunset_vacuum_match_contract,
    finite_temperature_sunset_vacuum_match_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_vacuum_match_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_sunset_vacuum_match.py"
THERMAL_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_full_sunset_sk_kms.py"
VACUUM_MODULE = ROOT / "docs/core/uet_o2_action_1pi_sunset_retarded.py"
VACUUM_ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_1pi_sunset_retarded_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    vacuum_artifact = json.loads(VACUUM_ARTIFACT.read_text(encoding="utf-8-sig"))
    reference = tuple(
        float(value)
        for value in vacuum_artifact["state"]["reference"]["euclidean_reference_response"]
    )
    state = finite_temperature_sunset_vacuum_match_state(
        0.05,
        0.5,
        0.8,
        reference,
    )
    contract = finite_temperature_sunset_vacuum_match_contract()
    finite_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key not in {"species_count"}
    )
    finite_state = all(math.isfinite(float(value)) for value in finite_values)
    threshold = FINITE_T_VACUUM_MATCH_THRESHOLD
    checks = {
        "matched_invariant_and_normalization": state.matched_invariant_and_normalization_witness,
        "vacuum_match_completed": state.vacuum_match_completed,
        "spectral_relative_residual_passes": state.spectral_relative_residual <= threshold,
        "retarded_spectral_relative_residual_passes": state.retarded_spectral_relative_residual <= threshold,
        "retarded_imaginary_relative_residual_passes": state.retarded_imaginary_relative_residual <= threshold,
        "principal_value_relative_residual_passes": state.principal_value_relative_residual <= threshold,
        "two_to_two_vacuum_fraction_passes": state.two_to_two_fraction <= threshold,
        "one_to_three_relative_residual_passes": state.one_to_three_relative_residual <= threshold,
        "vacuum_retarded_sign_is_negative": state.vacuum_retarded_imaginary_part < 0.0,
        "thermal_retarded_sign_is_negative": state.thermal_retarded_imaginary_part < 0.0,
        "state_is_finite": finite_state,
        "physical_renormalization_remains_open": not state.physical_renormalization_scheme_match_completed,
        "full_finite_temperature_1pi_remains_open": not state.full_finite_temperature_1pi_self_energy_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "covariant_entropy_remains_open": not state.covariant_entropy_current_completed,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "physical_boundary_is_explicit": contract["excluded"]["physical_renormalization_scheme_match"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = FINITE_T_VACUUM_MATCH_STATUS if not failed else "BLOCKED_ACTION_DERIVED_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE"
    open_blockers = [
        "physical_renormalization_scheme_match_missing",
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/uet_o2_finite_temperature_sunset_vacuum_match.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_finite_temperature_full_sunset_sk_kms.py", "sha256": sha256(THERMAL_MODULE)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_retarded.py", "sha256": sha256(VACUUM_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_action_1pi_sunset_retarded_audit.json", "sha256": sha256(VACUUM_ARTIFACT)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-sunset-vacuum-match-v1",
        "artifact": "t13_uet_o2_finite_temperature_sunset_vacuum_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "matched low-temperature finite-temperature and vacuum sunset invariant/normalization inputs",
                "relative spectral and retarded imaginary-part matching at T=0.05",
                "low-temperature principal-value real-part matching under the declared subtraction reference",
                "vanishing 2<->2 thermal scattering contribution in the vacuum limit",
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
            "dependency_unlocked": "low-temperature finite-temperature-to-vacuum consistency bridge only; no physical renormalization, complete 1PI, transport, entropy, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "vacuum_match_completed": state.vacuum_match_completed,
        "spectral_relative_residual": state.spectral_relative_residual,
        "retarded_spectral_relative_residual": state.retarded_spectral_relative_residual,
        "retarded_imaginary_relative_residual": state.retarded_imaginary_relative_residual,
        "principal_value_relative_residual": state.principal_value_relative_residual,
        "two_to_two_fraction": state.two_to_two_fraction,
        "physical_renormalization_scheme_match_completed": state.physical_renormalization_scheme_match_completed,
        "full_finite_temperature_1pi_self_energy_completed": state.full_finite_temperature_1pi_self_energy_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "physical_renormalization_scheme_match_missing",
        "next_controller": "derive a physical renormalization condition set that matches the vacuum subtraction and complete finite-temperature 1PI object",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE",
        "closure_level": closure_level,
        "data_role": state.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "failed_checks": failed,
        "artifact": str(OUT.relative_to(ROOT)),
        "temperature_low": state.temperature_low,
        "spectral_relative_residual": state.spectral_relative_residual,
        "retarded_imaginary_relative_residual": state.retarded_imaginary_relative_residual,
        "principal_value_relative_residual": state.principal_value_relative_residual,
        "two_to_two_fraction": state.two_to_two_fraction,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
