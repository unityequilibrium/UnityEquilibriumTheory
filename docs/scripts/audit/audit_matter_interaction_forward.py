"""Generate the matter-to-interaction forward correspondence artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402
from docs.core.matter_interaction_forward import (  # noqa: E402
    MatterInteractionForwardConfig,
    MatterSource,
    matter_to_interaction_forward,
)
from docs.core.relational_two_body_baseline import (  # noqa: E402
    RelationalBaselineConfig,
    circular_initial_state,
)


def _max_abs_vector_difference(left, right):
    return max(abs(a - b) for a, b in zip(left, right))


def build_artifact() -> dict:
    baseline = RelationalBaselineConfig(steps=0)
    state = circular_initial_state(baseline)
    forward_config = MatterInteractionForwardConfig()
    original_source = MatterSource(mass_a=1.0, mass_b=1.0)
    scaled_source = MatterSource(mass_a=2.0, mass_b=2.0)
    original = matter_to_interaction_forward(state, original_source, forward_config)
    scaled = matter_to_interaction_forward(state, scaled_source, forward_config)

    density_scale_residual = max(
        abs(scaled_value - 2.0 * original_value)
        for original_value, scaled_value in zip(
            original.density, scaled.density
        )
    )
    force_scale_residual = _max_abs_vector_difference(
        scaled.force_on_a,
        tuple(4.0 * value for value in original.force_on_a),
    )
    acceleration_scale_residual = _max_abs_vector_difference(
        scaled.acceleration_on_a,
        tuple(2.0 * value for value in original.acceleration_on_a),
    )
    energy_reconstruction_residual = abs(
        original.interaction_energy - original.interaction_energy_from_coordinate
    )
    gates = {
        "density_integral_matches_original_source_le_1e-6": abs(
            original.density_integral - 2.0
        )
        <= 1e-6,
        "density_integral_matches_scaled_source_le_1e-6": abs(
            scaled.density_integral - 4.0
        )
        <= 1e-6,
        "geometry_only_C_invariant_under_source_rescaling_le_1e-12": abs(
            original.interaction_coordinate - scaled.interaction_coordinate
        )
        <= 1e-12,
        "density_amplitude_scales_linearly_le_1e-12": density_scale_residual
        <= 1e-12,
        "pair_energy_scales_as_mass_product_le_1e-12": abs(
            scaled.interaction_energy / original.interaction_energy - 4.0
        )
        <= 1e-12,
        "force_scales_as_mass_product_le_1e-12": force_scale_residual <= 1e-12,
        "acceleration_A_scales_as_companion_mass_le_1e-12": acceleration_scale_residual
        <= 1e-12,
        "coordinate_reconstructs_standard_energy_le_1e-12": energy_reconstruction_residual
        <= 1e-12,
        "extra_UET_response_remains_blocked": (
            original.extra_uet_response_status
            == "BLOCKED_MISSING_CONSTITUTIVE_LAW"
        ),
    }

    return {
        "schema_version": "1.0",
        "artifact": "matter_interaction_forward_verification",
        "audit_status": (
            "PASS_WITH_UET_EXTENSION_BLOCKED" if all(gates) else "FAIL"
        ),
        "mapping_status": "FORWARD_SOURCE_TO_STANDARD_INTERACTION",
        "claim_status": "SIMULATION_ONLY",
        "evidence_class": "INTERNAL_STANDARD_COMPARATOR",
        "unit_lane": "normalized_comparator",
        "standard_counterpart": (
            "Newtonian two-body potential, force, acceleration, and kernel-smoothed density"
        ),
        "uet_status": "NO_EXTRA_RESPONSE_LAW_IMPLEMENTED",
        "config": {
            "G": baseline.G,
            "separation_reference": baseline.separation_reference,
            "mass_scale_factor": 2.0,
            "density_grid": {
                "grid_min": forward_config.density_lane.grid_min,
                "grid_max": forward_config.density_lane.grid_max,
                "grid_points": len(original.density),
                "kernel_width": forward_config.density_lane.kernel_width,
            },
        },
        "formula_audit": [
            {
                "formula_id": "FORWARD-SOURCE-001",
                "relation": "rho_obs(x)=m_A W_epsilon(x-x_A)+m_B W_epsilon(x-x_B)",
                "variables_and_units": "rho code mass/code length; m code mass; x and epsilon code length",
                "constant_origin": "standard_observable_definition_with_declared_kernel",
                "proof_status": "definition / checked local",
                "verification_role": "independent matter-source observable",
                "failure_mode": "source amplitude or smoothing kernel is hidden",
                "next_hardening_step": "select a dimensional source and instrument map",
            },
            {
                "formula_id": "FORWARD-C-002",
                "relation": "C_AB=-r_ref/r",
                "variables_and_units": "C dimensionless; r_ref and r code length",
                "constant_origin": "declared normalized relational comparator definition",
                "proof_status": "identity / checked local comparator",
                "verification_role": "relational coordinate layer",
                "failure_mode": "C is silently reinterpreted as mass or density",
                "next_hardening_step": "derive a lane-specific constitutive response if needed",
            },
            {
                "formula_id": "FORWARD-INTERACTION-003",
                "relation": "U_N=-(G*m_A*m_B)/r=U_0*C_AB; F_A=-grad U_N; a_A=F_A/m_A",
                "variables_and_units": "normalized code units; masses remain independent source/inertial inputs",
                "constant_origin": "standard_newtonian_comparator_relation",
                "proof_status": "checked local comparator",
                "verification_role": "forward amplitude and response audit",
                "failure_mode": "standard counterpart is presented as a UET derivation",
                "next_hardening_step": "declare and audit an explicit non-Newtonian constitutive term",
            },
        ],
        "metrics": {
            "C_original": original.interaction_coordinate,
            "C_source_rescaled": scaled.interaction_coordinate,
            "C_residual": abs(
                original.interaction_coordinate - scaled.interaction_coordinate
            ),
            "density_integral_original": original.density_integral,
            "density_integral_source_rescaled": scaled.density_integral,
            "density_scale_residual": density_scale_residual,
            "pair_energy_ratio": scaled.interaction_energy
            / original.interaction_energy,
            "force_scale_residual": force_scale_residual,
            "acceleration_scale_residual": acceleration_scale_residual,
            "energy_reconstruction_residual": energy_reconstruction_residual,
            "interpretation": (
                "independent matter source supplies amplitude; geometry supplies C; "
                "the standard interaction supplies force/acceleration"
            ),
        },
        "gates": gates,
        "limitations": [
            "normalized two-body comparator only",
            "density is a synthetic Gaussian-kernel observable definition",
            "no SI conversion, uncertainty, galaxy data, fitting, or holdout",
            "no extra UET constitutive response is implemented",
            "the forward map does not identify an inverse rho=f(C) map",
        ],
    }


def main() -> int:
    artifact = build_artifact()
    output = canonical_artifact_path("matter_interaction_forward_verification.json", "verification")
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
