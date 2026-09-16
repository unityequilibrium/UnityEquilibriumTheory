"""Verify the collective-behavior and observer-layer contract against local core surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/gates/matter_collective_behavior_observation_gate.json"


def _source(relative_path: str, markers: list[str]) -> dict[str, object]:
    path = ROOT / relative_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
    marker_results = {marker: marker in text for marker in markers}
    return {
        "path": relative_path,
        "exists": exists,
        "sha256": digest,
        "markers": marker_results,
        "source_gate": exists and all(marker_results.values()),
    }


def main() -> None:
    sources = [
        _source(
            "docs/core/AGENTS.md",
            [
                "`C` is a system-state coordinate",
                "`Phi` is an effective response variable",
                "`R` / `I_trace` is a derived causal/history observable",
            ],
        ),
        _source(
            "docs/core/02_equations/matter_space/uet_matter_space.py",
            [
                "class MatterSpaceState",
                "space_response",
                "matter_space_free_energy",
                "coupling_g",
            ],
        ),
        _source(
            "docs/topics/0.13_Thermodynamic_Bridge/MATTER_COLLECTIVE_BEHAVIOR_OBSERVATION_CONTRACT.md",
            [
                "Two ontological layers, not two substances",
                "C=\\mathcal C[B_{\\mathrm{sys}}]",
                "Persistence is not coordinate time",
                "Y_O=\\mathcal M_O",
            ],
        ),
    ]
    source_gate = all(source["source_gate"] for source in sources)
    artifact = {
        "schema_version": "matter-collective-behavior-observation-gate-v1",
        "topic": "0.13_Thermodynamic_Bridge",
        "audit_status": "PASS_WITH_OPEN_MAPPING_GATES" if source_gate else "FAIL_SOURCE_ALIGNMENT",
        "source_gate": source_gate,
        "sources": sources,
        "ontology_gate": {
            "C_collective_system_coordinate": True,
            "Phi_physical_response_candidate": True,
            "R_derived_trace_no_feedback": True,
            "observer_record_separate_from_physical_state": True,
            "information_not_new_substance": True,
        },
        "persistence_gate": {
            "persistence_is_system_lifetime_functional": True,
            "persistence_is_new_coordinate_time": False,
            "energy_reserve_scale_closed": False,
            "behavior_power_cost_closed": False,
        },
        "open_mapping_gates": [
            "matter_behavior_to_collective_C_coarse_graining",
            "collective_behavior_power_cost",
            "C_to_Phi_response_source_and_sign",
            "observer_measurement_operator_for_concrete_lane",
            "dimensional_energy_entropy_temperature_mapping",
        ],
        "core_dynamics_changed": False,
        "claim_boundary": "ontology and causal-architecture candidate; no physical information substance, lifetime law, temperature derivation, or spacetime replacement claimed",
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit_status": artifact["audit_status"], "output": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()

