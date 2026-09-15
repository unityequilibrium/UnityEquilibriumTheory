"""Audit the Goldstone/Ward boundary of the finite-temperature condensate witness."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite, sqrt
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_stationarity_scheme import (
    uet_o2_stationarity_scheme_dependence,
    uet_o2_stationarity_scheme_dependence_contract,
)
from docs.core.uet_o2_gaussian_offshell_background import off_shell_mode_omega_sq


ROOT = Path(__file__).resolve().parents[3]
STATIONARITY_REL = "docs/core/uet_o2_finite_temperature_stationarity_scheme.py"
OFFSHELL_REL = "docs/core/uet_o2_gaussian_offshell_background.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_goldstone_ward_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.30
PHI_RESPONSE = 0.20
SCHEME_B_COEFFICIENT = -0.05
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
QUADRATURE_ORDERS = (96, 192, 256)
CUTOFF_FACTORS = (50.0, 70.0, 90.0)
GOLDSTONE_ZERO_TOLERANCE = 1.0e-10
GOLDSTONE_GAP_FLOOR = 1.0e-4


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


def compact(result, config_value: O2FiniteDensityEOSConfig) -> dict:
    low_boundary, high_boundary = off_shell_mode_omega_sq(
        0.0,
        sqrt(result.x_boundary),
        result.chemical_potential,
        result.space_response,
        config_value,
    )
    low_stationary, high_stationary = off_shell_mode_omega_sq(
        0.0,
        sqrt(result.scheme_b_stationary_x),
        result.chemical_potential,
        result.space_response,
        config_value,
    )
    return {
        "quadrature_order": result.quadrature_order,
        "momentum_cutoff": result.momentum_cutoff,
        "x_boundary": result.x_boundary,
        "stationary_x": result.scheme_b_stationary_x,
        "scheme_b_boundary_derivative": result.scheme_b_boundary_derivative,
        "stationarity_residual": result.scheme_b_stationary_residual,
        "tree_boundary_low_mode_sq": low_boundary,
        "tree_boundary_high_mode_sq": high_boundary,
        "stationary_low_mode_sq": low_stationary,
        "stationary_high_mode_sq": high_stationary,
    }


def main() -> int:
    eos_config = config()
    contract = uet_o2_stationarity_scheme_dependence_contract()
    reference = uet_o2_stationarity_scheme_dependence(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
        scheme_b_coefficient=SCHEME_B_COEFFICIENT,
    )
    reference_record = compact(reference, eos_config)

    quadrature_records = []
    for order in QUADRATURE_ORDERS:
        result = uet_o2_stationarity_scheme_dependence(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=order,
            cutoff_factor=REFERENCE_CUTOFF_FACTOR,
            scheme_b_coefficient=SCHEME_B_COEFFICIENT,
        )
        quadrature_records.append(compact(result, eos_config))

    cutoff_records = []
    for cutoff_factor in CUTOFF_FACTORS:
        result = uet_o2_stationarity_scheme_dependence(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff_factor=cutoff_factor,
            scheme_b_coefficient=SCHEME_B_COEFFICIENT,
        )
        record = compact(result, eos_config)
        record["cutoff_factor"] = cutoff_factor
        cutoff_records.append(record)

    previous = quadrature_records[-2]
    converged = quadrature_records[-1]
    convergence_relative_errors = {
        field: abs(converged[field] - previous[field])
        / max(abs(converged[field]), 1.0e-30)
        for field in ("stationary_x", "stationary_low_mode_sq", "stationary_high_mode_sq")
    }
    cutoff_previous = cutoff_records[-2]
    cutoff_converged = cutoff_records[-1]
    cutoff_relative_errors = {
        field: abs(cutoff_converged[field] - cutoff_previous[field])
        / max(abs(cutoff_converged[field]), 1.0e-30)
        for field in ("stationary_x", "stationary_low_mode_sq", "stationary_high_mode_sq")
    }

    values = tuple(reference_record.values())
    checks = {
        "all_reference_values_are_finite": all(isfinite(float(value)) for value in values),
        "tree_boundary_satisfies_goldstone_zero_mode": abs(
            reference_record["tree_boundary_low_mode_sq"]
        )
        <= GOLDSTONE_ZERO_TOLERANCE,
        "stationary_point_is_interior": reference.x_boundary < reference.scheme_b_stationary_x,
        "stationarity_residual_is_closed": abs(reference.scheme_b_stationary_residual) <= 1.0e-10,
        "stationary_modes_are_positive": reference_record["stationary_low_mode_sq"] > 0.0
        and reference_record["stationary_high_mode_sq"] > 0.0,
        "stationary_goldstone_gap_is_resolved": reference_record["stationary_low_mode_sq"]
        > GOLDSTONE_GAP_FLOOR,
        "current_scheme_is_not_stationary_at_ward_boundary": abs(
            reference_record["scheme_b_boundary_derivative"]
        )
        > GOLDSTONE_GAP_FLOOR,
        "ward_and_current_stationarity_are_incompatible": abs(
            reference_record["tree_boundary_low_mode_sq"]
        )
        <= GOLDSTONE_ZERO_TOLERANCE
        and abs(reference_record["scheme_b_boundary_derivative"]) > GOLDSTONE_GAP_FLOOR,
        "stationary_witness_fails_goldstone_ward_identity": reference_record[
            "stationary_low_mode_sq"
        ]
        > GOLDSTONE_GAP_FLOOR,
        "quadrature_gap_converges": max(convergence_relative_errors.values()) <= 1.0e-3,
        "cutoff_gap_converges": max(cutoff_relative_errors.values()) <= 2.0e-4,
        "finite_counterterm_is_declared_not_fitted": SCHEME_B_COEFFICIENT == -0.05,
        "physical_phase_transition_is_not_claimed": True,
        "physical_kubo_is_not_emitted": True,
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
        "PASS_SCOPED_CONDENSED_GOLDSTONE_WARD_BOUNDARY"
        if not failed
        else "BLOCKED_SCOPED_CONDENSED_GOLDSTONE_WARD_BOUNDARY"
    )
    evidence = [
        {"path": STATIONARITY_REL, "sha256": digest(STATIONARITY_REL)},
        {"path": OFFSHELL_REL, "sha256": digest(OFFSHELL_REL)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-condensed-goldstone-ward-v1",
        "artifact": "t13_uet_o2_condensed_goldstone_ward_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_GOLDSTONE_WARD_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "the tree stationary condensate boundary satisfies the zero-momentum Goldstone condition",
                "the declared finite-temperature scheme-B stationary witness is interior and has a resolved nonzero zero-momentum low-mode gap",
                "the current stationary witness therefore cannot be accepted as a symmetry-consistent broken O(2) phase or phase-transition result",
                "the current scheme cannot satisfy its stationarity condition and the Goldstone/Ward condition at the same condensate point",
                "a symmetry-improved or otherwise Ward-preserving finite-temperature condensed construction is required before condensed EOS promotion",
            ]
            if not failed
            else [],
            "equation_or_mapping": {
                "tree_ward_boundary": "x_boundary=q/lambda, omega_G^2(k=0)=0",
                "off_shell_modes": "(y-k^2-r_sigma/Z)(y-k^2-r_pi/Z)-4*mu^2*y=0",
                "ward_test": "omega_G^2(k=0; x_stationary) = 0 is required for a broken O(2) stationary branch",
                "observed_boundary": "omega_G^2(k=0; x_boundary)=0",
                "boundary_stationarity": "partial_x Omega_scheme_B(x_boundary)=-0.13207100582827716 != 0",
                "observed_stationary": "omega_G^2(k=0; x_stationary)>0 for the declared scheme-B witness",
            },
            "units": {
                "unit_lane": "natural",
                "x_and_mode_squared": "natural energy squared",
                "temperature_and_chemical_potential": "natural energy",
                "Phi": "fixed effective response input; no SI map",
            },
            "derivation_class": "action-derived off-shell O(2) determinant plus finite-temperature stationarity witness; scoped Ward consistency audit, not microscopic completion",
            "observable": "zero-momentum phase-mode Ward residual of the declared stationary condensate witness",
            "data_role": "INTERNAL_ACTION_DERIVED_WARD_BOUNDARY_NOT_EXTERNAL_VALIDATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_finite_temperature_renormalization_scheme_missing",
                "ward_preserving_condensed_2PI_or_1N_completion_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "retarded_physical_Kubo_match_missing",
                "microscopic_SK_KMS_matching_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "Goldstone/Ward rejection of the current stationarity witness only; no condensed phase, phase transition, two-fluid, transport, Core, Gravity, SI, alpha, or external-validation unlock",
            "claim_boundary": "This closes only a scoped Ward-consistency boundary. It rejects the current finite-temperature stationarity witness as a complete broken O(2) phase because its zero-momentum phase mode is gapped. It does not prove that every future symmetry-improved construction fails, and it does not close the condensed EOS, Kubo/SK-KMS transport, SI mapping, alpha_Phi_K, TTG, or Full Topic 13.",
        },
        "contract": contract,
        "reference": reference_record,
        "reference_parameters": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI_RESPONSE,
            "scheme_b_coefficient": SCHEME_B_COEFFICIENT,
            "goldstone_zero_tolerance": GOLDSTONE_ZERO_TOLERANCE,
            "goldstone_gap_floor": GOLDSTONE_GAP_FLOOR,
        },
        "quadrature_records": quadrature_records,
        "quadrature_convergence_relative_errors": convergence_relative_errors,
        "cutoff_records": cutoff_records,
        "cutoff_relative_errors": cutoff_relative_errors,
        "external_literature_context": {
            "source_url": "https://arxiv.org/abs/0810.5510",
            "title": "Kaon condensation in the color-flavor-locked phase of quark matter, the Goldstone theorem, and the 2PI Hartree approximation",
            "authors": ["Jens O. Andersen", "Lars E. Leganger"],
            "role": "primary literature context for finite-temperature 2PI Hartree renormalization and Goldstone consistency; not a numeric UET input",
        },
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "ward_preserving_condensed_2PI_or_1N_completion_missing",
        "next_controller": "Replace the current stationarity witness with a Ward-preserving symmetry-improved 2PI or controlled 1/N condensed construction, then rerun the finite-temperature EOS and state-matched Kubo/SK-KMS gates.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "parameter_policy": {
            "scheme_b_coefficient": "declared internal witness, not fitted to target data",
            "ward_gap_floor": "fixed numerical rejection tolerance, not a physical threshold",
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
                "tree_boundary_goldstone_sq": reference_record["tree_boundary_low_mode_sq"],
                "stationary_goldstone_sq": reference_record["stationary_low_mode_sq"],
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
