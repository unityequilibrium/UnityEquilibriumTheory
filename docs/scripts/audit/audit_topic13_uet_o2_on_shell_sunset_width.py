"""Audit the action-matched neutral on-shell sunset width lane."""

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

from docs.core.uet_o2_on_shell_sunset_width import (
    SUNSET_WIDTH_CONVERGENCE_THRESHOLD,
    on_shell_sunset_collision_width_contract,
    on_shell_sunset_collision_width_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_on_shell_sunset_width_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_on_shell_sunset_width.py"
SUNSET = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_full_sunset_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = on_shell_sunset_collision_width_state(0.35, 0.5, 0.8)
    contract = on_shell_sunset_collision_width_contract()
    checks = {
        "state_is_finite": all(
            value == value and abs(float(value)) < float("inf")
            for value in asdict(state).values()
            if isinstance(value, (int, float))
        ),
        "neutral_scope_is_explicit": state.neutral_mu_scope_is_explicit and state.chemical_potential == 0.0,
        "channel_widths_are_positive": state.one_to_three_collision_width > 0.0 and state.two_to_two_collision_width > 0.0,
        "combined_width_is_channel_sum": abs(
            state.combined_collision_width
            - state.one_to_three_collision_width
            - state.two_to_two_collision_width
        )
        <= 1.0e-15,
        "retarded_cut_has_dissipative_sign": state.retarded_sign_is_dissipative,
        "width_is_positive": state.width_is_positive,
        "kms_residual_is_closed": state.combined_kms_log_ratio_residual <= 1.0e-12,
        "fdt_residual_is_closed": state.combined_fdt_residual <= 1.0e-12,
        "cut_convergence_is_bounded": state.cut_convergence_bound <= SUNSET_WIDTH_CONVERGENCE_THRESHOLD,
        "complete_off_shell_self_energy_remains_open": not state.complete_off_shell_1pi_self_energy_completed,
        "physical_transport_not_emitted": not state.physical_transport_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    status = (
        "PASS_ACTION_MATCHED_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE"
        if all(checks.values())
        else "FAIL_T13_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE"
    )
    report = {
        "schema_version": "t13-on-shell-sunset-width-audit-v1",
        "artifact": "t13_uet_o2_on_shell_sunset_width_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "action-matched neutral on-shell width from the declared 1<->3 plus labeled 2<->2 sunset cuts",
                "positive channel decomposition with natural-unit energy contract",
                "combined retarded-sign, KMS/FDT, and cut-convergence witness",
            ],
            "what_remains_open": [
                "complete_off_shell_finite_temperature_1pi_self_energy_missing",
                "unique_physical_renormalization_scheme_match_missing",
                "charged_finite_temperature_transport_state_match_missing",
                "physical_Kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_on_shell_sunset_width.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_full_sunset_sk_kms.py", "sha256": sha256(SUNSET)},
            ],
            "verification_status": status,
            "open_blockers": [
                "complete_off_shell_finite_temperature_1pi_self_energy_missing",
                "unique_physical_renormalization_scheme_match_missing",
                "charged_finite_temperature_transport_state_match_missing",
                "physical_Kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "neutral action-matched on-shell width input for a named natural-unit memory/collision lane only; no physical transport or Core unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "checks": checks,
        "contract": contract,
        "state": {"reference": asdict(state)},
        "controlling_blocker": "complete_off_shell_finite_temperature_1pi_self_energy_and_physical_transport_match_missing",
        "next_controller": "derive the charged finite-temperature off-shell retarded self-energy and matched current correlator; retain this neutral width as a lane witness",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "combined_collision_width": state.combined_collision_width,
        "cut_convergence_bound": state.cut_convergence_bound,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
