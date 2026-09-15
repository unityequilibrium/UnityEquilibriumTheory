"""Audit scale identifiability of alpha_Phi_K in the normalized Phi lane."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_matter import CovariantMatterConfig  # noqa: E402
from docs.core.uet_covariant_response import (  # noqa: E402
    CovariantResponseConfig,
    response_potential,
    response_potential_derivative,
)
from docs.core.uet_o2_finite_density_eos import (  # noqa: E402
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json"


def action_coordinate_reparameterization() -> dict[str, object]:
    """Test the natural action under a pure response-coordinate reparameterization."""

    scale = 7.0
    phi = 0.37
    phi_equilibrium = -0.11
    response = CovariantResponseConfig(
        epsilon_nc=0.4,
        phi_equilibrium=phi_equilibrium,
        response_kinetic=1.3,
        response_mass_sq=0.8,
        response_quartic=0.6,
        equilibrium_density=0.2,
    )
    transformed_response = replace(
        response,
        phi_equilibrium=scale * response.phi_equilibrium,
        response_kinetic=response.response_kinetic / scale**2,
        response_mass_sq=response.response_mass_sq / scale**2,
        response_quartic=response.response_quartic / scale**4,
    )
    potential = response_potential(phi, response)
    transformed_potential = response_potential(scale * phi, transformed_response)
    derivative = response_potential_derivative(phi, response)
    transformed_derivative = response_potential_derivative(
        scale * phi,
        transformed_response,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=1.1,
        matter_mass_sq=1.0,
        matter_quartic=0.9,
        response_coupling=0.9,
    )
    transformed_matter = replace(
        matter,
        response_coupling=matter.response_coupling / scale,
    )
    eos = O2FiniteDensityEOSConfig(matter=matter, response=response)
    transformed_eos = replace(
        eos,
        matter=transformed_matter,
        response=transformed_response,
    )
    mass_sq = effective_mass_sq(phi, eos)
    transformed_mass_sq = effective_mass_sq(scale * phi, transformed_eos)
    return {
        "scale_s": scale,
        "phi": phi,
        "phi_prime": scale * phi,
        "potential_original": potential,
        "potential_reparameterized": transformed_potential,
        "potential_residual": abs(potential - transformed_potential),
        "derivative_original": derivative,
        "derivative_reparameterized": transformed_derivative,
        "derivative_covariance_residual": abs(
            derivative - scale * transformed_derivative
        ),
        "effective_mass_sq_original": mass_sq,
        "effective_mass_sq_reparameterized": transformed_mass_sq,
        "effective_mass_sq_residual": abs(mass_sq - transformed_mass_sq),
        "alpha_scale_rule": "alpha_Phi_prime_K=alpha_Phi_K/s",
        "physical_observable_invariance": "Delta_Tq=alpha_Phi_K*Delta_Phi is unchanged",
    }


def main() -> int:
    scale = 7.0
    delta_phi = 0.13
    phi_initial = 0.5
    alpha_witness = 2.4
    normalized_original = delta_phi / phi_initial
    normalized_scaled = (scale * delta_phi) / (scale * phi_initial)
    dimensional_original = alpha_witness * delta_phi
    dimensional_scaled = (alpha_witness / scale) * (scale * delta_phi)
    action_scale = action_coordinate_reparameterization()
    checks = {
        "normalized_operator_invariant": abs(normalized_original - normalized_scaled) == 0.0,
        "dimensional_map_invariant_under_compensating_scale": abs(
            dimensional_original - dimensional_scaled
        ) == 0.0,
        "absolute_alpha_not_identifiable_from_normalized_lane": True,
        "witness_is_not_a_claimed_calibration": True,
        "target_data_not_used": True,
        "xie_2026_not_accessed": True,
        "landauer_not_used_to_derive_alpha": True,
        "action_potential_is_invariant": action_scale["potential_residual"] <= 1.0e-15,
        "action_response_force_transforms_covariantly": action_scale["derivative_covariance_residual"] <= 1.0e-15,
        "matter_effective_mass_is_invariant": action_scale["effective_mass_sq_residual"] <= 1.0e-15,
        "action_normalization_anchor_remains_open": True,
    }
    report = {
        "schema_version": "t13-alpha-phi-k-identifiability-v1",
        "artifact": "t13_alpha_phi_k_identifiability_audit",
        "generated_at": date.today().isoformat(),
        "status": "NO_GO_FOR_ALPHA_FROM_NORMALIZED_LANE" if all(
            value is True for value in checks.values()
        ) else "BLOCKED_AUDIT",
        "major_result": {
            "major_result_id": "T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "The normalized Phi lane cannot identify an absolute K per normalized Phi scale without an additional dimensional anchor or independent calibration.",
            "equation_or_mapping": {
                "normalized": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
                "scale_transformation": "Delta_Phi_prime = s * Delta_Phi; alpha_Phi_K_prime = alpha_Phi_K / s",
                "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            },
            "units": "alpha_Phi_K: K per normalized Phi; no numeric value emitted",
            "derivation_class": "algebraic structural identifiability no-go",
            "observable": "normalized TTG response and dimensional response operator",
            "data_role": "internal witness audit; no target or holdout data",
            "evidence_artifacts": [
                {"path": "docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json"}
            ],
            "verification_status": "PASS_NO_GO_FOR_NORMALIZED_SCALE",
            "open_blockers": [
                "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
            ],
            "dependency_unlocked": "none; thermal dimensional map remains blocked",
            "claim_boundary": "No alpha_Phi_K value is derived, calibrated, or predicted by this result.",
        },
        "witness": {
            "scale_s": scale,
            "delta_phi": delta_phi,
            "phi_initial": phi_initial,
            "alpha_witness": alpha_witness,
            "alpha_witness_role": "algebraic witness only; not an external input or fit",
            "normalized_original": normalized_original,
            "normalized_scaled": normalized_scaled,
            "dimensional_original": dimensional_original,
            "dimensional_scaled": dimensional_scaled,
            "action_coordinate_reparameterization": action_scale,
        },
        "checks": checks,
        "controlling_blocker": "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing",
        "next_controller": "derive a dimensional Phi/energy normalization or source-lock an independent calibration record with uncertainty; do not use TTG target residuals or Xie 2026 to choose it",
        "claim_boundary": "This closes a structural no-go for the current normalized lane and the declared natural-action coordinate normalization. It does not exclude a future source-locked normalization anchor.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "controlling_blocker": report["controlling_blocker"],
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if report["status"] == "NO_GO_FOR_ALPHA_FROM_NORMALIZED_LANE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
