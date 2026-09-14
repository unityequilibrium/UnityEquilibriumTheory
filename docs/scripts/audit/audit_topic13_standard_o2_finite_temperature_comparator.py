"""Audit the standard finite-temperature O(2) normal-branch comparator."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.core_paths import canonical_existing_path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.standard_o2_finite_temperature_comparator import (
    standard_o2_normal_state,
    standard_o2_thermal_comparator_contract,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/standard_o2_finite_temperature_comparator.py"
EOS_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/artifacts/t13_standard_o2_finite_temperature_comparator_audit.json"


def digest(rel: str) -> str:
    return hashlib.sha256(canonical_existing_path(ROOT / rel).read_bytes()).hexdigest()


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
    mu = 0.2
    phi = 0.2
    state = standard_o2_normal_state(temperature, mu, phi, eos_config)
    state_neg = standard_o2_normal_state(temperature, -mu, phi, eos_config)
    delta_mu = 1.0e-4
    delta_temperature = 1.0e-4
    p_mu_plus = standard_o2_normal_state(temperature, mu + delta_mu, phi, eos_config).pressure
    p_mu_minus = standard_o2_normal_state(temperature, mu - delta_mu, phi, eos_config).pressure
    p_t_plus = standard_o2_normal_state(temperature + delta_temperature, mu, phi, eos_config).pressure
    p_t_minus = standard_o2_normal_state(temperature - delta_temperature, mu, phi, eos_config).pressure
    dp_dmu = (p_mu_plus - p_mu_minus) / (2.0 * delta_mu)
    dp_dt = (p_t_plus - p_t_minus) / (2.0 * delta_temperature)
    contract = standard_o2_thermal_comparator_contract()
    checks = {
        "natural_unit_domain_is_declared": contract["domain"]["unit_lane"] == "natural",
        "normal_branch_is_declared": contract["domain"]["normal_branch"] == "Z*mu^2 < m_eff(Phi)^2",
        "pressure_is_positive": state.pressure > 0.0,
        "entropy_is_positive": state.entropy_density > 0.0,
        "energy_is_positive": state.energy_density > 0.0,
        "susceptibility_is_positive": state.charge_susceptibility > 0.0,
        "pressure_is_even_in_mu": abs(state.pressure - state_neg.pressure) <= 1.0e-10,
        "entropy_is_even_in_mu": abs(state.entropy_density - state_neg.entropy_density) <= 1.0e-10,
        "energy_is_even_in_mu": abs(state.energy_density - state_neg.energy_density) <= 1.0e-10,
        "charge_is_odd_in_mu": abs(state.charge_density + state_neg.charge_density) <= 1.0e-10,
        "charge_is_pressure_derivative": abs(dp_dmu - state.charge_density) <= 2.0e-7,
        "entropy_is_temperature_derivative": abs(dp_dt - state.entropy_density) <= 2.0e-7,
        "phi_enters_only_through_effective_mass": contract["uET_boundary"]["Phi"].startswith("enters only through"),
        "alpha_not_emitted": contract["uET_boundary"]["alpha_Phi_K"] == "not emitted",
        "kubo_not_emitted": contract["uET_boundary"]["physical_Kubo_coefficient"] == "not emitted",
        "si_map_not_emitted": contract["uET_boundary"]["si_map"] == "not emitted",
        "c_not_relabelled": contract["uET_boundary"]["C"] == "not relabeled as charge density",
        "trace_is_not_state": contract["uET_boundary"]["R_gen"] == "not used as state or feedback",
    }
    status = "PASS_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR" if all(checks.values()) else "FAIL_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR"
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-standard-o2-finite-temperature-comparator-v1",
        "artifact": "t13_standard_o2_finite_temperature_comparator_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "standard finite-temperature normal-branch thermodynamic integrals for a free complex scalar using the declared m_eff(Phi)",
                "pressure, charge-density, entropy, energy, and charge-susceptibility unit relations in the natural-unit comparator lane",
                "even/odd charge symmetry and numerical pressure-derivative first-law checks",
                "explicit separation of thermal comparator variables from UET Phi, C, R_gen, R_obs, alpha_Phi_K, and Kubo data",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": contract["equations"],
            "units": {
                "temperature": "natural energy units",
                "chemical_potential": "natural energy units",
                "pressure": "natural energy density",
                "charge_density": "natural charge density",
                "entropy_density": "natural entropy density",
                "energy_density": "natural energy density",
                "susceptibility": "charge density per natural chemical-potential unit",
            },
            "derivation_class": "standard finite-temperature free-complex-scalar grand-canonical comparator using UET m_eff(Phi) input; not UET finite-temperature derivation",
            "observable": "normal-branch thermal pressure, charge, entropy, energy, and susceptibility",
            "data_role": "STANDARD_THERMAL_QFT_COMPARATOR_NOT_UET_CLOSURE",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "finite_temperature_UET_effective_action_not_derived",
                "condensate_and_normal_two_fluid_sector_not_derived",
                "physical_Kubo_coefficient_record_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
                "SK_KMS_physical_matching_missing",
            ],
            "dependency_unlocked": "standard finite-temperature normal comparator lane only; no physical UET EOS, transport, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This is a standard thermodynamic comparator. It does not derive the finite-temperature UET action, a two-fluid normal component, transport coefficients, KMS matching, SI Phi calibration, external validation, or global UET closure.",
        },
        "state": {
            "temperature": state.temperature,
            "chemical_potential": state.chemical_potential,
            "space_response": state.space_response,
            "effective_mass": state.effective_mass,
            "pressure": state.pressure,
            "charge_density": state.charge_density,
            "entropy_density": state.entropy_density,
            "energy_density": state.energy_density,
            "charge_susceptibility": state.charge_susceptibility,
            "momentum_cutoff": state.momentum_cutoff,
            "quadrature_order": state.quadrature_order,
        },
        "finite_difference_checks": {
            "dp_dmu": dp_dmu,
            "dp_dT": dp_dt,
            "abs_dp_dmu_minus_n": abs(dp_dmu - state.charge_density),
            "abs_dp_dT_minus_s": abs(dp_dt - state.entropy_density),
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "finite_temperature_UET_effective_action_and_normal_two_fluid_sector_not_derived",
        "next_controller": "If the standard comparator is retained, source-lock the intended material/state regime; separately derive the UET finite-temperature effective action, Kubo coefficients, and SI Phi mapping.",
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
        "charge_density": state.charge_density,
        "entropy_density": state.entropy_density,
        "energy_density": state.energy_density,
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
