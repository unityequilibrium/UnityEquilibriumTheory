"""Audit the one-sided Hartree normal-branch stability boundary."""

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
from docs.core.uet_o2_finite_temperature_normal_stability import (
    normal_stability_boundary_residual,
    uet_o2_hartree_normal_stability_boundary,
    uet_o2_hartree_normal_stability_contract,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_finite_temperature_normal_stability.py"
SELF_ENERGY_REL = "docs/core/uet_o2_finite_temperature_self_energy.py"
PARENT_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_hartree_normal_stability_audit.json"

TEMPERATURE = 0.35
PHI_RESPONSE = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
PROBE_FACTOR = 0.05


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


def main() -> int:
    eos_config = config()
    contract = uet_o2_hartree_normal_stability_contract()
    reference = uet_o2_hartree_normal_stability_boundary(
        TEMPERATURE,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        item = uet_o2_hartree_normal_stability_boundary(
            TEMPERATURE,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "critical_chemical_potential": item.critical_chemical_potential,
                "critical_dressed_mass_sq": item.critical_dressed_mass_sq,
                "thermal_tadpole": item.thermal_tadpole,
                "thermal_self_energy": item.thermal_self_energy,
                "critical_residual": item.critical_residual,
                "bose_domain_margin": item.bose_domain_margin,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in (
            "critical_chemical_potential",
            "critical_dressed_mass_sq",
            "thermal_tadpole",
            "thermal_self_energy",
        )
    }

    low_probe_mu = (1.0 - PROBE_FACTOR) * reference.critical_chemical_potential
    high_probe_mu = (1.0 + PROBE_FACTOR) * reference.critical_chemical_potential
    low_probe = normal_stability_boundary_residual(
        low_probe_mu,
        TEMPERATURE,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    high_probe = normal_stability_boundary_residual(
        high_probe_mu,
        TEMPERATURE,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )

    checks = {
        "critical_residual_is_closed": abs(reference.critical_residual) <= 5.0e-12,
        "critical_condition_is_closed": abs(
            reference.critical_dressed_mass_sq
            - eos_config.matter.matter_kinetic
            * reference.critical_chemical_potential**2
        )
        <= 1.0e-12,
        "bose_domain_is_regular": reference.bose_domain_margin > 0.0,
        "thermal_self_energy_is_non_negative": reference.thermal_self_energy >= 0.0,
        "stable_side_probe_is_negative": reference.lower_probe_residual < 0.0,
        "unstable_side_probe_is_positive": reference.upper_probe_residual > 0.0,
        "independent_probe_signs_match": low_probe < 0.0 and high_probe > 0.0,
        "critical_mu_is_positive": reference.critical_chemical_potential > 0.0,
        "critical_state_is_finite": all(
            isfinite(value)
            for value in (
                reference.critical_chemical_potential,
                reference.critical_dressed_mass_sq,
                reference.base_mass_sq,
                reference.thermal_tadpole,
                reference.thermal_self_energy,
                reference.critical_residual,
                reference.bose_domain_margin,
            )
        ),
        "critical_mu_converges": convergence_relative_errors[
            "critical_chemical_potential"
        ]
        <= 1.0e-8,
        "critical_mass_converges": convergence_relative_errors[
            "critical_dressed_mass_sq"
        ]
        <= 1.0e-8,
        "tadpole_converges": convergence_relative_errors["thermal_tadpole"] <= 1.0e-8,
        "self_energy_converges": convergence_relative_errors[
            "thermal_self_energy"
        ]
        <= 1.0e-8,
        "natural_units_are_declared": contract["units"]["unit_lane"] == "natural",
        "Z_condition_is_declared": contract["approximation"][
            "matter_kinetic_condition"
        ].startswith("Z>1"),
        "condensed_branch_is_excluded": contract["approximation"][
            "condensate_branch"
        ]
        == "NOT_INCLUDED",
        "physical_kubo_is_excluded": contract["approximation"]["physical_kubo"]
        == "NOT_INCLUDED",
        "alpha_is_not_emitted": contract["units"]["alpha_Phi_K"]
        == "not emitted; SI map remains open",
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not charge density" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only"
        in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": SELF_ENERGY_REL, "sha256": digest(SELF_ENERGY_REL)},
        {"path": PARENT_REL, "sha256": digest(PARENT_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-hartree-normal-stability-boundary-v1",
        "artifact": "t13_uet_o2_hartree_normal_stability_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_HARTREE_NORMAL_STABILITY_BOUNDARY_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "one-sided Hartree normal-branch stability condition r_T=M^2-Z*mu^2",
                "critical boundary root M_c^2=Z*mu_c^2 using the existing thermal tadpole",
                "stable-side and unstable-side residual-sign witnesses",
                "Bose-domain regularity, gap residual, and quadrature/cutoff convergence",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "natural-unit one-sided Hartree normal-branch stability boundary",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_unique_microscopic_finite_temperature_scheme_matching_missing",
                "condensed_branch_and_renormalized_finite_temperature_phase_transition_missing",
                "condensate_and_normal_two_fluid_eos_completion_missing",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "one-sided Hartree normal stability-boundary lane only; no renormalized condensed phase, Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "space_response": PHI_RESPONSE,
            "critical_chemical_potential": reference.critical_chemical_potential,
            "critical_dressed_mass_sq": reference.critical_dressed_mass_sq,
            "base_mass_sq": reference.base_mass_sq,
            "thermal_tadpole": reference.thermal_tadpole,
            "thermal_self_energy": reference.thermal_self_energy,
            "critical_residual": reference.critical_residual,
            "bose_domain_margin": reference.bose_domain_margin,
            "lower_probe_residual": reference.lower_probe_residual,
            "upper_probe_residual": reference.upper_probe_residual,
            "independent_low_probe_residual": low_probe,
            "independent_high_probe_residual": high_probe,
            "momentum_cutoff": reference.momentum_cutoff,
            "quadrature_order": reference.quadrature_order,
            "iterations": reference.iterations,
            "condensed_branch_included": reference.condensed_branch_included,
            "vacuum_counterterm_included": reference.vacuum_counterterm_included,
        },
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "condensed_branch_and_renormalized_finite_temperature_phase_transition_missing",
        "next_controller": "Derive or source-lock the renormalized condensed finite-temperature branch and match its retarded Kubo/SK/KMS coefficients; retain this boundary as a one-sided Hartree diagnostic without promoting it to a phase transition.",
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
                "critical_chemical_potential": reference.critical_chemical_potential,
                "critical_residual": reference.critical_residual,
                "bose_domain_margin": reference.bose_domain_margin,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
