from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_strict_cfl_reference_has_compact_support():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["reference_status"] == "PASS"
    metrics = artifact["reference"]["metrics"]
    assert metrics["prearrival_target_abs"] == 0.0
    assert metrics["prearrival_max_outside_discrete_cone"] == 0.0
    assert metrics["support_violations"] == 0
    assert metrics["arrival_target_abs"] > 0.0


def test_reference_does_not_promote_default_candidate():
    artifact = load_artifact()
    assert artifact["default_candidate_status"] == "BLOCKED"
    assert artifact["default_candidate_causal_gate"] == "FAIL"
    assert artifact["default_candidate_prearrival_leakage_fraction"] > 1.0e-6


def test_reference_scope_is_narrow_and_explicit():
    artifact = load_artifact()
    assert artifact["reference"]["scope"] == (
        "linearized_space_response_with_frozen_C"
    )
    assert artifact["implementation_contract"]["required_cfl"] == 1.0
    assert "not a replacement" in artifact["implementation_contract"]["scope_boundary"]
