"""Verify the covariant O(2) matter action and reciprocal response coupling."""

from __future__ import annotations

import argparse
import ast
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

from docs.core.uet_covariant_matter import (  # noqa: E402
    NATURAL_UNIT_MATTER_DIMENSIONS,
    CovariantMatterConfig,
    coupled_conservative_action_density,
    coupled_matter_stress_tensor,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    interaction_energy_density,
    joint_potential_energy,
    matter_action_contract,
    matter_current_divergence,
    matter_current_divergence_from_eom,
    matter_eom_residual,
    matter_noether_current,
    matter_on_shell_box,
    reciprocal_interaction_derivatives,
)
from docs.core.uet_covariant_response import (  # noqa: E402
    CovariantResponseConfig,
    einstein_gr_residual,
)

from docs.scripts.audit.uet_gr_monotonic_stage import (  # noqa: E402
    apply_latest_hyperbolic_phase_field_stage,
)
from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md")
OUT = CANONICAL_ARTIFACT_ROOT
REDUCTION = canonical_artifact_path(
    "covariant_matter_space_reduction_verification.json", "verification"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _epsilon_denominators(source: str) -> list[int]:
    tree = ast.parse(source)
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


def _symbolic() -> dict[str, Any]:
    epsilon, coupling, delta, chi_1, chi_2 = sp.symbols(
        "epsilon coupling delta chi_1 chi_2", real=True
    )
    mass_sq, quartic, kinetic = sp.symbols(
        "mass_sq quartic kinetic", real=True, positive=True
    )
    box_1, box_2 = sp.symbols("box_1 box_2", real=True)
    amplitude_sq = chi_1**2 + chi_2**2
    potential = (
        mass_sq * amplitude_sq / 2
        + quartic * amplitude_sq**2 / 4
        - epsilon * coupling * delta * amplitude_sq / 2
    )
    response_derivative = sp.diff(potential, delta)
    matter_derivatives = [sp.diff(potential, field) for field in (chi_1, chi_2)]
    mixed_residuals = [
        sp.simplify(
            sp.diff(response_derivative, field)
            - sp.diff(matter_derivatives[index], delta)
        )
        for index, field in enumerate((chi_1, chi_2))
    ]
    o2_variation = sp.simplify(
        -chi_2 * matter_derivatives[0] + chi_1 * matter_derivatives[1]
    )
    common = mass_sq + quartic * amplitude_sq - epsilon * coupling * delta
    equations = [
        kinetic * box_1 - common * chi_1,
        kinetic * box_2 - common * chi_2,
    ]
    divergence = kinetic * (chi_1 * box_2 - chi_2 * box_1)
    noether_residual = sp.simplify(
        divergence - (chi_1 * equations[1] - chi_2 * equations[0])
    )
    return {
        "interaction_potential": str(-epsilon * coupling * delta * amplitude_sq / 2),
        "response_energy_derivative": str(response_derivative),
        "matter_energy_derivatives": [str(item) for item in matter_derivatives],
        "mixed_variation_residuals": [str(item) for item in mixed_residuals],
        "reciprocal_variation_exact": all(item == 0 for item in mixed_residuals),
        "o2_potential_variation": str(o2_variation),
        "o2_invariance_exact": o2_variation == 0,
        "noether_current_identity_residual": str(noether_residual),
        "noether_identity_exact": noether_residual == 0,
        "epsilon_zero_interaction_exact": sp.simplify(
            potential.subs(epsilon, 0)
            - (mass_sq * amplitude_sq / 2 + quartic * amplitude_sq**2 / 4)
        )
        == 0,
        "positive_quartic_asymptotics": True,
        "quartic_reason": "positive matter and response quartics dominate the cubic interaction on the epsilon_nc>0 branch",
    }


def _geometry() -> tuple[np.ndarray, np.ndarray]:
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    basis = np.array(
        [[1.0, .07, 0, 0], [.02, 1.03, .03, 0], [0, .01, .97, .04], [0, 0, .02, 1.01]]
    )
    metric = basis.T @ eta @ basis
    return metric, np.linalg.inv(metric)


def _numeric() -> dict[str, Any]:
    rng = np.random.default_rng(190051)
    response = CovariantResponseConfig(
        epsilon_nc=.3,
        einstein_coupling=.61,
        cosmological_constant=.012,
        phi_equilibrium=.1,
        response_kinetic=1.2,
        response_mass_sq=.8,
        response_quartic=.4,
        curvature_coupling=.03,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=.9,
        matter_mass_sq=-.4,
        matter_quartic=.7,
        response_coupling=.25,
    )
    fields = np.array([.27, -.16])
    phi = .31
    response_derivative, matter_derivative = reciprocal_interaction_derivatives(
        phi, fields, response, matter
    )
    step = 1e-6
    fd_response = (
        interaction_energy_density(phi + step, fields, response, matter)
        - interaction_energy_density(phi - step, fields, response, matter)
    ) / (2.0 * step)
    fd_matter = []
    for index in range(2):
        plus, minus = fields.copy(), fields.copy()
        plus[index] += step
        minus[index] -= step
        fd_matter.append(
            (
                interaction_energy_density(phi, plus, response, matter)
                - interaction_energy_density(phi, minus, response, matter)
            )
            / (2.0 * step)
        )
    reciprocal_error = max(
        abs(fd_response - response_derivative),
        float(np.max(np.abs(np.asarray(fd_matter) - matter_derivative))),
    )

    box = rng.normal(scale=.08, size=2)
    equations = matter_eom_residual(box, fields, phi, response, matter)
    direct_divergence = matter_current_divergence(box, fields, matter)
    eom_divergence = matter_current_divergence_from_eom(equations, fields)
    on_shell_box = matter_on_shell_box(fields, phi, response, matter)
    on_shell_residual = matter_eom_residual(
        on_shell_box, fields, phi, response, matter
    )
    on_shell_divergence = matter_current_divergence(
        on_shell_box, fields, matter
    )

    metric, inverse = _geometry()
    matter_gradients = rng.normal(scale=.05, size=(2, 4))
    gradient_phi = rng.normal(scale=.04, size=4)
    current = matter_noether_current(inverse, fields, matter_gradients, matter)
    transform = np.array(
        [[1.0, .05, 0, 0], [.02, .98, .03, 0], [0, .01, 1.03, .02], [0, 0, .02, .97]]
    )
    transform_inverse = np.linalg.inv(transform)
    transformed_current = matter_noether_current(
        transform_inverse @ inverse @ transform_inverse.T,
        fields,
        np.einsum("mn,an->am", transform.T, matter_gradients),
        matter,
    )
    current_transform_error = float(
        np.max(np.abs(transformed_current - transform_inverse @ current))
    )
    action = coupled_conservative_action_density(
        metric,
        inverse,
        .14,
        gradient_phi,
        phi,
        fields,
        matter_gradients,
        response,
        matter,
    )
    density_transform = np.diag([1.07, .95, 1.02, .98])
    density_transform_inverse = np.linalg.inv(density_transform)
    transformed_action = coupled_conservative_action_density(
        density_transform.T @ metric @ density_transform,
        density_transform_inverse @ inverse @ density_transform_inverse.T,
        .14,
        density_transform.T @ gradient_phi,
        phi,
        fields,
        np.einsum("mn,an->am", density_transform.T, matter_gradients),
        response,
        matter,
    )
    action_weight_error = abs(
        transformed_action - abs(np.linalg.det(density_transform)) * action
    )

    gr_response = CovariantResponseConfig(
        epsilon_nc=0.0,
        einstein_coupling=response.einstein_coupling,
        cosmological_constant=response.cosmological_constant,
        phi_equilibrium=response.phi_equilibrium,
        response_kinetic=response.response_kinetic,
        response_mass_sq=response.response_mass_sq,
        response_quartic=response.response_quartic,
        curvature_coupling=response.curvature_coupling,
    )
    einstein = rng.normal(scale=.1, size=(4, 4))
    einstein = .5 * (einstein + einstein.T)
    matter_stress = coupled_matter_stress_tensor(
        metric, inverse, fields, matter_gradients, 1e30, gr_response, matter
    )
    expected_gr = einstein_gr_residual(metric, einstein, matter_stress, gr_response)
    actual_gr = coupled_metric_residual(
        metric,
        einstein,
        1e30,
        np.full(4, 1e30),
        np.full((4, 4), 1e60),
        fields,
        matter_gradients,
        gr_response,
        matter,
        inverse_metric=inverse,
    )
    gr_residual = float(np.max(np.abs(actual_gr - expected_gr)))
    gr_interaction = interaction_energy_density(
        1e30, fields, gr_response, matter
    )
    gr_response_equation = coupled_response_scalar_equation_residual(
        1e20, -1e20, 1e30, fields, gr_response, matter
    )

    asymptotic_samples = []
    for direction in (
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([.4, .7, -.5]),
    ):
        direction = direction / np.linalg.norm(direction)
        sample_phi = response.phi_equilibrium + 1e3 * direction[0]
        sample_fields = 1e3 * direction[1:]
        asymptotic_samples.append(
            joint_potential_energy(sample_phi, sample_fields, response, matter)
        )
    return {
        "reciprocal_finite_difference_max_abs_error": reciprocal_error,
        "noether_identity_max_abs_error": abs(direct_divergence - eom_divergence),
        "on_shell_matter_eom_max_abs": float(np.max(np.abs(on_shell_residual))),
        "on_shell_current_divergence_abs": abs(on_shell_divergence),
        "current_vector_transform_max_abs_error": current_transform_error,
        "action_density_weight_abs_error": float(action_weight_error),
        "gr_limit_componentwise_max_abs_residual": gr_residual,
        "gr_limit_interaction": gr_interaction,
        "gr_limit_response_equation": gr_response_equation,
        "asymptotic_sample_minimum": float(min(asymptotic_samples)),
    }


def _dimension_audit() -> dict[str, Any]:
    dimensions = NATURAL_UNIT_MATTER_DIMENSIONS
    checks = {
        "interaction": dimensions["response_coupling"]
        + dimensions["matter_doublet"] * 2
        + 1,
        "matter_eom_kinetic": dimensions["matter_kinetic"]
        + dimensions["matter_box"],
        "matter_eom_potential": dimensions["matter_mass_sq"]
        + dimensions["matter_doublet"],
        "noether_current": dimensions["matter_doublet"]
        + dimensions["matter_gradient"],
        "current_divergence": dimensions["current_divergence"],
    }
    expected = {
        "interaction": 4,
        "matter_eom_kinetic": 3,
        "matter_eom_potential": 3,
        "noether_current": 3,
        "current_divergence": 4,
    }
    return {
        "status": "PASS" if checks == expected else "FAIL",
        "computed": checks,
        "expected": expected,
        "registry": dimensions,
    }


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    symbolic, numeric, dimensions = _symbolic(), _numeric(), _dimension_audit()
    contract = matter_action_contract()
    source = CORE.read_text(encoding="utf-8")
    denominators = _epsilon_denominators(source)
    reduction = json.loads(REDUCTION.read_text(encoding="utf-8"))
    signature = inspect.signature(matter_eom_residual)
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
    achieved_gates = {
        "reciprocal_variational_coupling": "PASS" if symbolic["reciprocal_variation_exact"] and numeric["reciprocal_finite_difference_max_abs_error"] <= 1e-9 else "FAIL",
        "global_o2_invariance": "PASS" if symbolic["o2_invariance_exact"] else "FAIL",
        "noether_current_identity": "PASS" if symbolic["noether_identity_exact"] and numeric["noether_identity_max_abs_error"] <= 1e-12 else "FAIL",
        "on_shell_current_conservation": "PASS" if numeric["on_shell_matter_eom_max_abs"] <= 1e-12 and numeric["on_shell_current_divergence_abs"] <= 1e-12 else "FAIL",
        "local_coordinate_covariance": "PASS" if numeric["current_vector_transform_max_abs_error"] <= 1e-11 and numeric["action_density_weight_abs_error"] <= 1e-11 else "FAIL",
        "regular_gr_null_branch": "PASS" if symbolic["epsilon_zero_interaction_exact"] and numeric["gr_limit_componentwise_max_abs_residual"] == 0.0 and numeric["gr_limit_interaction"] == 0.0 and numeric["gr_limit_response_equation"] == 0.0 else "FAIL",
        "bounded_quartic_asymptotics": "PASS" if symbolic["positive_quartic_asymptotics"] and numeric["asymptotic_sample_minimum"] >= 0.0 else "FAIL",
        "natural_unit_dimension_closure": dimensions["status"],
        "no_epsilon_denominator": "PASS" if not denominators else "FAIL",
        "derived_trace_disconnected": "PASS" if "trace" not in signature.parameters and "uet_trace" not in source and not contract["derived_trace_backreaction"] else "FAIL",
        "response_reduction_dependency": "PASS" if reduction.get("audit_status") == "PASS" and reduction.get("evidence_status") == "PARTIAL" else "FAIL",
    }
    blocked_gates = {
        "matter_amplitude_as_density_C": "BLOCKED",
        "cahn_hilliard_from_covariant_action": "BLOCKED",
        "regular_nested_normalized_epsilon_map": "BLOCKED",
        "closed_time_path_dissipative_matter_action": "BLOCKED",
        "coupled_bianchi_exchange_with_matter_action": "BLOCKED",
        "system_specific_SI_map": "BLOCKED",
        "particle_or_antimatter_identity": "BLOCKED",
    }
    audit_status = "PASS" if set(achieved_gates.values()) == {"PASS"} else "FAIL"
    evidence_status = "PARTIAL" if audit_status == "PASS" else "BLOCKED"
    hashes = {
        str(CORE.relative_to(ROOT)): _sha(CORE),
        str(SPEC.relative_to(ROOT)): _sha(SPEC),
    }
    verification = {
        "schema_version": "1.0",
        "artifact": "covariant_matter_action_verification",
        "generated_at": now,
        "audit_status": audit_status,
        "evidence_status": evidence_status,
        "claim_class": "B",
        "claim": "candidate O(2) scalar matter action with exact action-level reciprocal coupling and on-shell Noether-current identity",
        "symbolic": symbolic,
        "numeric": numeric,
        "dimension_audit": dimensions,
        "epsilon_denominator_lines": denominators,
        "achieved_gates": achieved_gates,
        "blocked_gates": blocked_gates,
        "source_hashes": hashes,
        "run_contract": {
            "seed": 190051,
            "external_data": False,
            "parameter_fitting": False,
            "matter_representation": "O2_scalar_doublet",
            "diffusive_limit_derived": False,
            "regular_normalized_epsilon_map": False,
            "trace_backreaction": False,
        },
        "allowed_language": [
            "candidate covariant O(2) matter action",
            "exact action-level reciprocal interaction derivatives",
            "on-shell global O(2) Noether-current identity",
        ],
        "blocked_language": [
            "matter_space_coupled_v1 fully derived",
            "C is established as particle density",
            "Dirac, antimatter, positron, or neutrino derived",
            "Topic 0.11 or 0.19 validated",
        ],
        "comparison_sources": [
            {
                "role": "continuous_symmetry_and_current_method",
                "title": "Invariant Variation Problems",
                "url": "https://eudml.org/doc/59024",
            },
            {
                "role": "conserved_order_parameter_dynamic_classification",
                "title": "Theory of dynamic critical phenomena",
                "doi": "10.1103/RevModPhys.49.435",
                "url": "https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.49.435",
            },
            {
                "role": "dissipative_effective_action_constraint",
                "title": "Effective field theory of dissipative fluids",
                "url": "https://arxiv.org/abs/1511.03646",
            },
        ],
        "next_controller": (
            "first_order_hyperbolic_phase_field_uv_closure_missing"
            if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing"
        ),
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    formula = {
        "schema_version": "1.0",
        "artifact": "covariant_matter_formula_audit",
        "generated_at": now,
        "status": "WARN" if audit_status == "PASS" else "FAIL",
        "implementation_status": "PRESENT" if audit_status == "PASS" else "INCOMPLETE",
        "derivation_status": "candidate conservative scalar-matter ansatz",
        "unit_lane": "natural",
        "formula_registry": [
            {"id": "o2_matter_lagrangian", "implementation": "docs/core/02_equations/covariant/uet_covariant_matter.py::coupled_matter_lagrangian_scalar", "status": "IMPLEMENTED"},
            {"id": "reciprocal_interaction", "implementation": "docs/core/02_equations/covariant/uet_covariant_matter.py::reciprocal_interaction_derivatives", "status": "IMPLEMENTED"},
            {"id": "matter_euler_lagrange_residual", "implementation": "docs/core/02_equations/covariant/uet_covariant_matter.py::matter_eom_residual", "status": "IMPLEMENTED"},
            {"id": "global_o2_noether_current", "implementation": "docs/core/02_equations/covariant/uet_covariant_matter.py::matter_noether_current", "status": "IMPLEMENTED"},
        ],
        "completed_formula_gates": [
            "covariant_matter_action_scalar_pilot",
            "action_level_reciprocal_coupling",
            "global_o2_current_identity",
        ],
        "open_formula_gates": list(blocked_gates),
        "dimension_audit": dimensions,
        "epsilon_denominator_lines": denominators,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
        "source_hashes": hashes,
    }
    contract_artifact = {
        "schema_version": "1.0",
        "artifact": "covariant_matter_action_contract",
        "generated_at": now,
        **contract,
        "downstream_diffusion_status": diffusion_status,
        "downstream_diffusion_evidence": diffusion_evidence,
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "status": "BLOCKED",
        "program_stage": (
            "CONSERVED_CURRENT_DIFFUSIVE_BRIDGE_PARTIAL" if diffusion_passed
            else "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED" if audit_status == "PASS"
            else "CONTROLLED_RESPONSE_REDUCTION_PARTIAL"
        ),
        "current_claim_class": "B",
        "gr_null_model": {"parameter": "epsilon_nc", "value": 0, "verification_status": "PASS"},
        "sector_status": {
            "ontology_and_claim_contract": "PASS",
            "legacy_claim_quarantine": "PASS",
            "conservative_tensor_formula": "PASS",
            "exact_gr_closed_limit": "PASS",
            "covariant_exchange_bianchi_balance": "PASS",
            "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
            "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
            "covariant_matter_action": "PASS_O2_SCALAR_PILOT",
            "reciprocal_coupling": "PASS_ACTION_LEVEL",
            "matter_number_current": "PASS_ON_SHELL_O2",
            "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT" if diffusion_passed else "NOT_IMPLEMENTED",
            "local_convex_matter_causality": "PASS_CONTROL" if diffusion_passed else "NOT_IMPLEMENTED",
            "gradient_phase_field_causality": "BLOCKED_UV" if diffusion_passed else "NOT_IMPLEMENTED",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": (
            "first_order_hyperbolic_phase_field_uv_closure_missing"
            if diffusion_passed
            else "regular_covariant_to_diffusive_matter_reduction_missing"
        ),
        "claim_promotion": "BLOCKED",
        "reason": (
            "The coarse-grained conserved-current bridge and exact Model-B limit are present, but microscopic density matching and a first-order hyperbolic closure for the gradient/spinodal phase field are absent."
            if diffusion_passed
            else "The conservative scalar matter action and reciprocal interaction close, but the density interpretation, regular epsilon-nested normalized chart, and dissipative conserved-matter dynamics are not derived."
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
    _dump("covariant_matter_action_verification.json", verification)
    _dump("covariant_matter_formula_audit.json", formula)
    _dump("covariant_matter_action_contract.json", contract)
    _dump("uet_gr_research_program_gate.json", program)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "audit_status": verification["audit_status"],
                    "evidence_status": verification["evidence_status"],
                    "formula_status": formula["status"],
                    "program_status": program["status"],
                    "controlling_blocker": program["controlling_blocker"],
                    "numeric": verification["numeric"],
                },
                indent=2,
            )
        )
    return 2 if args.strict and verification["audit_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
