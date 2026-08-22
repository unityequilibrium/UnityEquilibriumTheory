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
        "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY": {
            "depends_on": ["T13_FULL_THERMODYNAMIC_BRIDGE"],
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
        "unlock_order": [
            "T13_FULL_THERMODYNAMIC_BRIDGE",
            "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY",
            "GR_CLASSICAL_COMPATIBILITY_LANE",
            "CONSTITUTIVE_TRANSPORT_CORE_LANE",
            "GALAXY_COMPATIBILITY_TRACK",
        ],
        "claim_boundary": "Dependency decisions only; no downstream result is promoted by a checkpoint or comparator pass.",
    }
    # Preserve lane-level Topic 13 evidence and refresh known artifact hashes.
    previous = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.is_file() else {}
    if "topic13_partial_evidence" in previous:
        artifact["topic13_partial_evidence"] = previous["topic13_partial_evidence"]
    partial_routes = {
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
