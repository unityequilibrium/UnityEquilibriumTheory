"""Verify the controlled response-sector reduction to matter_space_coupled_v1."""

from __future__ import annotations

import argparse
import hashlib
import inspect
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

from docs.core.uet_covariant_reduction import (  # noqa: E402
    WeakFieldReductionConfig,
    compare_response_reduction,
    derive_response_coefficients,
    dimensional_scalar_source_minus_curvature_drive,
    matter_space_config_from_reduction,
    reduction_contract,
)
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_matter_space import MatterSpaceConfig  # noqa: E402
from docs.core.core_paths import canonical_artifact_path, canonical_existing_path  # noqa: E402

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_reduction.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
OUT = ROOT / "docs/core/07_artifacts"
CAUSAL = canonical_artifact_path("causal_nonclosed_kernel_verification.json", "verification")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _symbolic() -> dict[str, Any]:
    tau, mobility, T, L, Z, mass_sq, quartic, field_scale = sp.symbols(
        "tau mobility T L Z mass_sq quartic field_scale", positive=True
    )
    phi, phi3, lap, rate, matter_sq, coupling, drive = sp.symbols(
        "phi phi3 lap rate matter_sq coupling drive"
    )
    speed_sq = T**2 / L**2
    mass_rate = mass_sq * T**2 / Z
    quartic_rate = quartic * field_scale**2 * T**2 / Z
    a = tau * mass_rate / mobility
    b = tau * quartic_rate / mobility
    kappa = tau * speed_sq / mobility
    source = rate / tau - mobility * coupling * matter_sq / (2 * tau) - drive / tau
    covariant_acceleration = speed_sq * lap - mass_rate * phi - quartic_rate * phi3 - source
    chemical_potential = a * phi + b * phi3 - kappa * lap - coupling * matter_sq / 2
    matter_space_acceleration = (-rate - mobility * chemical_potential + drive) / tau
    difference = sp.simplify(covariant_acceleration - matter_space_acceleration)
    target_speed = sp.simplify(sp.sqrt(mobility * kappa / tau))
    return {
        "response_acceleration_difference": str(difference),
        "response_mapping_exact": difference == 0,
        "mapped_characteristic_speed": str(target_speed),
        "expected_normalized_light_speed": str(T / L),
        "characteristic_map_exact": sp.simplify(target_speed - T / L) == 0,
        "mapped_coefficients": {
            "a_space": str(a),
            "b_space": str(b),
            "kappa_space": str(kappa),
        },
    }


