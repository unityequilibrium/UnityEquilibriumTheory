"""Verify the Wave 5 fixed-background first-order hyperbolic control spine."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_theory_spine import (
    Covariant3p1State, TheorySpineConfig, characteristic_analysis,
    recommended_max_dt, theory_spine_contract, theory_spine_step,
)

ARTIFACTS = ROOT / "docs/core/artifacts"
CURVED_PARENT_GATE = ARTIFACTS / "core_curved_3p1_parent_gate.json"


def _config(damping: bool = True) -> TheorySpineConfig:
    return TheorySpineConfig(
        matter_speed=0.7, response_speed=0.5,
        matter_damping=0.1 if damping else 0.0,
        response_damping=0.2 if damping else 0.0,
        stability_safety=0.4, boundary_condition="periodic", unit_lane="natural",
        background_mode="minkowski_1p1_fixed",
        parameter_provenance="internal://wave5-preregistered-control",
    )


def _wave_state(cells: int, config: TheorySpineConfig) -> tuple[np.ndarray, float, Covariant3p1State]:
    x = np.linspace(0.0, 2.0 * np.pi, cells, endpoint=False)
    dx = float(x[1] - x[0])
    field = np.sin(x)
    gradient = (np.roll(field, -1) - np.roll(field, 1)) / (2.0 * dx)
    zero = np.zeros(cells)
    return x, dx, Covariant3p1State(field, zero, gradient, zero, zero, zero, np.diag([-1.0, 1.0]))


def _temporal_error(dt: float, final_time: float = 0.1) -> float:
    config = _config(damping=False)
    x, dx, state = _wave_state(256, config)
    steps = int(round(final_time / dt))
    for _ in range(steps):
        state = theory_spine_step(state, dt, dx, config).physical_state
    k_eff = np.sin(dx) / dx
    omega = config.matter_speed * k_eff
    exact = np.sin(x) * np.cos(omega * final_time)
    return float(np.linalg.norm(state.matter_coordinate - exact) / np.sqrt(x.size))


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    curved_parent = json.loads(CURVED_PARENT_GATE.read_text(encoding="utf-8"))
    curved_requirements = curved_parent.get("requirements", {})
    config = _config()
    characteristic = characteristic_analysis(config)
    _, dx, state = _wave_state(128, config)
    dt = 0.1 * recommended_max_dt(dx, config)
    result = theory_spine_step(state, dt, dx, config)
    errors = [_temporal_error(step) for step in (0.01, 0.005, 0.0025)]
    orders = [float(np.log(errors[i] / errors[i + 1]) / np.log(2.0)) for i in range(2)]
    metrics = {
        "maximum_characteristic_speed": characteristic["maximum_characteristic_speed"],
        "maximum_eigenvector_condition_number": max(item["eigenvector_condition_number"] for item in characteristic["sectors"].values()),
        "matter_gradient_constraint_max_abs": result.constraints.matter_gradient_constraint_max_abs,
        "response_gradient_constraint_max_abs": result.constraints.response_gradient_constraint_max_abs,
        "temporal_errors": errors, "temporal_orders": orders,
        "minimum_temporal_order": min(orders),
        "generated_trace": result.generated_trace,
        "one_step_balance_residual": abs(result.entropy_ledger["one_step_balance_residual"]),
    }
    thresholds = {"identity": 1e-10, "causal_speed": 1.0 + 1e-10, "constraint": 1e-10, "convergence_order": 1.5}
    checks = {
        "strong_hyperbolicity": characteristic["status"] == "PASS_STRONG_HYPERBOLIC_LINEAR_CONTROL",
        "subluminal_characteristics": metrics["maximum_characteristic_speed"] <= thresholds["causal_speed"],
        "matter_constraint": metrics["matter_gradient_constraint_max_abs"] <= thresholds["constraint"],
        "response_constraint": metrics["response_gradient_constraint_max_abs"] <= thresholds["constraint"],
        "temporal_convergence": metrics["minimum_temporal_order"] >= thresholds["convergence_order"],
        "no_clipping": result.diagnostics["field_clipping"] is False,
        "fixed_background_disclosed": result.diagnostics["curved_3p1"] is False,
        "curved_claim_blocked": theory_spine_contract()["curved_3p1"] == "BLOCKED",
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "covariant_theory_spine_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "INTERNAL_MINKOWSKI_1P1_HYPERBOLIC_CONTROL_ONLY",
        "operator_mode": "covariant_theory_spine_v1", "unit_lane": "natural",
        "metrics": metrics, "thresholds": thresholds, "checks": checks,
        "characteristic_analysis": characteristic, "contract": theory_spine_contract(),
        "claim_boundary": "first-order fixed-Minkowski 1+1 control; not curved 3+1, dynamical metric, or GR numerical validation",
    }
    formula = {
        "schema_version": "1.0", "artifact": "covariant_theory_spine_formula_audit",
        "generated_at": now, "status": "WARN",
        "relations": [
            {"formula_id": "UET-SPINE-FIRST-ORDER-001", "relation": "d_t phi=pi; d_t pi=c^2 d_x psi-gamma pi+J; d_t psi=d_x pi", "derivation_class": "first-order reduction of damped wave control", "unit_lane": "natural", "proof_status": "linear characteristic and convergence gates pass", "code_path": "docs/core/uet_covariant_theory_spine.py"},
            {"formula_id": "UET-SPINE-CONSTRAINT-002", "relation": "C_psi=psi-d_x phi", "derivation_class": "first-order auxiliary constraint", "unit_lane": "natural", "proof_status": "periodic one-step preservation gate", "code_path": "docs/core/uet_covariant_theory_spine.py"},
        ],
        "open_items": ["gauge-declared lapse/shift evolution", "dynamical spatial metric and extrinsic curvature", "strong-hyperbolicity proof for the curved evolution system", "constraint propagation/damping", "temporal convergence", "non-periodic curved boundary conditions", "parent-action coefficient matching"],
        "claim_ceiling": "Minkowski 1+1 strongly-hyperbolic numerical control",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave5_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "theory_spine_status": "PASS_MINKOWSKI_1P1_CONTROL_CURVED_BLOCKED" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_wave4_gate.json", "checks": checks,
        "controlling_blocker": curved_parent.get("controlling_blocker") if passed else "linear_hyperbolic_control_failure",
        "claim_promotion": False,
        "curved_3p1_companion_progress": {
            "parent_gate": "core_curved_3p1_parent_gate.json",
            "parent_status": curved_parent.get("status"),
            "parent_closure_level": curved_parent.get("major_result", {}).get("closure_level"),
            "adm_constraint_interface": curved_requirements.get("adm_constraint_interface"),
            "metric_to_ricci_operator": curved_requirements.get("metric_to_ricci_operator"),
            "spatial_geometry_convergence": curved_requirements.get("spatial_geometry_convergence"),
            "metric_and_extrinsic_curvature_evolution": curved_requirements.get("metric_and_extrinsic_curvature_evolution"),
            "constraint_propagation": curved_requirements.get("constraint_propagation"),
            "claim_boundary": curved_parent.get("major_result", {}).get("claim_boundary"),
        },
        "parallel_next_controller": "implement a gauge-declared curved metric/K evolution branch while preserving the fixed-Minkowski spine as a baseline",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_theory_spine_addendum",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json", "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.hyperbolic_spine_control", "version": "minkowski-1p1-spine-v1",
            "classification": "numerical_implementation", "relation_or_code_path": "docs/core/uet_covariant_theory_spine.py",
            "variables": {"phi": "sector coordinate", "pi": "time derivative", "psi": "declared spatial derivative", "c": "characteristic speed"},
            "mathematical_role": "first-order strongly-hyperbolic fixed-background control",
            "standard_physics_counterpart": "first-order reduction of damped relativistic wave/telegraph sectors",
            "observable_mapping": {"status": "OPEN", "reason": "fixed-background control has no dimensional detector map"},
            "unit_lane": "natural_only_v1", "parameter_dimensions": "natural-unit control parameters",
            "source_or_origin": "UET Main-Theory Wave 5 numerical control",
            "assumptions": ["fixed Minkowski 1+1", "periodic boundary", "linear principal part", "subluminal declared speeds"],
            "symmetry_and_conservation": "periodic gradient constraint and damped energy ledger; no GR constraints",
            "limiting_cases": ["zero damping gives wave control", "zero fields are exact fixed point"],
            "implementation_paths": ["docs/core/uet_covariant_theory_spine.py"],
            "verifier_paths": ["docs/scripts/audit/audit_uet_covariant_theory_spine.py", "docs/core/artifacts/covariant_theory_spine_verification.json", "docs/core/test/test_uet_covariant_theory_spine.py"],
            "evidence_class": "INTERNAL_NUMERICAL", "proof_status": "linear fixed-background hyperbolicity and convergence pass; curved 3+1 blocked",
            "downstream_dependencies": ["uet.main_theory.covariant_parent", "uet.main_theory.open_system", "uet.main_theory.gravity"],
            "claim_boundary": "causal numerical control, not a curved covariant solver",
            "failure_mode": "complex/incomplete characteristics, superluminal speed, constraint growth, or hidden stabilization",
            "next_hardening_step": "derive a 3+1 formulation with dynamical metric and GR constraint propagation",
        }],
    }
    return verification, formula, gate, addendum


def main() -> int:
    names = ("covariant_theory_spine_verification.json", "covariant_theory_spine_formula_audit.json", "uet_main_theory_wave5_gate.json", "uet_equation_correspondence_registry_theory_spine_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        (ARTIFACTS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = outputs["uet_main_theory_wave5_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"theory_spine_status={gate['theory_spine_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
