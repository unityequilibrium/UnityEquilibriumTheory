"""Audit the scoped finite-temperature sunset renormalization no-go."""

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

from docs.core.uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go import (  # noqa: E402
    CUT_INVARIANCE_THRESHOLD,
    RENORMALIZATION_IDENTIFIABILITY_NO_GO_STATUS,
    RENORMALIZATION_SCHEME_DEPENDENCE_THRESHOLD,
    sunset_renormalization_identifiability_no_go_contract,
    sunset_renormalization_identifiability_no_go_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go.py"
ONE_TO_THREE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py"
TWO_TO_TWO = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = sunset_renormalization_identifiability_no_go_state(0.35, 0.5, 0.8)
    contract = sunset_renormalization_identifiability_no_go_contract()
    finite_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key not in {"species_count"}
    )
    finite_state = all(math.isfinite(float(value)) for value in finite_values)
    checks = {
        "reference_points_are_distinct": len(state.reference_euclidean_s_points) >= 2,
        "reference_dependence_is_witnessed": state.reference_dependence_witness,
        "cut_is_invariant_under_reference_change": state.cut_invariance_witness,
        "renormalization_identifiability_no_go_is_completed": state.renormalization_identifiability_no_go_completed,
        "pv_relative_span_is_above_no_go_threshold": state.principal_value_relative_span >= RENORMALIZATION_SCHEME_DEPENDENCE_THRESHOLD,
        "spectral_invariance_is_within_numeric_control": state.spectral_invariance_residual <= CUT_INVARIANCE_THRESHOLD,
        "kms_invariance_is_within_numeric_control": state.kms_invariance_residual <= CUT_INVARIANCE_THRESHOLD,
        "fdt_invariance_is_within_numeric_control": state.fdt_invariance_residual <= CUT_INVARIANCE_THRESHOLD,
        "state_is_finite": finite_state,
        "physical_scheme_selection_remains_open": not state.physical_renormalization_scheme_match_completed,
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
        "no_go_boundary_is_explicit": contract["included"]["scoped_physical_scheme_identifiability_no_go"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = RENORMALIZATION_IDENTIFIABILITY_NO_GO_STATUS if not failed else "BLOCKED_ACTION_DERIVED_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO"
    open_blockers = [
        "physical_renormalization_scheme_selection_missing",
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py", "sha256": sha256(ONE_TO_THREE)},
        {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py", "sha256": sha256(TWO_TO_TWO)},
    ]
    closure_level = "CLOSED_AS_NO_GO" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-sunset-renormalization-identifiability-no-go-v1",
        "artifact": "t13_uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "scoped no-go for selecting a unique physical PV renormalization reference from the current thermal cut and natural-unit contract",
                "reference-dependent summed PV real part under fixed spectral/KMS/FDT observables",
                "explicit separation of cut invariants from local real-part subtraction data",
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
            "dependency_unlocked": "scoped renormalization identifiability no-go only; physical scheme selection, complete 1PI, transport, entropy, SI, alpha, Core, Gravity, and external-validation dependencies remain blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "renormalization_identifiability_no_go_completed": state.renormalization_identifiability_no_go_completed,
        "reference_dependence_witness": state.reference_dependence_witness,
        "cut_invariance_witness": state.cut_invariance_witness,
        "principal_value_relative_span": state.principal_value_relative_span,
        "spectral_invariance_residual": state.spectral_invariance_residual,
        "kms_invariance_residual": state.kms_invariance_residual,
        "fdt_invariance_residual": state.fdt_invariance_residual,
        "physical_renormalization_scheme_match_completed": state.physical_renormalization_scheme_match_completed,
        "full_finite_temperature_1pi_self_energy_completed": state.full_finite_temperature_1pi_self_energy_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "physical_renormalization_scheme_selection_missing",
        "next_controller": "introduce an independent physical renormalization condition set and re-evaluate the complete finite-temperature 1PI object",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO",
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
        "reference_points": state.reference_euclidean_s_points,
        "principal_value_real_parts": state.combined_principal_value_real_parts,
        "principal_value_relative_span": state.principal_value_relative_span,
        "spectral_invariance_residual": state.spectral_invariance_residual,
        "kms_invariance_residual": state.kms_invariance_residual,
        "fdt_invariance_residual": state.fdt_invariance_residual,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
