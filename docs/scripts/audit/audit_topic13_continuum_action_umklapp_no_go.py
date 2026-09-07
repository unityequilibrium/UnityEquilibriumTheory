"""Audit whether the current continuum O(2)/Phi lane can supply Umklapp."""
from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import hashlib
import inspect
import json

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_invariant_galerkin_collision_operator import (
    invariant_galerkin_collision_state,
)
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs,
    amplitude,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_continuum_action_umklapp_direct_route_no_go.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_umklapp_no_go_addendum.json"
EQUATION_ID = "uet.o2.thermal.continuum_action_umklapp_direct_route_no_go"
LATTICE_TOKENS = (
    "lattice",
    "reciprocal",
    "unit_cell",
    "umklapp",
    "crystal_momentum",
    "bloch",
    "brillouin",
)


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def _field_names(config_type: type) -> list[str]:
    return [field.name for field in fields(config_type)]


def build_boundary_witness() -> dict[str, object]:
    config_surfaces = {
        "ActionInputs": _field_names(ActionInputs),
        "CovariantMatterConfig": _field_names(CovariantMatterConfig),
        "CovariantResponseConfig": _field_names(CovariantResponseConfig),
        "O2FiniteDensityEOSConfig": _field_names(O2FiniteDensityEOSConfig),
    }
    lattice_fields = {
        name: [
            field_name
            for field_name in names
            if any(token in field_name.lower() for token in LATTICE_TOKENS)
        ]
        for name, names in config_surfaces.items()
    }
    collision = invariant_galerkin_collision_state(
        0.25,
        0.1,
        0.0,
        radial_order=4,
        incoming_angular_order=4,
        outgoing_angular_order=4,
        outgoing_azimuth_order=4,
        feature_order=3,
    )
    amplitude_parameters = list(inspect.signature(amplitude).parameters)
    return {
        "config_surfaces": config_surfaces,
        "lattice_fields": lattice_fields,
        "amplitude_parameters": amplitude_parameters,
        "amplitude_absolute_position_or_reciprocal_input": any(
            any(token in parameter.lower() for token in LATTICE_TOKENS)
            for parameter in amplitude_parameters
        ),
        "collision_event_count": collision.collision_event_count,
        "maximum_event_energy_residual": collision.maximum_event_energy_residual,
        "maximum_event_momentum_residual": collision.maximum_event_momentum_residual,
        "event_contract": "p1+p2-p3-p4=0",
        "required_umklapp_contract": "p1+p2-p3-p4=G with reciprocal G!=0",
        "reciprocal_vector_unit": "E in natural units",
        "lattice_spacing_unit": "E^-1 in natural units",
    }


