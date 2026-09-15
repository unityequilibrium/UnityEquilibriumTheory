"""Audit the formal finite-temperature off-shell O(2) 1PI lane."""

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

from docs.core.uet_o2_finite_temperature_offshell_1pi import (  # noqa: E402
    FINITE_T_OFFSHELL_1PI_STATUS,
    finite_temperature_offshell_1pi_contract,
    finite_temperature_offshell_1pi_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_offshell_1pi_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_offshell_1pi.py"
TENSOR = ROOT / "docs/core/uet_o2_action_1pi_sunset_tensor.py"
EUCLIDEAN = ROOT / "docs/core/uet_o2_action_1pi_sunset_euclidean.py"
FULL_CUT = ROOT / "docs/core/uet_o2_finite_temperature_full_sunset_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_offshell_1pi_state(0.35, 0.5, 0.8)
    contract = finite_temperature_offshell_1pi_contract()
    values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float))
        and key not in {"species_count", "external_matsubara_index"}
    )
    finite_state = all(math.isfinite(float(value)) for value in values)
    checks = {
        "state_is_finite": finite_state,
        "loop_integral_dimensions_are_closed": state.loop_integral_dimensions_closed,
        "species_diagonal_structure_is_closed": state.species_diagonal_structure_closed,
        "one_loop_tadpole_sum_integral_is_closed": state.one_loop_tadpole_sum_integral_closed,
        "two_loop_sunset_sum_integral_is_closed": state.two_loop_sunset_sum_integral_closed,
        "all_signed_cut_assignments_are_included": state.all_signed_cut_assignments_included,
        "retarded_continuation_is_closed": state.retarded_continuation_contract_closed,
        "spectral_representation_is_closed": state.spectral_representation_contract_closed,
        "KMS_relation_is_closed": state.kms_relation_contract_closed,
        "thermal_vacuum_UV_split_is_closed": state.thermal_vacuum_uv_split_closed,
        "local_counterterm_basis_is_closed": state.local_counterterm_basis_closed,
        "formal_offshell_1pi_object_is_completed": state.formal_offshell_1pi_object_completed,
        "formal_status_is_declared": contract["status"] == FINITE_T_OFFSHELL_1PI_STATUS,
        "tadpole_has_energy_squared_units": "energy squared" in contract["unit_contract"]["one_loop_sum_integral"],
        "sunset_has_energy_squared_units": "energy squared" in contract["unit_contract"]["two_loop_sum_integral"],
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "physical_renormalization_remains_open": contract["excluded"]["unique_physical_renormalization_anchor"],
        "physical_kubo_remains_open": contract["excluded"]["physical_Kubo_coefficient"],
        "alpha_boundary_is_explicit": contract["excluded"]["alpha_Phi_K"],
        "ding_numeric_boundary_is_explicit": contract["excluded"]["Ding_C_src_numeric_source"],
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = FINITE_T_OFFSHELL_1PI_STATUS if not failed else "BLOCKED_ACTION_DERIVED_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE"
    evidence = [
        {"path": "docs/core/uet_o2_finite_temperature_offshell_1pi.py", "sha256": sha256(MODULE)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_tensor.py", "sha256": sha256(TENSOR)},
        {"path": "docs/core/uet_o2_action_1pi_sunset_euclidean.py", "sha256": sha256(EUCLIDEAN)},
        {"path": "docs/core/uet_o2_finite_temperature_full_sunset_sk_kms.py", "sha256": sha256(FULL_CUT)},
    ]
    open_blockers = [
        "unique_physical_renormalization_scheme_match_missing",
        "physical_Kubo_coefficient_missing",
        "covariant_entropy_current_heat_flux_and_dissipative_balance_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed else "OPEN"
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-offshell-1pi-formal-v1",
        "artifact": "t13_uet_o2_finite_temperature_offshell_1pi_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": closure_level,
            "what_is_closed": [
                "formal finite-temperature O(2) off-shell two-point 1PI object through the declared one-loop tadpole and two-loop sunset order",
                "all signed three-line thermal cut assignments represented by the full Matsubara sum-integral rather than a selected channel",
                "retarded continuation, spectral representation, and KMS interface",
                "thermal-minus-vacuum UV split and local two-point/action counterterm basis",
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
            "dependency_unlocked": "formal finite-temperature off-shell 1PI/KMS interface only; physical renormalization, Kubo, entropy, SI, alpha, TTG, Core, and external validation remain blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "formal_offshell_1pi_object_completed": state.formal_offshell_1pi_object_completed,
        "unique_physical_renormalization_scheme_match_completed": state.unique_physical_renormalization_scheme_match_completed,
        "physical_numeric_evaluation_completed": state.physical_numeric_evaluation_completed,
        "physical_transport_coefficients_emitted": state.physical_kubo_coefficient_emitted,
        "covariant_entropy_current_completed": state.covariant_entropy_current_completed,
        "numeric_alpha_Phi_K_emitted": state.numeric_alpha_Phi_K_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "unique_physical_renormalization_scheme_or_external_anchor_missing",
        "next_controller": "select and source-lock a physical renormalization anchor, then evaluate the declared formal object without TTG target residuals or Xie 2026",
        "claim_promotion": False,
        "major_result_id": "T13_UET_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE",
        "closure_level": closure_level,
        "data_role": state.data_role,
        "open_blockers": open_blockers,
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "artifact": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
