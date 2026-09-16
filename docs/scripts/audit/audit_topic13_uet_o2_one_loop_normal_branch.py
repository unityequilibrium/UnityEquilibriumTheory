"""Audit the action-derived one-loop finite-temperature normal branch."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_one_loop_normal_branch import (
    uet_o2_one_loop_normal_branch_contract,
    uet_o2_one_loop_normal_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
MASS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
ACTION_REL = "docs/core/02_equations/covariant/uet_covariant_matter.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json"


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def main() -> int:
    eos_config = config()
    temperature = 0.35
    chemical_potential = 0.2
    phi = 0.2
    delta_phi = 1.0e-4
    delta_mu = 1.0e-4
    delta_temperature = 1.0e-4
    state = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        phi,
        eos_config,
    )
    state_phi_plus = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        phi + delta_phi,
        eos_config,
    )
    state_phi_minus = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        phi - delta_phi,
        eos_config,
    )
    state_mu_plus = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential + delta_mu,
        phi,
        eos_config,
    )
    state_mu_minus = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential - delta_mu,
        phi,
        eos_config,
    )
    state_t_plus = uet_o2_one_loop_normal_state(
        temperature + delta_temperature,
        chemical_potential,
        phi,
        eos_config,
    )
    state_t_minus = uet_o2_one_loop_normal_state(
        temperature - delta_temperature,
        chemical_potential,
        phi,
        eos_config,
    )
    p_phi = (state_phi_plus.pressure - state_phi_minus.pressure) / (2.0 * delta_phi)
    p_mu = (state_mu_plus.pressure - state_mu_minus.pressure) / (2.0 * delta_mu)
    p_t = (state_t_plus.pressure - state_t_minus.pressure) / (2.0 * delta_temperature)
    mass_plus = effective_mass_sq(phi + delta_phi, eos_config)
    mass_minus = effective_mass_sq(phi - delta_phi, eos_config)
    dm2_dphi_numeric = (mass_plus - mass_minus) / (2.0 * delta_phi)
    contract = uet_o2_one_loop_normal_branch_contract()
    expected_mass_derivative = -eos_config.response.epsilon_nc * eos_config.matter.response_coupling
    checks = {
        "normal_condition_passes": eos_config.matter.matter_kinetic * chemical_potential**2 < state.effective_mass_sq,
        "thermal_pressure_is_positive": state.pressure > 0.0,
        "thermal_entropy_is_positive": state.entropy_density > 0.0,
        "thermal_energy_is_positive": state.energy_density > 0.0,
        "thermal_susceptibility_is_positive": state.charge_susceptibility > 0.0,
        "thermal_scalar_density_is_positive": state.thermal_scalar_density > 0.0,
        "grand_potential_is_negative_pressure": abs(state.one_loop_thermal_grand_potential + state.pressure) <= 1.0e-14,
        "matter_normal_grand_potential_is_zero": state.matter_grand_potential == 0.0,
        "mass_derivative_matches_action": abs(dm2_dphi_numeric - expected_mass_derivative) <= 1.0e-12,
        "mass_derivative_is_emitted": abs(state.dm_eff_sq_dphi - expected_mass_derivative) <= 1.0e-15,
        "pressure_phi_derivative_matches_integral": abs(p_phi - state.pressure_phi_derivative) <= 2.0e-7,
        "charge_is_pressure_derivative": abs(p_mu - state.charge_density) <= 2.0e-7,
        "entropy_is_pressure_temperature_derivative": abs(p_t - state.entropy_density) <= 2.0e-7,
        "energy_identity_closes": abs(state.energy_density - (-state.pressure + temperature * state.entropy_density + chemical_potential * state.charge_density)) <= 1.0e-14,
        "vacuum_counterterm_is_explicitly_excluded": state.vacuum_counterterm_included is False and contract["approximation"]["vacuum_counterterm"] == "NOT_INCLUDED",
        "condensate_is_explicitly_excluded": state.condensate_contribution_included is False and contract["approximation"]["condensate_branch"] == "NOT_INCLUDED",
        "two_fluid_is_explicitly_open": state.normal_two_fluid_completion is False and contract["approximation"]["normal_two_fluid_completion"] == "NOT_INCLUDED",
        "natural_unit_lane_is_declared": contract["units"]["unit_lane"] == "natural",
        "phi_is_not_temperature": contract["ontology"]["Phi"] == "action response input; not temperature",
        "c_is_not_charge_density": contract["ontology"]["C"] == "not identified with charge density",
        "trace_is_not_state": contract["ontology"]["R_gen"] == "not used as state or feedback",
        "alpha_is_not_emitted": "alpha_Phi_K" not in json.dumps(contract),
        "kubo_is_not_emitted": (
            "KuboCoefficientRecord" not in (ROOT / MODULE_REL).read_text(encoding="utf-8")
            and "coefficient_records" not in (ROOT / MODULE_REL).read_text(encoding="utf-8")
        ),
    }
    status = "PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE" if all(checks.values()) else "FAIL_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE"
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": MASS_REL, "sha256": digest(MASS_REL)},
        {"path": ACTION_REL, "sha256": digest(ACTION_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-one-loop-normal-branch-v1",
        "artifact": "t13_uet_o2_one_loop_normal_branch_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_ONE_LOOP_NORMAL_BRANCH",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "thermal one-loop normal-background determinant derived from the declared O(2) action effective mass map",
                "normal-branch pressure, charge, entropy, energy, and susceptibility identities",
                "action response derivative of the thermal pressure with respect to Phi through m_eff(Phi)",
                "explicit exclusion of vacuum renormalization, condensate branch, and two-fluid completion",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived natural-unit thermal one-loop determinant on the homogeneous normal background; vacuum-renormalized and finite-temperature two-fluid completion not included",
            "observable": "normal-background thermal pressure, charge, entropy, energy, susceptibility, and Phi response derivative",
            "data_role": "ACTION_DERIVED_ONE_LOOP_NORMAL_LANE_NOT_FULL_UET_THERMAL_CLOSURE",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "interacting_finite_temperature_self_energy_not_derived",
                "condensate_goldstone_and_normal_two_fluid_completion_not_derived",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "action-derived normal-background thermodynamic lane only; no full finite-temperature UET EOS, transport, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This result derives only the thermal one-loop normal-background determinant from the declared natural-unit action mass map. It is not a renormalized full finite-temperature UET effective action, condensate/two-fluid derivation, physical Kubo transport, SI Phi calibration, external validation, or global UET closure.",
        },
        "state": {
            "temperature": state.temperature,
            "chemical_potential": state.chemical_potential,
            "space_response": state.space_response,
            "effective_mass_sq": state.effective_mass_sq,
            "dm_eff_sq_dphi": state.dm_eff_sq_dphi,
            "thermal_scalar_density": state.thermal_scalar_density,
            "pressure": state.pressure,
            "pressure_phi_derivative": state.pressure_phi_derivative,
            "charge_density": state.charge_density,
            "entropy_density": state.entropy_density,
            "energy_density": state.energy_density,
            "charge_susceptibility": state.charge_susceptibility,
            "matter_grand_potential": state.matter_grand_potential,
            "one_loop_thermal_grand_potential": state.one_loop_thermal_grand_potential,
            "vacuum_counterterm_included": state.vacuum_counterterm_included,
            "condensate_contribution_included": state.condensate_contribution_included,
            "normal_two_fluid_completion": state.normal_two_fluid_completion,
        },
        "finite_difference_checks": {
            "dp_dPhi": p_phi,
            "dp_dmu": p_mu,
            "dp_dT": p_t,
            "dm_eff_sq_dPhi_numeric": dm2_dphi_numeric,
            "abs_dp_dPhi_minus_analytic": abs(p_phi - state.pressure_phi_derivative),
            "abs_dp_dmu_minus_n": abs(p_mu - state.charge_density),
            "abs_dp_dT_minus_s": abs(p_t - state.entropy_density),
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "vacuum_counterterm_and_interacting_finite_temperature_UET_completion_not_closed",
        "next_controller": "Close the thermal one-loop vacuum/renormalization contract or explicitly retain the thermal-only scope, then derive the condensate/two-fluid sector and match physical Kubo/SI Phi observables.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "pressure": state.pressure,
        "pressure_phi_derivative": state.pressure_phi_derivative,
        "thermal_scalar_density": state.thermal_scalar_density,
        "dm_eff_sq_dphi": state.dm_eff_sq_dphi,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