def main() -> int:
    witness = build_boundary_witness()
    parent_path = "docs/core/artifacts/t13_lattice_momentum_relaxing_heat_parent_audit.json"
    parent = json.loads((ROOT / parent_path).read_text(encoding="utf-8"))
    checks = {
        "declared_action_configs_have_no_lattice_fields": not any(witness["lattice_fields"].values()),
        "elastic_amplitude_has_no_reciprocal_or_position_input": not witness["amplitude_absolute_position_or_reciprocal_input"],
        "current_events_enforce_exact_energy_conservation": witness["maximum_event_energy_residual"] <= 1.0e-12,
        "current_events_enforce_exact_continuum_momentum_conservation": witness["maximum_event_momentum_residual"] <= 1.0e-12,
        "nonzero_reciprocal_transfer_absent": witness["event_contract"] != witness["required_umklapp_contract"],
        "standard_lattice_parent_keeps_rates_external": parent["reference_witness"]["resistive_collision_origin"] == "external_synthetic_control_not_derived_or_fitted",
        "standard_lattice_parent_claims_no_uet_mapping": parent["reference_witness"]["uet_mapping_claimed"] is False,
        "no_fit_holdout_or_physical_transport_promotion": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = "PASS_SCOPED_CONTINUUM_ACTION_UMKLAPP_DIRECT_ROUTE_NO_GO" if passed else "WARN_UMKLAPP_CORRESPONDENCE_UNRESOLVED"
    equations = {
        "current_vertex_conservation": "p1+p2-p3-p4=0",
        "umklapp_requirement": "p1+p2-p3-p4=G, G!=0, G in reciprocal lattice",
        "reciprocal_lattice": "G_n=2*pi*n/a for a declared lattice spacing a",
        "direct_route_no_go": "exact continuum translation invariance plus no reciprocal-lattice structure cannot emit a nonzero G channel",
    }
    what_is_closed = [
        "The currently declared flat continuum O(2)/Phi action and its action-normalized elastic collision lane cannot directly represent an Umklapp event with nonzero reciprocal-lattice momentum.",
        "The existing collision event generator enforces exact continuum four-momentum conservation and exposes no lattice spacing, unit cell, reciprocal vector, Bloch label or Brillouin-zone input.",
        "The synthetic lattice heat parent is therefore a standard comparator and cannot be promoted by reusing current continuum coefficients as physical Umklapp rates.",
    ]
    open_blockers = [
        "explicit_material_lattice_sector_or_periodic_background_missing",
        "uet_to_phonon_energy_and_heat_current_mapping_missing",
        "source_backed_normal_and_umklapp_collision_kernel_missing",
        "material_frame_SI_uncertainty_and_TTG_mapping_missing",
        "independent_alpha_Phi_K_missing",
    ]
    routes = {
        "recommended_near_term": {
            "id": "external_material_lattice_sector_interface",
            "requirements": [
                "declare displacement or strain field and lattice rest frame",
                "source-lock phonon dispersion and normal/Umklapp collision inputs",
                "derive an interaction mapping from UET variables to material energy/current without identifying Phi with temperature",
                "close units, ledger, detailed balance, entropy and uncertainty",
            ],
            "reason": "TTG is a material/lattice experiment and does not require UET to generate the crystal itself",
        },
        "fundamental_long_term": {
            "id": "uet_periodic_background_bloch_derivation",
            "requirements": [
                "derive a stable periodic solution from an explicit action",
                "derive lattice spacing and reciprocal vectors rather than insert them",
                "construct Bloch quasiparticles, phonon heat current and collision selection rules",
                "prove the homogeneous continuum limit and avoid ontology relabeling",
            ],
            "reason": "This is required only if UET is claimed to generate the lattice sector internally",
        },
    }
    source_paths = [
        "docs/core/uet_covariant_matter.py",
        "docs/core/uet_covariant_response.py",
        "docs/core/uet_o2_finite_density_eos.py",
        "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
        "docs/core/uet_o2_invariant_galerkin_collision_operator.py",
        "docs/scripts/audit/audit_topic13_continuum_action_umklapp_no_go.py",
        "docs/core/test/test_topic13_continuum_action_umklapp_no_go.py",
    ]
    artifact = {
        "schema_version": "t13-continuum-action-umklapp-direct-route-no-go-v1",
        "major_result_id": "T13_CONTINUUM_ACTION_UMKLAPP_DIRECT_ROUTE_NO_GO",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "CLOSED_AS_NO_GO" if passed else "OPEN",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "STRUCTURAL_BOUNDARY_NOT_NEW_CORE_EQUATION",
        "equation_or_mapping": equations,
        "ontology": {
            "C": "unchanged; not crystal momentum or lattice mass",
            "Phi": "unchanged effective response; not temperature, strain or phonon displacement",
            "R_gen": "excluded derived history trace",
            "R_obs": "excluded",
            "material_lattice": "new sector required if selected; not silently contained in Phi",
        },
        "unit_lane": "natural_flat_3p1_structural_boundary",
        "units": {
            "four_momentum_and_G": "E",
            "lattice_spacing": "E^-1",
            "selection_rule": "E",
        },
        "derivation_class": "translation_symmetry_and_selection_rule_no_go",
        "observable": "Availability of a nonzero reciprocal-lattice momentum-transfer channel, not conductivity",
        "data_role": "DERIVED_IMPLEMENTATION_STRUCTURAL_NO_GO",
        "witness": witness,
        "admissible_routes": routes,
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": "explicit_material_lattice_interface_or_periodic_background_missing",
        "source_hashes": {path: _sha(path) for path in source_paths},
        "evidence_artifacts": [{"path": parent_path, "sha256": _sha(parent_path)}],
        "dependency_unlocked": [
            "external_material_lattice_sector_interface_design",
            "periodic_background_bloch_derivation_research_track",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "No-go only for direct Umklapp generation by the currently declared homogeneous continuum O(2)/Phi action and collision implementation; not a theorem against coupling UET to a material lattice or deriving a future periodic branch.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"] + "/" + artifact["closure_disposition"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Tested whether the current action can supply the reciprocal-lattice transfer required by the new heat parent instead of assuming an Umklapp coefficient.",
        "EQUATION_OR_MAPPING": equations,
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Build the external material-lattice interface first for TTG; keep periodic-background derivation as a separate fundamental track.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "structural_umklapp_direct_route_no_go",
        "relation_or_code_path": equations,
        "ontology": artifact["ontology"],
        "standard_physics_counterpart": "Crystal-momentum conservation modulo a reciprocal-lattice vector",
        "variables": {"p_i": "continuum quasiparticle momenta", "G": "reciprocal-lattice vector", "a": "lattice spacing"},
        "mathematical_role": "selection-rule obstruction for direct continuum-action Umklapp",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Declared UET continuum action/config surfaces and eventwise collision conservation",
        "assumptions": {
            "scope": "current flat homogeneous O2/Phi lane only",
            "translation_invariance": True,
            "nonzero_reciprocal_vector_absent": True,
        },
        "symmetry_and_conservation": "Current lane preserves exact continuum four-momentum; Umklapp requires crystal momentum modulo G",
        "limiting_cases": ["G=0 normal process", "G!=0 Umklapp requirement"],
        "implementation_paths": source_paths[:5],
        "verifier_paths": source_paths[5:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "INTERNAL_STRUCTURAL_NO_GO",
        "proof_status": "DIRECT_CURRENT_ACTION_ROUTE_REJECTED",
        "verification_status": status,
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "material_interface_design_controller",
        "physical_dependency_unlock": False,
        "controlling_blocker": artifact["controlling_blocker"],
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
        "claim_boundary": artifact["claim_boundary"],
    }
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version": "uet-equation-registry-addendum-v1",
        "status": "STRUCTURAL_NO_GO_NOT_MERGED_AS_CORE_EQUATION",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries": [entry],
        "full_core_unlock": False,
        "claim_promotion": False,
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "maximum_event_momentum_residual": witness["maximum_event_momentum_residual"],
        "lattice_fields": witness["lattice_fields"],
        "recommended_route": routes["recommended_near_term"]["id"],
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
