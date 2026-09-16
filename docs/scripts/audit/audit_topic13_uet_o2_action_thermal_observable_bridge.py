"""Audit the action-derived natural Phi-to-thermal bridge lane."""

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

from docs.core.uet_o2_action_thermal_observable_bridge import (  # noqa: E402
    ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS,
    action_natural_phi_thermal_bridge_contract,
    action_natural_phi_thermal_bridge_state,
)

OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_thermal_observable_bridge_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py"
EOS = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"
BETA = ROOT / "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = action_natural_phi_thermal_bridge_contract()
    state = action_natural_phi_thermal_bridge_state()
    checks = {
        "status_contract_is_named": contract["status"]
        == ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS,
        "action_eos_identity_is_explicit": contract["equations"]["action_eos"]
        == "p=p_qp(T,mu,Phi); epsilon=-p+T*partial_T p+mu*partial_mu p",
        "energy_response_equation_is_explicit": contract["equations"]["energy_response"]
        == "Delta_epsilon^nat=(partial_Phi epsilon)_(T,mu)*Delta_Phi",
        "thermal_response_equation_is_explicit": contract["equations"][
            "natural_temperature_response"
        ]
        == "Delta_T_q^nat=Delta_epsilon^nat/C_epsilon_T^nat",
        "fixed_mu_susceptibility_is_not_called_cv": "not source c_v"
        in contract["unit_contract"]["C_epsilon_T"],
        "normal_branch_is_locked": state.branch == "normal",
        "thermodynamic_identity_closes": abs(state.thermodynamic_identity_residual)
        <= 1.0e-12,
        "natural_susceptibility_is_positive": state.energy_temperature_susceptibility
        > 0.0
        and state.refined_energy_temperature_susceptibility > 0.0,
        "response_derivatives_are_finite": all(
            value == value and abs(value) < float("inf")
            for value in (
                state.energy_response_derivative,
                state.refined_energy_response_derivative,
                state.energy_temperature_susceptibility,
                state.refined_energy_temperature_susceptibility,
                state.alpha_phi_temperature_natural,
                state.refined_alpha_phi_temperature_natural,
            )
        ),
        "natural_bridge_map_is_resolved": abs(
            state.linear_energy_response
            - state.energy_temperature_susceptibility
            * state.linear_temperature_response_natural
        )
        <= 1.0e-14,
        "linear_response_is_local": state.linearization_relative_residual <= 1.0e-3,
        "response_refinement_is_stable": state.response_refinement_relative_change
        <= 1.0e-3,
        "susceptibility_refinement_is_stable": state.susceptibility_refinement_relative_change
        <= 1.0e-3,
        "coefficient_refinement_is_stable": state.coefficient_refinement_relative_change
        <= 1.0e-3,
        "phi_ontology_is_preserved": state.phi_ontology_preserved
        and contract["unit_contract"]["Phi"]
        == "existing effective response variable; normalization-dependent and not temperature",
        "physical_cv_is_not_emitted": state.physical_cv_emitted is False
        and contract["excluded"]["physical_cv"] is True,
        "si_alpha_is_not_emitted": state.numeric_alpha_phi_k_emitted is False
        and contract["excluded"]["numeric_alpha_Phi_K"] is True,
        "normalized_beta_is_not_emitted": state.normalized_beta_t13_emitted is False,
        "e0_is_not_emitted": state.numeric_e0_emitted is False,
        "landauer_is_not_used": state.landauer_identity_used is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "xie_holdout_is_unread": state.xie_2026_accessed is False,
    }
    status = (
        ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE"
    )
    report = {
        "schema_version": "t13-uet-o2-action-natural-phi-thermal-bridge-v1",
        "artifact": "t13_uet_o2_action_thermal_observable_bridge_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "full_core_unlock": False,
        "major_result": {
            "major_result_id": "T13_UET_O2_ACTION_NATURAL_PHI_THERMAL_BRIDGE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "action-derived natural-unit energy-density response to the existing Phi variable",
                "fixed-(mu,Phi) natural thermal susceptibility for the local response map",
                "first-order natural quasi-temperature response",
                "local derivative refinement and thermodynamic branch-lock controls",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS)},
                {"path": "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py", "sha256": sha256(BETA)},
            ],
            "verification_status": status,
            "open_blockers": [
                "physical_Phi_SI_energy_anchor_missing",
                "independent_alpha_Phi_K_calibration_missing",
                "fixed_density_c_v_or_Ding_C_src_not_source_locked",
                "material_regime_mapping_to_TTG_not_closed",
                "full_finite_temperature_EOS_transport_SK_KMS_entropy_completion_missing",
            ],
            "dependency_unlocked": "action-derived natural-unit Phi-to-thermal bridge lane only; no SI, alpha, TTG, physical transport, or Full Topic 13 unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "state": asdict(state),
        "contract": contract,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "calibration_path_may_read_holdout": False,
            "target_data_used": False,
            "parameter_fitting_performed": False,
        },
        "controlling_blocker": "physical_Phi_SI_energy_anchor_missing_and_independent_alpha_Phi_K_open",
        "next_controller": "source-lock an independent Phi/SI response record and fixed-density thermal-capacity source; do not relabel C_epsilon_T or emit alpha_Phi_K",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    failed = [name for name, passed in checks.items() if not passed]
    print(json.dumps({"status": status, "failed_checks": failed, "alpha_phi_temperature_natural": state.alpha_phi_temperature_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