def _numeric() -> dict[str, Any]:
    rng = np.random.default_rng(190041)
    covariant = CovariantResponseConfig(
        epsilon_nc=.3,
        response_kinetic=1.2,
        response_mass_sq=.8,
        response_quartic=.35,
    )
    reduction = WeakFieldReductionConfig(
        length_scale=2.0,
        time_scale=.8,
        response_field_scale=.45,
        mobility_space=.7,
        tau_space=1.3,
        coupling_g=.22,
    )
    shape = 128
    response = rng.normal(scale=.15, size=shape)
    rate = rng.normal(scale=.08, size=shape)
    laplacian = rng.normal(scale=.12, size=shape)
    matter = rng.normal(loc=.3, scale=.05, size=shape)
    drive = rng.normal(scale=.02, size=shape)
    comparison = compare_response_reduction(
        response, rate, laplacian, matter, drive, covariant, reduction
    )
    coefficients = comparison["coefficients"]
    template = MatterSpaceConfig(
        a_matter=-.5,
        b_matter=.8,
        kappa_matter=.4,
        mobility_matter=.3,
    )
    mapped = matter_space_config_from_reduction(covariant, reduction, template)
    source_dimensional = dimensional_scalar_source_minus_curvature_drive(
        comparison["required_dimensionless_scalar_source"], covariant, reduction
    )
    epsilon_zero_rejected = False
    try:
        derive_response_coefficients(
            CovariantResponseConfig(epsilon_nc=0.0), reduction
        )
    except ValueError:
        epsilon_zero_rejected = True
    return {
        "response_acceleration_max_abs_difference": comparison["max_abs_difference"],
        "mapped_speed": mapped.space_speed,
        "expected_normalized_light_speed": reduction.normalized_light_speed,
        "mapped_a_space": mapped.a_space,
        "mapped_b_space": mapped.b_space,
        "mapped_kappa_space": mapped.kappa_space,
        "matter_template_preserved": bool(
            mapped.a_matter == template.a_matter
            and mapped.b_matter == template.b_matter
            and mapped.kappa_matter == template.kappa_matter
            and mapped.mobility_matter == template.mobility_matter
        ),
        "dimensional_source_all_finite": bool(np.all(np.isfinite(source_dimensional))),
        "epsilon_zero_branch_rejected": epsilon_zero_rejected,
        "coefficient_record": {
            "a_space": coefficients.a_space,
            "b_space": coefficients.b_space,
            "kappa_space": coefficients.kappa_space,
            "mobility_space": coefficients.mobility_space,
            "tau_space": coefficients.tau_space,
            "coupling_g": coefficients.coupling_g,
        },
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic, numeric, contract = _symbolic(), _numeric(), reduction_contract()
    causal = json.loads(CAUSAL.read_text(encoding="utf-8"))
    source = CORE.read_text(encoding="utf-8")
    signature = inspect.signature(compare_response_reduction)
    matter_path = canonical_artifact_path("covariant_matter_action_verification.json", "verification")
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
    diffusion_path = canonical_artifact_path("covariant_diffusive_current_verification.json", "verification")
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
    achieved_gates = {
        "symbolic_response_equation_map": "PASS" if symbolic["response_mapping_exact"] else "FAIL",
        "numeric_response_equation_map": "PASS" if numeric["response_acceleration_max_abs_difference"] <= 1e-12 else "FAIL",
        "characteristic_scale_map": "PASS" if symbolic["characteristic_map_exact"] and abs(numeric["mapped_speed"] - numeric["expected_normalized_light_speed"]) <= 1e-12 else "FAIL",
        "matter_template_not_relabelled_as_derived": "PASS" if numeric["matter_template_preserved"] else "FAIL",
        "dimensional_source_map_finite": "PASS" if numeric["dimensional_source_all_finite"] else "FAIL",
        "gr_branch_not_divided_by_epsilon": "PASS" if numeric["epsilon_zero_branch_rejected"] and "/ covariant.epsilon_nc" not in source else "FAIL",
        "derived_trace_disconnected": "PASS" if "trace" not in signature.parameters and not contract["derived_trace_backreaction"] else "FAIL",
        "causal_dependency": "PASS" if causal["status"] == "PASS" else "FAIL",
    }
    blocked_gates = {
        ("first_order_hyperbolic_phase_field_uv_closure" if diffusion_passed else "regular_covariant_to_diffusive_matter_reduction" if matter_passed else "covariant_matter_action"): "BLOCKED",
        ("closed_time_path_kms_transport_matching" if diffusion_passed else "regular_nested_normalized_epsilon_map" if matter_passed else "reciprocal_matter_coupling_derivation"): "BLOCKED",
        "required_source_from_causal_kernel": "BLOCKED",
        "full_coupled_matter_space_reduction": "BLOCKED",
        "system_specific_SI_map": "BLOCKED",
    }
    audit_status = "PASS" if set(achieved_gates.values()) == {"PASS"} else "FAIL"
    evidence_status = "PARTIAL" if audit_status == "PASS" else "BLOCKED"
    hashes = {str(CORE.relative_to(ROOT)): _sha(CORE), str(SPEC.relative_to(ROOT)): _sha(SPEC)}
    verification = {
        "schema_version": "1.0", "artifact": "covariant_matter_space_reduction_verification",
        "generated_at": now, "audit_status": audit_status, "evidence_status": evidence_status,
        "claim_class": "B", "claim": "exact response-sector coefficient map under declared weak-field scaling assumptions",
        "symbolic": symbolic, "numeric": numeric,
        "achieved_gates": achieved_gates, "blocked_gates": blocked_gates,
        "source_hashes": hashes,
        "run_contract": {"seed": 190041, "external_data": False, "parameter_fitting": False,
                         "response_sector_only": True, "full_matter_equation_derived": False,
                         "epsilon_zero_operator_active": False, "trace_backreaction": False},
        "allowed_language": ["exact response-sector reduction under declared scaling", "partial bridge to matter_space_coupled_v1"],
        "blocked_language": ["full matter-space model derived from the covariant parent", "microscopic dissipative matter transport derived", "causal bath source derived", "Topic 0.11 or 0.19 validated"],
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing"
        ),
        "downstream_matter_status": matter_status,
        "downstream_matter_evidence": matter_evidence,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    contract_artifact = {
        "schema_version": "1.0", "artifact": "covariant_reduction_contract",
        "generated_at": now, **contract,
        "coefficient_map": symbolic["mapped_coefficients"],
        "source_map": "j_hat=Pi/tau-M*g*C^2/(2*tau)-J_Phi/tau",
        "epsilon_policy": "adapter requires epsilon_nc>0; epsilon_nc=0 selects GR and no response operator",
        "unit_policy": "declared natural scales to normalized coefficients; not an SI calibration",
        "downstream_matter_status": matter_status,
        "downstream_matter_evidence": matter_evidence,
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing" if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else contract["next_controller"]
        ),
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    program = {
        "schema_version": "1.0", "artifact": "uet_gr_research_program_gate",
        "generated_at": now, "status": "BLOCKED",
        "program_stage": (
            "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL" if diffusion_passed
            else
            "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED" if matter_passed
            else "CONTROLLED_RESPONSE_REDUCTION_PARTIAL" if audit_status == "PASS"
            else "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED"
        ),
        "current_claim_class": "B", "gr_null_model": {"parameter": "epsilon_nc", "value": 0, "verification_status": "PASS"},
        "sector_status": {"ontology_and_claim_contract": "PASS", "legacy_claim_quarantine": "PASS",
                          "conservative_tensor_formula": "PASS", "exact_gr_closed_limit": "PASS",
                          "covariant_exchange_bianchi_balance": "PASS", "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
                          "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
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
            else
            "regular_covariant_to_diffusive_matter_reduction_missing" if matter_passed
            else "covariant_matter_action_and_reciprocal_coupling_missing"
        ),
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse-grained conserved-current bridge and exact Model-B limit are present, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent." if diffusion_passed
            else "The conservative scalar matter action and reciprocal interaction close, but the density interpretation, regular epsilon-nested normalized chart, and dissipative conserved-matter dynamics are not derived." if matter_passed
            else "The response equation maps exactly, but the covariant matter equation, reciprocal coupling, and causal realization of the required source are absent."
        ),
    }
    apply_latest_hyperbolic_phase_field_stage(OUT, verification, contract_artifact, program)
    return verification, contract_artifact, program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    verification, contract, program = build_artifacts()
    _dump("covariant_matter_space_reduction_verification.json", verification)
    _dump("covariant_reduction_contract.json", contract)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(json.dumps({"audit_status": verification["audit_status"], "evidence_status": verification["evidence_status"],
                          "program_status": program["status"], "controlling_blocker": program["controlling_blocker"],
                          "numeric": verification["numeric"]}, indent=2))
    return 2 if args.strict and verification["audit_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
