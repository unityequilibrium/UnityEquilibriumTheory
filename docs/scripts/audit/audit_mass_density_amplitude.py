"""Verify the explicit amplitude/source contract for the C-density lane."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402
from docs.core.mass_density_amplitude import (  # noqa: E402
    MassDensityAmplitudeSource,
    amplitude_scaling_residual,
    augmented_density_from_geometry,
    normalized_geometry_density_shape,
)
from docs.core.mass_density_correspondence import (  # noqa: E402
    MassDensityLaneConfig,
    integrated_density,
    max_relative_difference,
)
from docs.core.relational_two_body_baseline import (  # noqa: E402
    RelationalBaselineConfig,
    circular_initial_state,
)


def build_artifact() -> dict:
    baseline = RelationalBaselineConfig(steps=0)
    lane = MassDensityLaneConfig()
    state = circular_initial_state(baseline)
    shape, dx = normalized_geometry_density_shape(state, lane)
    source_a = MassDensityAmplitudeSource(
        amplitude=2.0,
        source_id="synthetic:two_body_total_mass:v1:amplitude-2",
    )
    source_b = MassDensityAmplitudeSource(
        amplitude=4.0,
        source_id="synthetic:two_body_total_mass:v1:amplitude-4",
    )
    density_a, density_dx = augmented_density_from_geometry(state, lane, source_a)
    density_b, density_dx_b = augmented_density_from_geometry(state, lane, source_b)
    integral_a = integrated_density(density_a, density_dx)
    integral_b = integrated_density(density_b, density_dx_b)
    shape_integral = integrated_density(shape, dx)
    normalized_a = [value / integral_a for value in density_a]
    normalized_b = [value / integral_b for value in density_b]
    shape_residual = max_relative_difference(normalized_a, normalized_b)
    gates = {
        "shape_unit_integral_le_1e-12": abs(shape_integral - 1.0) <= 1e-12,
        "amplitude_source_explicit": bool(source_a.source_id and not source_a.fitted),
        "amplitude_unit_declared": source_a.unit_lane == "normalized_code_mass",
        "integral_matches_source_a_le_1e-12": abs(integral_a - source_a.amplitude) <= 1e-12,
        "integral_matches_source_b_le_1e-12": abs(integral_b - source_b.amplitude) <= 1e-12,
        "amplitude_scaling_le_1e-12": amplitude_scaling_residual(density_a, density_b, 2.0) <= 1e-12,
        "shape_not_amplitude": shape_residual <= 1e-12,
        "no_same_data_fit": not source_a.fitted and not source_b.fitted,
        "direct_C_only_remains_blocked": True,
    }
    return {
        "schema_version": "1.0",
        "artifact": "mass_density_amplitude_contract_verification",
        "audit_status": "PASS_WITH_BLOCKED_DIMENSIONAL_MAPPING" if all(gates.values()) else "FAIL",
        "mapping_status": "AUGMENTED_AMPLITUDE_EXPLICIT_SOURCE_NOT_DERIVED",
        "claim_status": "SIMULATION_ONLY",
        "evidence_class": "INTERNAL_CORRESPONDENCE_CONTRACT_DIAGNOSTIC",
        "unit_lane": "normalized_code_mass_per_code_length",
        "standard_counterpart": "kernel-smoothed density with separately declared total-mass amplitude",
        "formula_audit": [
            {
                "formula_id": "RHO-AUGMENTED-003",
                "relation": "rho(x)=A_m*rho_hat(x|geometry,relative_source_state)",
                "variables_and_units": "A_m normalized code mass; rho_hat inverse code length; rho normalized code mass/code length",
                "constant_origin": "explicit_source_contract_plus_standard_kernel_observable",
                "proof_status": "local algebraic and numerical contract check",
                "verification_role": "separate amplitude from collective/relational coordinate",
                "failure_mode": "A_m is fitted on the same target data or silently inferred from C",
                "next_hardening_step": "derive or source-lock a dimensional matter-amplitude contract with uncertainty",
            }
        ],
        "source_contract": {
            "source_id": source_a.source_id,
            "provenance_status": source_a.provenance_status,
            "amplitude_unit_lane": source_a.unit_lane,
            "fit_status": "NOT_FITTED",
            "relative_source_state": "declared equal two-body weights in synthetic lane",
        },
        "config": {
            "grid_min": lane.grid_min,
            "grid_max": lane.grid_max,
            "grid_points": lane.grid_points,
            "kernel_width": lane.kernel_width,
            "amplitude_a": source_a.amplitude,
            "amplitude_b": source_b.amplitude,
        },
        "metrics": {
            "shape_integral": shape_integral,
            "density_integral_a": integral_a,
            "density_integral_b": integral_b,
            "amplitude_ratio": source_b.amplitude / source_a.amplitude,
            "shape_residual_after_amplitude_rescaling": shape_residual,
            "interpretation": "the missing density amplitude is explicit, but is not derived from C in this lane",
        },
        "gates": gates,
        "limitations": [
            "normalized synthetic contract only",
            "A_m is an explicit source input, not a UET derivation",
            "no SI conversion, uncertainty package, galaxy data, fit, or holdout",
            "relative source weights are declared synthetic inputs",
            "direct C-to-rho identity remains blocked",
        ],
        "next_controller": "derive or source-lock dimensional A_m and relative matter-source observables before any galaxy fit",
    }


def main() -> int:
    artifact = build_artifact()
    output = canonical_artifact_path("mass_density_amplitude_contract_verification.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
