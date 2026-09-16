"""Audit the declared finite-temperature retarded response grid."""

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

from docs.core.uet_o2_finite_temperature_declared_retarded_1pi_grid import (  # noqa: E402
    DECLARED_RETARDED_1PI_GRID_STATUS,
    DECLARED_RETARDED_1PI_GRID_THRESHOLD,
    finite_temperature_declared_retarded_1pi_grid_contract,
    finite_temperature_declared_retarded_1pi_grid_state,
)


OUT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit.json"
)
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_declared_retarded_1pi_grid.py"
ONE_TO_THREE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py"
TWO_TO_TWO = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_declared_retarded_1pi_grid_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )
    contract = finite_temperature_declared_retarded_1pi_grid_contract()
    numeric_values = []
    for point in state.points:
        numeric_values.extend(
            value
            for key, value in asdict(point).items()
            if isinstance(value, (int, float)) and key != "invariant_s"
        )
    numeric_values.extend(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float)) and key != "species_count"
    )
    finite_state = all(math.isfinite(float(value)) for value in numeric_values)
    threshold = DECLARED_RETARDED_1PI_GRID_THRESHOLD
    checks = {
        "declared_response_grid_completed": state.declared_retarded_response_grid_completed,
        "declared_pole_subtracted_response_completed": state.declared_1pi_pole_subtracted_response_completed,
        "grid_has_multiple_points": len(state.points) >= 2,
        "all_points_above_three_body_threshold": all(
            point.invariant_s > state.three_body_threshold_s for point in state.points
        ),
        "matched_state_witness": state.matched_state_witness,
        "positive_spectral_grid": state.positive_spectral_grid_witness,
        "lower_half_plane_grid": state.lower_half_plane_grid_witness,
        "all_one_to_three_channel_contracts_completed": all(
            point.one_to_three_completed for point in state.points
        ),
        "all_two_to_two_channel_contracts_completed": all(
            point.two_to_two_completed for point in state.points
        ),
        "finite_numeric_state": finite_state,
        "kms_residual_within_threshold": (
            state.max_kms_log_ratio_residual <= threshold
        ),
        "fdt_residual_within_threshold": state.max_fdt_residual <= threshold,
        "pv_inner_convergence_within_threshold": (
            state.max_pv_inner_convergence_residual <= threshold
        ),
        "pv_outer_convergence_within_threshold": (
            state.max_pv_outer_convergence_residual <= threshold
        ),
        "retarded_i0_consistency": (
            state.max_retarded_i0_consistency_residual <= 1.0e-12
        ),
        "full_finite_temperature_1pi_self_energy_stays_open": (
            not state.full_finite_temperature_1pi_self_energy_completed
        ),
        "all_finite_temperature_sunset_channels_stays_open": (
            not state.all_finite_temperature_sunset_channels_completed
        ),
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "xie_2026_not_accessed": not state.xie_2026_accessed,
        "contract_excludes_full_1pi": contract["excluded"][
            "complete_finite_temperature_1pi_self_energy"
        ],
        "contract_excludes_physical_kubo": contract["excluded"][
            "physical_kubo_coefficient"
        ],
        "contract_excludes_holdout": contract["excluded"]["Xie_2026_holdout"],
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = DECLARED_RETARDED_1PI_GRID_STATUS if not failed_checks else "FAIL_DECLARED_RETARDED_1PI_RESPONSE_GRID"
    payload = {
        "schema_version": "1.0",
        "artifact": "t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit",
        "generated_at": str(date.today()),
        "status": status,
        "major_result_id": "T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE",
        "closure_level": "CLOSED_FOR_LANE" if not failed_checks else "OPEN",
        "state": asdict(state),
        "contract": contract,
        "checks": checks,
        "failed_checks": failed_checks,
        "full_core_unlock": False,
        "claim_promotion": False,
        "evidence_artifacts": [
            {"path": str(MODULE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MODULE)},
            {"path": str(ONE_TO_THREE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(ONE_TO_THREE)},
            {"path": str(TWO_TO_TWO.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(TWO_TO_TWO)},
        ],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "controlling_blocker": (
            "complete_finite_temperature_1pi_self_energy_and_all_channel_"
            "physical_renormalization_missing"
        ),
        "next_action": (
            "Derive the full interacting finite-temperature retarded 1PI self-energy "
            "and physical renormalization anchor; keep this declared grid lane non-SI "
            "and separate from physical Kubo admission."
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    payload["major_result"] = {
        "major_result_id": payload["major_result_id"],
        "topic": "Topic 13 Thermodynamic Bridge",
        "closure_level": payload["closure_level"],
        "what_is_closed": [
            "state-matched declared 1<->3 plus labeled 2<->2 retarded response grid",
            "grid-level KMS/FDT, retarded i0 sign, spectral positivity, and PV convergence",
        ],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "verification_status": status,
        "open_blockers": [
            "complete_finite_temperature_1pi_self_energy_missing",
            "all_finite_temperature_sunset_channels_missing",
            "physical_renormalization_anchor_missing",
        ],
        "dependency_unlocked": (
            "declared retarded response-grid lane only; no physical Kubo, SI, "
            "alpha, Core, Gravity, Galaxy, or external-validation unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
        "evidence_artifacts": payload["evidence_artifacts"],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
