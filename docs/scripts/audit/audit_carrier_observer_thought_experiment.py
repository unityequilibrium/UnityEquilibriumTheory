"""Package the finite-signal observer thought experiment.

The source dynamics come from the existing Newtonian comparator. This packet
only makes the event ordering explicit: source/emission, propagation delay,
arrival, and detector record. It is not a Lorentz-covariant derivation and it
does not identify a carrier with ``R_gen``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "docs/core/07_artifacts/verification/relational_two_body_baseline_verification.json"
OUT = ROOT / "docs/core/07_artifacts/archive/carrier_observer_thought_experiment.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source: dict[str, Any] = json.loads(SOURCE.read_text(encoding="utf-8"))
    observation = source["metrics"]["observation"]
    checks = {
        "source_event_declared": observation["event_time"] >= 0.0,
        "emission_to_arrival_delay_positive": observation["delay"] > 0.0,
        "detector_receives_past_source_state": observation["past_state_separation"] > 0.0,
        "source_state_at_arrival_differs": observation["received_position_a"] != observation["source_position_at_arrival"],
        "observer_record_is_not_source_state": True,
        "no_superluminal_inference": True,
        "lorentz_covariance_not_claimed": True,
    }
    artifact = {
        "schema_version": "1.0",
        "artifact": "carrier_observer_thought_experiment",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "SIMULATION_ONLY" if all(checks.values()) else "FAIL",
        "evidence_class": "internal_newtonian_finite_signal_comparator",
        "source_artifact": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": sha256(SOURCE),
            "audit_status": source.get("audit_status"),
        },
        "events": {
            "source_event": {"time": observation["event_time"], "position": observation["event_position_a"]},
            "emission_event": {"time": observation["event_time"], "carrier_role": "finite_signal_comparator"},
            "arrival_event": {"time": observation["arrival_time"], "delay": observation["delay"]},
            "detector_record": {"received_source_state": observation["received_position_a"], "arrival_index": observation["arrival_index"]},
        },
        "interpretation": {
            "what_is_shown": "A detector record can encode a source state from an earlier event because propagation takes finite time.",
            "what_is_not_shown": "No photon identity, no R_gen particle identity, no global vacuum claim, and no Lorentz-covariant UET derivation.",
            "physical_trace_layer": "R_gen remains a derived trace of source dynamics.",
            "observer_layer": "R_obs is a detector record and does not alter source dynamics in this comparator.",
        },
        "checks": checks,
        "claim_boundary": "simulation-only observer-layer correspondence; detector and carrier units remain open",
        "next_controller": "source-lock a dimensional photon detector map after foundation and carrier gates close",
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"artifact={OUT.relative_to(ROOT).as_posix()}")
    print(f"status={artifact['status']}")
    return 0 if artifact["status"] == "SIMULATION_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
