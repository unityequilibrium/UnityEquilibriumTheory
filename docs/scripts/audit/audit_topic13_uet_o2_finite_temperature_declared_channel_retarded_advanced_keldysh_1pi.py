"""Audit the declared-channel retarded/advanced/Keldysh 1PI interface."""

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

from docs.core.uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi import (  # noqa: E402
    DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD,
    DECLARED_CHANNEL_RETA_KELDYSH_1PI_STATUS,
    DECLARED_CHANNEL_RETA_KELDYSH_1PI_THRESHOLD,
    finite_temperature_declared_channel_reta_keldysh_1pi_contract,
    finite_temperature_declared_channel_reta_keldysh_1pi_state,
)


OUT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi_audit.json"
)
MODULE = ROOT / (
    "docs/core/"
    "uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py"
)
SOURCE_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_declared_retarded_1pi_grid.py"
SOURCE_ARTIFACT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_declared_channel_reta_keldysh_1pi_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )
    contract = finite_temperature_declared_channel_reta_keldysh_1pi_contract()
    numeric_values = []
    for point in state.points:
        numeric_values.extend(
            value
            for key, value in asdict(point).items()
            if isinstance(value, (int, float))
        )
    finite_state = all(math.isfinite(float(value)) for value in numeric_values)
    checks = {
        "declared_channel_component_triplet_completed": state.declared_channel_retarded_advanced_keldysh_1pi_completed,
        "grid_has_multiple_points": len(state.points) >= 2,
        "all_points_are_finite": finite_state,
        "all_one_to_three_channels_completed": all(point.one_to_three_completed for point in state.points),
        "all_two_to_two_channels_completed": all(point.two_to_two_completed for point in state.points),
        "retarded_advanced_conjugacy": state.max_retarded_advanced_conjugacy_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD,
        "retarded_discontinuity": state.max_retarded_discontinuity_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD,
        "keldysh_component_definition": state.max_keldysh_component_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD,
        "keldysh_fdt_within_threshold": state.max_keldysh_fdt_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_THRESHOLD,
        "bphz_subtraction_interface_preserved": state.bphz_subtraction_interface_preserved,
        "full_offshell_self_energy_stays_open": not state.complete_off_shell_finite_temperature_1pi_self_energy_completed,
        "all_sunset_channels_stays_open": not state.all_finite_temperature_sunset_channels_completed,
        "physical_renormalization_stays_open": not state.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "xie_2026_not_accessed": not state.xie_2026_accessed,
        "contract_excludes_full_offshell": contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"],
        "contract_excludes_physical_renormalization": contract["excluded"]["unique_physical_renormalization"],
        "contract_excludes_holdout": contract["excluded"]["Xie_2026_holdout"],
        "Phi_ontology_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_preserved": "derived physical/history trace" in contract["ontology"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["ontology"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = DECLARED_CHANNEL_RETA_KELDYSH_1PI_STATUS if not failed else (
        "BLOCKED_ACTION_DERIVED_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE"
    )
    open_blockers = [
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "all_finite_temperature_sunset_channels_missing",
        "unique_physical_renormalization_anchor_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    evidence = [
        {"path": "docs/core/uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_finite_temperature_declared_retarded_1pi_grid.py", "sha256": sha256(SOURCE_MODULE)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit.json", "sha256": sha256(SOURCE_ARTIFACT)},
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-declared-channel-reta-keldysh-1pi-v1",
        "artifact": "t13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "numerical retarded and advanced components for the declared 1<->3 and representative 2<->2 sunset channels",
                "explicit retarded discontinuity relation in the declared spectral normalization",
                "declared Keldysh/noise component and its finite-temperature FDT relation",
                "state-matched component residuals and BPHZ subtraction interface without target fitting",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "declared-channel real-time 1PI component interface only; complete off-shell all-channel self-energy, physical renormalization, Kubo, entropy, SI, alpha, TTG, Core, and external validation remain blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "declared_channel_retarded_advanced_keldysh_1pi_completed": state.declared_channel_retarded_advanced_keldysh_1pi_completed,
        "max_retarded_advanced_conjugacy_residual": state.max_retarded_advanced_conjugacy_residual,
        "max_retarded_discontinuity_residual": state.max_retarded_discontinuity_residual,
        "max_keldysh_component_residual": state.max_keldysh_component_residual,
        "max_keldysh_fdt_residual": state.max_keldysh_fdt_residual,
        "complete_off_shell_finite_temperature_1pi_self_energy_completed": state.complete_off_shell_finite_temperature_1pi_self_energy_completed,
        "all_finite_temperature_sunset_channels_completed": state.all_finite_temperature_sunset_channels_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "complete_off_shell_all_channel_1pi_and_physical_renormalization_anchor_missing",
        "next_controller": "complete the off-shell all-channel finite-temperature 1PI evaluation and source-lock an independent physical renormalization anchor without using TTG target residuals or Xie 2026",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE",
        "closure_level": closure_level,
        "data_role": state.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT)), "max_keldysh_fdt_residual": state.max_keldysh_fdt_residual}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
