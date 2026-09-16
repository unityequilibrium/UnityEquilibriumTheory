"""Audit the continuum thermal relative-flow response lane for Topic 13."""

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

from docs.core.uet_o2_continuum_relative_flow_kubo import (  # noqa: E402
    CONTINUUM_ACCEPTANCE_THRESHOLD,
    CONTINUUM_RELATIVE_FLOW_STATUS,
    continuum_relative_flow_contract,
    continuum_relative_flow_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_continuum_relative_flow_kubo_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_continuum_relative_flow_kubo.py"
EOS = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"
CONDENSED = ROOT / "docs/core/02_equations/o2/uet_o2_condensed_relative_flow_collision.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = continuum_relative_flow_state(
        0.20,
        1.28,
        0.15,
        radial_orders=(24, 32, 40),
        angular_order=24,
        angular_refined_order=36,
        radial_scale_factor=1.0,
        refined_scale_factor=0.5,
    )
    contract = continuum_relative_flow_contract()
    numeric_values = tuple(
        value
        for key, value in asdict(state).items()
        if isinstance(value, (int, float))
    )
    checks = {
        "continuum_integrals_are_finite": state.continuum_integrals_finite,
        "continuum_convergence_passes": state.continuum_convergence_passes,
        "threshold_is_unchanged": (
            CONTINUUM_ACCEPTANCE_THRESHOLD == 1.0e-2
            and state.radial_max_relative_change <= 1.0e-2
            and state.angular_refined_relative_change <= 1.0e-2
            and state.scale_refined_relative_change <= 1.0e-2
        ),
        "response_is_positive": state.dc_relative_response > 0.0,
        "collision_rate_is_positive": state.relative_collision_rate > 0.0,
        "operator_is_symmetric": state.symmetric_kernel_residual <= 1.0e-12,
        "common_flow_is_conserved": state.common_flow_conservation_residual <= 1.0e-12,
        "source_has_no_common_mode": state.source_common_mode_residual <= 1.0e-12,
        "operator_is_positive_semidefinite": min(state.collision_eigenvalues) >= -1.0e-12,
        "kms_is_closed": state.kms_residual <= 1.0e-12,
        "fdt_is_closed": state.fdt_residual <= 1.0e-12,
        "entropy_is_nonnegative": state.entropy_production_at_unit_force >= 0.0,
        "state_numeric_values_are_finite": all(math.isfinite(float(value)) for value in numeric_values),
        "no_finite_cutoff_is_used": state.finite_cutoff_used is False,
        "loop_renormalization_remains_open": state.loop_renormalized_vertex_completed is False,
        "physical_kubo_not_emitted": state.physical_kubo_coefficient_emitted is False,
        "numeric_alpha_not_emitted": state.numeric_alpha_phi_k_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "holdout_is_unread": state.xie_2026_accessed is False,
        "Phi_ontology_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_is_derived": "not an independent state" in contract["unit_contract"]["R_gen"],
        "R_obs_is_separate": "observer record" in contract["unit_contract"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = CONTINUUM_RELATIVE_FLOW_STATUS if not failed else "BLOCKED_T13_CONTINUUM_RELATIVE_FLOW_KUBO"
    artifact = {
        "schema_version": "t13-uet-o2-continuum-relative-flow-kubo-v1",
        "artifact": "t13_uet_o2_continuum_relative_flow_kubo_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONTINUUM_RELATIVE_FLOW_KUBO_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the screened contact-channel response is evaluated on a compactified k in [0,infinity) domain",
                "radial-order, angular-order, and compactification-scale refinements pass the unchanged 1e-2 controller",
                "the relative-flow operator is symmetric positive semidefinite and conserves common flow",
                "the continuum thermal response has a natural-unit retarded KMS/FDT and entropy interface",
            ] if not failed else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_continuum_relative_flow_kubo.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS)},
                {"path": "docs/core/02_equations/o2/uet_o2_condensed_relative_flow_collision.py", "sha256": sha256(CONDENSED)},
            ],
            "verification_status": status,
            "open_blockers": [
                "loop_renormalized_condensed_vertex_missing",
                "complete_condensed_scattering_channels_missing",
                "physical_Kubo_coefficient_record_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "continuum natural-unit screened contact response lane only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "state": {"reference": asdict(state)},
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": bool(not failed),
        "loop_renormalized_vertex_completed": state.loop_renormalized_vertex_completed,
        "physical_kubo_coefficient_emitted": state.physical_kubo_coefficient_emitted,
        "numeric_alpha_phi_k_emitted": state.numeric_alpha_phi_k_emitted,
        "parameter_fitting_performed": state.parameter_fitting_performed,
        "target_data_used": state.target_data_used,
        "xie_2026_accessed": state.xie_2026_accessed,
        "controlling_blocker": "loop_renormalized_condensed_vertex_and_physical_kubo_match_missing",
        "next_controller": "derive and source-lock the loop-renormalized condensed vertex/retarded correlator, then attach units and uncertainty; do not promote this continuum thermal contact response as physical Kubo",
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "failed_checks": failed,
        "radial_max_relative_change": state.radial_max_relative_change,
        "angular_refined_relative_change": state.angular_refined_relative_change,
        "scale_refined_relative_change": state.scale_refined_relative_change,
        "dc_relative_response": state.dc_relative_response,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
