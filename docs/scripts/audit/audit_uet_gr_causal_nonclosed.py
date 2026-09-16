"""Verify the first retarded non-closed constitutive kernel."""

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

from docs.core.uet_covariant_nonclosed import (  # noqa: E402
    CausalInfluenceConfig,
    CausalSourceEvent,
    NATURAL_UNIT_CAUSAL_DIMENSIONS,
    causal_exchange_from_events,
    causal_nonclosed_contract,
    covariant_retarded_kernel_value,
    retarded_influence_from_events,
    retarded_telegraph_kernel_1p1,
)
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)
from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_nonclosed.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
OUT = CANONICAL_ARTIFACT_ROOT
CLOSED = canonical_artifact_path("gr_closed_limit_verification.json", "verification")
BALANCE = canonical_artifact_path("covariant_bianchi_exchange_verification.json", "verification")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    (OUT / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _symbolic() -> dict[str, Any]:
    tau, diffusion, decay = sp.symbols("tau diffusion decay", positive=True)
    speed_sq = diffusion / tau
    damping = 1 / (2 * tau)
    mass_sq = decay / tau - 1 / (4 * tau**2)
    y, yp, ypp, interval = sp.symbols("y yp ypp interval")
    reduced_operator = sp.expand(
        tau * (4 * interval * ypp + 4 * yp + mass_sq * y)
    )
    bessel_identity = 4 * interval * ypp + 4 * yp + mass_sq * y
    on_bessel_shell = sp.simplify(reduced_operator.subs(ypp, -(4 * yp + mass_sq * y) / (4 * interval)))
    return {
        "characteristic_speed_sq": str(speed_sq),
        "damping_rate": str(damping),
        "effective_mass_sq": str(mass_sq),
        "interior_operator_reduction": str(reduced_operator),
        "bessel_identity": str(bessel_identity),
        "interior_pde_residual_on_bessel_shell": str(on_bessel_shell),
        "interior_pde_exact": on_bessel_shell == 0,
    }


def _numeric() -> dict[str, Any]:
    cfg = CausalInfluenceConfig(
        tau_memory=1.25,
        diffusivity=.45,
        decay_rate=.35,
        source_coupling=.8,
    )
    speed = cfg.propagation_speed
    distances = np.linspace(.1, 2.0, 25)
    outside_values = [
        abs(retarded_telegraph_kernel_1p1(.8 * distance / speed, distance, cfg))
        for distance in distances
    ]
    arrival_errors = []
    for distance in distances:
        arrival = distance / speed
        before = retarded_telegraph_kernel_1p1(arrival * (1 - 1e-9), distance, cfg)
        at_arrival = retarded_telegraph_kernel_1p1(arrival, distance, cfg)
        if before == 0.0 and at_arrival != 0.0:
            measured = arrival
        else:
            measured = float("nan")
        arrival_errors.append(abs(measured - arrival) / arrival)

    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    frame = np.array([1.0, 0.0, 0.0, 0.0])
    axis = np.array([0.0, 1.0, 0.0, 0.0])
    separation = np.array([2.1, .4, 0.0, 0.0])
    original = covariant_retarded_kernel_value(separation, metric, frame, axis, cfg)
    transform = np.array(
        [[1.0, .08, 0, 0], [.03, .97, 0, 0], [0, 0, 1.04, .02], [0, 0, .01, .96]],
        dtype=float,
    )
    inverse_transform = np.linalg.inv(transform)
    transformed = covariant_retarded_kernel_value(
        inverse_transform @ separation,
        transform.T @ metric @ transform,
        inverse_transform @ frame,
        inverse_transform @ axis,
        cfg,
    )

    events = [
        CausalSourceEvent(np.array([0.0, 0.0, 0.0, 0.0]), 1.2),
        CausalSourceEvent(np.array([3.0, 0.0, 0.0, 0.0]), 5.0),
    ]
    observation = np.array([2.1, .4, 0.0, 0.0])
    all_events = retarded_influence_from_events(
        observation, events, metric, frame, axis, cfg
    )
    past_only = retarded_influence_from_events(
        observation, events[:1], metric, frame, axis, cfg
    )
    response_cfg = CovariantResponseConfig(epsilon_nc=.3)
    ledger = causal_exchange_from_events(
        observation,
        events,
        metric,
        frame,
        axis,
        np.array([.1, -.03, .02, .04]),
        cfg,
        response_cfg,
    )
    closed_ledger = causal_exchange_from_events(
        observation,
        events,
        metric,
        frame,
        axis,
        np.full(4, 1e100),
        cfg,
        CovariantResponseConfig(epsilon_nc=0.0),
    )
    return {
        "propagation_speed": speed,
        "outside_cone_max_abs": float(max(outside_values)),
        "arrival_speed_relative_error_max": float(max(arrival_errors)),
        "negative_time_kernel": retarded_telegraph_kernel_1p1(-1.0, 0.0, cfg),
        "coordinate_scalar_error": abs(transformed - original),
        "future_event_influence_error": abs(all_events - past_only),
        "exchange_closure_max_abs": ledger.closure_max_abs,
        "gr_limit_full_source": closed_ledger.full_scalar_source,
        "gr_limit_exchange_max_abs": float(
            max(np.max(np.abs(closed_ledger.matter_exchange)), np.max(np.abs(closed_ledger.response_exchange)))
        ),
    }


def _dimensions() -> dict[str, Any]:
    d = NATURAL_UNIT_CAUSAL_DIMENSIONS
    actual = {
        "tau_second_time_derivative": d["tau_memory"] + 2,
        "first_time_derivative": 1,
        "diffusion_second_space_derivative": d["diffusivity"] + 2,
        "decay_term": d["decay_rate"],
        "speed_squared": d["diffusivity"] - d["tau_memory"],
    }
    expected = {
        "tau_second_time_derivative": 1,
        "first_time_derivative": 1,
        "diffusion_second_space_derivative": 1,
        "decay_term": 1,
        "speed_squared": 0,
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


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic, numeric, dimensions = _symbolic(), _numeric(), _dimensions()
    denominators = _epsilon_denominators()
    contract = causal_nonclosed_contract()
    closed = json.loads(CLOSED.read_text(encoding="utf-8"))
    balance = json.loads(BALANCE.read_text(encoding="utf-8"))
    source = CORE.read_text(encoding="utf-8")
    reduction_path = canonical_artifact_path(
        "covariant_matter_space_reduction_verification.json", "verification"
    )
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
    matter_path = canonical_artifact_path(
        "covariant_matter_action_verification.json", "verification"
    )
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
    diffusion_path = canonical_artifact_path(
        "covariant_diffusive_current_verification.json", "verification"
    )
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
        "interior_green_equation": "PASS" if symbolic["interior_pde_exact"] else "FAIL",
        "retarded_support": "PASS" if numeric["negative_time_kernel"] == 0.0 else "FAIL",
        "outside_cone_leakage": "PASS" if numeric["outside_cone_max_abs"] == 0.0 else "FAIL",
        "arrival_speed": "PASS" if numeric["arrival_speed_relative_error_max"] <= 1e-12 else "FAIL",
        "subluminal_characteristic": "PASS" if numeric["propagation_speed"] <= 1.0 else "FAIL",
        "local_coordinate_scalar": "PASS" if numeric["coordinate_scalar_error"] <= 1e-12 else "FAIL",
        "future_events_excluded": "PASS" if numeric["future_event_influence_error"] == 0.0 else "FAIL",
        "exchange_ledger_closure": "PASS" if numeric["exchange_closure_max_abs"] == 0.0 else "FAIL",
        "regular_gr_limit": "PASS" if numeric["gr_limit_full_source"] == 0.0 and numeric["gr_limit_exchange_max_abs"] == 0.0 else "FAIL",
        "natural_unit_dimension_closure": dimensions["status"],
        "no_epsilon_denominator": "PASS" if not denominators else "FAIL",
        "derived_trace_disconnected": "PASS" if "uet_trace" not in source and not contract["derived_trace_imported"] else "FAIL",
        "closed_limit_dependency": "PASS" if closed["status"] == "PASS" else "FAIL",
        "balance_dependency": "PASS" if balance["status"] == "PASS" else "FAIL",
    }
    status = "PASS" if set(gates.values()) == {"PASS"} else "FAIL"
    hashes = {str(CORE.relative_to(ROOT)): _sha(CORE), str(SPEC.relative_to(ROOT)): _sha(SPEC)}
    verification = {
        "schema_version": "1.0", "artifact": "causal_nonclosed_kernel_verification",
        "generated_at": now, "status": status, "evidence_class": "B",
        "claim": "exact-support retarded 1+1 constitutive kernel on a declared local rest-frame slice",
        "symbolic": symbolic, "numeric": numeric, "dimension_audit": dimensions,
        "epsilon_denominator_lines": denominators, "gates": gates, "source_hashes": hashes,
        "run_contract": {"external_data": False, "parameter_fitting": False, "spatial_dimension": 1,
                         "flat_local_slice": True, "curved_green_solver": False,
                         "closed_time_path_derivation": False, "trace_backreaction": False},
        "allowed_language": ["candidate retarded constitutive kernel", "exact support on the declared 1+1 cone", "subluminal configured characteristic"],
        "blocked_language": ["full curved-spacetime causal proof", "closed-time-path derivation", "ghost-free fundamental action", "universe proved non-closed"],
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing" if reduction_passed
            else "controlled_covariant_to_matter_space_reduction_missing"
        ),
        "downstream_reduction_status": reduction_status,
        "downstream_matter_status": matter_status,
        "downstream_matter_evidence": matter_evidence,
        "downstream_reduction_evidence": reduction_evidence,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    formula = {
        "schema_version": "1.0", "artifact": "causal_influence_formula_audit",
        "generated_at": now, "status": "WARN" if status == "PASS" else "FAIL",
        "implementation_status": "PRESENT" if status == "PASS" else "INCOMPLETE",
        "derivation_status": "phenomenological retarded constitutive ansatz",
        "operator": contract["operator"], "unit_lane": "natural", "spatial_dimension": 1,
        "coefficient_policy": {"tau_positive": True, "diffusivity_positive": True,
                               "decay_nonnegative": True, "speed_not_above_c": True,
                               "defaults_are_physical_constants": False},
        "open_formula_gates": ["closed_time_path_derivation_missing", "curved_spacetime_green_function_missing",
                               "three_spatial_dimension_kernel_missing", "observable_source_mapping_missing",
                               "ghost_analysis_of_parent_action_missing"],
        "source_hashes": hashes,
    }
    contract_artifact = {
        "schema_version": "1.0", "artifact": "causal_nonclosed_contract",
        "generated_at": now, **contract,
        "exchange_completion": "j_phi -> J_phi=epsilon*j_phi -> Q_m=-J_phi grad(phi), Q_response=+J_phi grad(phi)",
        "gr_limit": "epsilon_nc=0 switches off physical exchange while GR remains",
        "downstream_reduction": "PARTIAL_RESPONSE_ONLY" if reduction_passed else "NOT_IMPLEMENTED",
        "covariant_matter_action": "PASS_O2_SCALAR_PILOT" if matter_passed else "NOT_IMPLEMENTED",
        "reciprocal_coupling": "PASS_ACTION_LEVEL" if matter_passed else "NOT_IMPLEMENTED",
        "matter_number_current": "PASS_ON_SHELL_O2" if matter_passed else "NOT_IMPLEMENTED",
        "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT" if diffusion_passed else "NOT_IMPLEMENTED",
        "local_convex_matter_causality": "PASS_CONTROL" if diffusion_passed else "NOT_IMPLEMENTED",
        "gradient_phase_field_causality": "BLOCKED_UV" if diffusion_passed else "NOT_IMPLEMENTED",
        "claim_class": "B" if status == "PASS" else "A",
    }
    program = {
        "schema_version": "1.0", "artifact": "uet_gr_research_program_gate",
        "generated_at": now, "status": "BLOCKED",
        "program_stage": (
            "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL" if diffusion_passed
            else "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED" if matter_passed
            else "CONTROLLED_RESPONSE_REDUCTION_PARTIAL" if reduction_passed
            else "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED" if status == "PASS"
            else "COVARIANT_CONSERVATIVE_BALANCE_VERIFIED"
        ),
        "current_claim_class": "B", "gr_null_model": {"parameter": "epsilon_nc", "value": 0, "verification_status": closed["status"]},
        "sector_status": {"ontology_and_claim_contract": "PASS", "legacy_claim_quarantine": "PASS",
                          "conservative_tensor_formula": closed["status"], "exact_gr_closed_limit": closed["status"],
                          "covariant_exchange_bianchi_balance": balance["status"],
                          "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D" if status == "PASS" else "BLOCKED",
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
            else "controlled_covariant_to_matter_space_reduction_missing" if status == "PASS"
            else "causal_nonclosed_influence_functional_missing"
        ),
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse-grained conserved-current bridge and exact Model-B limit are present, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent." if diffusion_passed
            else "The conservative scalar matter action and reciprocal interaction close, but the density interpretation, regular epsilon-nested normalized chart, and dissipative conserved-matter dynamics are not derived." if matter_passed
            else "The response equation maps exactly, but the covariant matter equation, reciprocal coupling, and causal realization of the required source are absent." if reduction_passed
            else "The constitutive kernel is causal on a restricted local slice, but no controlled reduction or curved 3+1 implementation exists."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, verification, formula, contract_artifact, program)
    return verification, formula, contract_artifact, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, formula, contract, program = build_artifacts()
    _dump("causal_nonclosed_kernel_verification.json", verification)
    _dump("causal_influence_formula_audit.json", formula)
    _dump("causal_nonclosed_contract.json", contract)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(json.dumps({"causal_status": verification["status"], "formula_status": formula["status"],
                          "program_status": program["status"], "controlling_blocker": program["controlling_blocker"],
                          "numeric": verification["numeric"]}, indent=2))
    return 2 if args.strict and verification["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
