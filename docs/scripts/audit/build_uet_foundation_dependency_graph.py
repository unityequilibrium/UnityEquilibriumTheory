"""Build the explicit dependency graph and claim ceiling for the foundation program."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402


OUTPUT = ROOT / canonical_artifact_path("uet_foundation_dependency_graph.json", "gates")


def main() -> int:
    nodes: list[dict[str, Any]] = [
        {"id": "foundation.inventory", "status": "BLOCKED", "controller": "F0 inventory is not code-complete or correspondence-complete"},
        {"id": "foundation.ontology", "status": "WARN", "controller": "lane-specific physical realization and observer-layer review remain open"},
        {"id": "foundation.correspondence", "status": "BLOCKED", "controller": "standard counterpart and observable map are incomplete"},
        {"id": "foundation.units", "status": "BLOCKED", "controller": "normalized core has no complete SI lane"},
        {"id": "matter_space.core", "status": "CANDIDATE", "controller": "causal pilot leakage and upstream foundation gate"},
        {"id": "impact_effect.relation", "status": "CANDIDATE", "controller": "carrier-specific conservation, units, and detector map"},
        {"id": "phase_pilot.0.11", "status": "BLOCKED", "controller": "internal diagnostic only; structure-factor replicate/temporal controller remains open"},
        {"id": "thermal_pilot.0.13", "status": "BLOCKED", "controller": "dimensional thermal observable mapping remains open"},
        {"id": "carrier.comparator", "status": "BLOCKED", "controller": "matter-space and carrier-neutral contracts must precede particle lanes"},
        {"id": "photon.observer", "status": "BLOCKED", "controller": "phase/core gates and detector measurement operator"},
        {"id": "neutrino.0.7", "status": "BLOCKED", "controller": "benchmark compatibility is not a derivation of neutrino or I-field identity"},
        {"id": "orbit.cosmology", "status": "BLOCKED", "controller": "closed-limit and many-body correspondence remain unverified"},
    ]
    edges = [
        ("foundation.inventory", "foundation.ontology"),
        ("foundation.ontology", "foundation.correspondence"),
        ("foundation.correspondence", "foundation.units"),
        ("foundation.units", "matter_space.core"),
        ("matter_space.core", "impact_effect.relation"),
        ("matter_space.core", "phase_pilot.0.11"),
        ("matter_space.core", "thermal_pilot.0.13"),
        ("phase_pilot.0.11", "carrier.comparator"),
        ("impact_effect.relation", "carrier.comparator"),
        ("carrier.comparator", "photon.observer"),
        ("photon.observer", "neutrino.0.7"),
        ("photon.observer", "orbit.cosmology"),
    ]
    graph = {
        "schema_version": "uet-foundation-dependency-graph-v1",
        "artifact": "uet_foundation_dependency_graph",
        "generated_at": date.today().isoformat(),
        "status": "BLOCKED",
        "claim_ceiling": "candidate normalized effective model, candidate collective-behaviour coordinate, derived history observable, and simulation-only diagnostics",
        "status_rule": "a blocked upstream node prevents downstream PASS or physical promotion",
        "nodes": nodes,
        "edges": [{"from": source, "to": target} for source, target in edges],
        "required_order": [
            "ontology",
            "standard_physics_correspondence",
            "units",
            "derivation",
            "formal_verification",
            "numerical_verification",
            "observable_mapping",
            "real_data_comparison",
            "claim",
        ],
        "next_controller": "complete foundation inventory and correspondence review before adding physical interpretation or particle identity",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"nodes={len(nodes)}")
    print(f"edges={len(edges)}")
    print("status=BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
