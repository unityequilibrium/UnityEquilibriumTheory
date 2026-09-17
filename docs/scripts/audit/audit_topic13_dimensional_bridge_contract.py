"""Audit the conditional Topic 13 dimensional bridge and its open inputs."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_dimensional_bridge import (  # noqa: E402
    ConditionalThermalInputs,
    alpha_phi_k_from_local_equilibrium,
    dimensional_bridge_unit_contract,
    entropy_density_J_per_m3_K,
    free_energy_density_J_per_m3,
    joint_delta_temperature_K,
)


TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json"
DERIVATION = TOPIC / "Data/03_Research/thermal_closure_derivation_audit.json"
INVENTORY = TOPIC / "Data/03_Research/thermal_closure_source_inventory.json"
CALIBRATION = ROOT / "docs/core/07_artifacts/topic13/thermal_dimensional_calibration_contract.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    derivation = load(DERIVATION)
    inventory = load(INVENTORY)
    calibration = load(CALIBRATION)
    unit_contract = dimensional_bridge_unit_contract()
    witness_inputs = ConditionalThermalInputs(
        a_phi_T0=0.2,
        b_phi=1.0,
        phi0=0.5,
        da_phi_dT_per_K=0.01,
        e0_J_per_m3=3.0,
    )
    witness_alpha = alpha_phi_k_from_local_equilibrium(witness_inputs)
    witness_joint = joint_delta_temperature_K(
        witness_inputs,
        delta_phi=0.02,
        delta_c=0.01,
        coupling_g=0.3,
        c0=0.4,
    )
    witness_free_energy = free_energy_density_J_per_m3(0.25, 3.0)
    witness_entropy = entropy_density_J_per_m3_K(3.0, 0.5, 0.02)

    invalid_cases_rejected = True
    for bad_inputs in (
        ConditionalThermalInputs(0.2, 1.0, 0.0, 0.01),
        ConditionalThermalInputs(0.2, 1.0, 0.5, 0.0),
        ConditionalThermalInputs(-1.0, 1.0, 0.5, 0.01),
    ):
        try:
            alpha_phi_k_from_local_equilibrium(bad_inputs)
        except ValueError:
            continue
        invalid_cases_rejected = False

    records = {item.get("id"): item for item in inventory.get("records", [])}
    checks = {
        "conditional_alpha_formula_is_implemented": abs(witness_alpha + 190.0) <= 1.0e-12,
        "joint_response_formula_is_implemented": abs(witness_joint + 3.56) <= 1.0e-12,
        "free_energy_density_unit_path_is_implemented": abs(witness_free_energy - 0.75) <= 1.0e-12,
        "entropy_density_unit_path_is_implemented": abs(witness_entropy + 0.03) <= 1.0e-12,
        "regularity_domain_is_enforced": invalid_cases_rejected,
        "alpha_unit_contract_explicit": unit_contract["alpha_Phi_K"] == "K per normalized Phi",
        "energy_scale_unit_contract_explicit": unit_contract["e0_J_per_m3"] == "J m^-3",
        "entropy_unit_contract_explicit": unit_contract["entropy_density"] == "J m^-3 K^-1",
        "reference_formula_is_recorded": derivation["local_equilibrium_candidate"]["alpha_Phi_K_equilibrium"].startswith("-"),
        "temperature_law_missing_is_explicit": "temperature-dependent coefficient functions" in derivation["conditional_closure"]["required_open_inputs"],
        "energy_scale_missing_is_explicit": "dimensional free-energy-density scale e0" in derivation["conditional_closure"]["required_open_inputs"],
        "cross_lane_comparator_not_promoted": records["pt_011_normalized_a_T_comparator"]["can_define_a_Phi_T"] is False,
        "o2_finite_temperature_not_promoted": records["o2_finite_density_eos"]["can_define_a_Phi_T"] is False,
        "normalized_scale_no_go_preserved": calibration["structural_identifiability"]["status"] == "NON_IDENTIFIABLE_FROM_NORMALIZED_PHI",
        "target_data_not_used": derivation["fit_policy"]["target_data_used_to_choose_a_Phi_prime"] is False,
        "xie_2026_not_consumed": derivation["fit_policy"]["2026_graphite_holdout_consumed"] is False,
        "no_numeric_alpha_emitted": calibration["open_calibration_record"]["temperature_scale_K_per_phi"] is None,
    }
    report = {
        "schema_version": "t13-dimensional-bridge-contract-v1",
        "artifact": "t13_dimensional_bridge_contract_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_CONDITIONAL_FORMULA_OPEN_INPUTS" if all(checks.values()) else "FAIL",
        "major_result": {
            "major_result_id": "T13_ALPHA_PHI_K_CONDITIONAL_DERIVATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "The local-equilibrium alpha_Phi_K formula, regularity domain, and dimensional unit contract are implemented as an explicit conditional bridge.",
            "equation_or_mapping": {
                "free_energy": "f_th(C,Phi,T) = e0 * f_hat(C,Phi; a_Phi(T), ...)",
                "equilibrium": "a_Phi(T0)*Phi0 + b_Phi*Phi0^3 - (g/2)*C0^2 = 0",
                "alpha_conditional": "alpha_Phi_K = -(a_Phi(T0) + 3*b_Phi*Phi0^2) / (a_Phi'(T0)*Phi0)",
                "joint_response": "Delta_Tq = -((a_Phi + 3*b_Phi*Phi0^2)*Delta_Phi - g*C0*Delta_C)/(a_Phi'(T0)*Phi0)",
            },
            "units": unit_contract,
            "derivation_class": "conditional implicit-function derivation with explicit normalized-to-SI unit contract",
            "observable": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "data_role": "symbolic/formula audit; no target, calibration, or holdout data",
            "evidence_artifacts": [
                {"path": "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json"},
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_closure_derivation_audit.json", "sha256": sha256(DERIVATION)},
            ],
            "verification_status": "PASS_CONDITIONAL_FORMULA_OPEN_INPUTS",
            "open_blockers": [
                "a_Phi_T_origin_not_source_locked",
                "dimensional_free_energy_density_scale_e0_missing",
                "equilibrium_phi_reference_and_temperature_branch_missing",
                "independent_alpha_Phi_K_calibration_missing",
            ],
            "dependency_unlocked": "conditional formula/unit lane only; no Kelvin prediction or downstream transport dependency",
            "claim_boundary": "The formula is conditional on new thermal inputs and is not a first-principles UET prediction or numeric calibration.",
        },
        "conditional_inputs": {
            "a_Phi_T": {"status": "OPEN_NOT_SOURCE_LOCKED", "units": "dimensionless coefficient function"},
            "da_Phi_dT": {"status": "OPEN_NOT_SOURCE_LOCKED", "units": "K^-1"},
            "e0": {"status": "OPEN_NOT_SOURCE_LOCKED", "units": "J m^-3"},
            "Phi0": {"status": "OPEN_BRANCH_REFERENCE", "units": "normalized Phi"},
            "b_Phi_and_g": {"status": "NORMALIZED_CANDIDATE_ONLY", "units": "dimensionless in f_hat"},
        },
        "checks": checks,
        "input_identity": {
            "derivation_path": str(DERIVATION.relative_to(ROOT)).replace("\\", "/"),
            "derivation_sha256": sha256(DERIVATION),
            "inventory_path": str(INVENTORY.relative_to(ROOT)).replace("\\", "/"),
            "inventory_sha256": sha256(INVENTORY),
            "calibration_path": str(CALIBRATION.relative_to(ROOT)).replace("\\", "/"),
            "calibration_sha256": sha256(CALIBRATION),
        },
        "witness": {
            "role": "unit and regularity test only; not an external input or fitted alpha",
            "alpha_K_per_normalized_phi": witness_alpha,
            "joint_delta_Tq_K": witness_joint,
            "free_energy_density_J_per_m3": witness_free_energy,
            "entropy_density_J_per_m3_K": witness_entropy,
        },
        "controlling_blocker": "conditional_alpha_inputs_a_Phi_T_e0_and_equilibrium_reference_not_source_locked",
        "next_controller": "source-lock or derive a_Phi(T), da_Phi/dT, e0, and the equilibrium Phi branch independently of TTG target residuals and Xie 2026",
        "claim_boundary": "This closes a conditional formula and unit lane only. It does not close alpha_Phi_K, the dimensional observable map, the thermal bridge, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "controlling_blocker": report["controlling_blocker"], "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0 if report["status"] == "PASS_CONDITIONAL_FORMULA_OPEN_INPUTS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
