"""Close the field-rescaling no-go for the Topic 13 covariant action route.

The audit is structural. It proves that the current natural-unit response
scalar sector has a field-coordinate rescaling freedom, and therefore cannot
identify a numerical covariant-to-normalized field scale, ``e0``, or
``alpha_Phi_K``. It does not rule out a future source-locked normalization.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RESPONSE_REL = "docs/core/02_equations/covariant/uet_covariant_response.py"
SPEC_REL = "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
FORMULA_REL = "docs/core/07_artifacts/correspondence/covariant_action_formula_audit.json"
ACTION_ROUTE_REL = "docs/core/07_artifacts/topic13/t13_covariant_action_si_anchor_route_audit.json"
ENERGY_NO_GO_REL = "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"
ENERGY_BRIDGE_REL = "docs/core/03_lanes/thermal/thermal_energy_response_bridge.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json"


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


def rescale_scalar_sector(coefficients: dict[str, float], scale: float) -> dict[str, float]:
    """Apply ``delta_phi' = scale * delta_phi`` to the declared scalar sector."""

    if scale <= 0.0:
        raise ValueError("field scale must be positive")
    return {
        "phi_equilibrium": scale * coefficients["phi_equilibrium"],
        "response_kinetic": coefficients["response_kinetic"] / scale**2,
        "response_mass_sq": coefficients["response_mass_sq"] / scale**2,
        "response_quartic": coefficients["response_quartic"] / scale**4,
        "curvature_coupling": coefficients["curvature_coupling"] / scale**2,
        "equilibrium_density": coefficients["equilibrium_density"],
    }


def scalar_sector_witness() -> dict[str, Any]:
    """Check the rescaling identities with one deterministic, non-data witness."""

    coefficients = {
        "phi_equilibrium": 0.4,
        "response_kinetic": 1.7,
        "response_mass_sq": 2.3,
        "response_quartic": 0.8,
        "curvature_coupling": 0.12,
        "equilibrium_density": 0.6,
    }
    field_scale = 3.7
    delta_phi = 0.31
    gradient_norm_sq = 0.19
    phi_scale = 1.9
    transformed = rescale_scalar_sector(coefficients, field_scale)

    potential = (
        coefficients["equilibrium_density"]
        + 0.5 * coefficients["response_mass_sq"] * delta_phi**2
        + 0.25 * coefficients["response_quartic"] * delta_phi**4
    )
    transformed_delta = field_scale * delta_phi
    transformed_potential = (
        transformed["equilibrium_density"]
        + 0.5 * transformed["response_mass_sq"] * transformed_delta**2
        + 0.25 * transformed["response_quartic"] * transformed_delta**4
    )
    kinetic = 0.5 * coefficients["response_kinetic"] * gradient_norm_sq
    transformed_kinetic = (
        0.5 * transformed["response_kinetic"] * field_scale**2 * gradient_norm_sq
    )
    curvature_factor_base = coefficients["curvature_coupling"] * delta_phi**2
    transformed_curvature_factor_base = (
        transformed["curvature_coupling"] * transformed_delta**2
    )
    normalized_phi = delta_phi / phi_scale
    transformed_normalized_phi = transformed_delta / (field_scale * phi_scale)

    return {
        "field_transformation": "delta_phi_prime = s * delta_phi",
        "coefficient_transformation": {
            "Z_Phi_prime": "Z_Phi / s^2",
            "m_Phi_sq_prime": "m_Phi_sq / s^2",
            "lambda_Phi_prime": "lambda_Phi / s^4",
            "xi_Phi_prime": "xi_Phi / s^2",
            "rho_star_prime": "rho_star",
            "Phi_scale_prime": "s * Phi_scale",
        },
        "deterministic_witness": {
            "s": field_scale,
            "delta_phi": delta_phi,
            "potential": potential,
            "transformed_potential": transformed_potential,
            "kinetic": kinetic,
            "transformed_kinetic": transformed_kinetic,
            "curvature_factor_base": curvature_factor_base,
            "transformed_curvature_factor_base": transformed_curvature_factor_base,
            "normalized_phi": normalized_phi,
            "transformed_normalized_phi": transformed_normalized_phi,
        },
        "checks": {
            "potential_invariant": isclose(potential, transformed_potential, rel_tol=0.0, abs_tol=1.0e-14),
            "kinetic_invariant": isclose(kinetic, transformed_kinetic, rel_tol=0.0, abs_tol=1.0e-14),
            "curvature_factor_invariant": isclose(curvature_factor_base, transformed_curvature_factor_base, rel_tol=0.0, abs_tol=1.0e-14),
            "normalized_coordinate_invariant": isclose(normalized_phi, transformed_normalized_phi, rel_tol=0.0, abs_tol=1.0e-14),
        },
    }


