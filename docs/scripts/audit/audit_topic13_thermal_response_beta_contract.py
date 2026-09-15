"""Verify the named finite-temperature beta_T13 response-functional contract."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_response_beta_contract import (
    ThermalResponseBetaInputs,
    a_phi_of_temperature,
    beta_t13_from_stiffness_slope,
    da_phi_dT_per_K,
    entropy_density_J_per_m3_K,
    free_energy_density_J_per_m3,
    thermal_response_beta_contract,
)


CONTRACT_REL = "docs/core/thermal_response_beta_contract.py"
THERMAL_AUDIT_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_closure_derivation_audit.json"
PARAMETERS_REL = "docs/core/uet_parameters.py"
MASTER_REL = "docs/core/uet_master_equation.py"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def numerical_witness() -> dict[str, Any]:
    """Use synthetic coefficients solely to verify the declared derivatives."""

    inputs = ThermalResponseBetaInputs(300.0, 1.2, 0.18, 0.4, 0.3)
    e0 = 2.5
    c = 0.2
    phi = 0.7
    step_K = 1.0e-3
    t0 = inputs.reference_temperature_K
    free_plus = free_energy_density_J_per_m3(t0 + step_K, c, phi, inputs, e0)
    free_minus = free_energy_density_J_per_m3(t0 - step_K, c, phi, inputs, e0)
    finite_difference_entropy = -(free_plus - free_minus) / (2.0 * step_K)
    analytic_entropy = entropy_density_J_per_m3_K(phi, inputs, e0)
    slope = da_phi_dT_per_K(inputs)
    recovered_beta = beta_t13_from_stiffness_slope(t0, slope)
    return {
        "role": "synthetic derivative/unit witness only; not calibration or physical data",
        "inputs": {
            "reference_temperature_K": t0,
            "a_phi_T0": inputs.a_phi_T0,
            "beta_t13_dimensionless": inputs.beta_t13_dimensionless,
            "b_phi": inputs.b_phi,
            "coupling_g": inputs.coupling_g,
            "e0_J_per_m3": e0,
        },
        "computed": {
            "da_phi_dT_per_K": slope,
            "a_phi_T0": a_phi_of_temperature(t0, inputs),
            "analytic_entropy_density_J_per_m3_K": analytic_entropy,
            "finite_difference_entropy_density_J_per_m3_K": finite_difference_entropy,
            "recovered_beta_t13_dimensionless": recovered_beta,
        },
        "checks": {
            "reference_stiffness_recovers_a_phi_T0": abs(a_phi_of_temperature(t0, inputs) - inputs.a_phi_T0) <= 1.0e-14,
            "beta_recovers_from_slope": abs(recovered_beta - inputs.beta_t13_dimensionless) <= 1.0e-14,
            "entropy_derivative_matches_finite_difference": abs(finite_difference_entropy - analytic_entropy) <= 1.0e-10,
        },
    }


def main() -> int:
    contract_text = text(CONTRACT_REL)
    thermal = load(THERMAL_AUDIT_REL)
    parameters = text(PARAMETERS_REL)
    master = text(MASTER_REL)
    formula = text(FORMULA_REL)
    branch = thermal_response_beta_contract()
    witness = numerical_witness()
    checks = {
        "finite_temperature_functional_declared": "f_hat_T13(C,Phi,T)" in branch["functional"],
        "beta_t13_has_declared_action_term_and_units": branch["beta_T13"] == "dimensionless local stiffness-temperature slope" and branch["da_Phi_dT"] == "K^-1",
        "finite_temperature_density_scale_is_explicit": branch["e0"] == "J m^-3 external input" and branch["f"] == "J m^-3 after e0 is supplied",
        "entropy_identity_is_not_promoted_to_production": "not an entropy\n    production law" in contract_text,
        "landauer_is_not_used": branch["beta_th_identity"] == "not used" and "k_B" not in contract_text and "ln(2)" not in contract_text,
        "legacy_core_beta_is_not_identified": branch["beta_core_identity"].startswith("not asserted") and "Dimensionless normalized coupling (not Joules)" in parameters,
        "legacy_information_state_is_not_phi": "beta_U*C^2" in master and "information coupling" in master and "not Phi" in branch["beta_core_identity"],
        "beta_wave_is_not_identified": branch["beta_wave_identity"].startswith("not asserted"),
        "trace_has_no_backreaction": "derived history trace only" in branch["R_gen_identity"],
        "old_thermal_audit_remains_open_and_separate": thermal.get("status") == "DIMENSIONAL_THERMAL_CLOSURE_BLOCKED",
        "formula_record_present": "`T13-018`" in formula,
        "synthetic_derivative_witness_passes": all(witness["checks"].values()),
    }
    status = "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT" if all(checks.values()) else "FAIL_T13_THERMAL_RESPONSE_BETA_CONTRACT_AUDIT"
    report = {
        "schema_version": "t13-thermal-response-beta-contract-v1",
        "artifact": "t13_thermal_response_beta_contract_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_THERMAL_RESPONSE_BETA_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "a named finite-temperature normalized response functional now has an explicit a_Phi(T) Phi^2/2 action term",
                "beta_T13 is defined as the dimensionless local stiffness-temperature slope T0*(da_Phi/dT)|T0 with a declared K^-1 derivative",
                "the corresponding equilibrium entropy derivative has an explicit e0-dependent unit contract and matches a finite-difference witness",
                "beta_T13 is explicitly separated from beta_th, beta_core, beta_wave, base covariant Phi, and R_gen",
                "the lane is independent of Landauer identity reuse and contains no source rows, target data, fit, or holdout access",
            ],
            "equation_or_mapping": {
                "functional": branch["functional"],
                "beta_definition": branch["beta_definition"],
                "stiffness_path": branch["stiffness_path"],
                "entropy_identity": branch["entropy_identity"],
                "coefficient_origin": "declared candidate effective-functional coefficient; source-backed physical provenance remains open",
                "legacy_boundary": branch["beta_core_identity"],
            },
            "units": {
                "C": branch["C"],
                "Phi": branch["Phi"],
                "T": branch["T"],
                "beta_T13": branch["beta_T13"],
                "da_Phi_dT": branch["da_Phi_dT"],
                "e0": branch["e0"],
                "free_energy": branch["f"],
                "entropy_density": branch["s"],
            },
            "derivation_class": "declared local finite-temperature effective-functional definition plus analytic derivative and synthetic finite-difference verification",
            "observable": "conditional free-energy and equilibrium entropy-density map only after external e0 and coefficient provenance; no temperature, heat-flux, or TTG prediction",
            "data_role": "INTERNAL_FORMULA_AND_UNIT_CONTRACT_NO_CALIBRATION",
            "evidence_artifacts": [
                {"path": CONTRACT_REL, "sha256": sha256(CONTRACT_REL)},
                {"path": THERMAL_AUDIT_REL, "sha256": sha256(THERMAL_AUDIT_REL)},
                {"path": PARAMETERS_REL, "sha256": sha256(PARAMETERS_REL)},
                {"path": MASTER_REL, "sha256": sha256(MASTER_REL)},
                {"path": FORMULA_REL, "sha256": sha256(FORMULA_REL)},
                {"path": "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"},
            ],
            "verification_status": status,
            "open_blockers": [
                "beta_T13_source_backed_temperature_coefficient_provenance_missing",
                "physical_Phi_field_normalization_and_SI_energy_anchor_missing",
                "beta_T13_correspondence_to_any_core_or_covariant_coefficient_missing",
                "finite_temperature_EOS_transport_SK_KMS_entropy_production_and_dissipative_balance_missing",
                "independent_alpha_Phi_K_calibration_or_derivation_missing",
            ],
            "dependency_unlocked": "none; the lane has an explicit formula/unit contract but no source-backed physical coefficient or full thermodynamic bridge closure",
            "claim_boundary": "The declared beta_T13 is a candidate local response-stiffness slope. It is not a derived UET universal beta, the legacy core beta, an inverse temperature, a transport coefficient, or an externally validated thermodynamic observable.",
        },
        "named_contract": branch,
        "synthetic_derivative_witness": witness,
        "checks": checks,
        "numeric_beta_T13_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "beta_T13_source_backed_temperature_coefficient_provenance_and_physical_Phi_SI_anchor_missing",
        "next_controller": "Source-lock a material-relevant a_Phi(T) coefficient path and e0/Phi observable anchor independently of TTG target fitting; then test finite-temperature EOS, transport, SK/KMS, entropy production, and dissipation under the declared lane boundary.",
        "claim_boundary": "No numerical beta_T13, e0, alpha_Phi_K, Kelvin prediction, entropy-production positivity, transport coefficient, source calibration, target comparison, or Xie 2026 result is emitted by this contract audit.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT.relative_to(ROOT).as_posix(), "failed_checks": [name for name, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
