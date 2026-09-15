"""Audit the Topic 13 physical-renormalization condition contract."""

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

from docs.core.uet_o2_physical_renormalization_condition_contract import (  # noqa: E402
    ON_SHELL_CONDITION_THRESHOLD,
    PHYSICAL_RENORMALIZATION_CONTRACT_STATUS,
    physical_renormalization_condition_contract,
    physical_renormalization_condition_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_physical_renormalization_condition_contract.json"
MODULE = ROOT / "docs/core/uet_o2_physical_renormalization_condition_contract.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = physical_renormalization_condition_state(
        0.5,
        0.75,
        0.12,
        0.08,
    )
    contract = physical_renormalization_condition_contract()
    numeric_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key != "physical_anchor_supplied"
    )
    checks = {
        "below_threshold_domain_is_explicit": state.below_threshold_domain,
        "threshold_is_three_body_equal_mass_threshold": abs(
            state.three_body_threshold_s - 4.5
        ) <= ON_SHELL_CONDITION_THRESHOLD,
        "pole_condition_passes": state.inverse_propagator_pole_residual
        <= ON_SHELL_CONDITION_THRESHOLD,
        "unit_residue_condition_passes": state.inverse_propagator_residue_residual
        <= ON_SHELL_CONDITION_THRESHOLD,
        "counterterm_units_are_separated": (
            isinstance(state.mass_counterterm, float)
            and isinstance(state.wavefunction_counterterm, float)
        ),
        "state_is_finite": all(math.isfinite(float(value)) for value in numeric_values),
        "physical_anchor_remains_open": not state.physical_anchor_supplied,
        "physical_scheme_match_remains_open": not state.physical_renormalization_scheme_match_completed,
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
        "required_anchor_fields_are_declared": len(contract["required_external_anchor_fields"]) >= 8,
        "forbidden_holdout_inputs_are_declared": "Xie 2026 numeric holdout" in contract["forbidden_inputs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = PHYSICAL_RENORMALIZATION_CONTRACT_STATUS if not failed else "BLOCKED_ON_SHELL_PHYSICAL_RENORMALIZATION_CONDITION_CONTRACT"
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    evidence = [
        {
            "path": "docs/core/uet_o2_physical_renormalization_condition_contract.py",
            "sha256": sha256(MODULE),
        }
    ]
    open_blockers = [
        "external_physical_pole_or_residue_anchor_missing",
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    artifact = {
        "schema_version": "t13-uet-o2-physical-renormalization-condition-contract-v1",
        "artifact": "t13_uet_o2_physical_renormalization_condition_contract",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_PHYSICAL_RENORMALIZATION_CONDITION_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "below-threshold on-shell pole condition contract",
                "unit-residue condition contract",
                "mass-counterterm and wavefunction-counterterm unit separation",
                "external physical-anchor acceptance schema",
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
            "dependency_unlocked": "renormalization-condition acceptance protocol only; physical scheme, complete 1PI, Topic 13, Core, Gravity, and external-validation dependencies remain blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"formal_witness": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "physical_anchor_supplied": state.physical_anchor_supplied,
        "physical_renormalization_scheme_match_completed": state.physical_renormalization_scheme_match_completed,
        "full_finite_temperature_1pi_self_energy_completed": state.full_finite_temperature_1pi_self_energy_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "external_physical_pole_or_residue_anchor_missing",
        "next_controller": "source-lock an independent physical pole/residue or microscopic renormalization-condition record, then evaluate the complete finite-temperature 1PI object without using TTG target residuals or Xie 2026",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_PHYSICAL_RENORMALIZATION_CONDITION_CONTRACT",
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
        "closure_level": closure_level,
        "pole_residual": state.inverse_propagator_pole_residual,
        "residue_residual": state.inverse_propagator_residue_residual,
        "physical_anchor_supplied": state.physical_anchor_supplied,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
