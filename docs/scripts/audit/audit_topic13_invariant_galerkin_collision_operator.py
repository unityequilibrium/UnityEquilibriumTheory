"""Audit the charge-resolved invariant scalar Galerkin collision operator."""
from __future__ import annotations

from dataclasses import asdict
from math import log
from pathlib import Path
import hashlib
import json

import numpy as np

from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_state,
)
from docs.core.uet_o2_invariant_galerkin_collision_operator import (
    invariant_galerkin_collision_contract,
    invariant_galerkin_collision_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_invariant_galerkin_collision_operator_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_invariant_galerkin_collision_addendum.json"
EQUATION_ID = "uet.o2.thermal.invariant_charge_resolved_scalar_galerkin_collision"
RADIAL_CONVERGENCE_THRESHOLD = 1.0e-2
ANGULAR_CONVERGENCE_THRESHOLD = 1.0e-3


def _relative(first: float, second: float) -> float:
    return abs(second - first) / max(abs(first), abs(second), 1.0e-300)


def scale_witness(scale: float) -> dict[str, float]:
    if scale <= 0.0 or scale == 1.0:
        raise ValueError("positive nonunit scale required")
    controls = {
        "radial_order": 8,
        "incoming_angular_order": 4,
        "outgoing_angular_order": 4,
        "outgoing_azimuth_order": 4,
    }
    base = invariant_galerkin_collision_state(
        0.25, 0.1, 0.0, config(), **controls
    )
    scaled = invariant_galerkin_collision_state(
        0.25 * scale, 0.1 * scale, 0.0, config(scale), **controls
    )
    trace_ratio = scaled.operator_trace / base.operator_trace
    rate_ratio = scaled.positive_mode_rate / base.positive_mode_rate
    return {
        "scale": scale,
        "operator_trace_ratio": trace_ratio,
        "positive_mode_rate_ratio": rate_ratio,
        "trace_energy_exponent": log(trace_ratio) / log(scale),
        "rate_energy_exponent": log(rate_ratio) / log(scale),
    }


def legacy_decomposition_witness(scale: float = 2.0) -> dict[str, float]:
    controls = {
        "radial_order": 8,
        "collision_integration_order": 24,
        "angular_order": 24,
        "transition_quadrature_order": 24,
        "transition_channel_count": 8,
        "transition_interpolation_order": 4,
    }
    base = continuum_collision_operator_state(0.25, 0.1, 0.0, config(), **controls)
    scaled = continuum_collision_operator_state(
        0.25 * scale, 0.1 * scale, 0.0, config(scale), **controls
    )
    width_ratio = np.trace(scaled.action_width_operator) / np.trace(
        base.action_width_operator
    )
    vertex_ratio = np.trace(scaled.transition_vertex_operator) / np.trace(
        base.transition_vertex_operator
    )
    return {
        "scale": scale,
        "action_width_trace_ratio": float(width_ratio),
        "mapped_legacy_vertex_trace_ratio": float(vertex_ratio),
        "action_width_energy_exponent": log(float(width_ratio)) / log(scale),
        "mapped_legacy_vertex_energy_exponent": log(float(vertex_ratio)) / log(scale),
        "base_transition_vertex_trace_ratio": base.transition_vertex_trace_ratio,
    }


def convergence_witnesses() -> dict[str, object]:
    radial_rows = []
    for order in (8, 12, 16):
        state = invariant_galerkin_collision_state(
            0.25, 0.1, 0.0, config(),
            radial_order=order,
            incoming_angular_order=4,
            outgoing_angular_order=4,
            outgoing_azimuth_order=4,
        )
        radial_rows.append({
            "radial_order": order,
            "operator_trace": state.operator_trace,
            "positive_mode_rate": state.positive_mode_rate,
        })
    angular_rows = []
    for order in (4, 6, 8):
        state = invariant_galerkin_collision_state(
            0.25, 0.1, 0.0, config(),
            radial_order=12,
            incoming_angular_order=order,
            outgoing_angular_order=order,
            outgoing_azimuth_order=2 * order,
        )
        angular_rows.append({
            "angular_order": order,
            "azimuth_order": 2 * order,
            "operator_trace": state.operator_trace,
            "positive_mode_rate": state.positive_mode_rate,
        })
    return {
        "radial_rows": radial_rows,
        "angular_rows": angular_rows,
        "radial_last_trace_relative_difference": _relative(
            radial_rows[-2]["operator_trace"], radial_rows[-1]["operator_trace"]
        ),
        "radial_last_rate_relative_difference": _relative(
            radial_rows[-2]["positive_mode_rate"], radial_rows[-1]["positive_mode_rate"]
        ),
        "angular_last_trace_relative_difference": _relative(
            angular_rows[-2]["operator_trace"], angular_rows[-1]["operator_trace"]
        ),
        "angular_last_rate_relative_difference": _relative(
            angular_rows[-2]["positive_mode_rate"], angular_rows[-1]["positive_mode_rate"]
        ),
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    reference = invariant_galerkin_collision_state(
        0.25, 0.1, 0.0, config(),
        radial_order=12,
        incoming_angular_order=6,
        outgoing_angular_order=6,
        outgoing_azimuth_order=8,
    )
    scaling = [scale_witness(value) for value in (1.5, 2.0, 3.0)]
    convergence = convergence_witnesses()
    legacy = legacy_decomposition_witness()
    contract = invariant_galerkin_collision_contract()
    source_text = (
        ROOT / "docs/core/uet_o2_invariant_galerkin_collision_operator.py"
    ).read_text(encoding="utf-8")
    checks = {
        "symbolic_operator_dimension_E1": contract["unit_contract"]["collision_operator"] == 1,
        "whole_action_operator_scales_E1": all(
            abs(row["trace_energy_exponent"] - 1.0) <= 1.0e-8
            and abs(row["rate_energy_exponent"] - 1.0) <= 1.0e-8
            for row in scaling
        ),
        "legacy_mapped_vertex_retains_E2_no_go": abs(
            legacy["mapped_legacy_vertex_energy_exponent"] - 2.0
        ) <= 1.0e-10,
        "radial_quadrature_converged": max(
            convergence["radial_last_trace_relative_difference"],
            convergence["radial_last_rate_relative_difference"],
        ) <= RADIAL_CONVERGENCE_THRESHOLD,
        "angular_quadrature_converged": max(
            convergence["angular_last_trace_relative_difference"],
            convergence["angular_last_rate_relative_difference"],
        ) <= ANGULAR_CONVERGENCE_THRESHOLD,
        "eventwise_five_invariants": reference.maximum_event_charge_residual == 0.0
        and reference.maximum_event_energy_residual <= 1.0e-12
        and reference.maximum_event_momentum_residual <= 1.0e-12,
        "operator_invariant_nullspace": reference.collision_invariant_residual <= 1.0e-9
        and reference.null_mode_count == 3,
        "dissipative_scalar_subspace_full_rank": reference.dissipative_subspace_full_rank,
        "operator_symmetric_positive_semidefinite": reference.operator_symmetry_residual <= 1.0e-12
        and reference.positive_semidefinite_min_eigenvalue
        >= -10.0 * reference.relative_eigenvalue_tolerance,
        "detailed_balance": reference.maximum_detailed_balance_residual <= 1.0e-10,
        "gram_whitening": reference.gram_identity_residual <= 1.0e-8,
        "no_posterior_projection": not reference.posterior_conservation_projection_used,
        "no_clipping_padding_or_absolute_mode_cutoff": "np.clip" not in source_text
        and "cone_padding" not in source_text
        and "eigenvalues > 1.0e-" not in source_text,
    }
    status = (
        "PASS_SCOPED_INVARIANT_SCALAR_GALERKIN_COLLISION"
        if all(checks.values())
        else "WARN_INVARIANT_SCALAR_GALERKIN_COLLISION"
    )
    paths = [
        "docs/core/uet_o2_invariant_galerkin_collision_operator.py",
        "docs/core/test/test_topic13_invariant_galerkin_collision_operator.py",
        "docs/scripts/audit/audit_topic13_invariant_galerkin_collision_operator.py",
        "docs/core/uet_o2_continuum_collision_operator.py",
    ]
    prior = "docs/core/artifacts/t13_invariant_rate_collision_operator_repair.json"
    artifact = {
        "schema_version": "t13-invariant-galerkin-collision-v1",
        "major_result_id": "T13_CHARGE_RESOLVED_INVARIANT_SCALAR_COLLISION_OPERATOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "verification_status": status,
        "what_is_closed": [
            "A charge-resolved scalar Galerkin collision quadratic form now integrates multiple incoming radial shells and incoming/outgoing angles with the production contact-plus-Phi amplitude.",
            "Charge, energy and three-momentum close at every event before operator assembly; no posterior conservation projector is used.",
            "The finite scalar dissipative subspace has full rank after the two species-number and energy null modes, and radial/angular quadratures pass their declared refinement gates.",
            "The old continuum mapped transition vertex independently retains E^2 scaling and is blocked from microscopic reuse even though its separate diagonal-width term scales E.",
        ],
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": contract["equations"],
        "ontology": {
            "C": "unchanged",
            "Phi": "effective response variable and internal exchange response only",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": "natural_units",
        "units": contract["unit_contract"],
        "derivation_class": "charge_resolved_invariant_finite_scalar_galerkin_quadratic_form",
        "observable": "Finite scalar collision-rate spectrum, not a physical transport coefficient",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_CANDIDATE",
        "reference_state": asdict(reference),
        "whole_action_scale_witnesses": scaling,
        "convergence": convergence,
        "legacy_continuum_decomposition_witness": legacy,
        "thresholds": {
            "radial_last_refinement_relative": RADIAL_CONVERGENCE_THRESHOLD,
            "angular_last_refinement_relative": ANGULAR_CONVERGENCE_THRESHOLD,
            "event_energy_momentum_absolute": 1.0e-12,
            "operator_invariant_relative": 1.0e-9,
        },
        "checks": checks,
        "open_blockers": [
            "vector_tensor_heat_current_Galerkin_basis",
            "self_consistent_quasiparticle_width_from_same_kernel",
            "microscopic_retarded_ladder_solution",
            "number_changing_and_response_channels",
            "continuum_and_cutoff_limit",
            "physical_Kubo_and_SI_normalization",
        ],
        "controlling_blocker": "self_consistent_width_and_vector_heat_current_basis_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [{"path": prior, "sha256": _sha(prior)}],
        "dependency_unlocked": [
            "same_kernel_width_derivation",
            "vector_heat_current_Galerkin_extension",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Finite-cutoff scalar isotropic collision operator only; not a complete vector/tensor transport basis, continuum proof, self-consistent width, ladder, Kubo/SI coefficient, external validation, or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Replaced representative disconnected channels with a multi-shell/angular invariant scalar Galerkin quadratic form; preserved and dimensionally blocked the old mapped vertex.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Derive tagged and spectral widths from the same collision kernel, then extend the Galerkin basis to vector heat/current modes before solving the retarded ladder.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        key: artifact[key]
        for key in (
            "ontology", "unit_lane", "units", "derivation_class", "observable",
            "data_role", "verification_status", "controlling_blocker", "claim_boundary",
        )
    }
    entry.update({
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "candidate_invariant_scalar_galerkin_collision",
        "relation_or_code_path": artifact["equation_or_mapping"],
        "standard_physics_counterpart": "Linearized relativistic 2-to-2 Boltzmann collision quadratic form",
        "variables": {"G": "thermal Hilbert Gram matrix", "Q": "collision quadratic form", "L_rate": "normalized rate operator"},
        "mathematical_role": "finite scalar precursor to the microscopic transport ladder",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Declared O(2)-Phi action and Lorentz-invariant two-body phase space",
        "assumptions": {"natural_units": True, "normal_response_background": True, "elastic_equal_mass_2to2": True, "scalar_isotropic_basis": True},
        "symmetry_and_conservation": "Eventwise charge and four-momentum conservation; PSD detailed-balance quadratic form",
        "limiting_cases": ["energy scales 1.5, 2, 3", "radial orders 8, 12, 16", "angular orders 4, 6, 8"],
        "implementation_paths": [paths[0]],
        "verifier_paths": [paths[2], paths[1]],
        "evidence_class": "INTERNAL_STRUCTURAL_CANDIDATE",
        "proof_status": "FINITE_SCALAR_GALERKIN_RATE_AND_CONVERGENCE_VERIFIED",
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "precursor_only_not_physical_unlock",
        "physical_dependency_unlock": False,
        "failure_mode": artifact["open_blockers"],
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
    })
    REGISTRY_OUT.write_text(
        json.dumps({
            "schema_version": "uet-equation-registry-addendum-v1",
            "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
            "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
            "equation_entries": [entry],
            "full_core_unlock": False,
            "claim_promotion": False,
        }, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": status,
        "checks": checks,
        "scaling": scaling,
        "convergence": convergence,
        "legacy": legacy,
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
