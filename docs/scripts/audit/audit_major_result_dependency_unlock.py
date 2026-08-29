"""Report downstream major-result unlocks without promoting blocked lanes."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
OUT = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    levels = {entry["major_result_id"]: entry["closure_level"] for entry in register["entries"]}

    nodes = {
        "TOPIC_0_11_CHAOS_DIAGNOSTIC_ROLLOUT": {
            "depends_on": ["T13_THERMAL_DYNAMICAL_REGIME_CLASSIFIED"],
            "required_level": "CLOSED_FOR_LANE",
            "claim_boundary": "diagnostic method rollout only; no universality or exponent promotion",
        },
        "CORE_O2_CHAOS_DIAGNOSTIC_ROLLOUT": {
            "depends_on": ["T13_THERMAL_DYNAMICAL_REGIME_CLASSIFIED"],
            "required_level": "CLOSED_FOR_LANE",
            "claim_boundary": "diagnostic method rollout only; C is not relabelled as a signed O(2) charge",
        },
        "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY": {
            "depends_on": ["T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"],
            "required_level": "CLOSED_FOR_CORE",
            "claim_boundary": "curved 3+1 parent and constraint package only",
        },
        "GR_CLASSICAL_COMPATIBILITY_LANE": {
            "depends_on": ["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"],
            "required_level": "CLOSED_FOR_CORE",
            "claim_boundary": "bounded classical GR compatibility; not Einstein-equation closure",
        },
        "CONSTITUTIVE_TRANSPORT_CORE_LANE": {
            "depends_on": ["GR_CLASSICAL_COMPATIBILITY_LANE"],
            "required_level": "CLOSED_FOR_CORE",
            "claim_boundary": "constitutive transport lane; not Navier-Stokes proof",
        },
        "GALAXY_COMPATIBILITY_TRACK": {
            "depends_on": ["GR_CLASSICAL_COMPATIBILITY_LANE"],
            "required_level": "CLOSED_FOR_CORE",
            "claim_boundary": "galaxy comparison track; not dark-matter elimination",
        },
    }

    decisions = {}
    for node, spec in nodes.items():
        unmet = [
            {"result": dependency, "current_level": levels.get(dependency, "OPEN"), "required_level": spec["required_level"]}
            for dependency in spec["depends_on"]
            if levels.get(dependency) != spec["required_level"]
        ]
        decisions[node] = {
            "status": "UNLOCKED" if not unmet else "BLOCKED_DEPENDENCY",
            "depends_on": spec["depends_on"],
            "unmet_dependencies": unmet,
            "claim_boundary": spec["claim_boundary"],
        }

    artifact = {
        "schema_version": "uet-major-result-dependency-unlock-v1",
        "artifact": "uet_major_result_dependency_unlock_gate",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED_DOWNSTREAM_MAJOR_RESULTS",
        "claim_promotion": False,
        "register": {
            "path": REGISTER.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(REGISTER.read_bytes()).hexdigest(),
        },
        "decisions": decisions,
        "diagnostic_unlock_order": [
            "CORE_DYNAMICAL_STABILITY_DIAGNOSTIC_READY",
            "T010_CHAOS_METHOD_VALIDATED",
            "T13_THERMAL_DYNAMICAL_REGIME_CLASSIFIED",
        ],
        "unlock_order": [
            "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY",
            "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY",
            "GR_CLASSICAL_COMPATIBILITY_LANE",
            "CONSTITUTIVE_TRANSPORT_CORE_LANE",
            "GALAXY_COMPATIBILITY_TRACK",
        ],
        "claim_boundary": "Dependency decisions only; no downstream result is promoted by a checkpoint or comparator pass.",
    }
    curved_parent = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"
        ),
        None,
    )
    adm_interface = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_ADM_CONSTRAINT_INTERFACE_READY"
        ),
        None,
    )
    geometry_operator = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_GEOMETRY_OPERATOR_READY"
        ),
        None,
    )
    adm_evolution_rhs = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_ADM_EVOLUTION_RHS_READY"
        ),
        None,
    )
    fixed_gauge_no_go = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_FIXED_GAUGE_ADM_HYPERBOLICITY_NO_GO"
        ),
        None,
    )
    gh_principal_system = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_GH_PRINCIPAL_SYSTEM_READY"
        ),
        None,
    )
    gh_nonlinear_vacuum_rhs = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_GH_NONLINEAR_VACUUM_RHS_READY"
        ),
        None,
    )
    if any((curved_parent, adm_interface, geometry_operator, adm_evolution_rhs, fixed_gauge_no_go, gh_principal_system, gh_nonlinear_vacuum_rhs)):
        artifact["curved_3p1_progress"] = {
            "parent": curved_parent,
            "adm_constraint_interface": adm_interface,
            "geometry_operator": geometry_operator,
            "adm_evolution_rhs": adm_evolution_rhs,
            "fixed_gauge_adm_hyperbolicity_no_go": fixed_gauge_no_go,
            "generalized_harmonic_principal_system": gh_principal_system,
            "generalized_harmonic_nonlinear_vacuum_rhs": gh_nonlinear_vacuum_rhs,
            "gravity_unlock_status": decisions["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"],
            "controlling_blocker": (
                "curved_3p1_generalized_harmonic_time_integration_and_"
                "constraint_propagation_missing"
            ),
            "claim_boundary": (
                "ADM constraint, periodic spatial geometry, RHS operator, and "
                "fixed-gauge no-go, GH principal-system, and nonlinear vacuum-RHS progress only; "
                "the parent is not CLOSED_FOR_CORE and Gravity remains blocked"
            ),
        }
    # Preserve lane-level Topic 13 evidence and refresh known artifact hashes.
    previous = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.is_file() else {}
    if "topic13_partial_evidence" in previous:
        artifact["topic13_partial_evidence"] = previous["topic13_partial_evidence"]
    if "topic13_core_ready" in previous:
        artifact["topic13_core_ready"] = previous["topic13_core_ready"]
    topic13_core_entry = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
        ),
        None,
    )
    if topic13_core_entry is not None:
        core_ready = artifact.setdefault("topic13_core_ready", {})
        core_ready.update({
            "major_result_id": topic13_core_entry["major_result_id"],
            "closure_level": topic13_core_entry["closure_level"],
            "full_core_unlock": topic13_core_entry["closure_level"] == "CLOSED_FOR_CORE",
            "verification_status": topic13_core_entry.get("verification_status"),
            "evidence_artifacts": topic13_core_entry.get("evidence_artifacts", []),
            "claim_boundary": topic13_core_entry.get("claim_boundary"),
        })
    partial_routes = {
        "covariant_action_si_anchor_route": "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json",
        "covariant_field_normalization_no_go": "docs/core/artifacts/t13_covariant_field_normalization_identifiability_no_go.json",
        "phi_energy_anchor_no_go": "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json",
        "thermal_response_beta_contract": "docs/core/artifacts/t13_thermal_response_beta_contract_audit.json",
        "ding_experimental_heating_input_boundary": "docs/core/artifacts/t13_ding_experimental_heating_input_boundary_audit.json",
    }
    partial_evidence = artifact.get("topic13_partial_evidence", {})
    if isinstance(partial_evidence, dict):
        partial_evidence["register_sha256"] = artifact["register"]["sha256"]
    if isinstance(partial_evidence, dict):
        for key, relative_path in partial_routes.items():
            route = partial_evidence.get(key)
            source_path = ROOT / relative_path
            if isinstance(route, dict) and source_path.is_file():
                route["path"] = relative_path
                route["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        ding_path = ROOT / partial_routes["ding_experimental_heating_input_boundary"]
        if ding_path.is_file():
            partial_evidence["ding_experimental_heating_input_boundary"] = {
                "path": partial_routes["ding_experimental_heating_input_boundary"],
                "sha256": hashlib.sha256(ding_path.read_bytes()).hexdigest(),
                "summary": {
                    "status": "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY",
                    "closure_level": "CLOSED_FOR_LANE",
                    "full_core_unlock": False,
                },
            }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "decisions": decisions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
