"""Integrity checks for the locked resolution experiment, not convergence proof."""
import json
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def read(name):
    return json.loads((ROOT/"docs/core/artifacts"/name).read_text())


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


def test_recorded_input_hashes_match():
    artifact=read("t13_transport_resolution_audit.json")
    for evidence in artifact["evidence_artifacts"]:
        assert sha256((ROOT/evidence["path"]).read_bytes()).hexdigest()==evidence["sha256"]
