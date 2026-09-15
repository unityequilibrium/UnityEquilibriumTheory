"""Audit the action-derived covariant entropy and heat-flux balance lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (  # noqa: E402
    covariant_entropy_heat_flux_balance_contract,
    covariant_entropy_heat_flux_balance_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
MODULE = ROOT / "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py"
CONTINUUM_MODULE = ROOT / "docs/core/uet_o2_continuum_collision_operator.py"
EOS_MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = covariant_entropy_heat_flux_balance_state(0.22, 0.35, 0.15)
    contract = covariant_entropy_heat_flux_balance_contract()
    response = np.asarray(state.heat_response_matrix, dtype=float)
    response_eigenvalues = np.linalg.eigvalsh(response)
    checks = {
        "normal_quasiparticle_branch_is_explicit": state.eos_branch == "normal",
        "finite_cutoff_operator_is_symmetric": state.collision_operator_symmetry_residual <= 1.0e-12,
        "finite_cutoff_operator_is_positive": state.collision_operator_min_eigenvalue >= -1.0e-12,
        "heat_response_matrix_is_symmetric": np.max(np.abs(response - response.T)) <= 1.0e-12,
        "heat_response_matrix_is_positive_semidefinite": float(np.min(response_eigenvalues)) >= -1.0e-8,
        "heat_response_has_positive_scalar_lane": state.kappa_natural > 0.0,
        "declared_grid_is_nearly_isotropic": state.heat_response_isotropy_residual <= 1.0e-8,
        "landau_heat_flux_is_projected": state.heat_flux_orthogonality_residual <= 1.0e-12,
        "thermal_force_is_projected": state.force_orthogonality_residual <= 1.0e-12,
        "gram_projector_is_orthogonal": state.projector_orthogonality_residual <= 1.0e-12,
        "entropy_production_is_nonnegative": state.entropy_production >= -1.0e-10,
        "kinetic_entropy_matches_covariant_entropy": state.entropy_balance_residual <= 1.0e-7,
        "kinetic_response_equation_is_resolved": state.kinetic_equation_residual <= 1.0e-10,
        "charge_balance_is_closed": state.charge_balance_residual <= 1.0e-10,
        "energy_balance_is_closed": state.energy_balance_residual <= 1.0e-10,
        "momentum_balance_is_closed": state.momentum_balance_residual <= 1.0e-10,
        "heat_flux_response_is_resolved": state.heat_flux_response_residual <= 1.0e-7,
        "local_lorentz_covariance_is_resolved": state.lorentz_covariance_residual <= 1.0e-10,
        "equilibrium_has_zero_heat_flux": state.equilibrium_heat_flux_norm <= 1.0e-12,
        "physical_kubo_is_not_emitted": state.physical_kubo_coefficient_emitted is False,
        "numeric_alpha_is_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "xie_holdout_is_unread": state.xie_2026_accessed is False,
        "finite_cutoff_boundary_is_declared": state.finite_cutoff_boundary_declared is True,
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "physical_shortcuts_are_excluded": all(
            contract["excluded"][key]
            for key in (
                "physical_Kubo_coefficient",
                "SI_heat_flux",
                "finite_temperature_two_fluid_completion",
                "microscopic_SK_action_match",
                "curved_3p1_solver",
                "alpha_Phi_K",
                "TTG_validation",
            )
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"
        if not failed
        else "BLOCKED_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"
    )
    major_result = {
        "major_result_id": "T13_UET_O2_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "what_is_closed": [
            "the Landau-frame energy-current subtraction h=(epsilon+p)/n on the declared normal quasiparticle state",
            "a finite-cutoff heat-current source projected away from charge and four-momentum conserved moments",
            "a positive semidefinite action-derived natural-unit heat-response matrix on the declared grid",
            "the covariant projector lift q^mu=kappa*X_T^mu and J_S^mu=s*u^mu+q^mu/T",
            "the kinetic entropy identity and charge/energy/momentum dissipative balance",
        ] if not failed else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py", "sha256": sha256(MODULE)},
            {"path": "docs/core/uet_o2_continuum_collision_operator.py", "sha256": sha256(CONTINUUM_MODULE)},
            {"path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py", "sha256": sha256(EOS_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "finite_temperature_two_fluid_completion_missing",
            "microscopic_SK_action_and_KMS_match_missing",
            "physical_Kubo_coefficient_missing",
            "curved_3p1_transport_solver_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "dependency_unlocked": (
            "named finite-cutoff covariant entropy-current and formal heat-flux balance lane only; "
            "no physical Kubo, SI, alpha, TTG, curved 3+1, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-covariant-entropy-heat-flux-balance-v1",
        "artifact": "t13_uet_o2_covariant_entropy_heat_flux_balance_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "response_eigenvalues": [float(value) for value in response_eigenvalues],
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
    print(json.dumps({"status": status, "failed_checks": failed, "kappa_natural": state.kappa_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
