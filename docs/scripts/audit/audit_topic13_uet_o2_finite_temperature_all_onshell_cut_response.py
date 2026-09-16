"""Audit the all-positive-energy on-shell sunset-cut response grid."""

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

from docs.core.uet_o2_finite_temperature_all_onshell_cut_response import (  # noqa: E402
    ALL_ONSHELL_CUT_RESPONSE_STATUS,
    ALL_ONSHELL_CUT_RESPONSE_THRESHOLD,
    finite_temperature_all_onshell_cut_response_contract,
    finite_temperature_all_onshell_cut_response_state,
)


OUT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_all_onshell_cut_response_audit.json"
)
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_all_onshell_cut_response.py"
GRID = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_declared_retarded_1pi_grid.py"
MULTIPLICITY = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_cut_multiplicity.py"
TAXONOMY = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_signed_cut_coverage.py"
SCATTERING = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_all_onshell_cut_response_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )
    contract = finite_temperature_all_onshell_cut_response_contract()
    numeric_values = []
    for point in state.response_grid.points:
        numeric_values.extend(
            value
            for key, value in asdict(point).items()
            if isinstance(value, (int, float)) and key != "invariant_s"
        )
    numeric_values.extend(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float))
    )
    finite_state = all(math.isfinite(float(value)) for value in numeric_values)
    checks = {
        "all_positive_energy_signed_cuts_completed": state.all_positive_energy_signed_cuts_completed,
        "all_positive_energy_spectral_response_completed": state.all_positive_energy_on_shell_spectral_response_completed,
        "on_shell_retarded_grid_completed": state.on_shell_retarded_grid_completed,
        "one_to_three_pattern_count_is_one": state.cut_multiplicity.one_to_three_sign_pattern_count == 1,
        "two_to_two_pattern_count_is_three": state.cut_multiplicity.two_to_two_sign_pattern_count == 3,
        "two_to_two_graph_weight_is_one_half": abs(
            state.cut_multiplicity.two_to_two_graph_weight - 0.5
        )
        <= 1.0e-15,
        "representative_factor_matches_graph_weight": state.cut_multiplicity.current_factor_matches_two_to_two_graph_weight,
        "grid_has_multiple_invariants": len(state.response_grid.points) >= 2,
        "matched_state_grid": state.response_grid.matched_state_witness,
        "positive_spectral_grid": state.response_grid.positive_spectral_grid_witness,
        "lower_half_plane_grid": state.response_grid.lower_half_plane_grid_witness,
        "kms_within_threshold": state.response_grid.max_kms_log_ratio_residual <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD,
        "fdt_within_threshold": state.response_grid.max_fdt_residual <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD,
        "pv_inner_within_threshold": state.response_grid.max_pv_inner_convergence_residual <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD,
        "pv_outer_within_threshold": state.response_grid.max_pv_outer_convergence_residual <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD,
        "retarded_i0_consistency": state.response_grid.max_retarded_i0_consistency_residual <= 1.0e-12,
        "finite_state": finite_state,
        "full_finite_temperature_1pi_remains_open": not state.full_finite_temperature_1pi_self_energy_completed,
        "physical_renormalization_remains_open": not state.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "xie_2026_not_accessed": not state.xie_2026_accessed,
        "contract_includes_all_positive_energy_cuts": contract["included"][
            "all_positive_energy_equal_mass_signed_cuts"
        ],
        "contract_excludes_complete_offshell_1pi": contract["excluded"][
            "complete_off_shell_finite_temperature_1pi_self_energy"
        ],
        "contract_excludes_holdout": contract["excluded"]["Xie_2026_holdout"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed_checks = [key for key, value in checks.items() if not value]
    status = ALL_ONSHELL_CUT_RESPONSE_STATUS if not failed_checks else (
        "FAIL_ACTION_DERIVED_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE"
    )
    evidence = [
        {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
        for path in (MODULE, GRID, MULTIPLICITY, TAXONOMY, SCATTERING)
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed_checks else "OPEN"
    major_result_id = "T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE"
    open_blockers = [
        "complete_off_shell_finite_temperature_1pi_self_energy_missing",
        "unique_physical_renormalization_scheme_match_missing",
        "physical_scattering_normalization_identity_not_admitted",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
    ]
    payload = {
        "schema_version": "t13-uet-o2-finite-t-all-onshell-cut-response-v1",
        "artifact": "t13_uet_o2_finite_temperature_all_onshell_cut_response_audit",
        "generated_at": str(date.today()),
        "status": status,
        "major_result_id": major_result_id,
        "closure_level": closure_level,
        "state": asdict(state),
        "contract": contract,
        "checks": checks,
        "failed_checks": failed_checks,
        "full_core_unlock": False,
        "claim_promotion": False,
        "evidence_artifacts": evidence,
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "controlling_blocker": (
            "complete_off_shell_finite_temperature_1pi_and_physical_"
            "renormalization_missing"
        ),
        "next_action": (
            "Evaluate the complete off-shell retarded/advanced/Keldysh 1PI object "
            "and select an independent physical renormalization anchor; retain this "
            "all-onshell spectral response as a non-SI lane."
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    payload["major_result"] = {
        "major_result_id": major_result_id,
        "topic": "Topic 13 Thermodynamic Bridge",
        "closure_level": closure_level,
        "what_is_closed": [
            "all positive-energy equal-mass 1<->3 and 2<->2 on-shell signed-cut partition",
            "graph-weighted representative for all three 2<->2 permutations",
            "state-matched multi-invariant retarded spectral response grid",
            "grid-level spectral positivity, lower-half-plane sign, KMS/FDT, retarded i0, and PV convergence",
        ]
        if not failed_checks
        else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "verification_status": status,
        "open_blockers": open_blockers,
        "dependency_unlocked": (
            "all positive-energy on-shell cut spectral response lane only; no complete "
            "off-shell 1PI, physical renormalization, Kubo, entropy, SI, alpha, Core, "
            "Gravity, Galaxy, or external-validation unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
        "evidence_artifacts": evidence,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed_checks,
                "artifact": str(OUT.relative_to(ROOT)),
                "max_kms_residual": state.response_grid.max_kms_log_ratio_residual,
                "max_fdt_residual": state.response_grid.max_fdt_residual,
                "max_pv_inner_residual": state.response_grid.max_pv_inner_convergence_residual,
                "max_pv_outer_residual": state.response_grid.max_pv_outer_convergence_residual,
                "max_retarded_i0_residual": state.response_grid.max_retarded_i0_consistency_residual,
                "two_to_two_graph_weight": state.cut_multiplicity.two_to_two_graph_weight,
            },
            indent=2,
        )
    )
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
