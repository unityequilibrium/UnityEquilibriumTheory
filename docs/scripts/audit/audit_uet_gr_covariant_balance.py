"""Verify the conservative UET Noether/Bianchi and exchange identities."""

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

from docs.core.uet_covariant_balance import (  # noqa: E402
    NATURAL_UNIT_BALANCE_DIMENSIONS,
    balance_contract,
    evaluate_balance_identity,
    exchange_completed_ledger,
    sourced_on_shell_metric_divergence,
)
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

CORE = ROOT / "docs/core/uet_covariant_balance.py"
RESPONSE_CORE = ROOT / "docs/core/uet_covariant_response.py"
SPEC = ROOT / "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
OUT = ROOT / "docs/core/artifacts"
CLOSED = OUT / "gr_closed_limit_verification.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    (OUT / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _symbolic() -> dict[str, Any]:
    e, fp, R, L, k, Z, box, Up, grad, div_m, j = sp.symbols(
        "e fp R L k Z box Up grad div_m j"
    )
    scalar_eom = e * (Z * box - Up + fp * (R - 2 * L) / (2 * k))
    expanded = (
        -e * fp * (R - 2 * L) * grad / 2
        - k * div_m
        - k * e * (Z * box - Up) * grad
    )
    compact = -k * (div_m + scalar_eom * grad)
    identity_difference = sp.simplify(expanded - compact)
    full_source = e * j
    q_m, q_response = -full_source * grad, full_source * grad
    sourced_shell = sp.simplify(-k * (q_m + full_source * grad))
    return {
        "expanded_minus_compact": str(identity_difference),
        "identity_exact": identity_difference == 0,
        "exchange_sum": str(sp.simplify(q_m + q_response)),
        "exchange_closure_exact": sp.simplify(q_m + q_response) == 0,
        "sourced_on_shell_metric_divergence": str(sourced_shell),
        "sourced_on_shell_exact": sourced_shell == 0,
        "gr_limit_full_source": str(full_source.subs(e, 0)),
        "gr_limit_exchange_exact": q_m.subs(e, 0) == 0 and q_response.subs(e, 0) == 0,
    }


def _numeric() -> dict[str, Any]:
    rng = np.random.default_rng(190031)
    cfg = CovariantResponseConfig(
        epsilon_nc=.32,
        einstein_coupling=.61,
        cosmological_constant=.015,
        phi_equilibrium=.2,
        response_kinetic=1.4,
        response_mass_sq=.9,
        response_quartic=.3,
        curvature_coupling=.07,
    )
    gradient = rng.normal(scale=.2, size=4)
    matter_divergence = rng.normal(scale=.1, size=4)
    identity = evaluate_balance_identity(
        matter_divergence, gradient, .11, -.08, .37, cfg
    )
    ledger = exchange_completed_ledger(.23, gradient, cfg)
    on_shell = sourced_on_shell_metric_divergence(.23, gradient, cfg)

    transform = np.array(
        [[1, .07, 0, 0], [.03, .98, .04, 0], [0, .02, 1.03, .05], [0, 0, .01, .96]],
        dtype=float,
    )
    transformed_ledger = exchange_completed_ledger(.23, transform.T @ gradient, cfg)
    exchange_transform_error = float(
        np.max(np.abs(transformed_ledger.matter_exchange - transform.T @ ledger.matter_exchange))
    )
    closed_cfg = CovariantResponseConfig(epsilon_nc=0.0)
    closed_ledger = exchange_completed_ledger(1e100, np.full(4, 1e100), closed_cfg)
    return {
        "identity_max_abs_difference": identity["max_abs_difference"],
        "exchange_closure_max_abs": ledger.closure_max_abs,
        "sourced_on_shell_max_abs": float(np.max(np.abs(on_shell))),
        "exchange_covector_transform_max_abs": exchange_transform_error,
        "gr_limit_full_source": closed_ledger.full_scalar_source,
        "gr_limit_exchange_max_abs": float(
            max(
                np.max(np.abs(closed_ledger.matter_exchange)),
                np.max(np.abs(closed_ledger.response_exchange)),
            )
        ),
    }


def _dimension_status() -> dict[str, Any]:
    d = NATURAL_UNIT_BALANCE_DIMENSIONS
    actual = {
        "source_times_gradient": d["scalar_source"] + d["gradient_phi"],
        "kappa_times_stress_divergence": d["einstein_coupling"] + d["stress_divergence"],
        "kappa_times_eom_gradient": d["einstein_coupling"]
        + d["scalar_equation_residual"] + d["gradient_phi"],
    }
    expected = {
        "source_times_gradient": 5,
        "kappa_times_stress_divergence": 3,
        "kappa_times_eom_gradient": 3,
    }
    return {"status": "PASS" if actual == expected else "FAIL", "actual": actual, "expected": expected}


