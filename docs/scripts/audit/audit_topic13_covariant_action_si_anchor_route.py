"""Audit the covariant action route without promoting natural units to SI."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RESPONSE_REL = "docs/core/uet_covariant_response.py"
SPEC_REL = "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
FORMULA_REL = "docs/core/artifacts/covariant_action_formula_audit.json"
NO_GO_REL = "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json"
OUT = ROOT / "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
    response = text(RESPONSE_REL)
    spec = text(SPEC_REL)
    formula = load(FORMULA_REL)
    no_go = load(NO_GO_REL)
    candidate_route_text = response + "\n" + spec
    forbidden_physical_match_markers = (
        "G_N",
        "G_N_SI",
        "Newtonian constant of gravitation",
        "8*pi*G/c^4",
        "8πG/c^4",
    )
    checks = {
        "response_contract_is_natural_units": '"unit_lane": "natural"' in response,
        "response_claim_boundary_says_natural_only": '"natural_units_only"' in response,
        "response_defaults_not_measured": "Defaults are deterministic research controls, not measured constants." in response,
        "response_gravitational_coefficient_default_is_control": "einstein_coupling: float = 1.0" in response,
        "spec_declares_kappa_dimension_only": "`kappa_E` has mass dimension `-2`;" in spec,
        "candidate_route_has_no_newton_coupling_match": not any(
            marker in candidate_route_text for marker in forbidden_physical_match_markers
        ),
        "spec_action_is_natural_units": "In natural units (`c = hbar = 1`)" in spec,
        "spec_requires_later_si_map": "normalized coefficients require an explicit natural-unit and later SI map" in spec,
        "formula_unit_lane_is_natural": formula.get("unit_lane") == "natural",
        "formula_defaults_not_physical": formula.get("coefficient_policy", {}).get("defaults_are_physical_constants") is False,
        "formula_si_gate_open": "system_specific_SI_contract_missing" in formula.get("open_formula_gates", []),
        "phi_anchor_no_go_is_present": no_go.get("status") == "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR",
        "no_numeric_anchor_emitted": no_go.get("witness", {}).get("target_or_holdout_used") is False,
    }
    status = "PASS_NATURAL_UNIT_ROUTE_IDENTIFIED_SI_MAPPING_BLOCKED" if all(checks.values()) else "FAIL_COVARIANT_ACTION_SI_ANCHOR_AUDIT"
    report = {
        "schema_version": "t13-covariant-action-si-anchor-route-audit-v2",
        "artifact": "t13_covariant_action_si_anchor_route_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the covariant response action route is identified as the only current first-principles candidate source for an energy anchor",
                "the implemented parent is explicitly natural-unit only",
                "default response coefficients are research controls and cannot be treated as physical constants",
                "the action gravitational coupling slot is dimension-declared but has no source-backed SI or Newton-coupling match",
                "the system-specific natural-unit-to-SI and covariant-Phi-to-normalized-Phi maps are explicit blockers",
                "the route is separated from the normalized-Phi structural no-go and from material c_v data"
            ],
            "equation_or_mapping": {
                "candidate_action": "S = integral sqrt(-g)[F_epsilon(Phi)(R-2 Lambda)/(2 kappa_E) - epsilon_nc Z_Phi (nabla Phi)^2/2 - epsilon_nc U(Phi)] d^4x + S_m",
                "natural_unit_policy": "c = hbar = 1; action and coefficients remain in natural units",
                "required_bridge": "Phi_normalized = Phi_covariant / Phi_scale; e0 and Phi_scale require a declared SI contract",
                "thermal_bridge": "Delta_Tq = (e0/C_src) * Phi_E only after base Phi-to-Phi_E is derived",
            },
            "coefficient_provenance": {
                "kappa_E": {
                    "natural_unit_dimension": "mass^-2",
                    "numeric_value": None,
                    "status": "DIMENSION_DECLARED_ONLY",
                    "source_locator": SPEC_REL,
                    "si_or_newton_match": "NOT_DECLARED",
                },
                "einstein_coupling_config": {
                    "default_natural_value": 1.0,
                    "status": "RESEARCH_CONTROL_NOT_MEASURED_CONSTANT",
                    "source_locator": RESPONSE_REL,
                },
                "energy_reference_J": None,
                "phi_scale": None,
                "e0_J_per_m3": None,
            },
            "units": {
                "covariant_parent": "natural units; phi mass dimension 1",
                "e0_required": "J m^-3",
                "Phi_normalized": "dimensionless",
                "C_src": "J m^-3 K^-1",
                "alpha_Phi_K": "K per normalized Phi"
            },
            "derivation_class": "source/specification contract audit; no numeric SI conversion",
            "observable": "conditional Phi-to-thermal response route",
            "data_role": "FORMULA_AND_DEPENDENCY_AUDIT_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": RESPONSE_REL, "sha256": sha256(RESPONSE_REL)},
                {"path": SPEC_REL, "sha256": sha256(SPEC_REL)},
                {"path": FORMULA_REL, "sha256": sha256(FORMULA_REL)},
                {"path": NO_GO_REL, "sha256": sha256(NO_GO_REL)},
                {"path": "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "system_specific_SI_contract_missing",
                "covariant_Phi_to_normalized_Phi_map_missing",
                "dimensionful_phi_mass_or_field_scale_missing",
                "temperature_dependent_response_coefficients_and_provenance_missing",
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing"
            ],
            "dependency_unlocked": "none; conditional action route identified, but no SI thermal or Core dependency unlock",
            "claim_boundary": "This result does not convert natural-unit defaults into SI, does not derive e0, and does not identify covariant Phi with normalized Topic 13 Phi."
        },
        "checks": checks,
        "controlling_blocker": "system_specific_SI_contract_and_covariant_Phi_to_normalized_Phi_map_missing",
        "next_controller": "Specify a dimensionful field normalization and coefficient provenance for the covariant parent, then derive the SI action-to-observable map before any numeric e0 or alpha_Phi_K record.",
        "claim_boundary": "Conditional action route only; no numeric e0, alpha_Phi_K, Kelvin prediction, or external validation."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
