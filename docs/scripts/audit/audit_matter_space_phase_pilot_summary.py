"""Export the Topic 0.11 matter-space pilot under the foundation artifact name.

This is a provenance-preserving summary, not a second simulation.  It keeps
the topic's internal diagnostic status and its independent blockers visible to
the core dependency graph.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_matter_space_phase_coupling_diagnostic.json"
OUT = ROOT / "docs/core/07_artifacts/archive/matter_space_phase_pilot.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source: dict[str, Any] = json.loads(SOURCE.read_text(encoding="utf-8"))
    artifact = {
        "schema_version": "1.0",
        "artifact": "matter_space_phase_pilot",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "INTERNAL_DIAGNOSTIC",
        "verification_status": source["verification_status"],
        "simulation_status": source["simulation_status"],
        "dependency_status": source["dependency_status"],
        "topic_status_impact": source["topic_status_impact"],
        "source_artifact": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": sha256(SOURCE),
            "source_status": source["status"],
        },
        "operator_mode": source["operator_mode"],
        "unit_lane": source["unit_lane"],
        "comparators": source["comparators"],
        "initial_conditions": source["initial_conditions"],
        "diagnostics": {
            "same_C_different_space_state": source["same_C_different_space_state"],
            "same_complete_state_different_trace_history": source["same_complete_state_different_trace_history"],
            "resolution_control": source["resolution_control"],
            "causal_arrival": source["causal_arrival"],
            "local_checks": source["local_checks"],
        },
        "claim_boundary": source["claim_boundary"],
        "falsification_state": source["falsification_state"],
        "controlling_blocker": source["next_controller"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"artifact={OUT.relative_to(ROOT).as_posix()}")
    print(f"status={artifact['status']} dependency={artifact['dependency_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