def main() -> int:
    response = text(RESPONSE_REL)
    spec = text(SPEC_REL)
    formula = load(FORMULA_REL)
    action_route = load(ACTION_ROUTE_REL)
    energy_no_go = load(ENERGY_NO_GO_REL)
    energy_bridge = text(ENERGY_BRIDGE_REL)
    witness = scalar_sector_witness()
    action_open = action_route.get("major_result", {}).get("open_blockers", [])
    checks = {
        "response_is_natural_unit_only": 'unit_lane: str = "natural"' in response,
        "response_defaults_are_not_physical_constants": "Defaults are deterministic research controls, not measured constants." in response,
        "response_scalar_mass_dimension_declared": '"phi": 1' in response,
        "spec_declares_natural_units": "In natural units (`c = hbar = 1`)" in spec,
        "spec_declares_response_coefficients": all(phrase in spec for phrase in ("Z_Phi > 0", "m_Phi^2 >= 0", "lambda_Phi > 0")),
        "formula_audit_keeps_si_contract_open": "system_specific_SI_contract_missing" in formula.get("open_formula_gates", []),
        "prior_action_route_has_missing_covariant_map": "covariant_Phi_to_normalized_Phi_map_missing" in action_open,
        "prior_action_route_has_missing_field_scale": "dimensionful_phi_mass_or_field_scale_missing" in action_open,
        "named_energy_branch_does_not_identify_base_phi": '"base_Phi_to_Phi_E_map": "OPEN_DERIVATION_OR_CALIBRATION"' in energy_bridge,
        "normalized_energy_no_go_is_present": energy_no_go.get("status") == "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR",
        "no_target_or_holdout_in_prior_no_go": energy_no_go.get("witness", {}).get("target_or_holdout_used") is False,
        "scalar_rescaling_witness_passes": all(witness["checks"].values()),
    }
    status = "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION" if all(checks.values()) else "FAIL_COVARIANT_FIELD_NORMALIZATION_IDENTIFIABILITY_AUDIT"
    report = {
        "schema_version": "t13-covariant-field-normalization-identifiability-v1",
        "artifact": "t13_covariant_field_normalization_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COVARIANT_FIELD_NORMALIZATION_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the current covariant response-scalar sector has an explicit continuous field-rescaling redundancy",
                "a proportional covariant-Phi-to-normalized-Phi map remains non-identifiable while the field scale and scalar coefficients are not source-locked",
                "canonicalizing the kinetic coefficient is only a coordinate convention and does not supply a physical field amplitude, SI energy density, e0, or alpha_Phi_K",
                "the result is separated from the normalized-lane no-go, which already rejects extracting alpha from normalized TTG shape data",
                "a future source-locked observable-amplitude or independently calibrated alpha route remains admissible"
            ],
            "equation_or_mapping": {
                "scalar_action_sector": "Z_Phi/2 (nabla delta_phi)^2 + m_Phi^2/2 delta_phi^2 + lambda_Phi/4 delta_phi^4 with F_epsilon-1 = epsilon_nc xi_Phi delta_phi^2",
                "field_rescaling": "delta_phi_prime = s delta_phi",
                "coefficient_rescaling": "Z_prime=Z/s^2; m_Phi_sq_prime=m_Phi_sq/s^2; lambda_prime=lambda/s^4; xi_prime=xi/s^2; rho_star_prime=rho_star",
                "conditional_normalized_map": "Phi_normalized = delta_phi/Phi_scale with Phi_scale_prime=s Phi_scale",
                "consequence": "the action sector and normalized coordinate are invariant, so Phi_scale is not identified by the current natural-unit action alone",
                "thermal_boundary": "Delta_Tq=(e0/C_src) Phi_E requires a separately derived base Phi-to-Phi_E map"
            },
            "units": {
                "delta_phi": "natural mass dimension 1",
                "Phi_normalized": "dimensionless only after an external Phi_scale contract",
                "e0": "J m^-3; not emitted",
                "alpha_Phi_K": "K per normalized Phi; not emitted",
                "coefficient_lane": "natural units only; defaults are not physical constants"
            },
            "derivation_class": "algebraic field-redefinition identifiability no-go plus implementation/specification audit",
            "observable": "conditional covariant scalar to normalized thermal-response interface",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": [
                {"path": RESPONSE_REL, "sha256": sha256(RESPONSE_REL)},
                {"path": SPEC_REL, "sha256": sha256(SPEC_REL)},
                {"path": FORMULA_REL, "sha256": sha256(FORMULA_REL)},
                {"path": ACTION_ROUTE_REL, "sha256": sha256(ACTION_ROUTE_REL)},
                {"path": ENERGY_NO_GO_REL, "sha256": sha256(ENERGY_NO_GO_REL)},
                {"path": ENERGY_BRIDGE_REL, "sha256": sha256(ENERGY_BRIDGE_REL)},
                {"path": "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "declared_covariant_Phi_to_normalized_Phi_map_missing",
                "source_locked_physical_field_residue_or_observable_amplitude_missing",
                "system_specific_SI_coefficient_and_energy_density_contract_missing",
                "temperature_dependent_response_coefficient_provenance_missing",
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing"
            ],
            "dependency_unlocked": "none; this closes a field-coordinate no-go and does not unlock the SI thermal bridge, Core curved 3+1, or Gravity",
            "claim_boundary": "The no-go is limited to the current natural-unit covariant scalar implementation and its undeclared link to normalized Topic 13 Phi. It does not prove that a physical field normalization or independent alpha calibration cannot be supplied in a future, source-locked lane."
        },
        "field_rescaling_witness": witness,
        "checks": checks,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "physical_field_normalization_observable_and_SI_coefficient_provenance_missing",
        "next_controller": "Source-lock a covariant field residue or response-observable amplitude together with a system-specific SI coefficient/energy-density contract, or provide an independent non-TTG alpha_Phi_K calibration record; then derive base Phi-to-Phi_E without using Xie 2026.",
        "claim_boundary": "No numeric field scale, e0, alpha_Phi_K, Kelvin prediction, TTG fit, holdout access, or external validation is produced by this structural audit."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
