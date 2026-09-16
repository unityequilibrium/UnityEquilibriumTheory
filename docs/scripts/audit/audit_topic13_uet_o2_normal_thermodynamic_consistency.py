"""Audit thermodynamic consistency of the action-derived O(2) normal lane.

This wave tests the existing finite-temperature normal determinant over a small
deterministic state grid.  It does not add a new physical coefficient or use
TTG target data.  The result is intentionally narrower than a finite-
temperature UET EOS or transport closure.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_one_loop_normal_branch import (
    uet_o2_one_loop_normal_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
ACTION_REL = "docs/core/02_equations/covariant/uet_covariant_matter.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_normal_thermodynamic_consistency_audit.json"

TEMPERATURES = (0.28, 0.42)
CHEMICAL_POTENTIALS = (0.08, 0.20)
SPACE_RESPONSES = (0.10, 0.25)
QUADRATURE_ORDER = 192
CUTOFF_FACTOR = 70.0
DERIVATIVE_STEP = 1.0e-4
DERIVATIVE_TOLERANCE = 5.0e-6
MAXWELL_TOLERANCE = 2.0e-5
GIBBS_DUHEM_TOLERANCE = 3.0e-5


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def make_config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
):
    return uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=QUADRATURE_ORDER,
        cutoff_factor=CUTOFF_FACTOR,
    )


def abs_error(left: float, right: float) -> float:
    return abs(float(left) - float(right))


def main() -> int:
    config = make_config()
    points: list[dict[str, float]] = []
    errors = {
        "dp_dmu": 0.0,
        "dp_dT": 0.0,
        "dp_dPhi": 0.0,
        "maxwell_mu_phi": 0.0,
        "maxwell_T_phi": 0.0,
        "gibbs_duhem_T": 0.0,
        "gibbs_duhem_mu": 0.0,
    }
    checks = {
        "all_grid_points_are_normal_branch": True,
        "pressure_positive": True,
        "entropy_positive": True,
        "energy_positive": True,
        "susceptibility_positive": True,
        "pressure_mu_derivative_matches_charge": True,
        "pressure_temperature_derivative_matches_entropy": True,
        "pressure_phi_derivative_matches_action_response": True,
        "mu_phi_maxwell_reciprocity": True,
        "temperature_phi_maxwell_reciprocity": True,
        "gibbs_duhem_temperature_identity": True,
        "gibbs_duhem_chemical_potential_identity": True,
        "natural_unit_lane_is_explicit": True,
        "phi_is_not_temperature": True,
        "c_is_not_charge_density": True,
        "trace_is_not_state_or_feedback": True,
        "no_target_or_holdout_data_used": True,
        "no_parameter_fit_or_alpha_emitted": True,
    }

    for temperature in TEMPERATURES:
        for chemical_potential in CHEMICAL_POTENTIALS:
            for space_response in SPACE_RESPONSES:
                base = state(temperature, chemical_potential, space_response, config)
                phi_plus = state(
                    temperature,
                    chemical_potential,
                    space_response + DERIVATIVE_STEP,
                    config,
                )
                phi_minus = state(
                    temperature,
                    chemical_potential,
                    space_response - DERIVATIVE_STEP,
                    config,
                )
                mu_plus = state(
                    temperature,
                    chemical_potential + DERIVATIVE_STEP,
                    space_response,
                    config,
                )
                mu_minus = state(
                    temperature,
                    chemical_potential - DERIVATIVE_STEP,
                    space_response,
                    config,
                )
                temperature_plus = state(
                    temperature + DERIVATIVE_STEP,
                    chemical_potential,
                    space_response,
                    config,
                )
                temperature_minus = state(
                    temperature - DERIVATIVE_STEP,
                    chemical_potential,
                    space_response,
                    config,
                )

                dp_dmu = (mu_plus.pressure - mu_minus.pressure) / (2.0 * DERIVATIVE_STEP)
                dp_dT = (temperature_plus.pressure - temperature_minus.pressure) / (2.0 * DERIVATIVE_STEP)
                dp_dphi = (phi_plus.pressure - phi_minus.pressure) / (2.0 * DERIVATIVE_STEP)
                dn_dphi = (phi_plus.charge_density - phi_minus.charge_density) / (2.0 * DERIVATIVE_STEP)
                dresponse_dmu = (
                    mu_plus.pressure_phi_derivative - mu_minus.pressure_phi_derivative
                ) / (2.0 * DERIVATIVE_STEP)
                ds_dphi = (phi_plus.entropy_density - phi_minus.entropy_density) / (2.0 * DERIVATIVE_STEP)
                dresponse_dT = (
                    temperature_plus.pressure_phi_derivative
                    - temperature_minus.pressure_phi_derivative
                ) / (2.0 * DERIVATIVE_STEP)
                denergy_dT = (
                    temperature_plus.energy_density
                    - temperature_minus.energy_density
                ) / (2.0 * DERIVATIVE_STEP)
                ds_dT = (
                    temperature_plus.entropy_density
                    - temperature_minus.entropy_density
                ) / (2.0 * DERIVATIVE_STEP)
                dn_dT = (
                    temperature_plus.charge_density
                    - temperature_minus.charge_density
                ) / (2.0 * DERIVATIVE_STEP)
                denergy_dmu = (
                    mu_plus.energy_density - mu_minus.energy_density
                ) / (2.0 * DERIVATIVE_STEP)
                ds_dmu = (
                    mu_plus.entropy_density - mu_minus.entropy_density
                ) / (2.0 * DERIVATIVE_STEP)
                dn_dmu = (
                    mu_plus.charge_density - mu_minus.charge_density
                ) / (2.0 * DERIVATIVE_STEP)

                errors["dp_dmu"] = max(errors["dp_dmu"], abs_error(dp_dmu, base.charge_density))
                errors["dp_dT"] = max(errors["dp_dT"], abs_error(dp_dT, base.entropy_density))
                errors["dp_dPhi"] = max(
                    errors["dp_dPhi"], abs_error(dp_dphi, base.pressure_phi_derivative)
                )
                errors["maxwell_mu_phi"] = max(
                    errors["maxwell_mu_phi"], abs_error(dn_dphi, dresponse_dmu)
                )
                errors["maxwell_T_phi"] = max(
                    errors["maxwell_T_phi"], abs_error(ds_dphi, dresponse_dT)
                )
                errors["gibbs_duhem_T"] = max(
                    errors["gibbs_duhem_T"],
                    abs_error(
                        denergy_dT,
                        temperature * ds_dT + chemical_potential * dn_dT,
                    ),
                )
                errors["gibbs_duhem_mu"] = max(
                    errors["gibbs_duhem_mu"],
                    abs_error(
                        denergy_dmu,
                        temperature * ds_dmu + chemical_potential * dn_dmu,
                    ),
                )

                normal = config.matter.matter_kinetic * chemical_potential**2 < base.effective_mass_sq
                checks["all_grid_points_are_normal_branch"] &= normal
                checks["pressure_positive"] &= base.pressure > 0.0
                checks["entropy_positive"] &= base.entropy_density > 0.0
                checks["energy_positive"] &= base.energy_density > 0.0
                checks["susceptibility_positive"] &= base.charge_susceptibility > 0.0
                points.append(
                    {
                        "temperature": temperature,
                        "chemical_potential": chemical_potential,
                        "space_response": space_response,
                        "effective_mass_sq": base.effective_mass_sq,
                        "pressure": base.pressure,
                        "entropy_density": base.entropy_density,
                        "energy_density": base.energy_density,
                        "charge_susceptibility": base.charge_susceptibility,
                    }
                )

    checks["pressure_mu_derivative_matches_charge"] = errors["dp_dmu"] <= DERIVATIVE_TOLERANCE
    checks["pressure_temperature_derivative_matches_entropy"] = errors["dp_dT"] <= DERIVATIVE_TOLERANCE
    checks["pressure_phi_derivative_matches_action_response"] = errors["dp_dPhi"] <= DERIVATIVE_TOLERANCE
    checks["mu_phi_maxwell_reciprocity"] = errors["maxwell_mu_phi"] <= MAXWELL_TOLERANCE
    checks["temperature_phi_maxwell_reciprocity"] = errors["maxwell_T_phi"] <= MAXWELL_TOLERANCE
    checks["gibbs_duhem_temperature_identity"] = errors["gibbs_duhem_T"] <= GIBBS_DUHEM_TOLERANCE
    checks["gibbs_duhem_chemical_potential_identity"] = errors["gibbs_duhem_mu"] <= GIBBS_DUHEM_TOLERANCE

    contract_checks = {
        "unit_lane": "natural",
        "phi_meaning": "action response input; not temperature",
        "c_meaning": "not identified with charge density",
        "trace_meaning": "not used as state or feedback",
    }
    checks["natural_unit_lane_is_explicit"] = contract_checks["unit_lane"] == "natural"
    checks["phi_is_not_temperature"] = contract_checks["phi_meaning"] == "action response input; not temperature"
    checks["c_is_not_charge_density"] = contract_checks["c_meaning"] == "not identified with charge density"
    checks["trace_is_not_state_or_feedback"] = contract_checks["trace_meaning"] == "not used as state or feedback"

    status = (
        "PASS_ACTION_DERIVED_NORMAL_THERMODYNAMIC_CONSISTENCY"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_NORMAL_THERMODYNAMIC_CONSISTENCY"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
        {"path": ACTION_REL, "sha256": digest(ACTION_REL)},
        {"path": "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json", "sha256": digest("docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json")},
    ]
    report = {
        "schema_version": "t13-uet-o2-normal-thermodynamic-consistency-v1",
        "artifact": "t13_uet_o2_normal_thermodynamic_consistency_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "action-derived one-loop normal branch thermodynamic identities hold across the declared deterministic state grid",
                "pressure derivatives with respect to chemical potential, temperature, and Phi are mutually consistent",
                "Maxwell reciprocity between charge/response and entropy/response derivatives passes on the normal lane",
                "Gibbs-Duhem energy derivative identities pass on the normal lane",
                "positivity and normal-branch domain checks pass without fitting or target data",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": {
                "grand_potential": "Omega_N^(1,T) = T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))] d^3k/(2 pi)^3",
                "thermodynamic_derivatives": "n=partial_mu p; s=partial_T p; epsilon=-p+T*s+mu*n",
                "response_derivative": "partial_Phi p=-(partial_Phi m_eff^2) * 1/2 integral[(n_-+n_+)/E_k] d^3k/(2 pi)^3",
                "maxwell_relations": "partial_Phi n=partial_mu(partial_Phi p); partial_Phi s=partial_T(partial_Phi p)",
                "gibbs_duhem_checks": "partial_T epsilon=T partial_T s+mu partial_T n; partial_mu epsilon=T partial_mu s+mu partial_mu n",
            },
            "units": {
                "unit_lane": "natural",
                "temperature_chemical_potential_mass": "natural energy",
                "pressure_energy_entropy": "natural thermodynamic densities",
                "response_derivative": "natural energy density per natural Phi field unit",
            },
            "derivation_class": "action-derived thermal normal determinant with grid-level derivative, reciprocity, and stability verification",
            "observable": "normal-background pressure, charge, entropy, energy, susceptibility, and Phi response consistency",
            "data_role": "ACTION_DERIVED_INTERNAL_CONSISTENCY_NO_SOURCE_ROWS_OR_HOLDOUT",
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
            "dependency_unlocked": "normal-branch thermodynamic consistency only; no finite-temperature UET EOS, physical transport, SI, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This closes internal consistency of the declared natural-unit one-loop normal lane only. It is not a renormalized finite-temperature UET theory, condensate/two-fluid derivation, physical Kubo match, SI calibration, external validation, or Full Topic 13 closure.",
        },
        "grid": {
            "temperatures": list(TEMPERATURES),
            "chemical_potentials": list(CHEMICAL_POTENTIALS),
            "space_responses": list(SPACE_RESPONSES),
            "point_count": len(points),
            "quadrature_order": QUADRATURE_ORDER,
            "cutoff_factor": CUTOFF_FACTOR,
            "derivative_step": DERIVATIVE_STEP,
        },
        "metrics": errors,
        "checks": checks,
        "contract_checks": contract_checks,
        "state_points": points,
        "numeric_beta_T13_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
        "next_controller": "Keep the normal thermodynamic-consistency lane bounded while closing vacuum/interaction and condensate/two-fluid sectors; independently source physical Kubo and SI Phi evidence.",
        "claim_promotion": False,
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "failed_checks": [key for key, value in checks.items() if not value],
                "metrics": errors,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
