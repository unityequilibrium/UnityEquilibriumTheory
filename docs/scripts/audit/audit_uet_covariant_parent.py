"""Verify and register the integrated conservative covariant parent."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    interaction_energy_density,
    matter_on_shell_box,
)
from docs.core.uet_covariant_parent import (
    CovariantParentConfig,
    CovariantParentState,
    covariant_parent_contract,
    evaluate_conservative_parent,
)
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.core_paths import CANONICAL_ARTIFACT_ROOT, canonical_artifact_path


ARTIFACTS = CANONICAL_ARTIFACT_ROOT


def _state(
    response: CovariantResponseConfig,
    matter: CovariantMatterConfig,
) -> CovariantParentState:
    fields = np.array([0.3, -0.4])
    return CovariantParentState(
        metric=np.diag([-1.0, 1.0, 1.0, 1.0]),
        inverse_metric=np.diag([-1.0, 1.0, 1.0, 1.0]),
        einstein_tensor=np.zeros((4, 4)),
        curvature_scalar=0.0,
        phi=0.2,
        gradient_phi=np.array([0.1, -0.02, 0.03, 0.0]),
        box_phi=0.04,
        curvature_factor_base_hessian=np.zeros((4, 4)),
        matter_doublet=fields,
        matter_gradients=np.array(
            [[0.02, 0.01, -0.03, 0.0], [-0.01, 0.04, 0.02, 0.01]]
        ),
        matter_box=matter_on_shell_box(fields, 0.2, response, matter),
    )


def _finite_difference_reciprocity(
    state: CovariantParentState,
    config: CovariantParentConfig,
    step: float = 1e-6,
) -> tuple[float, float]:
    fields = np.asarray(state.matter_doublet, dtype=float)
    plus_phi = interaction_energy_density(
        state.phi + step, fields, config.response, config.matter
    )
    minus_phi = interaction_energy_density(
        state.phi - step, fields, config.response, config.matter
    )
    fd_phi = (plus_phi - minus_phi) / (2.0 * step)
    result = evaluate_conservative_parent(state, config)
    phi_error = abs(fd_phi - result.reciprocal_response_source)

    component_errors = []
    for index in range(2):
        plus = fields.copy()
        minus = fields.copy()
        plus[index] += step
        minus[index] -= step
        fd = (
            interaction_energy_density(
                state.phi, plus, config.response, config.matter
            )
            - interaction_energy_density(
                state.phi, minus, config.response, config.matter
            )
        ) / (2.0 * step)
        component_errors.append(abs(fd - result.reciprocal_matter_source[index]))
    return float(phi_error), float(max(component_errors))


def build_artifacts() -> tuple[dict, dict, dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    matter = CovariantMatterConfig(
        matter_kinetic=1.2,
        matter_mass_sq=0.8,
        matter_quartic=1.1,
        response_coupling=0.7,
    )
    null_response = CovariantResponseConfig(
        epsilon_nc=0.0,
        cosmological_constant=0.03,
        response_mass_sq=0.9,
        response_quartic=1.2,
        curvature_coupling=0.2,
    )
    coupled_response = CovariantResponseConfig(
        epsilon_nc=0.25,
        cosmological_constant=0.03,
        response_mass_sq=0.9,
        response_quartic=1.2,
        curvature_coupling=0.2,
    )
    null_config = CovariantParentConfig(null_response, matter)
    coupled_config = CovariantParentConfig(coupled_response, matter)
    null_result = evaluate_conservative_parent(_state(null_response, matter), null_config)
    coupled_state = _state(coupled_response, matter)
    coupled_result = evaluate_conservative_parent(coupled_state, coupled_config)
    phi_fd_error, matter_fd_error = _finite_difference_reciprocity(
        coupled_state, coupled_config
    )

    metrics = {
        "gr_null_max_abs": float(np.max(np.abs(null_result.gr_null_difference))),
        "null_response_equation_abs": abs(null_result.response_equation_residual),
        "null_exchange_max_abs": null_result.exchange_ledger.closure_max_abs,
        "coupled_matter_eom_max_abs": float(
            np.max(np.abs(coupled_result.matter_equation_residual))
        ),
        "coupled_noether_divergence_abs": abs(
            coupled_result.noether_current_divergence
        ),
        "coupled_exchange_closure_max_abs": (
            coupled_result.exchange_ledger.closure_max_abs
        ),
        "matter_stress_asymmetry_max_abs": float(
            np.max(
                np.abs(
                    coupled_result.matter_stress_energy
                    - coupled_result.matter_stress_energy.T
                )
            )
        ),
        "response_stress_asymmetry_max_abs": float(
            np.max(
                np.abs(
                    coupled_result.response_stress_energy
                    - coupled_result.response_stress_energy.T
                )
            )
        ),
        "reciprocal_phi_fd_error": phi_fd_error,
        "reciprocal_matter_fd_error": matter_fd_error,
    }
    thresholds = {
        "exact_identity": 1e-10,
        "finite_difference": 1e-8,
    }
    checks = {
        "exact_gr_null_nesting": metrics["gr_null_max_abs"]
        <= thresholds["exact_identity"],
        "response_decouples_at_null": metrics["null_response_equation_abs"]
        <= thresholds["exact_identity"],
        "null_exchange_vanishes": metrics["null_exchange_max_abs"]
        <= thresholds["exact_identity"],
        "matter_equation_on_shell": metrics["coupled_matter_eom_max_abs"]
        <= thresholds["exact_identity"],
        "o2_noether_current_on_shell": metrics["coupled_noether_divergence_abs"]
        <= thresholds["exact_identity"],
        "exchange_ledger_closes": metrics["coupled_exchange_closure_max_abs"]
        <= thresholds["exact_identity"],
        "matter_stress_is_symmetric": metrics["matter_stress_asymmetry_max_abs"]
        <= thresholds["exact_identity"],
        "response_stress_is_symmetric": metrics[
            "response_stress_asymmetry_max_abs"
        ]
        <= thresholds["exact_identity"],
        "reciprocal_phi_source_matches_fd": metrics["reciprocal_phi_fd_error"]
        <= thresholds["finite_difference"],
        "reciprocal_matter_source_matches_fd": metrics[
            "reciprocal_matter_fd_error"
        ]
        <= thresholds["finite_difference"],
        "trace_is_not_parent_state": not covariant_parent_contract()[
            "generated_trace_present"
        ],
    }
    passed = all(checks.values())

    verification = {
        "schema_version": "1.0",
        "artifact": "covariant_parent_verification",
        "generated_at": now,
        "audit_status": "PASS" if passed else "FAIL",
        "research_status": "INTERNAL_CONSERVATIVE_PARENT_ONLY",
        "operator": "covariant_theory_parent_formula_v1",
        "unit_lane": "natural",
        "metrics": metrics,
        "thresholds": thresholds,
        "checks": checks,
        "contract": covariant_parent_contract(),
        "claim_boundary": (
            "integrated conservative formula evaluator; not a metric PDE solver, "
            "open-system derivation, SI model, or physical GR validation"
        ),
    }

    formula_audit = {
        "schema_version": "1.0",
        "artifact": "covariant_parent_formula_audit",
        "generated_at": now,
        "status": "WARN",
        "relations": [
            {
                "formula_id": "UET-PARENT-ACTION-001",
                "relation": "S_parent = integral sqrt(-g)[F(Phi)(R-2Lambda)/(2kappa)+L_O2-epsilon U(Phi)]",
                "derivation_class": "candidate conservative action",
                "unit_lane": "natural",
                "code_path": "docs/core/02_equations/covariant/uet_covariant_parent.py",
                "proof_status": "integrated formula evaluator checked locally",
            },
            {
                "formula_id": "UET-PARENT-GR-LIMIT-002",
                "relation": "epsilon_nc=0 implies metric residual equals Einstein-GR residual",
                "derivation_class": "exact algebraic limiting relation",
                "unit_lane": "natural",
                "code_path": "docs/core/02_equations/covariant/uet_covariant_parent.py",
                "proof_status": "internal numerical identity gate",
            },
            {
                "formula_id": "UET-PARENT-EXCHANGE-003",
                "relation": "Q_m^nu + Q_response^nu = 0",
                "derivation_class": "local conservative exchange identity",
                "unit_lane": "natural",
                "code_path": "docs/core/02_equations/covariant/uet_covariant_balance.py",
                "proof_status": "internal local ledger identity",
            },
        ],
        "open_items": [
            "lane-specific covariant coarse graining",
            "Schwinger-Keldysh/KMS dissipative completion",
            "strongly hyperbolic curved 3+1 evolution",
            "SI and observable mapping",
            "external GR benchmarks",
        ],
        "claim_ceiling": "candidate integrated conservative parent in natural units",
    }

    gate = {
        "schema_version": "1.0",
        "artifact": "uet_main_theory_wave2_gate",
        "generated_at": now,
        "audit_status": "PASS" if passed else "FAIL",
        "parent_status": "PASS_CONSERVATIVE_PARENT_ONLY" if passed else "BLOCKED",
        "upstream_gate": "uet_main_theory_ontology_gate.json",
        "checks": checks,
        "controlling_blocker": (
            "lane_specific_covariant_coarse_graining_not_closed"
            if passed
            else "covariant_parent_formula_or_identity_failure"
        ),
        "claim_promotion": False,
        "next_controller": (
            "define explicit coarse-graining operators for charge, phase, density, "
            "and telegraph lanes"
        ),
    }

    addendum = {
        "schema_version": "1.0",
        "artifact": "uet_equation_correspondence_registry_main_theory_addendum",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_PENDING_MERGE",
        "equation_entries": [
            {
                "equation_id": "uet.main_theory.covariant_parent",
                "version": "covariant-parent-v1",
                "classification": "foundational_equation",
                "relation_or_code_path": "docs/core/02_equations/covariant/uet_covariant_parent.py",
                "variables": {
                    "g_munu": "Lorentz metric",
                    "chi_A": "global O(2) scalar matter doublet",
                    "Phi": "candidate response scalar",
                    "epsilon_nc": "closed/non-closed nesting parameter",
                },
                "mathematical_role": "integrated conservative scalar-tensor and O2 parent formula evaluator",
                "standard_physics_counterpart": "scalar-tensor effective action with global O2 matter",
                "observable_mapping": {
                    "status": "OPEN",
                    "reason": "curved solver, SI map, detector map, and external benchmark are absent",
                },
                "unit_lane": "natural_only_v1",
                "parameter_dimensions": "declared by covariant response and matter contracts",
                "source_or_origin": "candidate UET conservative parent assembled from existing action-derived modules",
                "assumptions": [
                    "four-dimensional Lorentz metric with signature (-,+,+,+)",
                    "global O2 scalar matter pilot",
                    "positive response kinetic and bounded quartic potentials",
                    "derived trace and observer state are absent",
                ],
                "symmetry_and_conservation": "diffeomorphism-compatible local tensor formulas, global O2 current, and exchange-completed total balance",
                "limiting_cases": [
                    "epsilon_nc=0 gives exact algebraic Einstein-GR residual with scalar matter",
                    "response coupling zero decouples matter and Phi interaction",
                ],
                "implementation_paths": [
                    "docs/core/02_equations/covariant/uet_covariant_parent.py",
                    "docs/core/02_equations/covariant/uet_covariant_response.py",
                    "docs/core/02_equations/covariant/uet_covariant_matter.py",
                    "docs/core/02_equations/covariant/uet_covariant_balance.py",
                ],
                "verifier_paths": [
                    "docs/scripts/audit/audit_uet_covariant_parent.py",
                    "docs/core/07_artifacts/verification/covariant_parent_verification.json",
                    "docs/core/test/test_uet_covariant_parent.py",
                ],
                "evidence_class": "INTERNAL_FORMAL",
                "proof_status": "conservative formula identities pass locally; physical closure remains blocked",
                "downstream_dependencies": [
                    "uet.main_theory.ontology",
                    "uet.main_theory.coarse_graining",
                    "uet.main_theory.open_system",
                    "uet.main_theory.curved_3p1",
                ],
                "claim_boundary": "candidate natural-unit conservative parent; not curved GR or empirical validation",
                "failure_mode": "component equations drift from the parent action or closed limit requires manual equation deletion",
                "next_hardening_step": "close lane-specific covariant coarse graining before dissipative and observable promotion",
            }
        ],
    }
    return verification, formula_audit, gate, addendum


def main() -> int:
    outputs = dict(
        zip(
            (
                "covariant_parent_verification.json",
                "covariant_parent_formula_audit.json",
                "uet_main_theory_wave2_gate.json",
                "uet_equation_correspondence_registry_main_theory_addendum.json",
            ),
            build_artifacts(),
        )
    )
    for name, payload in outputs.items():
        path = canonical_artifact_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    gate = outputs["uet_main_theory_wave2_gate.json"]
    print(f"audit_status={gate['audit_status']}")
    print(f"parent_status={gate['parent_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
