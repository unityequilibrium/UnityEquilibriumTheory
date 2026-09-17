"""Report downstream major-result unlocks without promoting blocked lanes."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
OUT = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_path_for  # noqa: E402


_LEGACY_ARTIFACT_PATH_RE = re.compile(r"docs/core/artifacts/[^\s,\\\"']+")


def _canonicalize_artifact_paths(value: object) -> object:
    """Normalize inherited legacy artifact references in values and keys."""

    if isinstance(value, dict):
        return {
            _canonicalize_artifact_paths(key) if isinstance(key, str) else key:
            _canonicalize_artifact_paths(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_canonicalize_artifact_paths(item) for item in value]
    if not isinstance(value, str) or "docs/core/artifacts/" not in value:
        return value

    def replace(match: re.Match[str]) -> str:
        return canonical_path_for(match.group(0))

    return _LEGACY_ARTIFACT_PATH_RE.sub(replace, value.replace("\\", "/"))


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
    gh_periodic_vacuum_evolution = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY"
        ),
        None,
    )
    topic13_prescribed_matter = next(
        (
            entry
            for entry in register["entries"]
            if entry.get("major_result_id")
            == "CORE_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING_READY"
        ),
        None,
    )
    if any((curved_parent, adm_interface, geometry_operator, adm_evolution_rhs, fixed_gauge_no_go, gh_principal_system, gh_nonlinear_vacuum_rhs, gh_periodic_vacuum_evolution, topic13_prescribed_matter)):
        artifact["curved_3p1_progress"] = {
            "parent": curved_parent,
            "adm_constraint_interface": adm_interface,
            "geometry_operator": geometry_operator,
            "adm_evolution_rhs": adm_evolution_rhs,
            "fixed_gauge_adm_hyperbolicity_no_go": fixed_gauge_no_go,
            "generalized_harmonic_principal_system": gh_principal_system,
            "generalized_harmonic_nonlinear_vacuum_rhs": gh_nonlinear_vacuum_rhs,
            "generalized_harmonic_periodic_vacuum_evolution": gh_periodic_vacuum_evolution,
            "topic13_prescribed_matter_wiring": topic13_prescribed_matter,
            "gravity_unlock_status": decisions["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"],
            "controlling_blocker": "curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing",
            "claim_boundary": (
                "ADM constraint, periodic spatial geometry, RHS operator, and "
                "fixed-gauge no-go, GH principal/nonlinear RHS, periodic vacuum evolution, "
                "and prescribed Topic 13 matter-source progress only; "
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
        # Refresh every promoted Topic 13 lane that is preserved in the
        # dependency artifact.  Keeping this list explicit prevents a stale
        # hash from surviving when the leaf audit is regenerated.
        "collective_response_eos_stability_contract": "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json",
        "causal_branch_selection": "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json",
        "beta_symbol_separation_noncircularity_no_go": "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json",
        "covariant_matter_coupling_normalization_no_go": "docs/core/07_artifacts/topic13/t13_covariant_matter_coupling_normalization_no_go.json",
        "formal_non_circular_bridge_boundary": "docs/core/07_artifacts/topic13/t13_formal_bridge_boundary_audit.json",
        "sk_kms_entropy_interface": "docs/core/07_artifacts/topic13/t13_sk_kms_entropy_contract_audit.json",
        "base_phi_independent_calibration_requirement": "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json",
        "phi_e_reference_normalization": "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json",
        "covariant_action_si_anchor_route": "docs/core/07_artifacts/topic13/t13_covariant_action_si_anchor_route_audit.json",
        "covariant_field_normalization_no_go": "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json",
        "phi_energy_anchor_no_go": "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json",
        "thermal_response_beta_contract": "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json",
        "ding_experimental_heating_input_boundary": "docs/core/07_artifacts/topic13/t13_ding_experimental_heating_input_boundary_audit.json",
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
    artifact = _canonicalize_artifact_paths(artifact)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "decisions": decisions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
