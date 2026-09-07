"""Audit the Topic 13 finite-temperature O(2) quasiparticle EOS lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FINITE_T_QUASIPARTICLE_EOS_STATUS,
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_quasiparticle_contract,
    finite_temperature_o2_state,
    quasiparticle_pressure,
)
from docs.scripts.audit.audit_topic13_fixed_phi_spectrum_repair import (
    fixed_phi_witnesses,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_uet_o2_finite_temperature_quasiparticle_eos_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def central(function, value: float, step: float = 2.0e-4) -> float:
    h = step * max(1.0, abs(float(value)))
    return (function(value + h) - function(value - h)) / (2.0 * h)


def state_record(state) -> dict:
    record = dict(state.__dict__)
    # Goldstone is inapplicable on the normal branch, not a failed numeric value.
    if state.branch == "normal":
        record["goldstone_energy_at_zero_momentum"] = None
        record["goldstone_evaluation"] = "NOT_APPLICABLE_NORMAL_BRANCH"
    else:
        record["goldstone_evaluation"] = "EVALUATED"
    return record


def main() -> int:
    failures: list[str] = []
    response = CovariantResponseConfig(
        epsilon_nc=0.05,
        phi_equilibrium=0.0,
        response_kinetic=1.0,
        response_mass_sq=1.0,
        response_quartic=1.0,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=1.0,
        matter_mass_sq=1.0,
        matter_quartic=1.0,
        response_coupling=0.8,
    )
    config = FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=matter, response=response),
        quadrature_order=160,
        cutoff_factor=65.0,
        derivative_step=1.0e-4,
    )

    normal_points = ((0.22, 0.35, 0.15), (0.31, 0.55, 0.20))
    condensed_points = ((0.12, 1.18, 0.15), (0.20, 1.28, 0.20))
    normal_states = [finite_temperature_o2_state(*point, config) for point in normal_points]
    condensed_states = [
        finite_temperature_o2_state(*point, config) for point in condensed_points
    ]

    for state in normal_states:
        check(state.branch == "normal", "normal point did not select normal branch", failures)
        check(state.pressure > 0.0, "normal pressure is not positive", failures)
        check(state.entropy_density > 0.0, "normal entropy is not positive", failures)
        check(state.energy_density > 0.0, "normal energy is not positive", failures)
        check(state.susceptibility >= -1.0e-8, "normal susceptibility is negative", failures)

    for state in condensed_states:
        check(state.branch == "condensed", "condensed point did not select condensed branch", failures)
        check(state.condensate_amplitude > 0.0, "condensed amplitude is not positive", failures)
        check(state.pressure > 0.0, "condensed pressure is not positive", failures)
        check(state.entropy_density > 0.0, "condensed entropy is not positive", failures)
        check(state.energy_density > 0.0, "condensed energy is not positive", failures)
        check(state.susceptibility >= -1.0e-8, "condensed susceptibility is negative", failures)
        check(
            abs(state.goldstone_energy_at_zero_momentum) <= 1.0e-8,
            "condensed lower quasiparticle is not gapless at zero momentum",
            failures,
        )

    for temperature, mu, phi in (*normal_points[:1], *condensed_points[:1]):
        pressure_plus = quasiparticle_pressure(temperature, mu, phi, config)
        pressure_minus = quasiparticle_pressure(temperature, -mu, phi, config)
        state_plus = finite_temperature_o2_state(temperature, mu, phi, config)
        state_minus = finite_temperature_o2_state(temperature, -mu, phi, config)
        check(
            np.isclose(pressure_plus, pressure_minus, rtol=2.0e-7, atol=2.0e-10),
            "pressure is not even in chemical potential",
            failures,
        )
        check(
            np.isclose(
                state_plus.charge_density,
                -state_minus.charge_density,
                rtol=2.0e-5,
                atol=2.0e-8,
            ),
            "charge density is not odd in chemical potential",
            failures,
        )
        check(
            np.isclose(
                state_plus.entropy_density,
                state_minus.entropy_density,
                rtol=2.0e-5,
                atol=2.0e-8,
            ),
            "entropy is not even in chemical potential",
            failures,
        )

    representative_checks: dict[str, bool] = {}
    for label, state in (("normal", normal_states[0]), ("condensed", condensed_states[0])):
        p_mu = central(
            lambda value: quasiparticle_pressure(
                state.temperature, value, state.space_response, config
            ),
            state.chemical_potential,
        )
        p_t = central(
            lambda value: quasiparticle_pressure(
                value, state.chemical_potential, state.space_response, config
            ),
            state.temperature,
        )
        representative_checks[f"{label}_charge_is_pressure_mu_derivative"] = np.isclose(
            p_mu, state.charge_density, rtol=2.0e-3, atol=2.0e-6
        )
        representative_checks[f"{label}_entropy_is_pressure_temperature_derivative"] = np.isclose(
            p_t, state.entropy_density, rtol=2.0e-3, atol=2.0e-6
        )
        representative_checks[f"{label}_gibbs_duhem_energy_identity"] = np.isclose(
            state.energy_density,
            -state.pressure
            + state.temperature * state.entropy_density
            + state.chemical_potential * state.charge_density,
            rtol=1.0e-12,
            atol=1.0e-12,
        )
        for key, passed in representative_checks.items():
            if key.startswith(f"{label}_"):
                check(bool(passed), key, failures)

    for temperature, mu, phi in condensed_points:
        for momentum in (0.0, 0.05, 0.5, 2.0, 8.0):
            e_plus, e_minus = condensed_quasiparticle_energies(
                momentum, mu, phi, config
            )
            check(e_plus >= e_minus >= 0.0, "quasiparticle energies violate ordering", failures)
            check(np.isfinite(e_plus) and np.isfinite(e_minus), "quasiparticle energy is non-finite", failures)

    representative_checks = {
        key: bool(value) for key, value in representative_checks.items()
    }
    contract = finite_temperature_o2_quasiparticle_contract()
    independent = fixed_phi_witnesses()
    checks = {
        **independent["checks"],
        "normal_branch_points_pass": all(state.branch == "normal" for state in normal_states),
        "condensed_branch_points_pass": all(state.branch == "condensed" for state in condensed_states),
        "normal_positivity_pass": all(
            state.pressure > 0.0 and state.entropy_density > 0.0 and state.energy_density > 0.0
            for state in normal_states
        ),
        "condensed_positivity_pass": all(
            state.pressure > 0.0 and state.entropy_density > 0.0 and state.energy_density > 0.0
            for state in condensed_states
        ),
        "condensed_goldstone_limit_pass": all(
            abs(state.goldstone_energy_at_zero_momentum) <= 1.0e-8
            for state in condensed_states
        ),
        "quasiparticle_spectrum_finite_and_nonnegative": not any(
            "quasiparticle" in failure for failure in failures
        ),
        "thermodynamic_derivative_checks_pass": all(representative_checks.values()),
        "gibbs_duhem_checks_pass": all(
            value for key, value in representative_checks.items() if "gibbs_duhem" in key
        ),
        "pressure_even_in_mu": not any("pressure is not even" in failure for failure in failures),
        "charge_odd_in_mu": not any("charge density is not odd" in failure for failure in failures),
        "entropy_even_in_mu": not any("entropy is not even" in failure for failure in failures),
        "C_not_relabelled_as_charge": contract["unit_contract"]["C"] == "not relabeled as charge density",
        "Phi_not_relabelled_as_temperature": contract["unit_contract"]["Phi"] == "action response input; not temperature",
        "R_gen_not_state": contract["R_gen"].startswith("derived history trace only"),
        "no_physical_transport_emitted": "transport" in contract["excluded_scope"],
        "no_SI_alpha_emitted": "alpha_Phi_K" in contract["excluded_scope"],
        "no_target_or_holdout": True,
    }
    failures.extend(
        f"contract check failed: {key}"
        for key, passed in checks.items()
        if not passed
    )
    check(not failures, "audit has failed checks", failures)

    artifact = {
        "schema_version": "t13-uet-o2-finite-temperature-quasiparticle-eos-v1",
        "artifact": "t13_uet_o2_finite_temperature_quasiparticle_eos_audit",
        "generated_at": str(date.today()),
        "status": FINITE_T_QUASIPARTICLE_EOS_STATUS if not failures else "BLOCKED_FINITE_T_QUASIPARTICLE_EOS_AUDIT",
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failures else "OPEN",
            "what_is_closed": [
                "tree-level O(2) condensate branch and phase selection",
                "finite-temperature normal and condensed quasiparticle pressure branches",
                "gapless ideal Goldstone limit on the tree condensate branch",
                "charge, entropy, energy, susceptibility, and Gibbs-Duhem checks for the declared approximate EOS",
                "even/odd chemical-potential symmetry without relabeling C or Phi",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": "action-derived approximate tree-condensate plus thermal quasiparticle determinant",
            "observable": "natural-unit pressure, charge, entropy, energy, and susceptibility",
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {
                    "path": "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py",
                    "sha256": sha256(MODULE),
                }
            ],
            "verification_status": (
                FINITE_T_QUASIPARTICLE_EOS_STATUS if not failures else "BLOCKED_FINITE_T_QUASIPARTICLE_EOS_AUDIT"
            ),
            "open_blockers": [
                "vacuum_counterterm_and_interacting_finite_temperature_self_energy_missing",
                "full_condensate_normal_two_fluid_SK_KMS_matching_missing",
                "physical_Kubo_coefficient_record_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "finite-temperature approximate EOS lane only; no physical transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "source_hashes": {
            path: sha256(ROOT / path)
            for path in (
                "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py",
                "docs/core/uet_o2_formal_transverse_response.py",
                "docs/core/uet_covariant_matter.py",
                "docs/core/uet_o2_finite_density_eos.py",
                "docs/scripts/audit/audit_topic13_fixed_phi_spectrum_repair.py",
                "docs/scripts/audit/audit_topic13_finite_temperature_quasiparticle_eos.py",
            )
        },
        "independent_action_witnesses": independent,
        "state_grid": {
            "normal": [state_record(state) for state in normal_states],
            "condensed": [state_record(state) for state in condensed_states],
        },
        "representative_checks": representative_checks,
        "checks": checks,
        "failed_checks": failures,
        "numeric_beta_T13_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "interacting_finite_temperature_self_energy_and_full_two_fluid_transport_missing",
        "next_controller": "Match the approximate EOS to a declared interacting finite-temperature action and state-specific Kubo/SK-KMS records without using TTG holdout data.",
        "claim_promotion": False,
        "full_core_unlock": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "closure_level": artifact["major_result"]["closure_level"], "failed_checks": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