def _epsilon_denominators() -> list[int]:
    tree = ast.parse(CORE.read_text(encoding="utf-8"))
    result: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if any(
            (isinstance(child, ast.Name) and child.id == "epsilon_nc")
            or (isinstance(child, ast.Attribute) and child.attr == "epsilon_nc")
            for child in ast.walk(node.right)
        ):
            result.append(node.lineno)
    return result


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic, numeric, dimensions = _symbolic(), _numeric(), _dimension_status()
    denominators = _epsilon_denominators()
    contract = balance_contract()
    closed = json.loads(CLOSED.read_text(encoding="utf-8"))
    causal_path = OUT / "causal_nonclosed_kernel_verification.json"
    causal_status = "NOT_RUN"
    if causal_path.exists():
        try:
            causal_status = json.loads(causal_path.read_text(encoding="utf-8")).get("status", "FAIL")
        except (OSError, json.JSONDecodeError):
            causal_status = "FAIL"
    causal_passed = causal_status == "PASS"
    reduction_path = OUT / "covariant_matter_space_reduction_verification.json"
    reduction_status = "NOT_RUN"
    reduction_evidence = "MISSING"
    if reduction_path.exists():
        try:
            reduction_payload = json.loads(reduction_path.read_text(encoding="utf-8"))
            reduction_status = reduction_payload.get("audit_status", "FAIL")
            reduction_evidence = reduction_payload.get("evidence_status", "BLOCKED")
        except (OSError, json.JSONDecodeError):
            reduction_status, reduction_evidence = "FAIL", "BLOCKED"
    reduction_passed = reduction_status == "PASS" and reduction_evidence == "PARTIAL"
    matter_path = OUT / "covariant_matter_action_verification.json"
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
    diffusion_path = OUT / "covariant_diffusive_current_verification.json"
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
        "expanded_compact_noether_identity": "PASS" if symbolic["identity_exact"] else "FAIL",
        "exchange_completed_total_balance": "PASS" if symbolic["exchange_closure_exact"] and numeric["exchange_closure_max_abs"] <= 1e-12 else "FAIL",
        "sourced_on_shell_bianchi_balance": "PASS" if symbolic["sourced_on_shell_exact"] and numeric["sourced_on_shell_max_abs"] <= 1e-12 else "FAIL",
        "regular_gr_exchange_limit": "PASS" if symbolic["gr_limit_exchange_exact"] and numeric["gr_limit_exchange_max_abs"] == 0 else "FAIL",
        "local_covector_transformation": "PASS" if numeric["exchange_covector_transform_max_abs"] <= 1e-12 else "FAIL",
        "natural_unit_dimension_closure": dimensions["status"],
        "no_epsilon_denominator": "PASS" if not denominators else "FAIL",
        "matter_number_not_conflated_with_stress_exchange": "PASS" if contract["matter_number_equation_independent"] else "FAIL",
        "derived_trace_disconnected": "PASS" if not contract["derived_trace_imported"] else "FAIL",
        "closed_limit_dependency": "PASS" if closed["status"] == "PASS" else "FAIL",
    }
    status = "PASS" if set(gates.values()) == {"PASS"} else "FAIL"
    hashes = {
        str(CORE.relative_to(ROOT)): _sha(CORE),
        str(RESPONSE_CORE.relative_to(ROOT)): _sha(RESPONSE_CORE),
        str(SPEC.relative_to(ROOT)): _sha(SPEC),
    }
    verification = {
        "schema_version": "1.0", "artifact": "covariant_bianchi_exchange_verification",
        "generated_at": now, "status": status, "evidence_class": "B",
        "claim": "symbolic local Noether/Bianchi identity and exchange-completed ledger for the candidate parent",
        "symbolic": symbolic, "numeric": numeric, "dimension_audit": dimensions,
        "epsilon_denominator_lines": denominators, "gates": gates, "source_hashes": hashes,
        "run_contract": {"seed": 190031, "external_data": False, "parameter_fitting": False,
                         "curved_derivative_solver": False, "causal_kernel": False,
                         "global_energy_theorem": False, "trace_backreaction": False},
        "allowed_language": ["candidate covariant balance identity", "exchange-completed local ledger", "matter stress exchange can coexist with an independent number-current equation"],
        "blocked_language": ["global universe conservation proved", "universe proved open",
                             "full curved-spacetime causal non-closed response", "physical GR validation"],
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing" if reduction_passed
            else "controlled_covariant_to_matter_space_reduction_missing" if causal_passed
            else "causal_nonclosed_influence_functional_missing"
        ),
        "downstream_causal_kernel_status": causal_status,
        "downstream_reduction_status": reduction_status,
        "downstream_matter_status": matter_status,
        "downstream_matter_evidence": matter_evidence,
        "downstream_reduction_evidence": reduction_evidence,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    exchange_contract = {
        "schema_version": "1.0", "artifact": "covariant_exchange_contract",
        "generated_at": now, "status": "CANDIDATE" if status == "PASS" else "BLOCKED",
        "scalar_equation": "E_phi = epsilon_nc * j_phi",
        "matter_stress_balance": "nabla_mu T_m^(mu nu) = -epsilon_nc*j_phi*nabla^nu(phi)",
        "response_balance": "nabla_mu T_response_eff^(mu nu) = +epsilon_nc*j_phi*nabla^nu(phi)",
        "total_modeled_balance": "nabla_mu(T_m+T_response_eff)^(mu nu) = 0",
        "matter_number_balance": "nabla_mu N^mu = 0 is an independent lane-specific equation",
        "gr_limit": "epsilon_nc=0 gives J_phi=Q_m=Q_response=0 exactly",
        "global_universe_closure": "UNRESOLVED",
        "causal_source_policy": "IMPLEMENTED_CONSTITUTIVE_1P1D" if causal_passed else "BLOCKED_UNTIL_WAVE_4",
        "downstream_reduction": "PARTIAL_RESPONSE_ONLY" if reduction_passed else "NOT_IMPLEMENTED",
        "covariant_matter_action": "PASS_O2_SCALAR_PILOT" if matter_passed else "NOT_IMPLEMENTED",
        "reciprocal_coupling": "PASS_ACTION_LEVEL" if matter_passed else "NOT_IMPLEMENTED",
        "matter_number_current": "PASS_ON_SHELL_O2" if matter_passed else "NOT_IMPLEMENTED",
        "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT" if diffusion_passed else "NOT_IMPLEMENTED",
        "local_convex_matter_causality": "PASS_CONTROL" if diffusion_passed else "NOT_IMPLEMENTED",
        "gradient_phase_field_causality": "BLOCKED_UV" if diffusion_passed else "NOT_IMPLEMENTED",
        "derived_trace_backreaction": False,
    }
    program = {
        "schema_version": "1.0", "artifact": "uet_gr_research_program_gate",
        "generated_at": now, "status": "BLOCKED",
        "program_stage": (
            "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL" if diffusion_passed
            else "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED" if matter_passed
            else "CONTROLLED_RESPONSE_REDUCTION_PARTIAL" if reduction_passed
            else "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED" if causal_passed
            else "COVARIANT_CONSERVATIVE_BALANCE_VERIFIED" if status == "PASS" else "CONSERVATIVE_PARENT_IMPLEMENTED"
        ),
        "current_claim_class": "B",
        "gr_null_model": {"parameter": "epsilon_nc", "value": 0, "verification_status": closed["status"]},
        "sector_status": {"ontology_and_claim_contract": "PASS", "legacy_claim_quarantine": "PASS",
                          "conservative_tensor_formula": closed["status"], "exact_gr_closed_limit": closed["status"],
                          "covariant_exchange_bianchi_balance": status,
                          "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D" if causal_passed else "NOT_IMPLEMENTED",
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
            else "causal_nonclosed_influence_functional_missing" if status == "PASS" else "covariant_bianchi_exchange_balance_missing"
        ),
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse-grained conserved-current bridge and exact Model-B limit are present, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent." if diffusion_passed
            else "The conservative scalar matter action and reciprocal interaction close, but the density interpretation, regular epsilon-nested normalized chart, and dissipative conserved-matter dynamics are not derived." if matter_passed
            else "The response equation maps exactly, but the covariant matter equation, reciprocal coupling, and causal realization of the required source are absent." if reduction_passed
            else "A restricted causal constitutive source passes, but the controlled weak-field reduction is missing." if causal_passed
            else "Local conservative exchange closes, but a causal non-closed constitutive source and its stability gates are not implemented."
        ),
        "artifact_dependencies": {"closed_limit": str(CLOSED.relative_to(ROOT)),
                                  "balance_verification": "docs/core/07_artifacts/verification/covariant_bianchi_exchange_verification.json",
                                  "exchange_contract": "docs/core/07_artifacts/archive/covariant_exchange_contract.json"},
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, verification, exchange_contract, program)
    return verification, exchange_contract, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, contract, program = build_artifacts()
    _dump("covariant_bianchi_exchange_verification.json", verification)
    _dump("covariant_exchange_contract.json", contract)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(json.dumps({"balance_status": verification["status"], "program_status": program["status"],
                          "controlling_blocker": program["controlling_blocker"], "numeric": verification["numeric"]}, indent=2))
    return 2 if args.strict and verification["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
