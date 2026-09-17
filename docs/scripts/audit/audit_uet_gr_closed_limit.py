"""Generate formula and exact-GR-limit evidence for the covariant UET pilot.

Passing this verifier establishes algebraic nesting and local tensor
consistency only. Bianchi/exchange closure, PDE characteristics, causal
non-closed dynamics, and physical GR validation remain blocked.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_response import (  # noqa: E402
    COVARIANT_RESPONSE_MODEL_STATUS,
    NATURAL_UNIT_MASS_DIMENSIONS,
    CovariantResponseConfig,
    curvature_factor,
    curvature_factor_base_derivative,
    effective_cosmological_constant,
    einstein_gr_residual,
    model_contract,
    response_potential_derivative,
    response_potential_hessian,
    response_scalar_equation_residual,
    response_stress_tensor,
    uet_metric_residual,
)
from docs.core.core_paths import canonical_artifact_path, canonical_existing_path  # noqa: E402

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_response.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
OUT = ROOT / "docs/core/07_artifacts"


def _artifact(name: str) -> Path:
    return canonical_artifact_path(name)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = _artifact(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _symbolic() -> dict[str, Any]:
    e, f, G, L, g, k, T, Tp, H, box = sp.symbols("e f G L g k T Tp H box")
    uet = (1 + e * f) * (G + L * g) + e * (g * box - H) - k * (T + e * Tp)
    gr = G + L * g - k * T
    metric_diff = sp.simplify(uet.subs(e, 0) - gr)

    d, rho, m2, lam, xi = sp.symbols("d rho m2 lam xi")
    U = rho + m2 * d**2 / 2 + lam * d**4 / 4
    F = 1 + e * xi * d**2
    scalar = e * sp.Symbol("scalar_bracket")
    return {
        "metric_closed_difference": str(metric_diff),
        "metric_closed_limit_exact": metric_diff == 0,
        "scalar_closed_difference": str(sp.simplify(scalar.subs(e, 0))),
        "scalar_closed_limit_exact": sp.simplify(scalar.subs(e, 0)) == 0,
        "factor_at_equilibrium": str(F.subs(d, 0)),
        "factor_first_at_equilibrium": str(sp.diff(F, d).subs(d, 0)),
        "potential_first_at_equilibrium": str(sp.diff(U, d).subs(d, 0)),
        "potential_second_at_equilibrium": str(sp.diff(U, d, 2).subs(d, 0)),
        "ordered_reference_exact": bool(
            F.subs(d, 0) == 1
            and sp.diff(F, d).subs(d, 0) == 0
            and sp.diff(U, d).subs(d, 0) == 0
        ),
    }


def _sym(rng: np.random.Generator, scale: float) -> np.ndarray:
    raw = rng.normal(scale=scale, size=(4, 4))
    return 0.5 * (raw + raw.T)


def _numeric() -> dict[str, Any]:
    rng = np.random.default_rng(190021)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    A = np.array(
        [[1, .12, 0, 0], [.05, 1.1, .07, 0], [0, .02, .92, .04], [0, 0, .03, 1.04]],
        dtype=float,
    )
    metric = A.T @ eta @ A
    inverse = np.linalg.inv(metric)
    einstein, matter = _sym(rng, .4), _sym(rng, .2)
    closed = CovariantResponseConfig(
        epsilon_nc=0.0,
        einstein_coupling=.37,
        cosmological_constant=.013,
        curvature_coupling=-2.5,
        equilibrium_density=7.0,
    )
    gr = einstein_gr_residual(metric, einstein, matter, closed)
    nested = uet_metric_residual(
        metric, einstein, matter, 1e100, np.full(4, 1e100),
        np.full((4, 4), 1e200), closed, inverse_metric=inverse
    )

    cfg = CovariantResponseConfig(
        epsilon_nc=.25,
        einstein_coupling=.6,
        cosmological_constant=.02,
        phi_equilibrium=.1,
        response_kinetic=1.3,
        response_mass_sq=.8,
        response_quartic=.4,
        curvature_coupling=.05,
        equilibrium_density=.03,
    )
    phi, gradient, hessian = .35, rng.normal(scale=.15, size=4), _sym(rng, .08)
    residual = uet_metric_residual(
        metric, einstein, matter, phi, gradient, hessian, cfg, inverse_metric=inverse
    )
    stress = response_stress_tensor(metric, inverse, gradient, phi, cfg)

    B = np.array(
        [[1, .08, 0, 0], [.03, .96, .05, 0], [0, .02, 1.07, .06], [0, 0, .04, .94]],
        dtype=float,
    )
    Bi = np.linalg.inv(B)
    transformed = uet_metric_residual(
        B.T @ metric @ B,
        B.T @ einstein @ B,
        B.T @ matter @ B,
        phi,
        B.T @ gradient,
        B.T @ hessian @ B,
        cfg,
        inverse_metric=Bi @ inverse @ Bi.T,
    )
    expected = B.T @ residual @ B
    p0 = cfg.phi_equilibrium
    return {
        "closed_limit_max_abs_residual": float(np.max(np.abs(nested - gr))),
        "closed_limit_componentwise_exact": bool(np.array_equal(nested, gr)),
        "scalar_closed_limit_residual": response_scalar_equation_residual(3, -9, 1e100, closed),
        "response_stress_symmetry_error": float(np.max(np.abs(stress - stress.T))),
        "local_tensor_transformation_max_abs_error": float(np.max(np.abs(transformed - expected))),
        "ordered_reference": {
            "curvature_factor": curvature_factor(p0, cfg),
            "curvature_factor_base_derivative": curvature_factor_base_derivative(p0, cfg),
            "potential_derivative": response_potential_derivative(p0, cfg),
            "potential_hessian": response_potential_hessian(p0, cfg),
            "lambda_effective": effective_cosmological_constant(cfg),
            "lambda_effective_expected": cfg.cosmological_constant
            + cfg.einstein_coupling * cfg.epsilon_nc * cfg.equilibrium_density,
        },
    }


def _dimension_audit() -> dict[str, Any]:
    d = NATURAL_UNIT_MASS_DIMENSIONS
    actual = {
        "gravitational_lagrangian": -d["einstein_coupling"] + 2,
        "kinetic_lagrangian": d["response_kinetic"] + 2 * (d["derivative"] + d["phi"]),
        "mass_potential": d["response_mass_sq"] + 2 * d["phi"],
        "quartic_potential": d["response_quartic"] + 4 * d["phi"],
        "curvature_factor_term": d["curvature_coupling"] + 2 * d["phi"],
        "stress_to_metric_equation": d["einstein_coupling"] + d["stress_tensor"],
    }
    expected = {
        "gravitational_lagrangian": 4, "kinetic_lagrangian": 4,
        "mass_potential": 4, "quartic_potential": 4,
        "curvature_factor_term": 0, "stress_to_metric_equation": 2,
    }
    return {
        "status": "PASS" if actual == expected else "FAIL",
        "declared": d, "actual": actual, "expected": expected,
    }


def _epsilon_denominators(source: str) -> list[int]:
    tree = ast.parse(source)
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if any(
            (isinstance(child, ast.Name) and child.id == "epsilon_nc")
            or (isinstance(child, ast.Attribute) and child.attr == "epsilon_nc")
            for child in ast.walk(node.right)
        ):
            lines.append(node.lineno)
    return lines


def _si_is_blocked() -> bool:
    try:
        CovariantResponseConfig(unit_lane="SI")
    except NotImplementedError:
        return True
    return False


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    source = CORE.read_text(encoding="utf-8")
    symbolic, numeric, dimensions = _symbolic(), _numeric(), _dimension_audit()
    denominator_lines = _epsilon_denominators(source)
    contract = model_contract()
    balance_path = _artifact("covariant_bianchi_exchange_verification.json")
    balance_status = "NOT_RUN"
    if balance_path.exists():
        try:
            balance_status = json.loads(balance_path.read_text(encoding="utf-8")).get("status", "FAIL")
        except (OSError, json.JSONDecodeError):
            balance_status = "FAIL"
    balance_passed = balance_status == "PASS"
    causal_path = _artifact("causal_nonclosed_kernel_verification.json")
    causal_status = "NOT_RUN"
    if causal_path.exists():
        try:
            causal_status = json.loads(causal_path.read_text(encoding="utf-8")).get("status", "FAIL")
        except (OSError, json.JSONDecodeError):
            causal_status = "FAIL"
    causal_passed = causal_status == "PASS"
    reduction_path = _artifact("covariant_matter_space_reduction_verification.json")
    reduction_status = "NOT_RUN"
    reduction_evidence = "MISSING"
    if reduction_path.exists():
        try:
            reduction_payload = json.loads(reduction_path.read_text(encoding="utf-8"))
            reduction_status, reduction_evidence = reduction_payload.get("audit_status", "FAIL"), reduction_payload.get("evidence_status", "BLOCKED")
        except (OSError, json.JSONDecodeError):
            reduction_status, reduction_evidence = "FAIL", "BLOCKED"
    reduction_passed = (
        reduction_status == "PASS" and reduction_evidence == "PARTIAL"
    )
    matter_path = _artifact("covariant_matter_action_verification.json")
    matter_status = "NOT_RUN"
    matter_evidence = "MISSING"
    if matter_path.exists():
        try:
            matter_payload = json.loads(matter_path.read_text(encoding="utf-8"))
            matter_status = matter_payload.get("audit_status", "FAIL")
            matter_evidence = matter_payload.get("evidence_status", "BLOCKED")
        except (OSError, json.JSONDecodeError):
            matter_status, matter_evidence = "FAIL", "BLOCKED"
    matter_passed = matter_status == "PASS" and matter_evidence == "PARTIAL"
    diffusion_path = _artifact("covariant_diffusive_current_verification.json")
    diffusion_status = "NOT_RUN"
    diffusion_evidence = "MISSING"
    if diffusion_path.exists():
        try:
            diffusion_payload = json.loads(
                diffusion_path.read_text(encoding="utf-8")
            )
            diffusion_status = diffusion_payload.get("audit_status", "FAIL")
            diffusion_evidence = diffusion_payload.get("evidence_status", "BLOCKED")
        except (OSError, json.JSONDecodeError):
            diffusion_status, diffusion_evidence = "FAIL", "BLOCKED"
    diffusion_passed = diffusion_status == "PASS" and diffusion_evidence == "PARTIAL"
    gates = {
        "symbolic_metric_closed_limit": "PASS" if symbolic["metric_closed_limit_exact"] else "FAIL",
        "symbolic_scalar_decoupling": "PASS" if symbolic["scalar_closed_limit_exact"] else "FAIL",
        "numeric_componentwise_closed_limit": "PASS" if numeric["closed_limit_componentwise_exact"] else "FAIL",
        "ordered_reference": "PASS" if symbolic["ordered_reference_exact"] and numeric["ordered_reference"]["potential_hessian"] > 0 else "FAIL",
        "symmetric_response_stress": "PASS" if numeric["response_stress_symmetry_error"] <= 1e-12 else "FAIL",
        "local_tensor_transformation": "PASS" if numeric["local_tensor_transformation_max_abs_error"] <= 1e-11 else "FAIL",
        "natural_unit_dimension_closure": dimensions["status"],
        "no_epsilon_denominator": "PASS" if not denominator_lines else "FAIL",
        "si_lane_quarantine": "PASS" if _si_is_blocked() else "FAIL",
        "derived_trace_disconnected": "PASS" if "uet_trace" not in source and not contract["derived_trace_backreaction"] else "FAIL",
    }
    status = "PASS" if set(gates.values()) == {"PASS"} else "FAIL"
    hashes = {str(CORE.relative_to(ROOT)): _sha(CORE), str(SPEC.relative_to(ROOT)): _sha(SPEC)}
    closed = {
        "schema_version": "1.0", "artifact": "gr_closed_limit_verification",
        "generated_at": now, "status": status, "evidence_class": "B",
        "claim": "exact algebraic GR null limit of a candidate tensor-formula evaluator",
        "thresholds": {"closed_limit": 1e-12, "symmetry": 1e-12, "tensor_transform": 1e-11},
        "symbolic": symbolic, "numeric": numeric, "gates": gates,
        "source_hashes": hashes,
        "run_contract": {"seed": 190021, "parameter_fitting": False, "external_data": False,
                         "metric_pde_solved": False, "bianchi_identity_proved": False,
                         "trace_backreaction": False},
        "allowed_language": ["candidate conservative covariant parent", "exact implemented GR closed-limit contract", "local tensor-transformation consistency"],
        "blocked_language": ["Einstein equations derived from UET", "physical GR validation", "Bianchi or Noether proof", "universe proved non-closed"],
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing" if reduction_passed
            else "controlled_covariant_to_matter_space_reduction_missing" if causal_passed
            else "causal_nonclosed_influence_functional_missing" if balance_passed else "covariant_bianchi_exchange_balance_missing"
        ),
    }
    registry = [
        ["covariant_conservative_action", "conservative_action_density", "candidate ansatz"],
        ["response_potential", "response_potential", "declared constitutive choice"],
        ["response_stress_tensor", "response_stress_tensor", "canonical scalar target"],
        ["nested_metric_residual", "uet_metric_residual", "candidate scalar-tensor equation"],
        ["nested_scalar_residual", "response_scalar_equation_residual", "candidate Euler-Lagrange equation"],
    ]
    formula = {
        "schema_version": "1.0", "artifact": "covariant_action_formula_audit",
        "generated_at": now, "status": "WARN" if status == "PASS" else "FAIL",
        "implementation_status": "PRESENT" if status == "PASS" else "INCOMPLETE",
        "model_status": COVARIANT_RESPONSE_MODEL_STATUS, "claim_class": "B",
        "unit_lane": "natural", "dimension_audit": dimensions,
        "epsilon_denominator_lines": denominator_lines,
        "formula_registry": [
            {"id": item[0], "status": "IMPLEMENTED", "implementation": f"docs/core/02_equations/covariant/uet_covariant_response.py::{item[1]}", "derivation_status": item[2]}
            for item in registry
        ],
        "coefficient_policy": {"defaults_are_physical_constants": False, "epsilon_is_open_percentage": False, "rho_star_maps_to_lambda_eff": True},
        "open_formula_gates": (
            ([] if balance_passed else ["covariant_bianchi_exchange_balance_missing"])
            + (["closed_time_path_derivation_missing"] if causal_passed else ["causal_influence_functional_missing"])
            + (["first_order_hyperbolic_phase_field_uv_closure_missing"] if diffusion_passed
               else ["regular_covariant_to_diffusive_matter_reduction_missing"] if matter_passed
               else ["covariant_matter_action_and_reciprocal_coupling_missing"] if reduction_passed
               else ["controlled_covariant_to_matter_space_reduction_missing"] if causal_passed else [])
            + ["principal_symbol_and_ghost_analysis_missing", "system_specific_SI_contract_missing"]
        ),
        "completed_formula_gates": (
            (["covariant_bianchi_exchange_balance"] if balance_passed else [])
            + (["causal_constitutive_kernel_1p1d"] if causal_passed else [])
            + (["controlled_response_sector_reduction_partial"] if reduction_passed else [])
            + (["conserved_current_diffusive_bridge_partial"] if diffusion_passed else [])
            + (["covariant_matter_action_reciprocity"] if matter_passed else [])
        ),
        "downstream_reduction_status": reduction_status,
        "downstream_reduction_evidence": reduction_evidence,
        "downstream_matter_status": matter_status,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
        "downstream_matter_evidence": matter_evidence,
        "source_hashes": hashes,
    }
    program = {
        "schema_version": "1.0", "artifact": "uet_gr_research_program_gate",
        "generated_at": now, "status": "BLOCKED",
        "program_stage": (
            "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL" if diffusion_passed
            else "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED" if matter_passed
            else "CONTROLLED_RESPONSE_REDUCTION_PARTIAL" if reduction_passed
            else "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED" if causal_passed
            else "COVARIANT_CONSERVATIVE_BALANCE_VERIFIED" if balance_passed else "CONSERVATIVE_PARENT_IMPLEMENTED"
        ),
        "current_claim_class": "B" if status == "PASS" else "A",
        "gr_null_model": {"parameter": "epsilon_nc", "value": 0.0, "verification_status": status},
        "sector_status": {"ontology_and_claim_contract": "PASS", "legacy_claim_quarantine": "PASS",
                          "conservative_tensor_formula": status, "exact_gr_closed_limit": status,
                          "covariant_exchange_bianchi_balance": "PASS" if balance_passed else "BLOCKED", "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D" if causal_passed else "NOT_IMPLEMENTED",
                          "weak_field_reduction": "PARTIAL_RESPONSE_ONLY" if reduction_passed else "NOT_IMPLEMENTED",
                          "covariant_matter_action": "PASS_O2_SCALAR_PILOT" if matter_passed else "NOT_IMPLEMENTED",
                          "reciprocal_coupling": "PASS_ACTION_LEVEL" if matter_passed else "NOT_IMPLEMENTED",
                          "matter_number_current": "PASS_ON_SHELL_O2" if matter_passed else "NOT_IMPLEMENTED",
                          "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT" if diffusion_passed else "NOT_IMPLEMENTED",
                          "local_convex_matter_causality": "PASS_CONTROL" if diffusion_passed else "NOT_IMPLEMENTED",
                          "gradient_phase_field_causality": "BLOCKED_UV" if diffusion_passed else "NOT_IMPLEMENTED",
                          "physical_gr_benchmarks": "NOT_STARTED"},
        "global_universe_closure": "UNRESOLVED", "topic_0_11_status_impact": "NONE", "topic_0_19_status_impact": "NONE",
        "controlling_blocker": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing" if reduction_passed
            else "controlled_covariant_to_matter_space_reduction_missing" if causal_passed
            else "causal_nonclosed_influence_functional_missing" if balance_passed else "covariant_bianchi_exchange_balance_missing"
        ),
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse-grained conserved-current bridge and exact Model-B limit are present, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent." if diffusion_passed
            else "The conservative scalar matter action and reciprocal interaction close, but the density interpretation, regular epsilon-nested normalized chart, and dissipative conserved-matter dynamics are not derived." if matter_passed
            else "The response equation maps exactly, but the covariant matter equation, reciprocal coupling, and causal realization of the required source are absent." if reduction_passed
            else "A restricted causal constitutive kernel exists, but the controlled weak-field reduction is missing." if causal_passed
            else "Local conservative exchange closes, but causal non-closed dynamics are missing." if balance_passed
            else "Algebraic GR nesting exists, but generated Bianchi/exchange and causal non-closed dynamics do not."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, formula, closed, program)
    return formula, closed, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    formula, closed, program = build_artifacts()
    _dump("covariant_action_formula_audit.json", formula)
    _dump("gr_closed_limit_verification.json", closed)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(json.dumps({"closed_limit_status": closed["status"], "formula_audit_status": formula["status"],
                          "program_status": program["status"], "controlling_blocker": program["controlling_blocker"],
                          "numeric": closed["numeric"]}, indent=2))
    return 2 if args.strict and closed["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
