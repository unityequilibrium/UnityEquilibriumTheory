from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AUDIT_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_krsw_two_face_common_norm.py"
SPEC = importlib.util.spec_from_file_location("krsw_two_face_common_norm_audit", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load audit module: {AUDIT_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)

ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_two_face_common_norm.json"


def test_exact_fixed_cycle_rules_out_strict_common_contraction() -> None:
    artifact = AUDIT.build_artifact()
    assert artifact["checks"]["round_trip_fixed_vector_exact"] is True
    assert artifact["checks"]["right_face_intermediate_nonzero"] is True
    assert artifact["composition"]["strict_common_contraction_is_impossible"] is True


def test_weak_common_norm_and_evolution_claims_remain_open() -> None:
    artifact = AUDIT.build_artifact()
    open_text = " ".join(artifact["major_result"]["what_remains_open"])
    assert "nonincreasing form" in open_text
    assert artifact["major_result"]["dependency_unlocked"] == "none"
    assert artifact["claim_promotion"] is False
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False


def test_artifact_rebuild_and_source_hashes_match() -> None:
    recorded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rebuilt = AUDIT.build_artifact()
    assert recorded["checks"] == rebuilt["checks"]
    assert recorded["composition"] == rebuilt["composition"]
    for relative_path, expected_hash in recorded["source_hashes"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
