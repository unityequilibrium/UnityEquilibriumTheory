"""Audit the covariant matter-coupling normalization boundary for Topic 13.

The current covariant response and O(2) matter pilots use natural-unit action
coefficients.  This audit records the field-coordinate transformation of the
reciprocal interaction and proves that the interaction coefficient does not
fix an absolute Phi amplitude without a source-locked physical anchor.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isclose
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MATTER_REL = "docs/core/uet_covariant_matter.py"
RESPONSE_REL = "docs/core/uet_covariant_response.py"
SPEC_REL = "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
MATTER_CONTRACT_REL = "docs/core/artifacts/covariant_matter_action_contract.json"
MATTER_FORMULA_REL = "docs/core/artifacts/covariant_matter_formula_audit.json"
FIELD_NO_GO_REL = "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json"
OUT = ROOT / "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"


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


def response_potential(delta_phi: float, coefficients: dict[str, float]) -> float:
    return float(
        coefficients["equilibrium_density"]
        + 0.5 * coefficients["response_mass_sq"] * delta_phi**2
        + 0.25 * coefficients["response_quartic"] * delta_phi**4
    )


def matter_potential(amplitude_sq: float, coefficients: dict[str, float]) -> float:
    return float(
        0.5 * coefficients["matter_mass_sq"] * amplitude_sq
        + 0.25 * coefficients["matter_quartic"] * amplitude_sq**2
    )


def interaction_energy(
    delta_phi: float,
    amplitude_sq: float,
    epsilon_nc: float,
    response_coupling: float,
) -> float:
    return float(-0.5 * epsilon_nc * response_coupling * delta_phi * amplitude_sq)


def rescale_coefficients(
    coefficients: dict[str, float], field_scale: float
) -> dict[str, float]:
    if field_scale <= 0.0:
        raise ValueError("field scale must be positive")
    return {
        "phi_equilibrium": field_scale * coefficients["phi_equilibrium"],
        "response_kinetic": coefficients["response_kinetic"] / field_scale**2,
        "response_mass_sq": coefficients["response_mass_sq"] / field_scale**2,
        "response_quartic": coefficients["response_quartic"] / field_scale**4,
        "curvature_coupling": coefficients["curvature_coupling"] / field_scale**2,
        "equilibrium_density": coefficients["equilibrium_density"],
        "response_coupling": coefficients["response_coupling"] / field_scale,
        "matter_mass_sq": coefficients["matter_mass_sq"],
        "matter_quartic": coefficients["matter_quartic"],
    }


def coupling_witness() -> dict[str, Any]:
    """Check action and derivative invariance under a response-field rescaling."""

    coefficients = {
        "phi_equilibrium": 0.4,
        "response_kinetic": 1.7,
        "response_mass_sq": 2.3,
        "response_quartic": 0.8,
        "curvature_coupling": 0.12,
        "equilibrium_density": 0.6,
        "response_coupling": 0.8,
        "matter_mass_sq": 0.9,
        "matter_quartic": 1.1,
    }
    epsilon_nc = 0.37
    field_scale = 3.7
    delta_phi = 0.31
    amplitude_sq = 0.2**2 + (-0.35) ** 2
    phi_scale = 1.9
    alpha_base = 2.4
    transformed = rescale_coefficients(coefficients, field_scale)
    transformed_delta = field_scale * delta_phi

    response_base = response_potential(delta_phi, coefficients)
    response_transformed = response_potential(transformed_delta, transformed)
    matter_base = matter_potential(amplitude_sq, coefficients)
    matter_transformed = matter_potential(amplitude_sq, transformed)
    interaction_base = interaction_energy(
        delta_phi,
        amplitude_sq,
        epsilon_nc,
        coefficients["response_coupling"],
    )
    interaction_transformed = interaction_energy(
        transformed_delta,
        amplitude_sq,
        epsilon_nc,
        transformed["response_coupling"],
    )
    response_force = -0.5 * epsilon_nc * coefficients["response_coupling"] * amplitude_sq
    transformed_response_force = (
        -0.5 * epsilon_nc * transformed["response_coupling"] * amplitude_sq
    )
    matter_force = -epsilon_nc * coefficients["response_coupling"] * delta_phi
    transformed_matter_force = (
        -epsilon_nc * transformed["response_coupling"] * transformed_delta
    )
    normalized_phi = delta_phi / phi_scale
    transformed_normalized_phi = transformed_delta / (field_scale * phi_scale)
    base_thermal_response = alpha_base * delta_phi
    transformed_base_alpha = alpha_base / field_scale
    transformed_base_thermal_response = transformed_base_alpha * transformed_delta

    return {
        "field_transformation": "delta_phi_prime = s * delta_phi",
        "coefficient_transformation": {
            "Z_Phi_prime": "Z_Phi / s^2",
            "m_Phi_sq_prime": "m_Phi_sq / s^2",
            "lambda_Phi_prime": "lambda_Phi / s^4",
            "xi_Phi_prime": "xi_Phi / s^2",
            "response_coupling_prime": "response_coupling / s",
            "epsilon_nc_prime": "epsilon_nc",
            "matter_coefficients_prime": "matter coefficients unchanged for fixed matter field chart",
            "Phi_scale_prime": "s * Phi_scale",
            "alpha_base_prime": "alpha_base / s for a raw delta_phi map",
            "normalized_alpha": "unchanged when Phi_scale_prime=s Phi_scale, but its SI origin remains open",
        },
        "deterministic_witness": {
            "s": field_scale,
            "delta_phi": delta_phi,
            "amplitude_sq": amplitude_sq,
            "response_potential": response_base,
            "transformed_response_potential": response_transformed,
            "matter_potential": matter_base,
            "transformed_matter_potential": matter_transformed,
            "interaction_energy": interaction_base,
            "transformed_interaction_energy": interaction_transformed,
            "response_force": response_force,
            "transformed_response_force": transformed_response_force,
            "matter_force": matter_force,
            "transformed_matter_force": transformed_matter_force,
            "normalized_phi": normalized_phi,
            "transformed_normalized_phi": transformed_normalized_phi,
            "base_thermal_response": base_thermal_response,
            "transformed_base_thermal_response": transformed_base_thermal_response,
        },
        "checks": {
            "response_potential_invariant": isclose(
                response_base, response_transformed, rel_tol=0.0, abs_tol=1.0e-14
            ),
            "matter_potential_invariant": isclose(
                matter_base, matter_transformed, rel_tol=0.0, abs_tol=1.0e-14
            ),
            "interaction_energy_invariant": isclose(
                interaction_base,
                interaction_transformed,
                rel_tol=0.0,
                abs_tol=1.0e-14,
            ),
            "response_force_covariant": isclose(
                transformed_response_force,
                response_force / field_scale,
                rel_tol=0.0,
                abs_tol=1.0e-14,
            ),
            "matter_force_invariant": isclose(
                matter_force, transformed_matter_force, rel_tol=0.0, abs_tol=1.0e-14
            ),
            "normalized_coordinate_invariant": isclose(
                normalized_phi,
                transformed_normalized_phi,
                rel_tol=0.0,
                abs_tol=1.0e-14,
            ),
            "raw_dimensional_response_invariant_under_alpha_compensation": isclose(
                base_thermal_response,
                transformed_base_thermal_response,
                rel_tol=0.0,
                abs_tol=1.0e-14,
            ),
        },
    }


def main() -> int:
    matter = text(MATTER_REL)
    response = text(RESPONSE_REL)
    spec = text(SPEC_REL)
    contract = load(MATTER_CONTRACT_REL)
    formula = load(MATTER_FORMULA_REL)
    field_no_go = load(FIELD_NO_GO_REL)
    witness = coupling_witness()

    checks = {
        "matter_interaction_implementation_present": all(
            phrase in matter
            for phrase in (
                "response_config.epsilon_nc",
                "matter_config.response_coupling",
                "interaction_energy_density",
            )
        ),
        "response_coefficients_are_natural_unit_only": all(
            phrase in response
            for phrase in (
                'unit_lane: str = "natural"',
                "Defaults are deterministic research controls, not measured constants.",
            )
        ),
        "matter_coupling_dimension_declared": '"response_coupling": 1' in matter,
        "spec_declares_reciprocal_interaction": all(
            phrase in spec
            for phrase in (
                "epsilon_nc h delta_Phi",
                "E_Phi,coupling = +epsilon_nc h C_amp^2/2",
                "h >= 0",
            )
        ),
        "contract_keeps_physical_map_open": contract.get("normalized_matter_space_map")
        == "PARTIAL_RESPONSE_ONLY",
        "formula_audit_keeps_si_gate_open": "system_specific_SI_map" in formula.get(
            "open_formula_gates", []
        ),
        "prior_field_no_go_passes": field_no_go.get("status")
        == "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION",
        "prior_field_no_go_did_not_use_target": field_no_go.get("target_data_used") is False,
        "coupling_rescaling_witness_passes": all(witness["checks"].values()),
    }
    status = (
        "PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION"
        if all(checks.values())
        else "FAIL_COVARIANT_MATTER_COUPLING_NORMALIZATION_AUDIT"
    )
    report = {
        "schema_version": "t13-covariant-matter-coupling-normalization-no-go-v1",
        "artifact": "t13_covariant_matter_coupling_normalization_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COVARIANT_MATTER_COUPLING_NORMALIZATION_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the reciprocal covariant interaction has an explicit response-field rescaling redundancy",
                "response_coupling_prime = response_coupling / s preserves the interaction when delta_phi_prime = s delta_phi",
                "a nonzero epsilon_nc and a canonical matter-field chart do not identify an absolute Phi amplitude or SI response coefficient",
                "the interaction and response-force relations remain reciprocal under the coordinate reparameterization",
                "the result is an action-coupling extension of the prior scalar field-normalization no-go, not an alpha calibration",
            ],
            "equation_or_mapping": {
                "interaction": "V_int = -epsilon_nc * response_coupling * delta_phi * (chi_1^2 + chi_2^2) / 2",
                "natural_dimensions": "[delta_phi]=[chi_A]=1, [epsilon_nc]=0, [response_coupling]=1, [V_int]=4",
                "field_rescaling": "delta_phi_prime = s delta_phi; response_coupling_prime = response_coupling / s",
                "response_coefficients": "Z_prime=Z/s^2; m_Phi_sq_prime=m_Phi_sq/s^2; lambda_prime=lambda/s^4; xi_prime=xi/s^2",
                "matter_chart": "chi_A and matter kinetic/mass/quartic coefficients held fixed in this witness",
                "thermal_compensation": "alpha_base_prime = alpha_base / s for raw delta_phi; normalized Phi remains invariant only after an external Phi_scale contract",
                "consequence": "the action and normalized/dimensional products are invariant while the absolute base-Phi scale is unanchored",
            },
            "units": {
                "delta_phi": "natural mass dimension 1",
                "chi_A": "natural mass dimension 1",
                "epsilon_nc": "dimensionless natural action parameter",
                "response_coupling": "natural mass dimension 1; no SI contract",
                "interaction_energy_density": "natural mass dimension 4",
                "alpha_Phi_K": "K per normalized Phi; not emitted",
            },
            "derivation_class": "algebraic action-coupling field-redefinition identifiability no-go plus implementation/unit audit",
            "observable": "conditional reciprocal response-matter action interface and normalized thermal-response product",
            "data_role": "INTERNAL_STRUCTURAL_AUDIT_NO_TARGET_OR_HOLDOUT",
            "evidence_artifacts": [
                {"path": MATTER_REL, "sha256": sha256(MATTER_REL)},
                {"path": RESPONSE_REL, "sha256": sha256(RESPONSE_REL)},
                {"path": SPEC_REL, "sha256": sha256(SPEC_REL)},
                {"path": MATTER_CONTRACT_REL, "sha256": sha256(MATTER_CONTRACT_REL)},
                {"path": MATTER_FORMULA_REL, "sha256": sha256(MATTER_FORMULA_REL)},
                {"path": FIELD_NO_GO_REL, "sha256": sha256(FIELD_NO_GO_REL)},
                {"path": "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"},
            ],
            "verification_status": status,
            "open_blockers": [
                "source_locked_physical_field_residue_or_response_amplitude_missing",
                "physical_interaction_coefficient_provenance_and_SI_contract_missing",
                "base_Phi_to_Phi_E_energy_anchor_and_independent_alpha_Phi_K_missing",
                "matter_amplitude_to_density_C_mapping_not_derived",
            ],
            "dependency_unlocked": "none; this closes only an action-coupling identifiability question and does not unlock the SI thermal bridge, Core curved 3+1, Gravity, or transport",
            "claim_boundary": "The no-go is limited to the current natural-unit covariant response/O(2) action and its undeclared thermal mapping. It does not prove that a future source-locked interaction residue, field normalization, or independent alpha calibration cannot be supplied.",
        },
        "coupling_rescaling_witness": witness,
        "checks": checks,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "landauer_used_for_derivation": False,
        "controlling_blocker": "physical_field_normalization_and_interaction_coefficient_provenance_missing",
        "next_controller": "Source-lock a physical response residue or interaction coefficient with canonical matter normalization and an SI energy/observable contract, or provide an independent non-TTG alpha_Phi_K calibration record; then derive base Phi-to-Phi_E without Xie 2026.",
        "claim_boundary": "No numeric field scale, e0, alpha_Phi_K, Kelvin prediction, TTG fit, holdout access, or external validation is produced by this structural audit.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "failed_checks": [key for key, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
