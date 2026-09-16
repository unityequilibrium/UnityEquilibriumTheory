"""Audit the non-Landauer action-origin thermal stiffness slope lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from math import isfinite
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_stiffness_beta import (  # noqa: E402
    action_thermal_stiffness_beta_contract,
    action_thermal_stiffness_beta_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_action_thermal_stiffness_beta_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"
MATTER_MODULE = ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py"
RESPONSE_MODULE = ROOT / "docs/core/02_equations/covariant/uet_covariant_response.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = action_thermal_stiffness_beta_state()
    contract = action_thermal_stiffness_beta_contract()
    checks = {
        "normal_branch_stencil_is_locked": state.branch == "normal",
        "action_response_coupling_is_nonzero": (
            state.response_epsilon_nc > 0.0 and state.response_coupling > 0.0
        ),
        "finite_temperature_pressure_is_positive": state.pressure > 0.0,
        "finite_temperature_entropy_is_positive": state.entropy_density > 0.0,
        "curvature_is_finite": isfinite(state.a_phi_natural),
        "action_beta_is_finite_and_nonzero": (
            isfinite(state.beta_phi_natural)
            and abs(state.beta_phi_natural) > 0.0
        ),
        "curvature_stencil_refinement_is_stable": state.curvature_relative_change <= 1.0e-3,
        "beta_stencil_refinement_is_stable": state.beta_relative_change <= 1.0e-3,
        "normalized_beta_is_not_emitted": state.normalized_beta_T13_emitted is False,
        "e0_is_not_emitted": state.numeric_e0_emitted is False,
        "numeric_alpha_is_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "landauer_is_not_used": state.landauer_identity_used is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "xie_holdout_is_unread": state.xie_2026_accessed is False,
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "normalized_and_physical_boundaries_are_explicit": all(
            contract["excluded"][key]
            for key in (
                "normalized_beta_T13",
                "physical_beta_source",
                "SI_Phi_normalization",
                "e0",
                "alpha_Phi_K",
                "physical_Kubo",
                "TTG_validation",
            )
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_THERMAL_STIFFNESS_BETA_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_THERMAL_STIFFNESS_BETA_LANE"
    )
    major_result = {
        "major_result_id": "T13_UET_O2_ACTION_THERMAL_STIFFNESS_BETA_LANE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "what_is_closed": [
            "the finite-temperature quasiparticle free-energy curvature with respect to the existing Phi response variable",
            "a non-Landauer natural-unit stiffness slope beta_Phi^nat=T*partial_T a_Phi^nat on one declared normal branch",
            "symmetric Phi and temperature stencil refinement checks for the action-derived derivative",
            "explicit separation of natural action beta from normalized beta_T13, SI normalization, and alpha_Phi_K",
        ] if not failed else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py", "sha256": sha256(MODULE)},
            {"path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
            {"path": "docs/core/02_equations/covariant/uet_covariant_matter.py", "sha256": sha256(MATTER_MODULE)},
            {"path": "docs/core/02_equations/covariant/uet_covariant_response.py", "sha256": sha256(RESPONSE_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "normalized_beta_T13_field_and_density_normalization_missing",
            "physical_beta_source_provenance_missing",
            "physical_Phi_SI_energy_anchor_missing",
            "independent_alpha_Phi_K_calibration_missing",
            "full_finite_temperature_EOS_transport_SK_KMS_entropy_completion_missing",
        ],
        "dependency_unlocked": (
            "non-Landauer action-origin stiffness-slope lane only; no normalized beta, SI, alpha, TTG, "
            "physical transport, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-action-thermal-stiffness-beta-v1",
        "artifact": "t13_uet_o2_action_thermal_stiffness_beta_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "beta_phi_natural": state.beta_phi_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
