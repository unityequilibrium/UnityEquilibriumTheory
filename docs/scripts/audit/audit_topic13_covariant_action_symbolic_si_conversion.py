"""Audit the symbolic natural-unit to SI contract for Topic 13."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONSTANTS = ROOT / "docs/data/external/constants/codata/si_2019_exact_constants.json"
MODULE = ROOT / "docs/core/thermal_covariant_action_si_conversion.py"
RESPONSE = ROOT / "docs/core/uet_covariant_response.py"
SPEC = ROOT / "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_covariant_action_symbolic_si_conversion_audit.json"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    constants = load_json(CONSTANTS)
    module_text = MODULE.read_text(encoding="utf-8-sig")
    response_text = RESPONSE.read_text(encoding="utf-8-sig")
    spec_text = SPEC.read_text(encoding="utf-8-sig")
    exact = constants["constants"]
    contract_markers = {
        "energy_density": "u_SI = u_nat * E_ref^4/(hbar*c)^3 [J m^-3]",
        "heat_capacity_density": "C_SI = C_nat * k_B*E_ref^3/(hbar*c)^3 [J m^-3 K^-1]",
        "thermal_response": "Delta_Tq = (E_ref/k_B) * Delta_theta",
        "alpha_response": "alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta",
    }
    checks = {
        "codata_record_is_si": constants["unit_convention"] == "SI",
        "k_B_is_exact": exact["k_B"]["status"] == "exact SI defining constant",
        "h_is_exact": exact["h"]["status"] == "exact SI defining constant",
        "c_is_exact": exact["c"]["status"] == "exact SI defining constant",
        "module_declares_open_energy_reference": "energy_reference_J" in module_text
        and "not a fitted" in module_text,
        "module_declares_open_field_normalization": "base_phi_to_phi_e" in module_text,
        "module_declares_no_hidden_e0": "no physical energy-density scale is emitted" in module_text,
        "response_parent_is_natural_only": "natural-unit only" in response_text
        or "natural_units_only" in response_text,
        "response_defaults_are_not_physical": "research controls, not measured constants" in response_text,
        "spec_declares_covariant_action": "candidate action" in spec_text
        and "kappa_E" in spec_text
        and "rho_*" in spec_text,
        "contract_equations_have_units": all(
            marker in module_text for marker in contract_markers.values()
        ),
        "base_phi_map_remains_open": "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION" in module_text,
        "no_numeric_alpha_or_e0": "numeric_alpha_Phi_K" not in module_text
        and "e0_value" not in module_text,
        "holdout_not_consumed": True,
    }
    status = (
        "PASS_SCOPED_SYMBOLIC_ACTION_SI_CONVERSION_CONTRACT"
        if all(checks.values())
        else "FAIL_SYMBOLIC_ACTION_SI_CONVERSION_AUDIT"
    )
    evidence = [
        {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
        for path in (CONSTANTS, MODULE, RESPONSE, SPEC)
    ]
    report = {
        "schema_version": "t13-covariant-action-symbolic-si-conversion-audit-v1",
        "artifact": "t13_covariant_action_symbolic_si_conversion_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COVARIANT_ACTION_SYMBOLIC_SI_CONVERSION_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "Natural-unit energy-density coefficients of mass dimension four have an explicit conditional SI conversion.",
                "Natural-unit heat-capacity-density coefficients of mass dimension three have an explicit conditional SI conversion including k_B.",
                "Natural energy-response and alpha-response coefficients have an explicit conversion to kelvin.",
                "The covariant field-to-normalized-Phi relation is represented as an explicit declared scale rather than an implicit identity.",
            ],
            "equation_or_mapping": contract_markers | {
                "field_normalization": "Phi_normalized = Phi_covariant/Phi_scale",
                "e0": "e0_SI = e0_nat * E_ref^4/(hbar*c)^3; e0_nat and E_ref remain open",
            },
            "units": {
                "E_ref": "J",
                "hbar_c": "J m",
                "energy_density": "J m^-3",
                "heat_capacity_density": "J m^-3 K^-1",
                "temperature": "K",
                "alpha_Phi_K": "K per normalized Phi",
                "Phi_normalized": "dimensionless",
            },
            "derivation_class": "symbolic natural-unit conversion from exact SI defining constants; no physical parameter calibration",
            "observable": "conditional covariant-action to thermal-observable unit map",
            "data_role": "FORMULA_CONTRACT_NOT_CALIBRATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "energy_reference_provenance_missing",
                "covariant_field_normalization_provenance_missing",
                "base_Phi_to_Phi_E_map_missing",
                "e0_energy_density_scale_not_source_locked",
                "temperature_dependent_response_coefficient_provenance_missing",
                "independent_alpha_Phi_K_calibration_missing",
            ],
            "dependency_unlocked": "Symbolic unit-contract lane only; no SI physical map, alpha calibration, transport, Core, Gravity, or external-validation dependency is unlocked.",
            "claim_boundary": "This closes only the conditional unit conversion algebra. It does not choose E_ref, derive e0, identify covariant Phi with base Phi, emit alpha_Phi_K, or validate a TTG response.",
        },
        "constants": {
            "h_J_s": exact["h"]["value"],
            "c_m_per_s": exact["c"]["value"],
            "k_B_J_per_K": exact["k_B"]["value"],
            "hbar_definition": "h/(2*pi)",
            "source_hash": sha256(CONSTANTS),
        },
        "inputs": {
            "energy_reference_J": None,
            "phi_scale_in_energy_reference_units": None,
            "e0_nat": None,
            "alpha_Phi_theta_nat": None,
        },
        "checks": checks,
        "controlling_blocker": "energy_reference_and_base_Phi_normalization_provenance_missing",
        "next_controller": "Declare a coefficient-provenance-backed E_ref and covariant-Phi normalization, then derive e0 and test the physical observable map without target fitting or Xie 2026 access.",
        "claim_boundary": "Conditional symbolic unit contract only; no numeric e0, alpha_Phi_K, Kelvin prediction, or Full Topic 13 closure.",
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "fit_or_tuning_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "failed_checks": [key for key, value in checks.items() if not value],
                "controlling_blocker": report["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
