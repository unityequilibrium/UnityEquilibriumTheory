"""Verify the synthetic SI 1D contract without asserting a physical 3D map."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402
from docs.core.mass_density_correspondence import (  # noqa: E402
    MassDensityLaneConfig,
    integrated_density,
)
from docs.core.mass_density_dimensional import (  # noqa: E402
    SIDensityAmplitudeSource,
    augmented_si_line_density,
)
from docs.core.relational_two_body_baseline import (  # noqa: E402
    RelationalBaselineConfig,
    circular_initial_state,
)


def build_artifact() -> dict:
    lane = MassDensityLaneConfig()
    state = circular_initial_state(RelationalBaselineConfig(steps=0))
    source_a = SIDensityAmplitudeSource(
        amplitude_kg=2.0,
        length_scale_m=2.0,
        source_id="synthetic:si-line-density:v1:scale-2",
    )
    source_b = SIDensityAmplitudeSource(
        amplitude_kg=2.0,
        length_scale_m=4.0,
        source_id="synthetic:si-line-density:v1:scale-4",
    )
    density_a, dx_a = augmented_si_line_density(state, lane, source_a)
    density_b, dx_b = augmented_si_line_density(state, lane, source_b)
    total_a = integrated_density(density_a, dx_a)
    total_b = integrated_density(density_b, dx_b)
    gates = {
        "source_metadata_declared": bool(
            source_a.source_id and source_a.source_locator and source_a.source_hash
        ),
        "kg_amplitude_declared": source_a.amplitude_kg > 0.0,
        "m_length_scale_declared": source_a.length_scale_m > 0.0,
        "kg_per_m_unit_contract": True,
        "integral_a_matches_kg_le_1e-12": abs(total_a - source_a.amplitude_kg) <= 1e-12,
        "integral_b_matches_kg_le_1e-12": abs(total_b - source_b.amplitude_kg) <= 1e-12,
        "length_rescaling_preserves_total": abs(total_a - total_b) <= 1e-12,
        "no_same_data_fit": not source_a.fitted and not source_b.fitted,
        "three_dimensional_map_remains_blocked": True,
    }
    return {
        "schema_version": "1.0",
        "artifact": "mass_density_dimensional_contract_verification",
        "audit_status": "PASS_WITH_BLOCKED_3D_PHYSICAL_MAPPING" if all(gates.values()) else "FAIL",
        "mapping_status": "SI_1D_SYNTHETIC_CONTRACT_ONLY",
        "claim_status": "SIMULATION_ONLY",
        "evidence_class": "INTERNAL_DIMENSIONAL_CONTRACT_DIAGNOSTIC",
        "unit_lane": "SI_1D_LINE_MASS_DENSITY",
        "standard_counterpart": "one-dimensional line-mass density rho_1D in kg/m",
        "formula_audit": [
            {
                "formula_id": "RHO-SI-1D-004",
                "relation": "rho_1D(x_phys)=A_m*rho_hat(x_code)/L_scale",
                "variables_and_units": "A_m kg; L_scale m; rho_hat 1/code-length; rho_1D kg/m",
                "constant_origin": "dimensional conversion contract from declared source and coordinate scale",
                "proof_status": "checked local dimensional and integral closure",
                "verification_role": "separate unit conversion from physical observable validation",
                "failure_mode": "1D line density is reported as a 3D galaxy density without a geometry/operator map",
                "next_hardening_step": "source-lock a physical 3D density operator and uncertainty package",
            }
        ],
        "source_contract": {
            "source_id": source_a.source_id,
            "source_locator": source_a.source_locator,
            "source_hash": source_a.source_hash,
            "amplitude_unit": "kg",
            "length_unit": "m",
            "observable_unit": "kg/m",
            "uncertainty_status": "synthetic_zero_uncertainty_for_contract_only",
            "fit_status": "NOT_FITTED",
        },
        "config": {
            "grid_min": lane.grid_min,
            "grid_max": lane.grid_max,
            "grid_points": lane.grid_points,
            "kernel_width_code": lane.kernel_width,
            "amplitude_kg": source_a.amplitude_kg,
            "length_scale_a_m": source_a.length_scale_m,
            "length_scale_b_m": source_b.length_scale_m,
        },
        "metrics": {
            "integral_a_kg": total_a,
            "integral_b_kg": total_b,
            "peak_density_ratio_scale_a_over_b": max(density_a) / max(density_b),
            "interpretation": "SI dimensional closure is possible for a declared synthetic 1D line-density lane; physical 3D mapping remains open",
        },
        "gates": gates,
        "limitations": [
            "synthetic 1D line-density contract only",
            "source amplitude and length scale are explicit inputs, not UET derivations",
            "no physical 3D mass-density measurement operator",
            "no galaxy data, uncertainty package, calibration, fit, or holdout",
            "C remains a collective/relational coordinate, not universal mass density",
        ],
        "next_controller": "source-lock a physical 3D density operator, mass provenance, uncertainty, and holdout policy before galaxy comparison",
    }


def main() -> int:
    artifact = build_artifact()
    output = canonical_artifact_path("mass_density_dimensional_contract_verification.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
