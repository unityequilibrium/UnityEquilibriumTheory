"""Audit the invariant vector current and Landau heat-rank boundary."""
from __future__ import annotations

from dataclasses import asdict
from math import log
from pathlib import Path
import hashlib
import json

import numpy as np

from docs.core.uet_o2_invariant_vector_current_galerkin import (
    invariant_vector_current_contract,
    invariant_vector_current_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_vector_current_heat_rank_boundary_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_vector_current_addendum.json"
EQUATION_ID = "uet.o2.thermal.invariant_vector_current_landau_heat_rank_boundary"
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
    base = invariant_vector_current_state(0.25, 0.1, 0.0, config(), **controls)
    scaled = invariant_vector_current_state(
        0.25 * scale, 0.1 * scale, 0.0, config(scale), **controls
    )
    ratios = {
        "operator_trace": scaled.operator_trace / base.operator_trace,
        "positive_mode_rate": scaled.positive_mode_rate / base.positive_mode_rate,
        "charge_response_form": scaled.charge_response_form / base.charge_response_form,
        "heat_response_form": scaled.heat_response_form / base.heat_response_form,
    }
    return {
        "scale": scale,
        **{f"{name}_ratio": value for name, value in ratios.items()},
        **{
            f"{name}_energy_exponent": log(value) / log(scale)
            for name, value in ratios.items()
        },
    }


def convergence_witnesses() -> dict[str, object]:
    radial_rows = []
    for order in (12, 16, 24):
        state = invariant_vector_current_state(
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
            "charge_response_form": state.charge_response_form,
        })
    angular_rows = []
    for order in (4, 6, 8):
        state = invariant_vector_current_state(
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
            "charge_response_form": state.charge_response_form,
        })
    names = ("operator_trace", "positive_mode_rate", "charge_response_form")
    radial_differences = {
        name: _relative(radial_rows[-2][name], radial_rows[-1][name]) for name in names
    }
    angular_differences = {
        name: _relative(angular_rows[-2][name], angular_rows[-1][name]) for name in names
    }
    return {
        "radial_rows": radial_rows,
        "angular_rows": angular_rows,
        "radial_last_relative_differences": radial_differences,
        "angular_last_relative_differences": angular_differences,
    }


