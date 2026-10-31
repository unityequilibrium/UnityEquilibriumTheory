from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT_REL = (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_jordan_normalization.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_GATE = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
PARENT_GATE = ROOT / "docs/core/07_artifacts/gates/core_curved_3p1_parent_gate.json"
RESULT_ID = "CORE_CURVED_3P1_GH_RINNE_NEGATIVE_SHIFT_JORDAN_DEGENERACY"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_jordan_artifact_passes_with_bounded_claim() -> None:
    artifact = json.loads((ROOT / ARTIFACT_REL).read_text(encoding="utf-8"))
    assert artifact["STATUS"] == "PASS_EXACT_NEGATIVE_SHIFT_JORDAN_DEGENERACY_LANE"
    assert all(artifact["VERIFICATION"]["checks"].values())
    assert artifact["claim_promotion"] is False
    assert "Not a full complex-frequency transfer estimate" in artifact["CLAIM_BOUNDARY"]
    assert "generic_determinant_confluent_limit" in artifact["VERIFICATION"]["analytic_derivation"]


def test_result_is_registered_with_current_evidence_hash() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    matches = [row for row in register["entries"] if row["major_result_id"] == RESULT_ID]
    assert len(matches) == 1
    entry = matches[0]
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert entry["verification_status"] == "PASS_EXACT_NEGATIVE_SHIFT_JORDAN_DEGENERACY_LANE"
    assert entry["evidence_artifacts"][0]["path"] == ARTIFACT_REL
    assert entry["evidence_artifacts"][0]["sha256"] == _sha256(ROOT / ARTIFACT_REL)
    assert entry["dependency_unlocked"].startswith("none;")


def test_parent_and_dependency_gates_do_not_promote() -> None:
    dependency = json.loads(DEPENDENCY_GATE.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    assert dependency["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
    assert dependency["claim_promotion"] is False
    assert parent["status"] == "PARTIAL_CURVED_3P1_GH_PERIODIC_PRESCRIBED_MATTER_READY"


def test_source_hashes_match() -> None:
    artifact = json.loads((ROOT / ARTIFACT_REL).read_text(encoding="utf-8"))
    for relative, expected in artifact["VERIFICATION"]["source_hashes"].items():
        assert _sha256(ROOT / relative) == expected


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
