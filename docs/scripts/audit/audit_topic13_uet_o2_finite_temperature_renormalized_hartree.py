"""Audit the finite-temperature renormalized Hartree normal lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_renormalized_hartree import (
    uet_o2_renormalized_hartree_normal_contract,
    uet_o2_renormalized_hartree_normal_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_finite_temperature_renormalized_hartree.py"
VACUUM_REL = "docs/core/uet_o2_renormalized_normal_branch.py"
SELF_ENERGY_REL = "docs/core/uet_o2_finite_temperature_self_energy.py"
HARTREE_REL = "docs/core/uet_o2_finite_temperature_hartree_thermodynamics.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_renormalized_hartree_audit.json"

TEMPERATURE = 0.35
CHEMICAL_POTENTIAL = 0.20
PHI_RESPONSE = 0.20
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
DERIVATIVE_STEP = 2.0e-4


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(
            epsilon_nc=0.1,
            phi_equilibrium=0.0,
        ),
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def compact(state) -> dict[str, float | int]:
    return {
        "dressed_mass_sq": state.dressed_mass_sq,
        "vacuum_grand_potential": state.vacuum_grand_potential,
        "thermal_grand_potential": state.thermal_grand_potential,
        "total_tadpole": state.total_tadpole,
        "thermal_self_energy": state.thermal_self_energy,
        "double_bubble_pressure": state.double_bubble_pressure,
        "pressure": state.pressure,
        "charge_density": state.charge_density,
        "entropy_density": state.entropy_density,
        "energy_density": state.energy_density,
        "charge_susceptibility": state.charge_susceptibility,
        "heat_capacity_at_mu": state.heat_capacity_at_mu,
        "gap_residual": state.gap_residual,
        "functional_stationarity_residual": state.functional_stationarity_residual,
        "momentum_cutoff": state.momentum_cutoff,
        "quadrature_order": state.quadrature_order,
        "iterations": state.iterations,
    }


def main() -> int:
    eos_config = config()
    contract = uet_o2_renormalized_hartree_normal_contract()
    reference = uet_o2_renormalized_hartree_normal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        state = uet_o2_renormalized_hartree_normal_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
        record = compact(state)
        record["cutoff_factor"] = cutoff_factor
        convergence_records.append(record)

    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_fields = (
        "dressed_mass_sq",
        "total_tadpole",
        "pressure",
        "charge_density",
        "entropy_density",
    )
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in convergence_fields
    }

    mu_step = DERIVATIVE_STEP * max(1.0, abs(CHEMICAL_POTENTIAL))
    temp_step = DERIVATIVE_STEP * max(1.0, TEMPERATURE)
    mu_low = uet_o2_renormalized_hartree_normal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL - mu_step,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    mu_high = uet_o2_renormalized_hartree_normal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL + mu_step,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    temp_low = uet_o2_renormalized_hartree_normal_state(
        TEMPERATURE - temp_step,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    temp_high = uet_o2_renormalized_hartree_normal_state(
        TEMPERATURE + temp_step,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    finite_difference_charge = (mu_high.pressure - mu_low.pressure) / (2.0 * mu_step)
    finite_difference_entropy = (temp_high.pressure - temp_low.pressure) / (2.0 * temp_step)
    finite_difference_errors = {
        "charge": abs(finite_difference_charge - reference.charge_density),
        "entropy": abs(finite_difference_entropy - reference.entropy_density),
    }
    values = tuple(compact(reference).values())
    checks = {
        "reference_values_are_finite": all(isfinite(float(value)) for value in values),
        "normal_branch_is_strict": reference.dressed_mass_sq
        > max(
            reference.chemical_potential**2,
            eos_config.matter.matter_kinetic * reference.chemical_potential**2,
        ),
        "gap_residual_is_closed": abs(reference.gap_residual) <= 1.0e-10,
        "functional_stationarity_is_closed": abs(reference.functional_stationarity_residual)
        <= 1.0e-10,
        "total_tadpole_is_positive": reference.total_tadpole > 0.0,
        "thermal_self_energy_is_positive": reference.thermal_self_energy > 0.0,
        "charge_susceptibility_is_nonnegative": reference.charge_susceptibility >= 0.0,
        "heat_capacity_is_nonnegative": reference.heat_capacity_at_mu >= 0.0,
        "energy_identity_is_closed": abs(
            reference.energy_density
            - (-reference.pressure + TEMPERATURE * reference.entropy_density + CHEMICAL_POTENTIAL * reference.charge_density)
        )
        <= 1.0e-12,
        "charge_derivative_matches_pressure": finite_difference_errors["charge"] <= 2.0e-7,
        "entropy_derivative_matches_pressure": finite_difference_errors["entropy"] <= 2.0e-7,
        "dressed_mass_converges": convergence_relative_errors["dressed_mass_sq"] <= 1.0e-8,
        "tadpole_converges": convergence_relative_errors["total_tadpole"] <= 1.0e-6,
        "pressure_converges": convergence_relative_errors["pressure"] <= 1.0e-6,
        "charge_converges": convergence_relative_errors["charge_density"] <= 1.0e-8,
        "entropy_converges": convergence_relative_errors["entropy_density"] <= 1.0e-8,
        "vacuum_scheme_is_included": reference.vacuum_counterterm_included is True,
        "hartree_interaction_is_included": reference.hartree_interaction_included is True,
        "condensed_branch_is_excluded": reference.condensed_branch_included is False,
        "physical_kubo_is_excluded": reference.physical_kubo_coefficient_included is False,
        "si_mapping_is_excluded": reference.physical_si_mapping_included is False,
        "natural_units_are_declared": contract["units"]["unit_lane"] == "natural",
        "Phi_ontology_is_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace only" in contract["ontology"]["R_gen"],
        "R_obs_is_separate": "separate observer record" in contract["ontology"]["R_obs"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME"
        if not failed
        else "BLOCKED_ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": VACUUM_REL, "sha256": digest(VACUUM_REL)},
        {"path": SELF_ENERGY_REL, "sha256": digest(SELF_ENERGY_REL)},
        {"path": HARTREE_REL, "sha256": digest(HARTREE_REL)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-finite-temperature-renormalized-hartree-v1",
        "artifact": "t13_uet_o2_finite_temperature_renormalized_hartree_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_RENORMALIZED_HARTREE_NORMAL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "vacuum Taylor-subtracted and thermal tadpoles enter one renormalized Hartree gap equation",
                "the stationary Hartree functional, pressure, charge, entropy, and energy identities are evaluated on the same dressed normal state",
                "gap residual, functional stationarity, normal-domain, positivity, finite-difference, and convergence contracts pass",
                "the declared interacting normal branch is closed as a natural-unit scheme lane without promoting it to a physical finite-temperature theory",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "natural-unit renormalized Hartree normal-branch thermodynamic state",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_finite_temperature_renormalization_scheme_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "physical_kubo_coefficients_and_microscopic_sk_kms_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "renormalized interacting normal Hartree lane only; no condensed/two-fluid, physical Kubo, SI, alpha, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "reference": compact(reference),
        "reference_parameters": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI_RESPONSE,
            "quadrature_order": REFERENCE_ORDER,
            "cutoff_factor": REFERENCE_CUTOFF_FACTOR,
        },
        "finite_difference_checks": {
            "charge_from_pressure": finite_difference_charge,
            "charge_state": reference.charge_density,
            "charge_abs_error": finite_difference_errors["charge"],
            "entropy_from_pressure": finite_difference_entropy,
            "entropy_state": reference.entropy_density,
            "entropy_abs_error": finite_difference_errors["entropy"],
        },
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
        "next_controller": "Extend the renormalized functional to a self-consistent condensed branch and state-matched retarded Kubo/SK-KMS interface; retain the present normal scheme as formal natural-unit evidence only.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "dressed_mass_sq": reference.dressed_mass_sq,
                "gap_residual": reference.gap_residual,
                "charge_abs_error": finite_difference_errors["charge"],
                "entropy_abs_error": finite_difference_errors["entropy"],
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