def conjugation_witness() -> dict[str, float]:
    controls = {
        "radial_order": 12,
        "incoming_angular_order": 4,
        "outgoing_angular_order": 4,
        "outgoing_azimuth_order": 4,
    }
    positive = invariant_vector_current_state(0.25, 0.1, 0.0, config(), **controls)
    negative = invariant_vector_current_state(0.25, -0.1, 0.0, config(), **controls)
    feature_order = positive.feature_order
    permutation = np.r_[
        np.arange(feature_order, 2 * feature_order), np.arange(0, feature_order)
    ]
    first_operator = np.asarray(positive.collision_operator)
    second_operator = np.asarray(negative.collision_operator)[
        np.ix_(permutation, permutation)
    ]
    first_source = np.asarray(positive.landau_projected_charge_current_source)
    second_source = np.asarray(negative.landau_projected_charge_current_source)[
        permutation
    ]
    return {
        "operator_relative_residual": float(
            np.linalg.norm(first_operator - second_operator)
            / np.linalg.norm(first_operator)
        ),
        "odd_charge_source_relative_residual": float(
            np.linalg.norm(first_source + second_source)
            / np.linalg.norm(first_source)
        ),
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    reference = invariant_vector_current_state(
        0.25, 0.1, 0.0, config(),
        radial_order=16,
        incoming_angular_order=6,
        outgoing_angular_order=6,
        outgoing_azimuth_order=8,
    )
    zero_mu = invariant_vector_current_state(
        0.25, 0.0, 0.0, config(),
        radial_order=12,
        incoming_angular_order=4,
        outgoing_angular_order=4,
        outgoing_azimuth_order=4,
    )
    scaling = [scale_witness(value) for value in (1.5, 2.0, 3.0)]
    convergence = convergence_witnesses()
    conjugation = conjugation_witness()
    contract = invariant_vector_current_contract()
    source_text = (
        ROOT / "docs/core/uet_o2_invariant_vector_current_galerkin.py"
    ).read_text(encoding="utf-8")
    checks = {
        "symbolic_vector_operator_dimension_E1": contract["unit_contract"]["collision_operator"] == 1,
        "whole_action_scaling": all(
            abs(row["operator_trace_energy_exponent"] - 1.0) <= 1.0e-8
            and abs(row["positive_mode_rate_energy_exponent"] - 1.0) <= 1.0e-8
            and abs(row["charge_response_form_energy_exponent"] - 1.0) <= 1.0e-8
            and abs(row["heat_response_form_energy_exponent"] - 3.0) <= 1.0e-8
            for row in scaling
        ),
        "radial_quadrature_converged": max(
            convergence["radial_last_relative_differences"].values()
        ) <= RADIAL_CONVERGENCE_THRESHOLD,
        "angular_quadrature_converged": max(
            convergence["angular_last_relative_differences"].values()
        ) <= ANGULAR_CONVERGENCE_THRESHOLD,
        "eventwise_five_invariants": reference.maximum_event_charge_residual == 0.0
        and reference.maximum_event_energy_residual <= 1.0e-12
        and reference.maximum_event_momentum_residual <= 1.0e-12,
        "vector_momentum_null_mode": reference.momentum_null_residual <= 1.0e-9
        and reference.null_mode_count == 1,
        "vector_dissipative_subspace_full_rank": reference.dissipative_subspace_full_rank,
        "operator_symmetric_positive_semidefinite": reference.operator_symmetry_residual <= 1.0e-12
        and reference.positive_semidefinite_min_eigenvalue
        >= -10.0 * reference.relative_eigenvalue_tolerance,
        "detailed_balance": reference.maximum_detailed_balance_residual <= 1.0e-10,
        "landau_heat_charge_rank_one": reference.projected_source_rank == 1
        and reference.projected_heat_charge_rank_residual <= 1.0e-10,
        "zero_mu_projected_heat_vanishes": np.linalg.norm(
            zero_mu.landau_projected_grand_heat_current_source
        ) <= 1.0e-10,
        "charge_conjugation": max(conjugation.values()) <= 1.0e-10,
        "no_posterior_collision_projection": not reference.posterior_collision_projection_used,
        "no_clipping_fit_or_absolute_mode_cutoff": "np.clip" not in source_text
        and "eigenvalues > 1.0e-" not in source_text
        and not reference.parameter_fitting_performed,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_VECTOR_CURRENT_HEAT_RANK_BOUNDARY"
        if all(checks.values())
        else "WARN_VECTOR_CURRENT_HEAT_RANK_BOUNDARY"
    )
    paths = [
        "docs/core/uet_o2_invariant_vector_current_galerkin.py",
        "docs/core/test/test_topic13_invariant_vector_current_galerkin.py",
        "docs/scripts/audit/audit_topic13_vector_current_heat_rank_boundary.py",
        "docs/core/uet_o2_invariant_galerkin_collision_operator.py",
        "docs/core/uet_o2_same_kernel_tagged_width.py",
    ]
    prior = "docs/core/artifacts/t13_same_kernel_tagged_spectral_width_audit.json"
    artifact = {
        "schema_version": "t13-vector-current-heat-rank-boundary-v1",
        "major_result_id": "T13_VECTOR_CURRENT_GALERKIN_AND_HEAT_RANK_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "closure_disposition": "VECTOR_LANE_CLOSED_AND_INDEPENDENT_HEAT_CHANNEL_CLOSED_AS_NO_GO",
        "verification_status": status,
        "what_is_closed": [
            "An invariant isotropic vector Galerkin collision block now preserves the momentum null mode event by event and has a full-rank dissipative complement.",
            "Charge-current and grand-heat sources are explicitly projected to the Landau frame without altering the collision operator.",
            "For the elastic equal-mass two-charge lane, the projected identity J_Q_perp=-mu*J_charge_perp is verified and the two sources have rank one; at mu=0 the projected heat source vanishes.",
            "An independent heat-current transport channel is therefore structurally absent in this lane and cannot be created by rerunning the same elastic kernel.",
        ],
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": contract["equations"],
        "ontology": {
            "C": "unchanged",
            "Phi": "effective response variable; internal exchange only",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": "natural_units",
        "units": contract["unit_contract"],
        "derivation_class": "invariant_vector_galerkin_with_landau_source_rank_no_go",
        "observable": "Vector charge/heat source rank and collision response form, not conductivity",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_CANDIDATE",
        "reference_state": asdict(reference),
        "zero_mu_state": asdict(zero_mu),
        "whole_action_scale_witnesses": scaling,
        "convergence": convergence,
        "charge_conjugation_witness": conjugation,
        "thresholds": {
            "radial_last_refinement_relative": RADIAL_CONVERGENCE_THRESHOLD,
            "angular_last_refinement_relative": ANGULAR_CONVERGENCE_THRESHOLD,
            "source_rank_relative": 1.0e-10,
        },
        "checks": checks,
        "open_blockers": [
            "additional_normal_component_or_response_channel_for_independent_heat_transport",
            "same_width_dressed_RA_ladder",
            "tensor_shear_channel",
            "number_changing_and_response_cuts",
            "physical_Kubo_and_SI_frame_normalization",
        ],
        "controlling_blocker": "additional_heat_carrier_channel_and_dressed_RA_ladder_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [{"path": prior, "sha256": _sha(prior)}],
        "dependency_unlocked": [
            "charge_current_dressed_RA_ladder",
            "multicomponent_heat_channel_design",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Finite vector charge-current lane and structural Landau-frame heat-rank no-go only; not a heat conductivity, complete normal component, dressed ladder, Kubo/SI coefficient, external validation, or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE/CLOSED_AS_NO_GO_FOR_INDEPENDENT_HEAT_CHANNEL",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added the invariant vector collision block and Landau-frame charge/heat source-rank audit.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Use the charge-current vector lane in the same-width dressed RA ladder, and add a genuinely independent normal/response carrier before reopening heat conductivity.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {key: artifact[key] for key in (
        "ontology", "unit_lane", "units", "derivation_class", "observable",
        "data_role", "verification_status", "controlling_blocker", "claim_boundary",
    )}
    entry.update({
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "candidate_vector_current_and_heat_rank_no_go",
        "relation_or_code_path": artifact["equation_or_mapping"],
        "standard_physics_counterpart": "Linearized relativistic vector collision operator and Landau-frame current projection",
        "variables": {"L_vector": "vector collision rate operator", "J_charge": "Noether charge current source", "J_Q": "grand heat current source"},
        "mathematical_role": "vector transport precursor and independent-heat-channel rank gate",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Same invariant O(2)-Phi elastic kernel and Landau-frame decomposition",
        "assumptions": {"natural_units": True, "equal_mass_two_charge_species": True, "elastic_2to2_only": True, "normal_response_background": True},
        "symmetry_and_conservation": "Eventwise momentum conservation, charge conjugation and PSD vector quadratic form",
        "limiting_cases": ["mu=0 heat-source null", "energy scales 1.5, 2, 3", "radial orders 12, 16, 24", "angular orders 4, 6, 8"],
        "implementation_paths": [paths[0]],
        "verifier_paths": [paths[2], paths[1]],
        "evidence_class": "INTERNAL_STRUCTURAL_CANDIDATE",
        "proof_status": "VECTOR_LANE_VERIFIED_INDEPENDENT_HEAT_CHANNEL_REJECTED_IN_DECLARED_LANE",
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "charge_ladder_precursor_and_heat_channel_no_go",
        "physical_dependency_unlock": False,
        "failure_mode": artifact["open_blockers"],
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
    })
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version": "uet-equation-registry-addendum-v1",
        "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries": [entry],
        "full_core_unlock": False,
        "claim_promotion": False,
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "checks": checks,
        "scaling": scaling,
        "convergence": convergence,
        "conjugation": conjugation,
        "rank_residual": reference.projected_heat_charge_rank_residual,
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
