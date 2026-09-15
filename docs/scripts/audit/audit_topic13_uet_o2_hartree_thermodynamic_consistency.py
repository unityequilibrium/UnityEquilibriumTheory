"""Audit equilibrium thermodynamic consistency of the O(2) Hartree lane."""

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
from docs.core.uet_o2_finite_temperature_hartree_thermodynamics import (
    uet_o2_hartree_thermodynamic_contract,
    uet_o2_hartree_thermodynamic_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_finite_temperature_hartree_thermodynamics.py"
SELF_ENERGY_REL = "docs/core/uet_o2_finite_temperature_self_energy.py"
PARENT_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_hartree_thermodynamic_consistency_audit.json"

TEMPERATURE = 0.35
CHEMICAL_POTENTIAL = 0.2
PHI_RESPONSE = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
THERMAL_STEP = 1.0e-4
CHEMICAL_STEP = 1.0e-4


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


def state(
    temperature: float,
    chemical_potential: float,
    phi: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int = REFERENCE_ORDER,
    cutoff_factor: float = REFERENCE_CUTOFF_FACTOR,
):
    return uet_o2_hartree_thermodynamic_state(
        temperature,
        chemical_potential,
        phi,
        eos_config,
        quadrature_order=order,
        cutoff_factor=cutoff_factor,
    )


def main() -> int:
    eos_config = config()
    contract = uet_o2_hartree_thermodynamic_contract()
    reference = state(TEMPERATURE, CHEMICAL_POTENTIAL, PHI_RESPONSE, eos_config)
    temperature_plus = state(
        TEMPERATURE + THERMAL_STEP,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
    )
    temperature_minus = state(
        TEMPERATURE - THERMAL_STEP,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
    )
    chemical_plus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL + CHEMICAL_STEP,
        PHI_RESPONSE,
        eos_config,
    )
    chemical_minus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL - CHEMICAL_STEP,
        PHI_RESPONSE,
        eos_config,
    )

    entropy_from_pressure = (
        temperature_plus.pressure - temperature_minus.pressure
    ) / (2.0 * THERMAL_STEP)
    charge_from_pressure = (
        chemical_plus.pressure - chemical_minus.pressure
    ) / (2.0 * CHEMICAL_STEP)
    entropy_mu_fd = (
        chemical_plus.entropy_density - chemical_minus.entropy_density
    ) / (2.0 * CHEMICAL_STEP)
    charge_temperature_fd = (
        temperature_plus.charge_density - temperature_minus.charge_density
    ) / (2.0 * THERMAL_STEP)
    charge_susceptibility_fd = (
        chemical_plus.charge_density - chemical_minus.charge_density
    ) / (2.0 * CHEMICAL_STEP)
    heat_capacity_fd = TEMPERATURE * (
        temperature_plus.entropy_density - temperature_minus.entropy_density
    ) / (2.0 * THERMAL_STEP)
    energy_identity = (
        -reference.pressure
        + TEMPERATURE * reference.entropy_density
        + CHEMICAL_POTENTIAL * reference.charge_density
    )

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        item = state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "dressed_mass_sq": item.dressed_mass_sq,
                "thermal_tadpole": item.thermal_tadpole,
                "one_loop_pressure": item.one_loop_pressure,
                "double_bubble_pressure": item.double_bubble_pressure,
                "pressure": item.pressure,
                "charge_density": item.charge_density,
                "entropy_density": item.entropy_density,
                "energy_density": item.energy_density,
                "gap_residual": item.gap_residual,
                "pressure_stationarity_residual": item.pressure_stationarity_residual,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: abs(previous[field] - converged[field])
        / max(abs(converged[field]), 1.0e-30)
        for field in (
            "dressed_mass_sq",
            "thermal_tadpole",
            "pressure",
            "charge_density",
            "entropy_density",
            "energy_density",
        )
    }

    finite_difference_checks = {
        "entropy_from_pressure": entropy_from_pressure,
        "entropy_density": reference.entropy_density,
        "entropy_pressure_abs_error": abs(
            entropy_from_pressure - reference.entropy_density
        ),
        "charge_from_pressure": charge_from_pressure,
        "charge_density": reference.charge_density,
        "charge_pressure_abs_error": abs(
            charge_from_pressure - reference.charge_density
        ),
        "entropy_mu_fd": entropy_mu_fd,
        "charge_temperature_fd": charge_temperature_fd,
        "maxwell_abs_error": abs(entropy_mu_fd - charge_temperature_fd),
        "charge_susceptibility_finite_difference": charge_susceptibility_fd,
        "heat_capacity_finite_difference": heat_capacity_fd,
        "energy_identity": energy_identity,
        "energy_identity_abs_error": abs(energy_identity - reference.energy_density),
    }

    # The state fields are fixed-dressed-mass excitation susceptibilities. The
    # finite differences above include the stationary Hartree mass response.
    checks = {
        "gap_residual_is_closed": abs(reference.gap_residual) <= 5.0e-12,
        "pressure_stationarity_is_closed": abs(
            reference.pressure_stationarity_residual
        )
        <= 1.0e-10,
        "pressure_entropy_identity_passes": finite_difference_checks[
            "entropy_pressure_abs_error"
        ]
        <= 1.0e-7,
        "pressure_charge_identity_passes": finite_difference_checks[
            "charge_pressure_abs_error"
        ]
        <= 1.0e-8,
        "maxwell_relation_passes": finite_difference_checks["maxwell_abs_error"]
        <= 1.0e-7,
        "energy_identity_passes": finite_difference_checks["energy_identity_abs_error"]
        <= 1.0e-14,
        "equilibrium_charge_susceptibility_is_positive": charge_susceptibility_fd
        > 0.0,
        "equilibrium_heat_capacity_is_positive": heat_capacity_fd > 0.0,
        "fixed_mass_charge_susceptibility_is_positive": reference.charge_susceptibility
        > 0.0,
        "fixed_mass_heat_capacity_is_positive": reference.heat_capacity_at_mu > 0.0,
        "double_bubble_pressure_is_non_negative": reference.double_bubble_pressure
        >= 0.0,
        "normal_branch_is_selected": reference.equilibrium_normal_branch,
        "dressed_mass_converges": convergence_relative_errors["dressed_mass_sq"]
        <= 1.0e-8,
        "pressure_converges": convergence_relative_errors["pressure"] <= 1.0e-8,
        "entropy_converges": convergence_relative_errors["entropy_density"]
        <= 1.0e-8,
        "all_reference_values_finite": all(
            isfinite(value)
            for value in (
                reference.dressed_mass_sq,
                reference.thermal_tadpole,
                reference.pressure,
                reference.charge_density,
                reference.entropy_density,
                reference.energy_density,
                reference.charge_susceptibility,
                reference.heat_capacity_at_mu,
            )
        ),
        "natural_units_are_declared": contract["units"]["unit_lane"] == "natural",
        "stationary_functional_is_declared": "hartree_2pi_functional"
        in contract["equations"],
        "entropy_is_equilibrium_only": "equilibrium thermodynamic consistency"
        in contract["claim_boundary"],
        "physical_transport_is_excluded": contract["approximation"]["physical_kubo"]
        == "NOT_INCLUDED",
        "alpha_is_not_emitted": contract["units"]["alpha_Phi_K"]
        == "not emitted; SI map remains open",
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not charge density" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMICS"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMICS"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": SELF_ENERGY_REL, "sha256": digest(SELF_ENERGY_REL)},
        {"path": PARENT_REL, "sha256": digest(PARENT_REL)},
    ]
    equations = dict(contract["equations"])
    equations["stability_checks"] = (
        "chi_1=(partial n_1/partial mu)_M>=0 and "
        "c_mu,1=T*(partial s_1/partial T)_M>=0; stationary equilibrium "
        "susceptibility and heat capacity are checked by finite differences"
    )
    report = {
        "schema_version": "t13-uet-o2-hartree-equilibrium-thermodynamics-v1",
        "artifact": "t13_uet_o2_hartree_thermodynamic_consistency_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "stationary thermal 2PI/Hartree functional on the homogeneous normal branch",
                "pressure, charge, entropy, and energy identities from one equilibrium functional",
                "Maxwell relation and stationary pressure derivative checks",
                "quadrature/cutoff convergence and positive equilibrium finite-difference stability witnesses",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": equations,
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "natural-unit equilibrium pressure, charge, entropy, and energy on the Hartree normal branch",
            "data_role": "ACTION_DERIVED_EQUILIBRIUM_INTERNAL_NO_EXTERNAL_CALIBRATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_unique_microscopic_finite_temperature_scheme_matching_missing",
                "condensate_and_normal_two_fluid_completion_missing",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "equilibrium Hartree thermodynamic-consistency lane only; no full EOS/transport/KMS/entropy, Topic 13, Core, Gravity, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "phi_response": PHI_RESPONSE,
            "base_mass_sq": reference.base_mass_sq,
            "dressed_mass_sq": reference.dressed_mass_sq,
            "thermal_tadpole": reference.thermal_tadpole,
            "one_loop_pressure": reference.one_loop_pressure,
            "double_bubble_pressure": reference.double_bubble_pressure,
            "pressure": reference.pressure,
            "charge_density": reference.charge_density,
            "entropy_density": reference.entropy_density,
            "energy_density": reference.energy_density,
            "charge_susceptibility_fixed_mass": reference.charge_susceptibility,
            "heat_capacity_fixed_mass": reference.heat_capacity_at_mu,
            "gap_residual": reference.gap_residual,
            "pressure_stationarity_residual": reference.pressure_stationarity_residual,
        },
        "finite_difference_checks": finite_difference_checks,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "vacuum_counterterm_and_unique_microscopic_finite_temperature_scheme_matching_missing",
        "next_controller": "Close the named finite-temperature renormalization scheme and then match physical SK/KMS/Kubo and dimensional Phi interfaces; keep the equilibrium Hartree lane separate from physical transport and alpha calibration.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
                "maxwell_abs_error": finite_difference_checks["maxwell_abs_error"],
                "entropy_pressure_abs_error": finite_difference_checks[
                    "entropy_pressure_abs_error"
                ],
                "charge_pressure_abs_error": finite_difference_checks[
                    "charge_pressure_abs_error"
                ],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
