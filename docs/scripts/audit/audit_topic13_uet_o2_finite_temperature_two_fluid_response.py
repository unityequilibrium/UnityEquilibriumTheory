"""Audit the finite-temperature two-sector static response lane."""

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

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_finite_temperature_two_fluid_response import (  # noqa: E402
    FINITE_T_TWO_FLUID_STATIC_RESPONSE_STATUS,
    finite_temperature_two_fluid_static_contract,
    finite_temperature_two_fluid_static_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_two_fluid_response_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_two_fluid_response.py"
SECTOR_MODULE = ROOT / "docs/core/uet_o2_formal_two_sector_thermodynamics.py"
STATIC_MODULE = ROOT / "docs/core/uet_o2_formal_transverse_response.py"
HEAT_MODULE = ROOT / "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _close(left: float, right: float, *, atol: float = 1.0e-10) -> bool:
    return bool(np.isclose(float(left), float(right), rtol=1.0e-9, atol=atol))


def main() -> int:
    config = FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=160,
        cutoff_factor=65.0,
    )
    points = {
        "normal_high_temperature": (0.22, 0.35, 0.15, True),
        "normal_low_temperature": (0.06, 0.35, 0.15, False),
        "condensed_high_temperature": (0.20, 1.28, 0.15, False),
        "condensed_low_temperature": (0.04, 1.28, 0.15, False),
    }
    states = {
        label: finite_temperature_two_fluid_static_state(
            temperature,
            chemical_potential,
            space_response,
            config,
            include_normal_heat_flux_balance=include_heat,
        )
        for label, (temperature, chemical_potential, space_response, include_heat) in points.items()
    }
    contract = finite_temperature_two_fluid_static_contract()
    normal = states["normal_high_temperature"]
    condensed = states["condensed_high_temperature"]

    checks = {
        "normal_branch_is_explicit": all(
            states[key].branch == "normal"
            for key in ("normal_high_temperature", "normal_low_temperature")
        ),
        "condensed_branch_is_explicit": all(
            states[key].branch == "condensed"
            for key in ("condensed_high_temperature", "condensed_low_temperature")
        ),
        "pressure_split_closes": all(
            _close(state.total_pressure, state.condensate_pressure + state.normal_pressure)
            for state in states.values()
        ),
        "charge_split_closes": all(
            _close(
                state.total_charge_density,
                state.condensate_charge_density + state.normal_charge_density,
            )
            for state in states.values()
        ),
        "entropy_split_closes": all(
            _close(
                state.total_entropy_density,
                state.condensate_entropy_density + state.normal_entropy_density,
            )
            for state in states.values()
        ),
        "energy_split_closes": all(
            _close(
                state.total_energy_density,
                state.condensate_energy_density + state.normal_energy_density,
            )
            for state in states.values()
        ),
        "susceptibility_split_closes": all(
            _close(
                state.total_susceptibility,
                state.condensate_susceptibility + state.normal_susceptibility,
            )
            for state in states.values()
        ),
        "total_entropy_is_nonnegative_on_reference_grid": all(
            state.total_entropy_density >= -1.0e-12 for state in states.values()
        ),
        "total_susceptibility_is_nonnegative_on_reference_grid": all(
            state.total_susceptibility >= -1.0e-10 for state in states.values()
        ),
        "sector_derivative_sign_boundary_is_explicit": (
            "signed derivatives" in contract["unit_contract"]["sector_derivative_sign_policy"]
            and "not imposed on a residual sector"
            in contract["unit_contract"]["sector_derivative_sign_policy"]
        ),
        "condensed_signed_sector_values_are_not_clipped": (
            states["condensed_high_temperature"].normal_charge_density < 0.0
            and states["condensed_low_temperature"].normal_energy_density < 0.0
        ),
        "condensate_entropy_is_zero_in_declared_tree_sector": all(
            abs(states[key].condensate_entropy_density) <= 1.0e-12
            for key in states
        ),
        "static_normal_response_is_finite_and_nonnegative": all(
            np.isfinite(state.normal_momentum_susceptibility)
            and state.normal_momentum_susceptibility >= 0.0
            for state in states.values()
        ),
        "condensate_stiffness_is_positive_only_on_condensed_branch": (
            all(
                states[key].condensate_phase_stiffness == 0.0
                for key in ("normal_high_temperature", "normal_low_temperature")
            )
            and all(
                states[key].condensate_phase_stiffness > 0.0
                for key in ("condensed_high_temperature", "condensed_low_temperature")
            )
        ),
        "normal_static_response_decreases_at_low_temperature": states[
            "normal_low_temperature"
        ].normal_momentum_susceptibility < normal.normal_momentum_susceptibility,
        "condensed_static_response_decreases_at_low_temperature": states[
            "condensed_low_temperature"
        ].normal_momentum_susceptibility
        < condensed.normal_momentum_susceptibility,
        "normal_heat_flux_lane_is_available": (
            normal.heat_flux_kappa_natural is not None
            and normal.heat_flux_kappa_natural > 0.0
        ),
        "normal_entropy_balance_is_closed": (
            normal.entropy_balance_residual is not None
            and normal.entropy_balance_residual <= 1.0e-7
        ),
        "normal_charge_balance_is_closed": (
            normal.charge_balance_residual is not None
            and normal.charge_balance_residual <= 1.0e-10
        ),
        "normal_energy_balance_is_closed": (
            normal.energy_balance_residual is not None
            and normal.energy_balance_residual <= 1.0e-10
        ),
        "normal_momentum_balance_is_closed": (
            normal.momentum_balance_residual is not None
            and normal.momentum_balance_residual <= 1.0e-10
        ),
        "condensed_dissipative_lane_is_not_claimed": all(
            states[key].heat_flux_kappa_natural is None
            for key in ("condensed_high_temperature", "condensed_low_temperature")
        ),
        "normal_response_is_not_landau_density": (
            "not Landau normal mass density"
            in contract["unit_contract"]["normal_momentum_susceptibility"]
        ),
        "physical_kubo_is_excluded": "retarded physical Kubo coefficient"
        in contract["excluded_scope"],
        "si_and_alpha_are_excluded": (
            "SI heat-flux or Phi normalization" in contract["excluded_scope"]
            and "numeric alpha_Phi_K" in contract["excluded_scope"]
        ),
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "not an independent state" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "no_parameter_fitting": all(not state.parameter_fitting_performed for state in states.values()),
        "no_target_data": all(not state.target_data_used for state in states.values()),
        "xie_holdout_is_unread": all(not state.xie_2026_accessed for state in states.values()),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [name for name, passed in checks.items() if not passed]
    status = (
        FINITE_T_TWO_FLUID_STATIC_RESPONSE_STATUS
        if not failed
        else "BLOCKED_ACTION_DERIVED_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE"
    )
    major_result = {
        "major_result_id": "T13_UET_O2_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "what_is_closed": [
            "finite-temperature condensate/normal pressure, charge, entropy, energy, and susceptibility split",
            "branch-resolved static quasiparticle momentum response",
            "condensed-branch tree phase stiffness boundary",
            "normal-branch finite-cutoff covariant heat-flux and entropy-balance interface",
            "explicit separation of static response from Landau density and retarded Kubo claims",
            "total-state entropy and susceptibility stability boundary on the declared reference grid",
        ]
        if not failed
        else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/uet_o2_finite_temperature_two_fluid_response.py", "sha256": sha256(MODULE)},
            {"path": "docs/core/uet_o2_formal_two_sector_thermodynamics.py", "sha256": sha256(SECTOR_MODULE)},
            {"path": "docs/core/uet_o2_formal_transverse_response.py", "sha256": sha256(STATIC_MODULE)},
            {"path": "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py", "sha256": sha256(HEAT_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "interacting_finite_temperature_self_energy_and_renormalization_missing",
            "retarded_physical_Kubo_match_missing",
            "condensed_dissipative_two_fluid_transport_missing",
            "microscopic_SK_KMS_action_match_missing",
            "curved_3p1_transport_solver_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "dependency_unlocked": (
            "finite-temperature action-derived static two-fluid response lane only; "
            "no physical Kubo, SI, alpha, TTG, curved 3+1, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-finite-temperature-two-fluid-static-response-v1",
        "artifact": "t13_uet_o2_finite_temperature_two_fluid_response_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state_grid": {label: asdict(state) for label, state in states.items()},
        "checks": checks,
        "failed_checks": failed,
        "physical_transport_coefficients_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
        "controlling_blocker": "retarded_physical_Kubo_match_missing",
        "next_controller": (
            "match the static response to a state-matched retarded microscopic Kubo record, "
            "then extend the condensed dissipative sector without changing Phi ontology or SI gates"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "normal_kappa_natural": normal.heat_flux_kappa_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
