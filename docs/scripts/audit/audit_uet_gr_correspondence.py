"""Generate Wave 9 analytic GR correspondence artifacts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_existing_path  # noqa: E402
GR_CORRESPONDENCE_SOURCE = canonical_existing_path(ROOT / ("docs/core/" + "uet_gr_correspondence.py")).relative_to(ROOT).as_posix()

from docs.core.uet_gr_correspondence import (
    flat_flrw_control, gr_correspondence_contract, minkowski_null_control,
    newtonian_poisson_residual, schwarzschild_exterior_null_control,
)

ARTIFACTS = ROOT / "docs/core/artifacts"


def build_artifacts() -> tuple[dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    records = [
        minkowski_null_control(),
        flat_flrw_control(1.3, 0.15, -0.02, cosmological_constant=0.01),
        schwarzschild_exterior_null_control(12.0, 1.0),
    ]
    density = np.linspace(0.0, 0.5, 16)
    poisson = newtonian_poisson_residual(4.0 * np.pi * 0.25 * density, density, 0.25)
    parent = json.loads((ARTIFACTS / "covariant_parent_verification.json").read_text(encoding="utf-8"))
    spine = json.loads((ARTIFACTS / "covariant_theory_spine_verification.json").read_text(encoding="utf-8"))
    metrics = {
        "maximum_analytic_einstein_residual": max(float(np.max(np.abs(record.residual))) for record in records),
        "newtonian_poisson_residual": float(np.max(np.abs(poisson))),
        "parent_gr_null_residual": float(parent["metrics"]["gr_null_max_abs"]),
        "linear_maximum_characteristic_speed": float(spine["metrics"]["maximum_characteristic_speed"]),
    }
    thresholds = {"identity": 1e-10, "causal_speed": 1.0 + 1e-10}
    checks = {
        "analytic_tensor_inputs_close": metrics["maximum_analytic_einstein_residual"] <= thresholds["identity"],
        "newtonian_poisson_limit": metrics["newtonian_poisson_residual"] <= thresholds["identity"],
        "parent_exact_gr_null_nesting": metrics["parent_gr_null_residual"] <= thresholds["identity"],
        "linear_propagation_subluminal": metrics["linear_maximum_characteristic_speed"] <= thresholds["causal_speed"],
        "curvature_from_metric_not_claimed": gr_correspondence_contract()["curvature_from_metric"] == "NOT_IMPLEMENTED",
        "curved_constraint_evolution_not_claimed": gr_correspondence_contract()["constraint_evolution"] == "NOT_IMPLEMENTED",
    }
    passed = all(checks.values())
    verification = {
        "schema_version": "1.0", "artifact": "gr_correspondence_verification",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "research_status": "ANALYTIC_TENSOR_INPUT_CONTROLS_ONLY",
        "metrics": metrics, "thresholds": thresholds, "checks": checks,
        "benchmark_ids": [record.benchmark_id for record in records] + ["newtonian_poisson"],
        "contract": gr_correspondence_contract(),
        "claim_boundary": "standard analytic correspondence inputs and exact parent null nesting; no curvature computation, gauge test, or curved numerical validation",
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave9_gate",
        "generated_at": now, "audit_status": "PASS" if passed else "FAIL",
        "gravity_status": "PASS_ANALYTIC_CONTROLS_CURVED_NUMERICS_BLOCKED" if passed else "BLOCKED",
        "upstream_gates": ["uet_main_theory_wave2_gate.json", "uet_main_theory_wave5_gate.json"],
        "checks": checks,
        "controlling_blockers": ["curvature_from_metric_not_implemented", "dynamical_metric_constraint_evolution_not_implemented", "gauge_invariant_observable_benchmarks_missing"],
        "claim_promotion": False,
        "next_controller": "derive and verify a curved 3+1 formulation before gravity, galaxy, or cosmology application unlock",
    }
    addendum = {
        "schema_version": "1.0", "artifact": "uet_equation_correspondence_registry_gr_controls_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json", "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [{
            "equation_id": "uet.main_theory.gr_correspondence_controls", "version": "gr-controls-v1",
            "classification": "standard_physics_interface", "relation_or_code_path": GR_CORRESPONDENCE_SOURCE,
            "variables": {"g_munu": "analytic metric input", "G_munu": "analytic Einstein-tensor input", "T_munu": "matching standard stress tensor", "Phi_N": "Newtonian potential"},
            "mathematical_role": "analytic GR and weak-field correspondence controls",
            "standard_physics_counterpart": "Einstein equation, FLRW perfect fluid, Schwarzschild exterior vacuum, and Poisson equation",
            "observable_mapping": {"status": "OPEN", "reason": "no gauge-invariant numerical metric observable or external dataset"},
            "unit_lane": "natural_control", "parameter_dimensions": "standard GR control conventions",
            "source_or_origin": "standard analytic formulas used as UET null/limit controls",
            "assumptions": ["analytic tensors supplied", "no curvature derivation", "fixed coordinates", "closed response branch"],
            "symmetry_and_conservation": "Einstein residual identity only; curved Bianchi evolution not tested",
            "limiting_cases": ["Minkowski vacuum", "flat FLRW perfect fluid", "Schwarzschild exterior", "Newtonian Poisson"],
            "implementation_paths": [GR_CORRESPONDENCE_SOURCE],
            "verifier_paths": ["docs/scripts/audit/audit_uet_gr_correspondence.py", "docs/core/07_artifacts/correspondence/gr_correspondence_verification.json", "docs/core/test/test_uet_gr_correspondence.py"],
            "evidence_class": "STANDARD_THEORY_REPRODUCTION", "proof_status": "analytic tensor-input identities pass; curved numerical closure blocked",
            "downstream_dependencies": ["uet.main_theory.covariant_parent", "uet.main_theory.hyperbolic_spine_control", "uet.main_theory.gravity_observables"],
            "claim_boundary": "correspondence controls, not a UET derivation or numerical GR validation",
            "failure_mode": "GR null limit fails or curved claims rely on supplied Einstein tensors as if computed",
            "next_hardening_step": "implement curvature, dynamical metric, constraints, and gauge-invariant observables",
        }],
    }
    return verification, gate, addendum


def main() -> int:
    names = ("gr_correspondence_verification.json", "uet_main_theory_wave9_gate.json", "uet_equation_correspondence_registry_gr_controls_addendum.json")
    outputs = dict(zip(names, build_artifacts()))
    for name, payload in outputs.items():
        (ARTIFACTS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    gate = outputs["uet_main_theory_wave9_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"gravity_status={gate['gravity_status']}")
    print("controlling_blockers=" + ",".join(gate["controlling_blockers"]))
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
