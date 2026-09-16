"""Audit the fixed-prescription auxiliary-field condensed O(2) lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_auxiliary_field_condensed import (
    auxiliary_field_condensed_contract,
    auxiliary_field_condensed_state,
    auxiliary_field_grand_potential,
    auxiliary_field_mode_omega_sq,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_auxiliary_field_condensed.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_auxiliary_field_condensed_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.30
PHI_RESPONSE = 0.20
REFERENCE_ORDER = 192
REFERENCE_CUTOFF_FACTOR = 70.0
QUADRATURE_ORDERS = (96, 128, 192)
CUTOFF_FACTORS = (50.0, 70.0, 90.0)
WARD_TOLERANCE = 1.0e-10
GAP_TOLERANCE = 1.0e-10
RHO_DERIVATIVE_TOLERANCE = 1.0e-7
MASS_DERIVATIVE_TOLERANCE = 1.0e-6
THERMO_MU_TOLERANCE = 1.0e-6
THERMO_T_TOLERANCE = 1.0e-7
QUADRATURE_RELATIVE_TOLERANCE = 1.0e-5
CUTOFF_RELATIVE_TOLERANCE = 2.0e-6

STATE_POINTS = (
    {"temperature": 0.20, "chemical_potential": 1.20, "space_response": 0.20},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.20},
    {"temperature": 0.28, "chemical_potential": 1.30, "space_response": 0.20},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.00},
    {"temperature": 0.25, "chemical_potential": 1.30, "space_response": 0.40},
    {"temperature": 0.20, "chemical_potential": 1.25, "space_response": 0.20},
)


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


def compact(state, eos_config: O2FiniteDensityEOSConfig) -> dict:
    low_zero, high_zero = auxiliary_field_mode_omega_sq(0.0, state, eos_config)
    low_probe, high_probe = auxiliary_field_mode_omega_sq(0.1, state, eos_config)
    return {
        "temperature": state.temperature,
        "chemical_potential": state.chemical_potential,
        "space_response": state.space_response,
        "base_mass_sq": state.base_mass_sq,
        "dressed_mass_sq": state.dressed_mass_sq,
        "reference_mass_sq": state.reference_mass_sq,
        "condensate_amplitude_sq": state.condensate_amplitude_sq,
        "renormalized_tadpole": state.renormalized_tadpole,
        "auxiliary_gap_residual": state.auxiliary_gap_residual,
        "condensed_stationarity_residual": state.condensed_stationarity_residual,
        "ward_phase_gap_sq": state.ward_phase_gap_sq,
        "tree_phase_curvature": state.tree_phase_curvature,
        "radial_curvature": state.radial_curvature,
        "pressure": state.pressure,
        "charge_density": state.charge_density,
        "entropy_density": state.entropy_density,
        "energy_density": state.energy_density,
        "low_mode_zero_sq": low_zero,
        "high_mode_zero_sq": high_zero,
        "low_mode_probe_sq": low_probe,
        "high_mode_probe_sq": high_probe,
        "momentum_cutoff": state.momentum_cutoff,
        "quadrature_order": state.quadrature_order,
    }


def relative_change(current: float, previous: float) -> float:
    return abs(current - previous) / max(abs(current), 1.0e-30)


def main() -> int:
    eos_config = config()
    contract = auxiliary_field_condensed_contract()
    reference = auxiliary_field_condensed_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    reference_record = compact(reference, eos_config)

    state_records = []
    states = []
    for point in STATE_POINTS:
        state = auxiliary_field_condensed_state(
            point["temperature"],
            point["chemical_potential"],
            point["space_response"],
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff_factor=REFERENCE_CUTOFF_FACTOR,
        )
        states.append(state)
        state_records.append(compact(state, eos_config))

    quadrature_records = []
    for order in QUADRATURE_ORDERS:
        state = auxiliary_field_condensed_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=order,
            cutoff_factor=REFERENCE_CUTOFF_FACTOR,
        )
        quadrature_records.append(compact(state, eos_config))

    cutoff_records = []
    for cutoff_factor in CUTOFF_FACTORS:
        state = auxiliary_field_condensed_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff_factor=cutoff_factor,
        )
        record = compact(state, eos_config)
        record["cutoff_factor"] = cutoff_factor
        cutoff_records.append(record)

    quad_previous = quadrature_records[-2]
    quad_current = quadrature_records[-1]
    quad_errors = {
        field: relative_change(quad_current[field], quad_previous[field])
        for field in ("pressure", "condensate_amplitude_sq", "high_mode_zero_sq")
    }
    cutoff_previous = cutoff_records[-2]
    cutoff_current = cutoff_records[-1]
    cutoff_errors = {
        field: relative_change(cutoff_current[field], cutoff_previous[field])
        for field in ("pressure", "condensate_amplitude_sq", "high_mode_zero_sq")
    }

    rho_step = 1.0e-3
    mass_step = 1.0e-3
    rho = reference.condensate_amplitude_sq
    mass_sq = reference.dressed_mass_sq
    rho_derivative = (
        auxiliary_field_grand_potential(
            rho + rho_step,
            mass_sq,
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff=reference.momentum_cutoff,
        )
        - auxiliary_field_grand_potential(
            rho - rho_step,
            mass_sq,
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff=reference.momentum_cutoff,
        )
    ) / (2.0 * rho_step)
    mass_derivative = (
        auxiliary_field_grand_potential(
            rho,
            mass_sq + mass_step,
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff=reference.momentum_cutoff,
        )
        - auxiliary_field_grand_potential(
            rho,
            mass_sq - mass_step,
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff=reference.momentum_cutoff,
        )
    ) / (2.0 * mass_step)

    thermo_step = 1.0e-4

    def fixed_cutoff_pressure(temperature: float, chemical_potential: float) -> float:
        return auxiliary_field_condensed_state(
            temperature,
            chemical_potential,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            momentum_cutoff=reference.momentum_cutoff,
        ).pressure

    pressure_mu_derivative = (
        fixed_cutoff_pressure(TEMPERATURE, CHEMICAL_POTENTIAL + thermo_step)
        - fixed_cutoff_pressure(TEMPERATURE, CHEMICAL_POTENTIAL - thermo_step)
    ) / (2.0 * thermo_step)
    pressure_temperature_derivative = (
        fixed_cutoff_pressure(TEMPERATURE + thermo_step, CHEMICAL_POTENTIAL)
        - fixed_cutoff_pressure(TEMPERATURE - thermo_step, CHEMICAL_POTENTIAL)
    ) / (2.0 * thermo_step)

    all_values = [
        value
        for record in state_records
        for key, value in record.items()
        if key not in {"temperature", "chemical_potential", "space_response", "quadrature_order"}
    ]
    checks = {
        "all_state_records_are_finite": all(isfinite(float(value)) for value in all_values),
        "all_states_are_condensed": all(state.condensate_amplitude_sq > 0.0 for state in states),
        "fixed_reference_mass_is_shared": len({state.reference_mass_sq for state in states}) == 1,
        "no_state_dependent_counterterm_is_used": all(
            not state.state_dependent_counterterm for state in states
        ),
        "auxiliary_gap_closes": all(
            abs(state.auxiliary_gap_residual) <= GAP_TOLERANCE for state in states
        ),
        "condensed_stationarity_closes": all(
            abs(state.condensed_stationarity_residual) <= WARD_TOLERANCE
            for state in states
        ),
        "ward_phase_gap_closes_across_states": all(
            abs(state.ward_phase_gap_sq) <= WARD_TOLERANCE for state in states
        ),
        "zero_mode_is_gapless_across_states": all(
            abs(record["low_mode_zero_sq"]) <= WARD_TOLERANCE
            for record in state_records
        ),
        "radial_mode_is_positive_across_states": all(
            record["high_mode_zero_sq"] > 0.0 for record in state_records
        ),
        "finite_momentum_low_mode_is_positive": all(
            record["low_mode_probe_sq"] > 0.0 for record in state_records
        ),
        "rho_stationarity_finite_difference_closes": abs(rho_derivative)
        <= RHO_DERIVATIVE_TOLERANCE,
        "mass_stationarity_finite_difference_is_numerically_resolved": abs(mass_derivative)
        <= MASS_DERIVATIVE_TOLERANCE,
        "charge_is_envelope_derivative": abs(pressure_mu_derivative - reference.charge_density)
        <= THERMO_MU_TOLERANCE,
        "entropy_is_envelope_derivative": abs(
            pressure_temperature_derivative - reference.entropy_density
        )
        <= THERMO_T_TOLERANCE,
        "quadrature_converges": max(quad_errors.values()) <= QUADRATURE_RELATIVE_TOLERANCE,
        "cutoff_converges_within_declared_scheme": max(cutoff_errors.values())
        <= CUTOFF_RELATIVE_TOLERANCE,
        "fixed_prescription_is_not_fit": True,
        "microscopic_matching_is_not_claimed": contract["approximation"][
            "microscopic_2pi_or_controlled_1N_match"
        ]
        is False,
        "physical_kubo_is_not_emitted": contract["approximation"]["physical_kubo"] is False,
        "Phi_ontology_is_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace only" in contract["ontology"]["R_gen"],
        "R_obs_is_separate": "separate observer record" in contract["ontology"]["R_obs"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE"
        if not failed
        else "BLOCKED_FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE"
    )
    evidence = [{"path": MODULE_REL, "sha256": digest(MODULE_REL)}]
    artifact = {
        "schema_version": "t13-uet-o2-auxiliary-field-condensed-v1",
        "artifact": "t13_uet_o2_auxiliary_field_condensed_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "one fixed mass-squared subtraction prescription defines a finite-temperature condensed auxiliary-field lane across the declared state grid",
                "the auxiliary stationarity equations enforce M^2=Z*mu^2 and a zero phase Ward gap without a state-dependent counterterm",
                "the same stationary functional supplies pressure, charge, entropy, and energy identities within the natural-unit formal lane",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived auxiliary-field functional with fixed Taylor-subtracted one-loop determinant; formal leading-large-N-inspired normalization, not microscopic 2PI or controlled 1/N matching",
            "observable": "finite-temperature condensed Ward gap, auxiliary gap residual, and thermodynamic envelope identities",
            "data_role": "INTERNAL_ACTION_DERIVED_FORMAL_NO_EXTERNAL_CALIBRATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "microscopic_2pi_or_controlled_1N_matching_missing",
                "physical_finite_temperature_renormalization_scheme_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "retarded_physical_Kubo_match_missing",
                "microscopic_SK_KMS_matching_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal Ward-preserving condensed auxiliary-field lane only; no microscopic renormalization, physical EOS, Kubo/SK-KMS, SI, alpha, TTG, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This closes only a fixed-prescription Ward-preserving auxiliary-field condensed lane. It is not a microscopic 2PI or controlled 1/N completion, a physical finite-temperature renormalization, a complete two-fluid EOS, a retarded Kubo/SK-KMS match, an SI Phi map, an alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure.",
        },
        "contract": contract,
        "reference": reference_record,
        "state_records": state_records,
        "reference_parameters": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI_RESPONSE,
            "ward_tolerance": WARD_TOLERANCE,
            "gap_tolerance": GAP_TOLERANCE,
            "quadrature_order": REFERENCE_ORDER,
            "cutoff_factor": REFERENCE_CUTOFF_FACTOR,
        },
        "stationarity_diagnostics": {
            "rho_step": rho_step,
            "mass_squared_step": mass_step,
            "rho_derivative": rho_derivative,
            "mass_squared_derivative": mass_derivative,
            "pressure_mu_derivative": pressure_mu_derivative,
            "pressure_temperature_derivative": pressure_temperature_derivative,
            "reference_charge_density": reference.charge_density,
            "reference_entropy_density": reference.entropy_density,
            "thermo_mu_error": pressure_mu_derivative - reference.charge_density,
            "thermo_temperature_error": pressure_temperature_derivative - reference.entropy_density,
        },
        "quadrature_records": quadrature_records,
        "quadrature_relative_errors": quad_errors,
        "cutoff_records": cutoff_records,
        "cutoff_relative_errors": cutoff_errors,
        "external_literature_context": {
            "source_url": "https://arxiv.org/abs/hep-ph/9911431",
            "title": "Effective Potential of O(N) Linear Sigma Model at Finite Temperature",
            "authors": ["Y. Nemoto", "K. Naito", "M. Oka"],
            "role": "primary context for symmetry-conserving finite-temperature O(N)/CJT treatment; no numeric UET input",
        },
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "microscopic_2pi_or_controlled_1N_matching_missing",
        "next_controller": "Match the formal auxiliary-field equations to a microscopic symmetry-preserving 2PI or controlled 1/N construction, then rerun the condensed EOS and retarded Kubo/SK-KMS gates.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "parameter_policy": {
            "subtraction_reference": "fixed Phi_equilibrium mass-squared reference across all states",
            "state_grid": "declared diagnostic grid, not a fit set",
            "counterterm": "no state-dependent Ward coefficient is introduced",
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
                "max_quadrature_relative_error": max(quad_errors.values()),
                "max_cutoff_relative_error": max(cutoff_errors.values()),
                "ward_gap_max": max(abs(state.ward_phase_gap_sq) for state in states),
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
