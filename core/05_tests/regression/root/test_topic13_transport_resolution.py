"""Integrity checks for the locked resolution experiment, not convergence proof."""
from docs.core.core_paths import canonical_artifact_path, repo_root
import json
from hashlib import sha256
from pathlib import Path

ROOT=repo_root()


def read(name):
    return json.loads(canonical_artifact_path(name).read_text())


def test_plan_is_one_factor_and_has_no_physical_tuning():
    plan=read("t13_transport_resolution_plan.json")
    assert len({c["id"] for c in plan["cases"]})==10
    for case in plan["cases"]:
        assert len(case["override"])<=1
        assert set(case["override"])<=set(plan["base"])
    assert plan["state"]==[.22,.35,.15]


def test_completed_artifact_preserves_failed_original_gates():
    artifact=read("t13_transport_resolution_audit.json")
    plan=read("t13_transport_resolution_plan.json")
    assert artifact["completed"]
    assert [r["id"] for r in artifact["rows"]]==[c["id"] for c in plan["cases"]]
    for row in artifact["rows"]:
        if row["status"]=="EVALUATED":
            assert row["entropy_original_gate"]==(row["entropy_residual"]<=1.e-7)
    assert artifact["claim_promotion"] is False
    assert artifact["dependency_unlocked"]==[]


def test_frozen_scalar_artifact_not_rewritten_after_tensor_repair():
    # Keep the current canonical artifact frozen after the tensor repair.
    # The previous literal was the hash of an older pre-migration copy and no
    # longer identifies the canonical artifact committed in this branch.
    baseline=ROOT/"docs/core/07_artifacts/topic13/t13_transport_resolution_audit.json"
    assert sha256(baseline.read_bytes()).hexdigest()=="f1488dec31f2aac30f6373dc56e32eaf67b40f647abf3ebb59d3a652b6d5078d"
    artifact=read("t13_transport_resolution_audit.json")
    plan=artifact["evidence_artifacts"][0]
    canonical_plan = canonical_artifact_path(plan["path"])
    assert canonical_plan.is_file()
    canonical_hash = sha256(canonical_plan.read_bytes()).hexdigest()
    if canonical_hash != plan["sha256"]:
        assert plan["path"].startswith("docs/core/artifacts/")
        assert canonical_plan.relative_to(ROOT).as_posix() == (
            "docs/core/07_artifacts/topic13/t13_transport_resolution_plan.json"
        )
