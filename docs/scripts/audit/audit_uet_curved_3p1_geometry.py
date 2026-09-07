"""Audit periodic metric-to-Ricci and momentum-divergence operators."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from math import log2, pi
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_constraints import (
    ADMMatterProjection,
    evaluate_adm_constraints,
)
from docs.core.uet_curved_3p1_geometry import (
    adm_geometry_from_periodic_grid,
    compute_periodic_momentum_tensor_divergence,
    compute_periodic_spatial_geometry,
    curved_3p1_geometry_operator_contract,
    periodic_central_derivative,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE = ROOT / "docs/data/external/gr_3p1/gourgoulhon_2007/source_record.json"
MODULE = ROOT / "docs/core/uet_curved_3p1_geometry.py"
AUDIT_SCRIPT = Path(__file__).resolve()
VERIFY = ARTIFACTS / "curved_3p1_geometry_operator_verification.json"
FORMULA = ARTIFACTS / "curved_3p1_geometry_operator_formula_audit.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _l2(error: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(error))))


def _orders(errors: list[float]) -> list[float]:
    return [log2(errors[index] / errors[index + 1]) for index in range(len(errors) - 1)]


def _flat_metric(resolution: int) -> np.ndarray:
    return np.broadcast_to(
        np.eye(3), (resolution, resolution, resolution, 3, 3)
    ).copy()


def _conformal_control(
    resolution: int,
    *,
    amplitude: float,
) -> tuple[np.ndarray, np.ndarray]:
    length = 2.0 * pi
    x = np.arange(resolution, dtype=float) * length / resolution
    x_grid = x[:, None, None]
    psi = np.broadcast_to(
        1.0 + amplitude * np.cos(x_grid),
        (resolution, resolution, resolution),
    )
    metric = psi[..., None, None] ** 4 * np.eye(3)
    analytic_ricci_scalar = np.broadcast_to(
        8.0 * amplitude * np.cos(x_grid) / psi**5,
        psi.shape,
    )
    return metric, analytic_ricci_scalar


def _momentum_control(
    resolution: int,
    *,
    amplitude: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    length = 2.0 * pi
    x = np.arange(resolution, dtype=float) * length / resolution
    x_grid = x[:, None, None]
    metric = _flat_metric(resolution)
    curvature = np.zeros_like(metric)
    curvature[..., 0, 1] = amplitude * np.sin(x_grid)
    curvature[..., 1, 0] = amplitude * np.sin(x_grid)
    analytic = np.zeros(metric.shape[:3] + (3,), dtype=float)
    analytic[..., 1] = amplitude * np.cos(x_grid)
    return metric, curvature, analytic


def build_artifacts() -> tuple[dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract = curved_3p1_geometry_operator_contract()
    resolutions = [12, 24, 48]
    length = 2.0 * pi
    conformal_amplitude = 0.05
    momentum_amplitude = 0.1

    flat = compute_periodic_spatial_geometry(
        _flat_metric(8),
        (length / 8.0,) * 3,
    )

    ricci_errors: list[float] = []
    divergence_errors: list[float] = []
    compatibility_residuals: list[float] = []
    antisymmetry_residuals: list[float] = []
    for resolution in resolutions:
        spacing = (length / resolution,) * 3
        metric, analytic_ricci = _conformal_control(
            resolution,
            amplitude=conformal_amplitude,
        )
        geometry = compute_periodic_spatial_geometry(metric, spacing)
        ricci_errors.append(_l2(geometry.ricci_scalar - analytic_ricci))
        compatibility_residuals.append(
            geometry.max_abs_metric_compatibility_residual
        )
        antisymmetry_residuals.append(geometry.max_abs_ricci_antisymmetry)

        flat_metric, curvature, analytic_divergence = _momentum_control(
            resolution,
            amplitude=momentum_amplitude,
        )
        divergence = compute_periodic_momentum_tensor_divergence(
            flat_metric,
            curvature,
            spacing,
        )
        divergence_errors.append(_l2(divergence - analytic_divergence))

    ricci_orders = _orders(ricci_errors)
    divergence_orders = _orders(divergence_errors)

    integration_resolution = 16
    integration_spacing = (length / integration_resolution,) * 3
    integration_metric, _ = _conformal_control(
        integration_resolution,
        amplitude=conformal_amplitude,
    )
    integration_curvature = np.zeros_like(integration_metric)
    adm_geometry, integration_geometry = adm_geometry_from_periodic_grid(
        lapse=1.0,
        shift=np.zeros(integration_metric.shape[:3] + (3,)),
        spatial_metric=integration_metric,
        extrinsic_curvature=integration_curvature,
        spacing=integration_spacing,
    )
    matched_matter = ADMMatterProjection(
        energy_density=integration_geometry.ricci_scalar / (16.0 * pi),
        momentum_density=np.zeros(integration_metric.shape[:3] + (3,)),
    )
    matched_constraints = evaluate_adm_constraints(adm_geometry, matched_matter)
    mismatched_constraints = evaluate_adm_constraints(
        adm_geometry,
        ADMMatterProjection(
            energy_density=1.1 * matched_matter.energy_density,
            momentum_density=matched_matter.momentum_density,
        ),
    )

    invalid_spacing_rejected = False
    try:
        periodic_central_derivative(np.zeros((5, 5, 5)), axis=0, spacing=0.0)
    except ValueError:
        invalid_spacing_rejected = True

    thresholds = {
        "flat_max_abs_ricci_scalar": 1e-14,
        "metric_compatibility_max_abs": 1e-12,
        "ricci_antisymmetry_max_abs": 1e-12,
        "minimum_observed_spatial_order": 1.8,
        "finest_ricci_l2_error": 2e-3,
        "finest_momentum_divergence_l2_error": 1.5e-4,
        "matched_adm_constraint_max_abs": 1e-12,
        "negative_control_min_abs": 1e-4,
    }
    metrics = {
        "flat_max_abs_christoffel": float(
            np.max(np.abs(flat.christoffel_symbols))
        ),
        "flat_max_abs_ricci_scalar": float(np.max(np.abs(flat.ricci_scalar))),
        "ricci_l2_errors": ricci_errors,
        "ricci_observed_orders": ricci_orders,
        "momentum_divergence_l2_errors": divergence_errors,
        "momentum_divergence_observed_orders": divergence_orders,
        "max_metric_compatibility_residual": max(compatibility_residuals),
        "max_ricci_antisymmetry": max(antisymmetry_residuals),
        "matched_adm_hamiltonian_residual": matched_constraints.max_abs_hamiltonian_residual,
        "matched_adm_momentum_residual": matched_constraints.max_abs_momentum_residual,
        "mismatched_density_hamiltonian_residual": mismatched_constraints.max_abs_hamiltonian_residual,
    }
    checks = {
        "source_identity_locked": source.get("arxiv_id") == "gr-qc/0703035",
        "flat_connection_exact_zero": metrics["flat_max_abs_christoffel"] == 0.0,
        "flat_ricci_exact_zero": metrics["flat_max_abs_ricci_scalar"] <= thresholds["flat_max_abs_ricci_scalar"],
        "metric_compatibility": metrics["max_metric_compatibility_residual"] <= thresholds["metric_compatibility_max_abs"],
        "ricci_symmetry": metrics["max_ricci_antisymmetry"] <= thresholds["ricci_antisymmetry_max_abs"],
        "ricci_spatial_convergence": min(ricci_orders) >= thresholds["minimum_observed_spatial_order"],
        "momentum_divergence_spatial_convergence": min(divergence_orders) >= thresholds["minimum_observed_spatial_order"],
        "ricci_finest_error": ricci_errors[-1] <= thresholds["finest_ricci_l2_error"],
        "momentum_divergence_finest_error": divergence_errors[-1] <= thresholds["finest_momentum_divergence_l2_error"],
        "adm_adapter_constraint_match": max(
            matched_constraints.max_abs_hamiltonian_residual,
            matched_constraints.max_abs_momentum_residual,
        ) <= thresholds["matched_adm_constraint_max_abs"],
        "matter_negative_control_detected": mismatched_constraints.max_abs_hamiltonian_residual > thresholds["negative_control_min_abs"],
        "invalid_spacing_rejected": invalid_spacing_rejected,
        "no_clipping_or_fitting": not flat.diagnostics["field_clipping"] and not flat.diagnostics["parameter_fitting"],
        "metric_is_not_phi": contract["ontology"]["gamma_ij"] == "standard spatial metric; not Phi",
        "trace_and_observer_excluded": contract["ontology"]["R_gen"] == "excluded derived history trace" and contract["ontology"]["R_obs"] == "excluded observer record",
        "metric_evolution_not_claimed": "spatial-metric and extrinsic-curvature evolution" in contract["not_implemented"],
    }
    passed = all(checks.values())

    verification = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_geometry_operator_verification",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "periodic-geometry-operator-v1",
        "benchmark_role": "internal analytic and convergence gate",
        "method_label": "second-order periodic Levi-Civita/Ricci/divergence operators",
        "status": "PASS_CURVED_3P1_GEOMETRY_OPERATOR" if passed else "FAIL",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GEOMETRY_OPERATOR_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "periodic-grid metric-to-Levi-Civita connection",
                "periodic-grid metric-to-spatial-Ricci tensor and scalar",
                "periodic-grid covariant ADM momentum-tensor divergence",
                "second-order spatial convergence on independent analytic controls",
                "adapter into the existing ADM constraint evaluator",
            ] if passed else [],
            "equation_or_mapping": contract["relations"],
            "units": {
                "coordinates_and_spacing": "L",
                "gamma_ij": "dimensionless in the declared geometric chart lane",
                "Gamma^k_ij": "L^-1",
                "R_ij_and_R3": "L^-2",
                "K_ij": "L^-1",
                "D_j_B^j_i": "L^-2",
            },
            "derivation_class": "standard differential geometry with second-order numerical approximation",
            "observable": "spatial curvature and constraint-input diagnostics; no detector observable",
            "data_role": "analytic manufactured controls; no fitted or holdout data",
            "verification_status": "PASS_CURVED_3P1_GEOMETRY_OPERATOR" if passed else "FAIL",
            "open_blockers": contract["not_implemented"],
            "dependency_unlocked": "lapse/shift and metric/K evolution research wave only; Gravity remains blocked",
            "claim_boundary": contract["claim_boundary"],
        },
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": _sha256(SOURCE),
            "identity": source,
        },
        "source_hashes": {
            MODULE.relative_to(ROOT).as_posix(): _sha256(MODULE),
            AUDIT_SCRIPT.relative_to(ROOT).as_posix(): _sha256(AUDIT_SCRIPT),
            SOURCE.relative_to(ROOT).as_posix(): _sha256(SOURCE),
        },
        "input_identity": {
            "module": "docs/core/uet_curved_3p1_geometry.py",
            "source_record": SOURCE.relative_to(ROOT).as_posix(),
            "analytic_controls": [
                "periodic Cartesian flat metric",
                "gamma_ij = psi^4 delta_ij with psi = 1 + 0.05 cos(x)",
                "flat-metric K_xy = 0.1 sin(x) momentum-divergence control",
            ],
            "negative_controls": [
                "10 percent ADM matter-density mismatch",
                "non-positive grid spacing",
            ],
        },
        "config": {
            "domain": "[0, 2*pi)^3",
            "resolutions": resolutions,
            "boundary_condition": "periodic_all_axes",
            "spatial_stencil": "second_order_centered",
            "conformal_amplitude": conformal_amplitude,
            "momentum_amplitude": momentum_amplitude,
            "parameter_fitting": False,
            "field_clipping": False,
        },
        "thresholds": thresholds,
        "metrics": metrics,
        "checks": checks,
        "contract": contract,
        "notes": [
            "Analytic controls are independent of the finite-difference implementation.",
            "The ADM adapter match is a wiring check, not independent physical validation.",
            "Periodic single-chart geometry does not establish boundary treatment, evolution well-posedness, or Gravity compatibility.",
            "No C-to-mass, Phi-to-metric, Pi-to-K, R_gen-to-state, fitting, clipping, or holdout use is introduced.",
        ],
        "claim_promotion": False,
    }

    formula = {
        "schema_version": "1.0",
        "artifact": "curved_3p1_geometry_operator_formula_audit",
        "generated_at": now,
        "topic": "docs/core curved 3+1 parent",
        "version": "periodic-geometry-operator-v1",
        "benchmark_role": "formula and unit audit",
        "method_label": verification["method_label"],
        "status": "PASS_NUMERICAL_GEOMETRY_FORMULAS" if passed else "FAIL",
        "relations": [
            {
                "formula_id": "UET-CURVED3P1-CHRISTOFFEL-003",
                "relation": contract["relations"]["christoffel"],
                "variables": {"gamma_ij": "spatial metric", "Gamma^k_ij": "Levi-Civita connection", "d_i": "periodic centered coordinate derivative"},
                "units": {"gamma_ij": "dimensionless chart component", "d_i": "L^-1", "Gamma^k_ij": "L^-1"},
                "conversion_steps": "none in geometric chart lane; spacing is supplied in L",
                "constant_origin": {"1/2": "exact Levi-Civita identity"},
                "derivation_class": "standard identity plus numerical approximation",
                "unit_lane": "geometric periodic Cartesian chart",
                "unit_closure": "L^-1 on both sides",
                "proof_status": "flat exact-zero and metric-compatibility controls pass",
                "verification_role": "formal/numerical prerequisite",
                "failure_mode": "index placement or derivative error corrupts every curvature and divergence result",
                "next_hardening_step": "add non-periodic boundary/multiple-chart implementation only after evolution requirements are defined",
                "code_path": "docs/core/uet_curved_3p1_geometry.py",
            },
            {
                "formula_id": "UET-CURVED3P1-RICCI-004",
                "relation": contract["relations"]["ricci_tensor"] + "; " + contract["relations"]["ricci_scalar"],
                "variables": {"R_ij": "spatial Ricci tensor", "R3": "spatial Ricci scalar", "Gamma": "Levi-Civita connection", "gamma^ij": "inverse spatial metric"},
                "units": {"R_ij": "L^-2", "R3": "L^-2", "Gamma": "L^-1"},
                "conversion_steps": "none in geometric chart lane",
                "constant_origin": "no fitted constants",
                "derivation_class": "standard identity plus second-order finite differences",
                "unit_lane": "geometric periodic Cartesian chart",
                "unit_closure": "L^-2 on every term",
                "proof_status": "conformally-flat analytic control converges at observed order >= 1.8",
                "verification_role": "spatial convergence gate",
                "failure_mode": "incorrect Ricci curvature invalidates the Hamiltonian constraint input",
                "next_hardening_step": "couple to gauge-declared metric/K evolution and test constraint propagation",
                "code_path": "docs/core/uet_curved_3p1_geometry.py",
            },
            {
                "formula_id": "UET-CURVED3P1-MOMENTUM-DIVERGENCE-005",
                "relation": contract["relations"]["momentum_tensor"] + "; " + contract["relations"]["momentum_divergence"],
                "variables": {"B^j_i": "mixed ADM momentum tensor", "K^j_i": "mixed extrinsic curvature", "K": "trace of K_ij", "D_j": "spatial covariant derivative"},
                "units": {"K_ij": "L^-1", "B^j_i": "L^-1", "D_j_B^j_i": "L^-2"},
                "conversion_steps": "raise the first K index with gamma^jk before differentiation",
                "constant_origin": "Kronecker delta identity; no fitted constants",
                "derivation_class": "standard tensor identity plus second-order finite differences",
                "unit_lane": "geometric periodic Cartesian chart",
                "unit_closure": "L^-2 on both sides",
                "proof_status": "manufactured off-diagonal K control converges at observed order >= 1.8",
                "verification_role": "spatial convergence and ADM-input gate",
                "failure_mode": "connection sign/index drift produces a false momentum-constraint residual",
                "next_hardening_step": "test propagation under a declared strongly-hyperbolic evolution system",
                "code_path": "docs/core/uet_curved_3p1_geometry.py",
            },
        ],
        "source": verification["source"],
        "thresholds": thresholds,
        "metrics": metrics,
        "open_items": contract["not_implemented"],
        "claim_ceiling": contract["claim_boundary"],
    }
    return verification, formula


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula = build_artifacts()
    VERIFY.write_text(
        json.dumps(verification, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    FORMULA.write_text(
        json.dumps(formula, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": verification["status"],
                "ricci_orders": verification["metrics"]["ricci_observed_orders"],
                "momentum_divergence_orders": verification["metrics"]["momentum_divergence_observed_orders"],
                "claim_promotion": verification["claim_promotion"],
            },
            indent=2,
        )
    )
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
