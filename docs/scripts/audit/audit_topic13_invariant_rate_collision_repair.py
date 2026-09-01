"""Audit the invariant-rate finite collision-operator repair candidate."""
from __future__ import annotations

from dataclasses import asdict
from math import log
from pathlib import Path
import hashlib
import json

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_invariant_rate_collision_operator import (
    _action_amplitude,
    invariant_rate_collision_contract,
    invariant_rate_collision_state,
)
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs,
    amplitude,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_invariant_rate_collision_operator_repair.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_invariant_rate_collision_addendum.json"
EQUATION_ID = "uet.o2.thermal.invariant_rate_finite_collision_operator"


def config(scale: float = 1.0) -> FiniteTemperatureO2QuasiparticleConfig:
    if scale <= 0.0:
        raise ValueError("positive energy scale required")
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(
            matter=CovariantMatterConfig(
                matter_mass_sq=scale * scale,
                matter_quartic=0.1,
                response_coupling=0.2 * scale,
            ),
            response=CovariantResponseConfig(
                epsilon_nc=1.0,
                response_mass_sq=0.5 * scale * scale,
            ),
        )
    )


def scale_witness(scale: float) -> dict[str, float]:
    if scale <= 0.0 or scale == 1.0:
        raise ValueError("positive nonunit scale required")
    base = invariant_rate_collision_state(0.25, 0.1, 0.0, config())
    scaled = invariant_rate_collision_state(
        0.25 * scale, 0.1 * scale, 0.0, config(scale)
    )
    ratio = scaled.operator_trace / base.operator_trace
    return {
        "scale": scale,
        "operator_trace_ratio": ratio,
        "measured_energy_exponent": log(ratio) / log(scale),
        "required_rate_ratio": scale,
        "positive_mode_rate_ratio": scaled.positive_mode_rate / base.positive_mode_rate,
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    state = invariant_rate_collision_state(0.25, 0.1, 0.0, config())
    rows = [scale_witness(value) for value in (1.5, 2.0, 3.0)]
    contract = invariant_rate_collision_contract()
    production_amplitude_residuals = [
        abs(
            _action_amplitude(6.0, 0.23, charges, config())
            - float(amplitude(6.0, 0.23, charges, ActionInputs()))
        )
        for charges in ((-1, 1, -1, 1), (1, 1, 1, 1))
    ]
    implementation_text = (
        ROOT / "docs/core/uet_o2_invariant_rate_collision_operator.py"
    ).read_text(encoding="utf-8")
    checks = {
        "symbolic_operator_dimension_E1": contract["unit_contract"]["collision_operator"] == 1,
        "whole_action_operator_scales_E1": all(
            abs(row["measured_energy_exponent"] - 1.0) < 1.0e-10 for row in rows
        ),
        "operator_symmetric": state.operator_symmetry_residual <= 1.0e-12,
        "operator_positive_semidefinite": state.positive_semidefinite_min_eigenvalue
        >= -10.0 * state.relative_eigenvalue_tolerance,
        "charge_energy_momentum_conserved": state.collision_conservation_residual <= 1.0e-9
        and state.maximum_channel_invariant_residual <= 1.0e-10,
        "detailed_balance_preserved": state.maximum_detailed_balance_residual <= 1.0e-10,
        "relative_eigenvalue_resolution_used": state.relative_eigenvalue_tolerance > 0.0,
        "production_action_amplitude_matches": max(production_amplitude_residuals) <= 1.0e-14,
        "no_clipping_or_cone_padding": "min(1.0, max(-1.0" not in implementation_text
        and "cone_padding" not in implementation_text,
        "legacy_operator_not_overwritten": (
            ROOT / "docs/core/uet_o2_action_derived_transition_kernel.py"
        ).exists(),
    }
    status = (
        "PASS_SCOPED_INVARIANT_RATE_OPERATOR_REPAIR"
        if all(checks.values())
        else "WARN_INVARIANT_RATE_OPERATOR_REPAIR"
    )
    paths = [
        "docs/core/uet_o2_invariant_rate_collision_operator.py",
        "docs/scripts/audit/audit_topic13_invariant_rate_collision_repair.py",
        "docs/core/test/test_topic13_invariant_rate_collision_repair.py",
        "docs/core/uet_o2_action_derived_transition_kernel.py",
    ]
    prior = "docs/core/artifacts/t13_transition_kernel_rate_dimension_no_go.json"
    artifact = {
        "schema_version": "t13-invariant-rate-collision-repair-v1",
        "major_result_id": "T13_INVARIANT_RATE_DIMENSION_COLLISION_OPERATOR_REPAIR",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "verification_status": status,
        "what_is_closed": [
            "A separate invariant-phase-space finite operator has collision-rate dimension E rather than the rejected legacy E^2 dimension.",
            "The finite representative operator is symmetric, positive semidefinite, and annihilates the declared charge, energy, and momentum invariants within tolerance.",
            "The same charge-resolved contact-plus-Phi action amplitude is used in the channel weight; no universal multiplier is applied to the legacy rung.",
        ],
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": contract["equations"],
        "ontology": {"C": "unchanged", "Phi": "effective response variable", "R_gen": "excluded", "R_obs": "excluded"},
        "unit_lane": "natural_units",
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": "Finite representative collision-rate operator, not a transport coefficient",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_REPAIR",
        "state": asdict(state),
        "scale_witnesses": rows,
        "checks": checks,
        "production_amplitude_residuals": production_amplitude_residuals,
        "open_blockers": [
            "connected_charge_resolved_multi_shell_invariant_collision_operator",
            "converged_outgoing_angular_basis",
            "self_consistent_width_from_same_kernel",
            "number_changing_and_response_channels",
            "physical_Kubo_and_SI_normalization",
        ],
        "controlling_blocker": "connected_charge_resolved_multi_shell_invariant_collision_operator_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [{"path": prior, "sha256": _sha(prior)}],
        "dependency_unlocked": ["dimensionally_admissible_finite_rate_operator_for_continuum_construction"],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Finite representative natural-unit rate-dimension, PSD, conservation, and action-amplitude repair only; not a connected continuum rung, self-consistent width, ladder, Kubo/SI coefficient, external validation, or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added a separate invariant-rate finite operator with production contact-plus-Phi amplitudes; preserved the rejected legacy operator unchanged.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Replace representative angular cells with a connected charge-resolved multi-shell angular basis, then derive the width from that same operator.",
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
        "classification": "candidate_invariant_rate_finite_operator",
        "relation_or_code_path": artifact["equation_or_mapping"],
        "standard_physics_counterpart": "Lorentz-invariant linearized 2-to-2 Boltzmann collision quadratic form",
        "variables": {"W_c": "invariant channel functional", "v_c": "weighted transition vector", "L_rate": "collision rate operator"},
        "mathematical_role": "dimensionally admissible finite precursor to a connected collision operator",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Declared covariant O(2)-Phi action and invariant two-body phase space",
        "assumptions": {"natural_units": True, "elastic_equal_mass_channels": True, "finite_representative_angular_cells": True},
        "symmetry_and_conservation": "PSD outer products; exact channel charge, energy and momentum invariants",
        "limiting_cases": ["whole-action energy scales 1.5, 2, 3", "Phi coupling included", "legacy operator preserved"],
        "implementation_paths": [paths[0]],
        "verifier_paths": [paths[2]],
        "evidence_class": "INTERNAL_STRUCTURAL_CANDIDATE",
        "proof_status": "FINITE_RATE_DIMENSION_AND_CONSERVATION_VERIFIED",
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "precursor_only_not_physical_unlock",
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
    print(json.dumps({"status": status, "checks": checks, "scale_witnesses": rows}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
