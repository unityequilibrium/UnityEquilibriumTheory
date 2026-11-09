from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_GATE = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
ARTIFACT_REL = (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_zero_shift_kreiss_symbol.json"
)
RESULT_ID = "CORE_CURVED_3P1_GH_RINNE_ZERO_SHIFT_KREISS_SYMBOL"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_zero_shift_lane_is_registered_with_source_artifact() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    entries = [entry for entry in register["entries"] if entry["major_result_id"] == RESULT_ID]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert entry["verification_status"] == "SOURCE_MATCHED_ZERO_SHIFT_KREISS_LANE_CLOSED"
    assert entry["evidence_artifacts"][0]["path"] == ARTIFACT_REL
    assert entry["evidence_artifacts"][0]["sha256"] == _sha256(ROOT / ARTIFACT_REL)
    assert entry["dependency_unlocked"].startswith("none;")
    assert register["claim_promotion"] is False


def test_dependency_gate_tracks_register_without_unlocking_downstream() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    dependency = json.loads(DEPENDENCY_GATE.read_text(encoding="utf-8"))
    assert dependency["register"]["path"] == REGISTER.relative_to(ROOT).as_posix()
    assert dependency["register"]["sha256"] == _sha256(REGISTER)
    assert dependency["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
    assert dependency["claim_promotion"] is False
    assert register["claim_promotion"] is False


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
