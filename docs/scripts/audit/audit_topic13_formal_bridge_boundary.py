"""Audit the formal, non-circular boundary of the Topic 13 bridge.

This wave composes already-audited formula and no-go lanes.  It does not
invent a physical coefficient, convert the normalized Phi coordinate into SI,
or consume target/holdout data.  The result closes only the formal boundary
that separates declared interfaces from physical bridge evidence.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_formal_bridge_boundary_audit.json"

INPUTS = {
    "beta_symbol_no_go": "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json",
    "beta_contract": "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json",
    "dimensional_bridge": "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json",
    "energy_response": "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json",
    "phi_e_reference": "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json",
    "phi_energy_no_go": "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json",
    "covariant_normalization_no_go": "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json",
    "eos_contract": "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json",
    "sk_kms_entropy": "docs/core/07_artifacts/topic13/t13_sk_kms_entropy_contract_audit.json",
    "kubo_provenance": "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json",
}


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def major(value: dict[str, Any]) -> dict[str, Any]:
    result = value.get("major_result")
    if not isinstance(result, dict):
        raise ValueError("input artifact has no major_result object")
    return result


def lane_closed(value: dict[str, Any]) -> bool:
    return (
        str(value.get("status", "")).startswith("PASS")
        and major(value).get("closure_level") == "CLOSED_FOR_LANE"
    )


def no_claim_promotion(value: dict[str, Any]) -> bool:
    """Accept explicit top-level or verifier-check no-target evidence."""

    checks = value.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    flags = {
        "parameter_fitting_performed": value.get("parameter_fitting_performed"),
        "target_data_used": value.get("target_data_used"),
        "xie_2026_accessed": value.get("xie_2026_accessed"),
        "target_curve_unused": checks.get("no_target_curve_used"),
        "target_or_holdout_unused": checks.get("no_target_or_holdout"),
        "target_or_holdout_witness_unused": checks.get("no_holdout_or_target_in_witness"),
        "target_not_used": checks.get("target_data_not_used"),
        "prior_no_go_target_unused": checks.get("no_target_or_holdout_in_prior_no_go"),
        "holdout_unused": checks.get("holdout_not_accessed") or checks.get("holdout_not_consumed"),
        "calibration_excludes_holdout": checks.get("calibration_path_excludes_holdout"),
        "xie_unused": checks.get("xie_2026_not_accessed") or checks.get("xie_2026_not_consumed"),
    }
    present = {name: flag for name, flag in flags.items() if flag is not None}
    for name in ("parameter_fitting_performed", "target_data_used", "xie_2026_accessed"):
        if name in present and present[name] is not False:
            return False
    positive_witness = any(
        flag is True
        for name, flag in present.items()
        if name not in {"parameter_fitting_performed", "target_data_used", "xie_2026_accessed"}
    )
    return positive_witness or all(
        present.get(name) is False
        for name in ("parameter_fitting_performed", "target_data_used", "xie_2026_accessed")
    )


def physical_coefficient_not_emitted(value: dict[str, Any]) -> bool:
    """Accept explicit no-coefficient evidence from either schema layer."""

    checks = value.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    flags = {
        "numeric_alpha_Phi_K_emitted": value.get("numeric_alpha_Phi_K_emitted"),
        "numeric_base_alpha_Phi_K_emitted": value.get("numeric_base_alpha_Phi_K_emitted"),
        "numeric_transport_coefficients_emitted": value.get("numeric_transport_coefficients_emitted"),
        "numeric_alpha_not_emitted": checks.get("numeric_alpha_not_emitted")
        or checks.get("no_numeric_alpha_emitted"),
        "base_alpha_not_calibrated": checks.get("no_base_alpha_calibration_emitted"),
        "numeric_transport_not_emitted": checks.get("numeric_transport_coefficient_not_emitted"),
        "no_default_physical_coefficient": checks.get("no_default_physical_coefficient_is_allowed"),
    }
    present = {name: flag for name, flag in flags.items() if flag is not None}
    for name in (
        "numeric_alpha_Phi_K_emitted",
        "numeric_base_alpha_Phi_K_emitted",
        "numeric_transport_coefficients_emitted",
    ):
        if name in present and present[name] is not False:
            return False
    return bool(present)


def evidence(relative: str, value: dict[str, Any]) -> dict[str, Any]:
    result = major(value)
    return {
        "path": relative,
        "sha256": digest(relative),
        "summary": {
            "status": value.get("status"),
            "major_result_id": result.get("major_result_id"),
            "closure_level": result.get("closure_level"),
        },
    }


def main() -> int:
    artifacts = {name: load(relative) for name, relative in INPUTS.items()}
    beta_no_go = artifacts["beta_symbol_no_go"]
    beta_contract = artifacts["beta_contract"]
    dimensional = artifacts["dimensional_bridge"]
    energy = artifacts["energy_response"]
    phi_e_reference = artifacts["phi_e_reference"]
    phi_energy_no_go = artifacts["phi_energy_no_go"]
    covariant_no_go = artifacts["covariant_normalization_no_go"]
    eos = artifacts["eos_contract"]
    sk = artifacts["sk_kms_entropy"]
    kubo = artifacts["kubo_provenance"]

    checks = {
        "beta_symbol_no_go_is_lane_closed": lane_closed(beta_no_go)
        and beta_no_go.get("status") == "PASS_SCOPED_NO_GO_BETA_SYMBOL_IDENTIFICATION",
        "beta_contract_is_lane_closed": lane_closed(beta_contract)
        and beta_contract.get("status") == "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT",
        "conditional_dimensional_formula_is_lane_closed": lane_closed(dimensional),
        "named_energy_response_map_is_lane_closed": lane_closed(energy),
        "named_phi_e_reference_is_lane_closed": lane_closed(phi_e_reference),
        "normalized_phi_energy_no_go_is_lane_closed": lane_closed(phi_energy_no_go),
        "covariant_normalization_no_go_is_lane_closed": lane_closed(covariant_no_go),
        "eos_formula_stability_contract_is_lane_closed": lane_closed(eos),
        "sk_kms_entropy_interface_is_lane_closed": lane_closed(sk),
        "kubo_gate_is_lane_closed_but_physical_value_open": lane_closed(kubo)
        and kubo.get("transport_verification", {}).get("physical_coefficient_evidence") == "BLOCKED_NOT_PROVIDED",
        "landauer_non_derivation_is_explicit": beta_no_go.get("checks", {}).get(
            "core_constraint_gate_forbids_landauer_beta_derivation"
        ) is True
        and beta_contract.get("checks", {}).get("landauer_is_not_used") is True,
        "beta_action_term_is_not_promoted_to_physical_coefficient": (
            "beta_T13_source_backed_temperature_coefficient_provenance_missing"
            in major(beta_contract).get("open_blockers", [])
        ),
        "base_phi_map_remains_separate_from_phi_e": (
            energy.get("checks", {}).get("base_phi_to_named_branch_remains_open") is True
            and phi_e_reference.get("checks", {}).get("base_phi_map_remains_open") is True
        ),
        "normalized_scale_no_go_is_explicit": (
            phi_energy_no_go.get("checks", {}).get("normalized_observable_invariant_under_phi_scale") is True
            and covariant_no_go.get("checks", {}).get("scalar_rescaling_witness_passes") is True
        ),
        "formal_entropy_is_not_physical_transport": (
            sk.get("full_SK_KMS_completion") == "INTERFACE_ONLY_NOT_FULL_MATCH"
            and sk.get("physical_coefficient_evidence") == "BLOCKED_NOT_PROVIDED"
        ),
        "no_input_used_target_or_holdout": all(no_claim_promotion(item) for item in artifacts.values()),
        "no_numeric_base_alpha_emitted": all(
            physical_coefficient_not_emitted(item)
            for item in (beta_no_go, beta_contract, dimensional, energy, phi_e_reference, phi_energy_no_go, covariant_no_go, eos, sk, kubo)
        ),
    }
    status = "PASS_FORMAL_NONCIRCULAR_BRIDGE_BOUNDARY" if all(checks.values()) else "FAIL_FORMAL_BRIDGE_BOUNDARY_AUDIT"

    report = {
        "schema_version": "t13-formal-bridge-boundary-v1",
        "artifact": "t13_formal_bridge_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_FORMAL_NONCIRCULAR_BRIDGE_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the non-Landauer beta boundary: beta_th, beta_core, beta_wave, and the candidate beta_T13 are not interchangeable by symbol alias",
                "the named finite-temperature beta_T13 functional, derivative, and unit contract are formal interfaces rather than source-backed physical coefficients",
                "the named Phi_E bridge Delta_Tq=(e0/c_v)*Phi_E has explicit units and uncertainty boundaries while base Phi remains unmapped",
                "the normalized-lane and covariant-field rescaling no-gos prevent a numeric base alpha_Phi_K from being extracted without an additional dimensional anchor",
                "the normalized collective-response EOS, SK/KMS, entropy-current, and dissipative-balance interfaces are declared with their physical-coefficient boundary",
                "the current evidence cannot promote a formal interface, synthetic witness, or standard comparator into a physical Topic 13 bridge",
            ],
            "equation_or_mapping": {
                "beta_boundary": "beta_th=1/(k_B*T); beta_T13=T0*(da_Phi/dT)|T0; beta_T13 is not beta_th or beta_core",
                "named_energy_bridge": "Phi_E=Delta_u/e0; Delta_Tq=(e0/c_v)*Phi_E",
                "base_observable_boundary": "y_TTG^UET=Delta_Phi(t)/Delta_Phi(0); Delta_Tq=alpha_Phi_K*Delta_Phi",
                "scale_no_go": "Delta_Phi'=s*Delta_Phi; alpha_Phi_K'=alpha_Phi_K/s",
                "formal_eos": "f_hat(C,Phi,T)=a_C*C^2/2+b_C*C^4/4+a_Phi(T)*Phi^2/2+b_Phi*Phi^4/4-g*C^2*Phi/2",
                "formal_sk_kms_entropy": "N(omega)=coth(beta_th*omega/2)*2*Im(D_R); nabla_mu J_S^mu>=0",
            },
            "units": {
                "base_Phi": "dimensionless normalized response; SI scale open",
                "Phi_E": "dimensionless named energy-response coordinate",
                "e0": "J m^-3; open for base Phi",
                "c_v": "J m^-3 K^-1 or source-specific C_src with regime matching open",
                "Delta_Tq": "K",
                "alpha_Phi_K": "K per normalized base Phi; not emitted",
                "beta_T13": "dimensionless local stiffness-temperature slope; source provenance open",
            },
            "derivation_class": "cross-artifact formal interface composition plus scoped algebraic identifiability/no-go audit",
            "observable": "formal response, energy-to-temperature, entropy, and transport interfaces only; no physical Kelvin or heat-flux prediction",
            "data_role": "INTERNAL_FORMAL_BOUNDARY_AUDIT_NO_CALIBRATION",
            "evidence_artifacts": [evidence(relative, artifacts[name]) for name, relative in INPUTS.items()],
            "verification_status": status,
            "open_blockers": [
                "physical_Phi_field_normalization_and_SI_energy_anchor_missing",
                "independent_alpha_Phi_K_calibration_missing",
                "beta_T13_source_backed_temperature_coefficient_provenance_missing",
                "ding_pbte_numeric_C_src_or_independent_reproduction_package_missing",
                "physical_Kubo_coefficient_provenance_missing",
                "finite_temperature_normal_component_not_derived",
                "full_SK_KMS_microscopic_matching_entropy_production_and_dissipative_balance_missing",
                "non_circular_UET_bridge_core_derivation_missing",
            ],
            "dependency_unlocked": "formal Topic 13 boundary only; no Full Topic 13, Core curved 3+1, Gravity, transport, Galaxy, or external-validation unlock",
            "claim_boundary": "The formal bridge boundary is closed as a lane-level result. It does not derive a physical UET beta, identify base Phi with Phi_E, emit alpha_Phi_K, close EOS/transport/KMS/entropy physically, or promote Topic 13.",
        },
        "checks": checks,
        "physical_bridge_status": {
            "beta_T13_source_provenance": "OPEN",
            "base_Phi_SI_anchor": "OPEN",
            "alpha_Phi_K": "OPEN_CALIBRATION",
            "physical_kubo_coefficients": "BLOCKED_NOT_PROVIDED",
            "finite_temperature_normal_component": "BLOCKED",
            "full_SK_KMS_entropy_dissipation": "INTERFACE_ONLY_NOT_FULL_MATCH",
        },
        "numeric_beta_T13_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "numeric_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "physical_Phi_SI_anchor_and_independent_alpha_Phi_K_missing",
        "next_controller": "Acquire or derive a source-locked dimensional response amplitude for base Phi, or an independent paired Phi/SI observable record; then source-lock beta_T13 and one state-matched physical Kubo coefficient before testing full EOS/transport/KMS/entropy closure.",
        "claim_boundary": "No physical temperature prediction, base-alpha calibration, fit, source-row calibration, or Xie 2026 holdout result is produced by this audit.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT.relative_to(ROOT).as_posix(), "failed_checks": [name for name, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
