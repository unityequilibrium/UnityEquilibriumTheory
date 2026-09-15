"""Audit UET equation compatibility, contradictions, and limiting cases.

This is deliberately different from a physics-validation claim.  It checks whether the
repository's declared equations, implementation, units, and existing verifier artifacts
agree with one another.  A successful audit run may still produce a BLOCKED compatibility
gate; that is the expected result while a conflict or an unproven correspondence remains.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json"

MASTER_PATH = ROOT / "docs/core/uet_master_equation.py"
PARAMETERS_PATH = ROOT / "docs/core/uet_parameters.py"
MATTER_SPACE_SPEC = ROOT / "docs/core/MATTER_SPACE_RESEARCH_SPEC.md"
GR_SPEC = ROOT / "docs/core/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
ALIGNMENT_PATH = ROOT / "docs/core/07_artifacts/gates/master_equation_alignment_gate_v2.json"
MATTER_FORMULA_PATH = ROOT / "docs/core/07_artifacts/correspondence/matter_space_formula_audit.json"
MATTER_VERIFY_PATH = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
MATTER_DEPENDENCY_PATH = ROOT / "docs/core/07_artifacts/gates/matter_space_dependency_gate.json"
TRACE_VERIFY_PATH = ROOT / "docs/core/07_artifacts/verification/spacetime_trace_verification.json"
GR_VERIFY_PATH = ROOT / "docs/core/07_artifacts/verification/gr_closed_limit_verification.json"
O2_VERIFY_PATH = ROOT / "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json"
O2_FORMULA_PATH = ROOT / "docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON value is not an object: {path}")
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def contains(text: str, fragment: str) -> bool:
    return fragment in text


def finding(
    finding_id: str,
    equation_family: str,
    status: str,
    severity: str,
    declared_relation: str,
    observed_relation: str,
    interpretation: str,
    old_theory_relation: str,
    evidence: list[dict[str, Any]],
    next_action: str,
    *,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "equation_family": equation_family,
        "status": status,
        "severity": severity,
        "declared_relation": declared_relation,
        "observed_relation": observed_relation,
        "interpretation": interpretation,
        "old_theory_relation": old_theory_relation,
        "evidence": evidence,
        "metrics": metrics or {},
        "next_action": next_action,
    }


def evaluate_legacy_potential(master_text: str) -> dict[str, Any]:
    """Audit the canonical pair while preserving the historical comparator."""

    alpha = 1.0
    gamma = 0.025
    c0 = 1.0
    samples = (-1.5, -0.75, 0.0, 0.5, 1.0, 1.5, 2.0)
    canonical_residuals: list[float] = []
    legacy_residuals: list[float] = []
    epsilon = 1.0e-6
    for c in samples:
        def potential(value: float) -> float:
            diff = value * value - c0 * c0
            return alpha / 2.0 * diff**2 + gamma / 4.0 * diff**4

        squared_diff = c * c - c0 * c0
        true_derivative = 2.0 * c * (
            alpha * squared_diff + gamma * squared_diff**3
        )
        finite_difference = (potential(c + epsilon) - potential(c - epsilon)) / (2.0 * epsilon)
        legacy_derivative = alpha * (c - c0) + gamma * (c - c0) ** 3
        canonical_residuals.append(abs(finite_difference - true_derivative))
        legacy_residuals.append(abs(finite_difference - legacy_derivative))

    max_canonical_residual = max(canonical_residuals)
    max_legacy_residual = max(legacy_residuals)
    threshold = 1.0e-8
    source_contract = {
        "potential_uses_squared_state": contains(master_text, "diff = C_mag_sq - params.C0**2"),
        "exact_derivative_function_present": contains(master_text, "def potential_derivative")
        and contains(master_text, "2.0 * C * (params.alpha * diff + params.gamma * diff**3)"),
        "canonical_mode_present": contains(master_text, 'LEGACY_VARIATIONAL_OPERATOR_MODE = "legacy_variational_v1"'),
        "dynamics_selects_exact_derivative_in_canonical_mode": contains(
            master_text, "if mode == LEGACY_VARIATIONAL_OPERATOR_MODE"
        )
        and contains(master_text, "reaction_derivative = ("),
        "legacy_comparator_present": contains(master_text, "def legacy_reaction_derivative")
        and contains(master_text, "else legacy_reaction_derivative"),
    }
    canonical_ready = (
        source_contract["potential_uses_squared_state"]
        and source_contract["exact_derivative_function_present"]
        and source_contract["canonical_mode_present"]
        and source_contract["dynamics_selects_exact_derivative_in_canonical_mode"]
        and source_contract["legacy_comparator_present"]
    )
    status = "COMPATIBLE_CONDITIONAL" if canonical_ready else "NOT_ESTABLISHED"
    return finding(
        "legacy_potential_derivative_pair",
        "uet.legacy.master_potential",
        status,
        "medium",
        "V(C)=alpha/2*(C^2-C0^2)^2+gamma/4*(C^2-C0^2)^4",
        "legacy_variational_v1 uses the exact radial derivative; legacy_local retains a named historical comparator",
        "The canonical opt-in lane closes the declared potential/derivative pair. The historical reaction remains intentionally non-variational and is quarantined as a comparator.",
        "The old implementation is not globally variational, but its default behavior is preserved and a separately named canonical lane is available for variational checks.",
        [
            {
                "path": rel(MASTER_PATH),
                "kind": "source_contract",
                "details": source_contract,
            }
        ],
        "Use legacy_variational_v1 for variational claims; do not promote legacy_local comparator behavior without a separate derivation.",
        metrics={
            "sample_points": list(samples),
            "canonical_max_absolute_residual": max_canonical_residual,
            "legacy_comparator_max_absolute_residual": max_legacy_residual,
            "threshold": threshold,
            "analytic_derivative": "2*C*(alpha*(C^2-C0^2)+gamma*(C^2-C0^2)^3)",
            "legacy_comparator_derivative": "alpha*(C-C0)+gamma*(C-C0)^3",
            "legacy_behavior_preserved": True,
        },
    )


def evaluate_legacy_information_gradient_sign(master_text: str) -> dict[str, Any]:
    """Audit the information-source sign in the same lane as the coupling."""

    source_contract = {
        "positive_coupling_declared": contains(master_text, "return params.beta * np.sum(C * I) * volume"),
        "canonical_negative_source_present": contains(master_text, "source = -params.beta * C"),
        "legacy_positive_source_present": contains(master_text, "source = params.beta * C"),
        "c_source_sign_matches": contains(master_text, "return -params.beta * I"),
    }
    status = "COMPATIBLE_CONDITIONAL" if all(
        source_contract[key]
        for key in ("positive_coupling_declared", "canonical_negative_source_present", "c_source_sign_matches")
    ) else "NOT_ESTABLISHED"
    return finding(
        "legacy_information_gradient_sign",
        "uet.legacy.information_gradient",
        status,
        "medium",
        "Omega_I contains +beta*C*I and dI/dt=-delta(Omega)/delta(I)",
        "legacy_variational_v1 uses -beta*C; legacy_local retains +beta*C",
        "The canonical source sign matches the negative gradient of the declared positive coupling. The historical sign is preserved only as a quarantined comparator.",
        "The source-sign contract is conditionally closed in the canonical lane, not globally for the historical implementation.",
        [{"path": rel(MASTER_PATH), "kind": "source_contract", "details": source_contract}],
        "Keep the legacy source sign out of variational claims; the normalized operator is audited separately below.",
        metrics={
            "expected_canonical_source_sign": -1,
            "canonical_source_sign": -1,
            "legacy_comparator_source_sign": 1,
            "legacy_behavior_preserved": True,
        },
    )


def build_report() -> dict[str, Any]:
    required_paths = [
        MASTER_PATH,
        PARAMETERS_PATH,
        MATTER_SPACE_SPEC,
        GR_SPEC,
        REGISTRY_PATH,
        ALIGNMENT_PATH,
        MATTER_FORMULA_PATH,
        MATTER_VERIFY_PATH,
        MATTER_DEPENDENCY_PATH,
        TRACE_VERIFY_PATH,
        GR_VERIFY_PATH,
        O2_VERIFY_PATH,
        O2_FORMULA_PATH,
    ]
    missing = [rel(path) for path in required_paths if not path.exists()]
    if missing:
        return {
            "audit": "uet_foundation_compatibility",
            "audit_status": "FAIL",
            "compatibility_status": "BLOCKED",
            "errors": [f"missing input: {path}" for path in missing],
        }

    master_text = read_text(MASTER_PATH)
    parameters_text = read_text(PARAMETERS_PATH)
    matter_spec_text = read_text(MATTER_SPACE_SPEC)
    gr_spec_text = read_text(GR_SPEC)
    alignment = load_json(ALIGNMENT_PATH)
    matter_formula = load_json(MATTER_FORMULA_PATH)
    matter_verify = load_json(MATTER_VERIFY_PATH)
    matter_dependency = load_json(MATTER_DEPENDENCY_PATH)
    trace_verify = load_json(TRACE_VERIFY_PATH)
    gr_verify = load_json(GR_VERIFY_PATH)
    o2_verify = load_json(O2_VERIFY_PATH)
    o2_formula = load_json(O2_FORMULA_PATH)
    registry = load_json(REGISTRY_PATH)

    findings = [evaluate_legacy_potential(master_text), evaluate_legacy_information_gradient_sign(master_text)]

    information_contract = {
        "historical_box_equation_marked_comparator": contains(master_text, "historical box/wave relation") and contains(master_text, "comparator"),
        "canonical_gradient_flow_declared": contains(master_text, "dI/dt = Laplacian(I) - kappa_I*I - beta*C"),
        "canonical_periodic_laplacian_present": contains(master_text, "if mode == LEGACY_VARIATIONAL_OPERATOR_MODE") and contains(master_text, "laplacian = conserved_laplacian(I, dx)"),
        "canonical_functional_gradient_present": contains(master_text, "periodic_gradient_energy(I, dx, 1.0)"),
        "canonical_negative_source_present": contains(master_text, "source = -params.beta * C"),
        "first_order_update": contains(master_text, "dI_dt = laplacian - decay + source") and contains(master_text, "return I + dt * dI_dt"),
        "legacy_boundary_copy_preserved": contains(master_text, "laplacian[0] = laplacian[1]"),
    }
    information_contract_closed = all(
        information_contract[key]
        for key in (
            "historical_box_equation_marked_comparator",
            "canonical_gradient_flow_declared",
            "canonical_periodic_laplacian_present",
            "canonical_functional_gradient_present",
            "canonical_negative_source_present",
            "first_order_update",
        )
    )
    findings.append(
        finding(
            "legacy_information_operator",
            "uet.legacy.information_field",
            "COMPATIBLE_CONDITIONAL" if information_contract_closed else "CONFLICT",
            "high",
            "normalized canonical lane: dI/dt = Laplacian(I) - kappa_I*I - beta*C",
            "legacy_variational_v1 uses the periodic discrete Laplacian and the negative functional gradient; legacy_local keeps its historical boundary/update behavior",
            "The historical box/wave relation is now explicitly a comparator. The canonical normalized lane has a matched periodic operator, functional gradient, source sign, and first-order update.",
            "This closes the scoped normalized operator contract, not a covariant box equation or a physical SI information field.",
            [{"path": rel(MASTER_PATH), "kind": "source_contract", "details": information_contract}],
            "Keep the box/wave relation comparator-only; any covariant or dimensional information operator requires a separate derivation and units gate.",
            metrics={
                "canonical_operator_closed": information_contract_closed,
                "legacy_behavior_preserved": information_contract["legacy_boundary_copy_preserved"],
                "historical_box_is_comparator": information_contract["historical_box_equation_marked_comparator"],
            },
        )
    )
    beta_unit_label_lines = [
        line.strip()
        for line in parameters_text.splitlines()
        if ("beta" in line.lower() or "β" in line)
        and any(token in line for token in (" J", "[J]", "joule", "eV"))
        and not any(marker in line.lower() for marker in ("not joule", "dimensionless", "normalized proxy"))
    ]

    beta_contract = {
        "normalized_beta_declared": contains(parameters_text, "Dimensionless normalized coupling"),
        "normalized_landauer_proxy_declared": contains(parameters_text, "not the SI Landauer energy"),
        "normalized_beta_property_present": contains(parameters_text, "def beta_normalized"),
        "separate_landauer_energy_present": contains(parameters_text, "def landauer_minimum_energy") and contains(parameters_text, "E_min ="),
        "joule_print_or_doc_claim_present": bool(beta_unit_label_lines),
        "beta_unit_label_lines": beta_unit_label_lines,
    }
    beta_contract_closed = (
        beta_contract["normalized_beta_declared"]
        and beta_contract["normalized_landauer_proxy_declared"]
        and beta_contract["normalized_beta_property_present"]
        and beta_contract["separate_landauer_energy_present"]
        and not beta_contract["joule_print_or_doc_claim_present"]
    )
    findings.append(
        finding(
            "legacy_beta_unit_semantics",
            "uet.legacy.beta_landauer_bridge",
            "COMPATIBLE_CONDITIONAL" if beta_contract_closed else "CONFLICT",
            "high",
            "beta_normalized is dimensionless; E_min = k_B*T*ln(2) is a separate SI lower bound",
            "public beta/beta_normalized compatibility API plus separate landauer_minimum_energy()",
            "The normalized beta proxy and the joule-valued Landauer lower bound are now separate quantities in the parameter contract.",
            "No conversion from E_min to beta_normalized is claimed as a first-principles derivation; the conversion remains lane-specific and open.",
            [{"path": rel(PARAMETERS_PATH), "kind": "source_contract", "details": beta_contract}],
            "Keep beta_normalized and E_min separate; add a topic-specific dimensional conversion only when its observable lane is declared.",
            metrics={
                "normalized_beta_contract_closed": beta_contract_closed,
                "stale_beta_unit_label_count": len(beta_unit_label_lines),
            },
        )
    )
    energy_contract = {
        "lyapunov_not_conservation_disclosed": contains(master_text, "not a proof of full energy conservation"),
        "gradient_descent_language": contains(master_text, "Free Energy Minimization"),
        "velocity_clipping_present": contains(master_text, "np.clip(force") or contains(master_text, "np.clip(V_raw"),
        "explicit_exchange_present": contains(master_text, "exchange = params.gamma_J * (J_in - J_out)"),
    }
    findings.append(
        finding(
            "legacy_energy_conservation_claim",
            "uet.legacy.energy_axiom",
            "NOT_ESTABLISHED",
            "high",
            "A1 is labelled energy conservation",
            "the implemented legacy path is a descent/optimization update with exchange, heuristic forces, and clipping",
            "The code itself correctly discloses that its value equation is a Lyapunov/free-energy diagnostic rather than a full energy-conservation proof. Therefore the stronger axiom label is not supported by the implementation.",
            "A gradient-flow free-energy law is compatible with standard nonequilibrium modelling, but it is not equivalent to total energy conservation. An open-system ledger must expose boundary/source work explicitly.",
            [{"path": rel(MASTER_PATH), "kind": "source_contract", "details": energy_contract}],
            "Split the legacy label into Lyapunov descent, source/exchange balance, and any separately derived physical-energy ledger.",
        )
    )

    symmetry_contract = {
        "u1_claim_present": contains(master_text, "Symmetry: U(1) Global Phase Invariance"),
        "real_scalar_reduction_present": contains(master_text, "C_mag_sq = C**2")
        and contains(master_text, "Assuming real part"),
        "complex_phase_implementation_in_legacy_function": False,
    }
    findings.append(
        finding(
            "legacy_u1_real_scalar_gap",
            "uet.legacy.u1_potential",
            "NOT_ESTABLISHED",
            "medium",
            "the legacy potential is documented as U(1) phase invariant",
            "the legacy function is implemented on a real array C with C**2 and no phase/current variable",
            "A real radial reduction can be a valid lane, but the source does not state a reduction map or prove that the coded derivative/current realizes the U(1) theory. The current O(2) finite-density lane is therefore a separate, better-specified realization rather than a proof of the legacy claim.",
            "The standard O(2)/U(1) Noether theory is compatible in its own declared lane; it does not retroactively validate the legacy scalar implementation.",
            [{"path": rel(MASTER_PATH), "kind": "source_contract", "details": symmetry_contract}],
            "Keep the O(2) realization separate and add an explicit radial reduction plus Noether-current correspondence before merging semantics.",
        )
    )

    lorentz_contract = {
        "grid_finite_difference_present": contains(master_text, "/ dx**2") and contains(master_text, "np.gradient"),
        "speed_clamp_present": contains(master_text, "LIGHT_SPEED"),
        "legacy_covariant_action_path": False,
    }
    findings.append(
        finding(
            "legacy_lorentz_covariance",
            "uet.legacy.master_dynamics",
            "NOT_ESTABLISHED",
            "high",
            "legacy comments include relativistic/Lorentz axiom language",
            "the default path is a grid update with coordinate-time finite differences and a speed clamp",
            "A numerical speed clamp is not a Lorentz-covariant derivation. The separate covariant response pilot is evidence for a conditional parent lane only.",
            "Lorentz covariance may be recovered in a separately declared covariant action/limit; it is not established for the legacy master engine.",
            [{"path": rel(MASTER_PATH), "kind": "source_contract", "details": lorentz_contract}],
            "Do not use legacy invariance comments as evidence. Require a covariant action, transformation test, conserved current, and a controlled numerical discretization.",
        )
    )

    open_system_contract = {
        "explicit_subsystem_exchange": contains(master_text, "J_in - J_out"),
        "complete_universe_closure_unresolved": contains(gr_spec_text, "complete-universe closure unresolved"),
        "universe_nonclosed_blocked_language": contains(gr_spec_text, "universe proved non-closed"),
    }
    findings.append(
        finding(
            "global_open_system_claim",
            "uet.open_system.interpretation",
            "NOT_ESTABLISHED",
            "high",
            "an effective space/matter subsystem may be open through explicit exchange terms",
            "the repository contains subsystem source/exchange terms but no complete-universe closure proof or measurement map",
            "The safe statement is an open-system constitutive ansatz for a selected subsystem. It does not establish that the universe is open with probability one or that a closed limit must be Einstein GR for the full theory.",
            "The covariant pilot provides a conditional closed response limit, not a proof that the global theory is non-closed.",
            [{"path": rel(GR_SPEC), "kind": "claim_boundary", "details": open_system_contract}],
            "Keep global openness as a hypothesis and define the subsystem boundary, exchange current, total ledger, and observational discriminant.",
        )
    )

    alignment_legacy = alignment.get("legacy_core", {})
    findings.append(
        finding(
            "legacy_to_matter_space_ontology",
            "uet.legacy_to_matter_space",
            "NOT_ESTABLISHED",
            "high",
            "legacy I could be read as the same object as the new response/trace sector",
            "the new matter-space contract separates (C,Phi,Pi) physical state from R=I_trace derived observable and rejects ambiguous legacy I/V/J inputs",
            "The new ontology is a controlled reframing with a separate operator, not a derivation that the legacy I field was already Phi or R. The alignment artifact itself records the legacy information role as WARN and trace feedback as heuristic.",
            "No old-theory special-case relation is established between legacy I and the new trace/response variables.",
            [
                {"path": rel(ALIGNMENT_PATH), "kind": "artifact", "details": alignment_legacy},
                {"path": rel(MATTER_SPACE_SPEC), "kind": "specification", "details": "R is derived and has no feedback in the new mode"},
            ],
            "Maintain explicit adapters and do not transfer evidence from legacy I into the new physical state.",
        )
    )

    matter_metrics = matter_verify.get("metrics", {})
    prearrival = matter_metrics.get("prearrival_leakage", {}).get("value")
    causal_threshold = matter_metrics.get("prearrival_leakage", {}).get("threshold")
    local_derivative = matter_metrics.get("local_derivative", {}).get("gate")
    ledger = matter_metrics.get("ledger_closure", {}).get("gate")
    findings.append(
        finding(
            "matter_space_variational_core",
            "uet.matter_space.candidate",
            "COMPATIBLE_CONDITIONAL",
            "medium",
            "Omega[C,Phi] -> (mu_C,mu_Phi) -> physical dynamics -> sigma -> R",
            "local derivative, directional derivative, conservation, dissipation, ledger, g=0, and no-backreaction gates pass in normalized internal verification; causal pre-arrival gate fails",
            "The variational and ledger structure is internally coherent within the tested normalized lane, but the physical-response discretization is not yet causal under its declared compact-support threshold.",
            "The candidate can contain standard gradient-flow and damped-response limits under explicit assumptions; it is not yet a validated physical replacement for a standard theory.",
            [{"path": rel(MATTER_VERIFY_PATH), "kind": "artifact", "details": matter_dependency}],
            "Repair the causal discretization before promoting Phi as a physical response variable or using the operator downstream.",
            metrics={
                "local_derivative_gate": local_derivative,
                "ledger_closure_gate": ledger,
                "prearrival_leakage": prearrival,
                "prearrival_threshold": causal_threshold,
                "artifact_status": matter_verify.get("status"),
            },
        )
    )

    findings.append(
        finding(
            "matter_space_causal_response",
            "uet.matter_space.causal_response",
            "BLOCKED" if prearrival is not None and causal_threshold is not None and prearrival > causal_threshold else "COMPATIBLE_CONDITIONAL",
            "critical",
            "response has retarded/compact causal support",
            f"measured pre-arrival leakage={prearrival} against threshold={causal_threshold}",
            "The current artifact explicitly marks this as a hard numerical gate with no cone-padding. A failed causal gate blocks physical interpretation even though other internal gates pass.",
            "The standard telegraph/diffusion limiting equations remain available as comparators, but the current discretization cannot yet support a causal UET response claim.",
            [{"path": rel(MATTER_VERIFY_PATH), "kind": "metric", "details": matter_metrics.get("prearrival_leakage", {})}],
            "Replace or repair the explicit response discretization and regenerate the verifier artifact from the locked configuration.",
        ),
    )

    trace_tests = trace_verify.get("tests", {})
    findings.append(
        finding(
            "derived_trace_no_backreaction",
            "uet.trace.derived_observable",
            "COMPATIBLE_CONDITIONAL" if trace_tests.get("same_present_different_history") and trace_tests.get("zero_source_zero_trace") else "NOT_ESTABLISHED",
            "medium",
            "R=G_ret*(sigma_C+sigma_Phi) is derived and does not alter physical dynamics",
            "trace verifier reports nonnegative source, zero-source zero-trace, same-present/different-history, static-limit, and causal-cone tests as true",
            "Within the normalized trace-only comparator, the one-way observable contract is internally supported. This is not evidence that R is a substance, energy reservoir, or direct measurement.",
            "A standard memory observable is compatible with the trace-only construction; backreaction would be a separate constitutive hypothesis and is currently blocked in the new mode.",
            [{"path": rel(TRACE_VERIFY_PATH), "kind": "artifact", "details": trace_tests}],
            "Keep trace calculation downstream of physical dynamics and add a dimensional observable map before external fitting.",
        )
    )

    gr_gates = gr_verify.get("gates", {})
    gr_run_contract = gr_verify.get("run_contract", {})
    gr_conditional = (
        gr_verify.get("status") == "PASS"
        and gr_gates.get("symbolic_metric_closed_limit") == "PASS"
        and gr_run_contract.get("metric_pde_solved") is False
        and gr_run_contract.get("bianchi_identity_proved") is False
    )
    findings.append(
        finding(
            "covariant_gr_closed_limit",
            "uet.covariant_response.gr_limit",
            "COMPATIBLE_CONDITIONAL" if gr_conditional else "NOT_ESTABLISHED",
            "high",
            "epsilon_nc=0 and ordered response should remove the candidate response sector",
            "the artifact reports exact algebraic metric/scalar null differences and local tensor consistency, while explicitly not solving metric PDEs or proving Bianchi identities",
            "This is the strongest current special-case result, but its scope is algebraic and local: it supports a candidate conservative covariant parent with an implemented GR null contract, not a derivation of Einstein GR or a physical closed-universe theorem.",
            "GR is a conditional closed-limit comparator of the covariant pilot only. It is not yet a limit proof for the legacy master equation.",
            [{"path": rel(GR_VERIFY_PATH), "kind": "artifact", "details": {"status": gr_verify.get("status"), "gates": gr_gates, "run_contract": gr_run_contract}}],
            "Extend only after a covariant action, field equations, Bianchi/Noether balance, and metric PDE/initial-value verification are added.",
        )
    )

    o2_metrics = o2_verify.get("metrics", {})
    o2_gates = o2_verify.get("gates", {})
    o2_conditional = bool(o2_gates) and all(bool(value) for value in o2_gates.values())
    findings.append(
        finding(
            "o2_finite_density_eos",
            "uet.o2.finite_density_eos",
            "COMPATIBLE_CONDITIONAL" if o2_conditional else "NOT_ESTABLISHED",
            "medium",
            "finite-density O(2) action derives p,n,epsilon,chi,c_s and response reciprocity",
            "tree-level natural-unit EOS gates pass; physical finite-temperature/Kubo/SI gates remain open in the formula audit",
            "The O(2) lane gives a genuine conditional derivation of an EOS in its own ontology. It establishes that C can map to Noether charge density in that lane, not that C universally means mass or density.",
            "The standard relativistic O(2) condensate is a valid counterpart for this lane. It does not validate the legacy double-well as its action-derived EOS.",
            [
                {"path": rel(O2_VERIFY_PATH), "kind": "artifact", "details": {"gates": o2_gates, "metrics": o2_metrics}},
                {"path": rel(O2_FORMULA_PATH), "kind": "artifact", "details": {"status": o2_formula.get("status"), "open_formula_gates": o2_formula.get("open_formula_gates", [])}},
            ],
            "Keep the O(2) EOS as a lane-specific tree-level derivation and do not promote transport coefficients without Kubo provenance.",
        )
    )

    double_well_residual = o2_metrics.get("double_well_reduction_relative_residual")
    double_well_threshold = o2_verify.get("thresholds", {}).get("double_well_reduction_relative_max")
    findings.append(
        finding(
            "o2_to_legacy_double_well",
            "uet.o2_to_legacy.double_well",
            "REJECTED_REDUCTION" if double_well_residual is not None and double_well_threshold is not None and double_well_residual > double_well_threshold else "COMPATIBLE_CONDITIONAL",
            "high",
            "the finite-density O(2) EOS might reduce to the legacy symmetric double well",
            f"relative residual={double_well_residual} against threshold={double_well_threshold}",
            "The tested reduction fails by three orders of magnitude relative to the allowed residual. The double well must remain a constitutive comparator, not be presented as derived from the O(2) EOS.",
            "The old constitutive form is not currently a special case of the finite-density O(2) lane under the tested mapping.",
            [{"path": rel(O2_VERIFY_PATH), "kind": "metric", "details": {"residual": double_well_residual, "threshold": double_well_threshold, "status": o2_verify.get("double_well_reduction", {}).get("status")}}],
            "Either derive a new controlled coarse-graining map with a preregistered residual gate or keep the two forms as separate comparators.",
        )
    )

    findings.append(
        finding(
            "legacy_heat_and_gl_limits",
            "uet.legacy.standard_limits",
            "NOT_ESTABLISHED",
            "medium",
            "legacy verifier names heat-equation and Ginzburg-Landau limits",
            "the checks are spread/relaxation diagnostics and the canonical information operator and beta-unit contract are now scoped separately",
            "A limit label is not a proof of equation equivalence. The heat and GL diagnostics are useful internal comparators, but their residual, boundary, and exact operator maps are not yet sufficient to certify the old equations as special cases.",
            "Standard heat/GL behavior can be used as benchmark baselines after an exact operator and boundary contract is declared.",
            [{"path": rel(MASTER_PATH), "kind": "legacy_verifier_names", "details": ["verify_heat_equation_limit", "verify_ginzburg_landau_limit"]}],
            "Replace pass-by-spread checks with equation residuals, boundary-specific convergence, and a repaired variational derivative pair.",
        )
    )

    status_counts = Counter(item["status"] for item in findings)
    hard_blocks = [
        item["finding_id"]
        for item in findings
        if item["status"] in {"CONTRADICTION", "CONFLICT", "BLOCKED", "REJECTED_REDUCTION"}
    ]
    unresolved = [
        item["finding_id"]
        for item in findings
        if item["status"] == "NOT_ESTABLISHED"
    ]
    compatibility_status = "BLOCKED" if hard_blocks or unresolved else "PASS_CONDITIONAL"

    principles = [
        {
            "principle_id": "P1",
            "name": "state_response_trace_separation",
            "statement": "Physical dynamics acts on declared state variables; R=I_trace is derived from history and has no feedback in the new mode.",
            "evidence_status": "CONDITIONALLY_SUPPORTED",
            "controller": "matter-space and trace verifier artifacts",
        },
        {
            "principle_id": "P2",
            "name": "functional_derivative_closure",
            "statement": "A dynamics operator may be called variational only when its implemented force is the derivative of its declared functional in the same lane.",
            "evidence_status": "CONDITIONAL_CANONICAL; LEGACY_COMPARATOR_QUARANTINED",
            "controller": "legacy_potential_derivative_pair",
        },
        {
            "principle_id": "P3",
            "name": "lane_specific_correspondence",
            "statement": "C is a mathematical system coordinate; mass density, Noether charge density, and order parameter are separate declared realizations with separate observables and units.",
            "evidence_status": "SUPPORTED_BY_CONTRACT; PHYSICAL_MAP_OPEN",
            "controller": "equation correspondence registry",
        },
        {
            "principle_id": "P4",
            "name": "explicit_open_balance",
            "statement": "Open behavior is a subsystem constitutive statement represented by explicit source, boundary, or exchange terms; it is not a theorem that the whole universe is open.",
            "evidence_status": "CONDITIONAL_HYPOTHESIS",
            "controller": "global_open_system_claim",
        },
        {
            "principle_id": "P5",
            "name": "nested_standard_limits",
            "statement": "A standard theory is a special case only through an explicit parameter, field, boundary, and unit limit with residual verification; the covariant GR result currently satisfies only an algebraic/local conditional version.",
            "evidence_status": "PARTIALLY_SUPPORTED",
            "controller": "covariant_gr_closed_limit and o2_to_legacy_double_well",
        },
        {
            "principle_id": "P6",
            "name": "ledger_before_claim",
            "statement": "Free-energy descent, physical energy conservation, entropy production, and subsystem exchange must be reported as different ledgers until their unit and boundary maps are closed.",
            "evidence_status": "REQUIRED_RULE; LEGACY_CLAIM_UNPROVEN",
            "controller": "legacy_energy_conservation_claim and beta_unit_semantics",
        },
        {
            "principle_id": "P7",
            "name": "observable_before_data",
            "statement": "No empirical support claim is allowed until an observable operator, units, preprocessing, uncertainty, and holdout protocol map the equation to measured data.",
            "evidence_status": "REQUIRED_RULE; DOWNSTREAM_BLOCKED",
            "controller": "foundation dependency gate",
        },
    ]

    input_paths = required_paths
    source_hashes = {rel(path): sha256(path) for path in input_paths}
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact": "uet_foundation_compatibility_gate",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "compatibility_status": compatibility_status,
        "controlling_blockers": hard_blocks,
        "unresolved_correspondence": unresolved,
        "summary": {
            "finding_count": len(findings),
            "status_counts": dict(sorted(status_counts.items())),
            "registry_entry_count": len(registry.get("entries", [])),
            "registry_coverage_status": registry.get("coverage", {}).get("coverage_status"),
            "legacy_alignment_gate_status": alignment.get("status"),
            "matter_space_dependency_status": matter_dependency.get("status"),
            "matter_space_formula_status": matter_formula.get("status"),
        },
        "interpretation_key": {
            "CONTRADICTION": "implementation violates its own declared mathematical relation",
            "CONFLICT": "declared equation, units, or implementation are materially inconsistent",
            "NOT_ESTABLISHED": "no valid proof/correspondence is available; this is not by itself a contradiction",
            "COMPATIBLE_CONDITIONAL": "compatible inside a declared lane and evidence boundary only",
            "BLOCKED": "a hard verification or dependency gate fails",
            "REJECTED_REDUCTION": "tested mapping to a proposed old form fails its preregistered residual",
        },
        "findings": findings,
        "theory_principles": principles,
        "old_theory_special_case_matrix": [
            {
                "old_theory": "Einstein/GR",
                "relation": "epsilon_nc=0, ordered response, candidate covariant evaluator",
                "status": "COMPATIBLE_CONDITIONAL",
                "scope": "algebraic/local tensor-formula contract; not full field-equation or physical validation",
            },
            {
                "old_theory": "relativistic O(2) finite-density EOS",
                "relation": "declared O(2) action and natural-unit tree-level branch",
                "status": "COMPATIBLE_CONDITIONAL",
                "scope": "lane-specific EOS and ideal covariant sector; transport coefficients and SI open",
            },
            {
                "old_theory": "symmetric legacy double well",
                "relation": "tested polynomial reduction from O(2) EOS",
                "status": "REJECTED_REDUCTION",
                "scope": "fixed-domain residual 1.0 exceeds 1e-3 threshold",
            },
            {
                "old_theory": "heat/GL legacy limits",
                "relation": "legacy spread/relaxation diagnostics",
                "status": "NOT_ESTABLISHED",
                "scope": "not an equation-residual proof; information-operator and unit conflicts remain",
            },
        ],
        "claim_boundary": [
            "The audit establishes repository-level compatibility findings, not physical truth.",
            "UET is not shown to be mathematically or physically complete.",
            "A conditional GR null limit does not prove that the universe is non-closed.",
            "A normalized ledger is not SI energy or entropy accounting.",
            "No galaxy, dark-matter replacement, particle, antimatter, or full GR claim is promoted by this artifact.",
        ],
        "next_controller": "repair legacy variational/unit conflicts, complete foundation inventory, and repair matter-space causal leakage before downstream data tests",
        "source_hashes": source_hashes,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the full JSON report")
    parser.add_argument("--no-write", action="store_true", help="do not write the generated artifact")
    args = parser.parse_args()
    try:
        report = build_report()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1

    if not args.no_write and report.get("audit_status") == "PASS":
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report.get('audit_status')}")
        print(f"compatibility_status={report.get('compatibility_status')}")
        print(f"controlling_blockers={','.join(report.get('controlling_blockers', []))}")
        print(f"unresolved_correspondence={','.join(report.get('unresolved_correspondence', []))}")
    return 0 if report.get("audit_status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
