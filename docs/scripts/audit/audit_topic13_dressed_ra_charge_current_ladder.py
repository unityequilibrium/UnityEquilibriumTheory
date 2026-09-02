"""Audit the same-kernel dressed RA charge-current ladder."""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from math import log
from pathlib import Path
import hashlib
import json

import numpy as np

from docs.core.uet_o2_dressed_ra_charge_current_ladder import (
    dressed_ra_charge_current_ladder_contract,
    dressed_ra_charge_current_ladder_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_dressed_ra_charge_current_ladder_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_dressed_ra_charge_ladder_addendum.json"
EQUATION_ID = "uet.o2.thermal.same_kernel_dressed_ra_charge_current_ladder"
LOSS_MATCH_THRESHOLD = 5.0e-3
RADIAL_REFINEMENT_THRESHOLD = 1.0e-2
ANGULAR_REFINEMENT_THRESHOLD = 1.0e-3
ALGEBRAIC_THRESHOLD = 1.0e-10


@lru_cache(maxsize=None)
def _state(
    scale: float,
    radial_order: int,
    angular_order: int,
    azimuth_order: int,
    feature_order: int,
):
    return dressed_ra_charge_current_ladder_state(
        0.25 * scale,
        0.1 * scale,
        0.0,
        config(scale),
        radial_order=radial_order,
        incoming_angular_order=angular_order,
        outgoing_angular_order=angular_order,
        outgoing_azimuth_order=azimuth_order,
        feature_order=feature_order,
    )


def _relative(first: float, second: float) -> float:
    return abs(second - first) / max(abs(first), abs(second), 1.0e-300)


def scale_witness(scale: float) -> dict[str, object]:
    if scale <= 0.0 or scale == 1.0:
        raise ValueError("positive nonunit scale required")
    base = _state(1.0, 6, 4, 4, 3)
    scaled = _state(scale, 6, 4, 4, 3)
    quantities = {
        "ra_diagonal_trace": (
            np.trace(np.asarray(base.normalized_ra_diagonal)),
            np.trace(np.asarray(scaled.normalized_ra_diagonal)),
        ),
        "collision_trace": (
            np.trace(np.asarray(base.normalized_collision_operator)),
            np.trace(np.asarray(scaled.normalized_collision_operator)),
        ),
        "gain_rung_norm": (
            np.linalg.norm(np.asarray(base.normalized_gain_rung)),
            np.linalg.norm(np.asarray(scaled.normalized_gain_rung)),
        ),
        "dressed_response": (
            base.dressed_ladder_response_form,
            scaled.dressed_ladder_response_form,
        ),
    }
    ratios = {name: float(pair[1] / pair[0]) for name, pair in quantities.items()}
    exponents = {
        name: log(value) / log(scale) for name, value in ratios.items()
    }
    enhancement_ratio = (
        scaled.ladder_enhancement_factor / base.ladder_enhancement_factor
    )
    return {
        "scale": scale,
        "ratios": ratios,
        "energy_exponents": exponents,
        "enhancement_ratio": enhancement_ratio,
    }


def convergence_witnesses() -> dict[str, object]:
    radial_rows = []
    for order in (8, 12, 16):
        state = _state(1.0, order, 4, 4, 4)
        radial_rows.append({
            "radial_order": order,
            "event_width_loss_relative_residual": state.event_width_loss_relative_residual,
            "dressed_response": state.dressed_ladder_response_form,
            "free_response": state.free_ra_response_form,
            "enhancement": state.ladder_enhancement_factor,
            "deflated_kernel_spectral_radius": state.deflated_kernel_spectral_radius,
            "neumann_converged": state.neumann_converged,
        })
    angular_rows = []
    for order in (4, 6, 8):
        state = _state(1.0, 12, order, 2 * order, 4)
        angular_rows.append({
            "angular_order": order,
            "azimuth_order": 2 * order,
            "event_width_loss_relative_residual": state.event_width_loss_relative_residual,
            "dressed_response": state.dressed_ladder_response_form,
            "free_response": state.free_ra_response_form,
            "enhancement": state.ladder_enhancement_factor,
            "deflated_kernel_spectral_radius": state.deflated_kernel_spectral_radius,
            "neumann_converged": state.neumann_converged,
        })
    keys = ("dressed_response", "free_response", "enhancement")
    return {
        "radial_rows": radial_rows,
        "angular_rows": angular_rows,
        "radial_last_relative_differences": {
            key: _relative(radial_rows[-2][key], radial_rows[-1][key])
            for key in keys
        },
        "angular_last_relative_differences": {
            key: _relative(angular_rows[-2][key], angular_rows[-1][key])
            for key in keys
        },
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    reference = _state(1.0, 12, 4, 8, 4)
    scaling = [scale_witness(value) for value in (1.5, 2.0, 3.0)]
    convergence = convergence_witnesses()
    contract = dressed_ra_charge_current_ladder_contract()
    source_text = (
        ROOT / "docs/core/uet_o2_dressed_ra_charge_current_ladder.py"
    ).read_text(encoding="utf-8")
    radial_max = max(convergence["radial_last_relative_differences"].values())
    angular_max = max(convergence["angular_last_relative_differences"].values())
    checks = {
        "kms_retarded_width_used_in_ra_pair": reference.retarded_width_used_in_ra_pair
        and not reference.tagged_out_rate_used_as_ra_width
        and reference.maximum_kms_gain_loss_residual <= 1.0e-12,
        "event_width_loss_blocks_agree": reference.event_width_loss_relative_residual
        <= LOSS_MATCH_THRESHOLD,
        "d_minus_gain_rung_equals_collision": reference.d_minus_k_collision_relative_residual
        <= ALGEBRAIC_THRESHOLD,
        "gain_rung_symmetric": reference.rung_symmetry_residual <= ALGEBRAIC_THRESHOLD,
        "single_momentum_null_mode": reference.preconditioned_null_count == 1
        and reference.collision_null_residual <= ALGEBRAIC_THRESHOLD,
        "ladder_matches_kinetic_response": reference.ladder_kinetic_response_relative_residual
        <= ALGEBRAIC_THRESHOLD,
        "ladder_matches_kinetic_solution": reference.ladder_kinetic_solution_relative_residual
        <= ALGEBRAIC_THRESHOLD,
        "ladder_equation_residual": reference.equation_residual <= ALGEBRAIC_THRESHOLD,
        "whole_action_scaling": all(
            max(abs(value - 1.0) for value in row["energy_exponents"].values())
            <= 1.0e-9
            and abs(row["enhancement_ratio"] - 1.0) <= 1.0e-9
            for row in scaling
        ),
        "radial_convergence": radial_max <= RADIAL_REFINEMENT_THRESHOLD,
        "angular_convergence": angular_max <= ANGULAR_REFINEMENT_THRESHOLD,
        "finite_positive_responses": all(
            np.isfinite(value) and value > 0.0
            for value in (
                reference.free_ra_response_form,
                reference.dressed_ladder_response_form,
                reference.kinetic_galerkin_response_form,
            )
        ),
        "no_clipping_fit_or_absolute_mode_cutoff": "np.clip" not in source_text
        and "eigenvalues > 1.0e-" not in source_text
        and not reference.fitted_relaxation_time_used
        and not reference.parameter_fitting_performed,
        "no_holdout_or_physical_kubo": not reference.xie_2026_accessed
        and not reference.physical_kubo_coefficient_emitted,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    status = (
        "PASS_SCOPED_SAME_KERNEL_DRESSED_RA_CHARGE_CURRENT_LADDER"
        if all(checks.values())
        else "WARN_DRESSED_RA_CHARGE_CURRENT_LADDER"
    )
    paths = [
        "docs/core/uet_o2_dressed_ra_charge_current_ladder.py",
        "docs/core/uet_o2_same_kernel_tagged_width.py",
        "docs/core/uet_o2_invariant_vector_current_galerkin.py",
        "docs/core/test/test_topic13_dressed_ra_charge_current_ladder.py",
        "docs/scripts/audit/audit_topic13_dressed_ra_charge_current_ladder.py",
    ]
    priors = [
        "docs/core/artifacts/t13_same_kernel_tagged_spectral_width_audit.json",
        "docs/core/artifacts/t13_vector_current_heat_rank_boundary_audit.json",
    ]
    artifact = {
        "schema_version": "t13-dressed-ra-charge-current-ladder-v1",
        "major_result_id": "T13_SAME_KERNEL_DRESSED_RA_CHARGE_CURRENT_LADDER",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
        "verification_status": status,
        "what_is_closed": [
            "The RA diagonal uses the same-kernel KMS retarded width Gamma_R, not the tagged out-scattering rate.",
            "An independently assembled width-loss block agrees with the event-expanded loss block, and L_vector=D_RA-K_gain is explicit.",
            "The directly resummed finite-basis Bethe-Salpeter charge-current solution agrees with the kinetic Galerkin solution without a fitted relaxation time.",
            "The deflated rung spectral radius is reported explicitly; a failed Neumann series cannot be misreported as a converged ladder.",
        ],
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": contract["equations"],
        "ontology": {
            "C": "unchanged",
            "Phi": "effective response variable; internal exchange line only",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": "natural_units",
        "units": contract["unit_contract"],
        "derivation_class": "same_kernel_kms_retarded_width_direct_bethe_salpeter_charge_ladder",
        "observable": "Finite-basis charge-current response form, not SI conductivity",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_CANDIDATE",
        "reference_state": asdict(reference),
        "whole_action_scale_witnesses": scaling,
        "convergence": convergence,
        "thresholds": {
            "event_width_loss_relative": LOSS_MATCH_THRESHOLD,
            "radial_last_refinement_relative": RADIAL_REFINEMENT_THRESHOLD,
            "angular_last_refinement_relative": ANGULAR_REFINEMENT_THRESHOLD,
            "algebraic_relative": ALGEBRAIC_THRESHOLD,
        },
        "checks": checks,
        "open_blockers": [
            "self_consistent_dressed_width_and_resonant_resummation",
            "continuum_and_cutoff_limit",
            "additional_normal_or_response_heat_carrier",
            "tensor_shear_channel",
            "number_changing_and_response_cuts",
            "physical_Kubo_and_SI_frame_normalization",
        ],
        "controlling_blocker": "independent_heat_carrier_and_continuum_physical_Kubo_mapping_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [
            {"path": path, "sha256": _sha(path)} for path in priors
        ],
        "dependency_unlocked": [
            "charge_current_continuum_ladder_hardening",
            "multicomponent_heat_carrier_ladder_design",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": contract["claim_boundary"],
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Repaired the KMS retarded width and solved the same-kernel finite-basis charge-current RA ladder.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Take the charge ladder toward a continuum/cutoff limit and introduce a genuinely independent normal or response carrier before constructing heat conductivity.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(
        json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    entry = {
        key: artifact[key]
        for key in (
            "ontology",
            "unit_lane",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "controlling_blocker",
            "claim_boundary",
        )
    }
    entry.update({
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "candidate_same_kernel_dressed_ra_charge_ladder",
        "relation_or_code_path": artifact["equation_or_mapping"],
        "standard_physics_counterpart": "Pinch-pole Bethe-Salpeter charge-current ladder and linearized Boltzmann equivalence",
        "variables": {
            "D_RA": "retarded-width diagonal",
            "K_gain": "same-kernel gain rung",
            "chi": "dressed charge-current vertex coefficients",
        },
        "mathematical_role": "finite-basis microscopic-to-kinetic charge-current ladder",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Declared O(2)-Phi tree action, KMS cuts, and invariant vector collision form",
        "assumptions": {
            "natural_units": True,
            "normal_response_background": True,
            "elastic_tree_channels_only": True,
            "finite_galerkin_basis": True,
        },
        "symmetry_and_conservation": "Charge conjugation, detailed balance, and Landau-deflated momentum null mode",
        "limiting_cases": [
            "energy scales 1.5, 2, 3",
            "radial orders 8, 12, 16",
            "angular orders 4, 6, 8",
        ],
        "implementation_paths": [paths[0], paths[1], paths[2]],
        "verifier_paths": [paths[3], paths[4]],
        "evidence_class": "INTERNAL_STRUCTURAL_CANDIDATE",
        "proof_status": "FINITE_BASIS_DIRECT_LADDER_KINETIC_MATCH_VERIFIED",
        "evidence_artifacts": [
            {"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}
        ],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "charge_ladder_precursor_not_physical_unlock",
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
        "reference": {
            "event_width_loss_relative_residual": reference.event_width_loss_relative_residual,
            "deflated_kernel_spectral_radius": reference.deflated_kernel_spectral_radius,
            "neumann_converged": reference.neumann_converged,
            "neumann_iterations": reference.neumann_iterations,
            "ladder_enhancement_factor": reference.ladder_enhancement_factor,
            "response_relative_residual": reference.ladder_kinetic_response_relative_residual,
        },
        "scaling": scaling,
        "convergence": convergence,
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
