"""Regression tests for the strict all-wave completion audit."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path

ROOT = repo_root()
SCRIPT = ROOT / "docs/scripts/audit/audit_uet_all_waves_completion.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "uet_all_waves_completion_audit", SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load completion audit script: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_wave_completion_packet_is_closed_without_physics_promotion():
    report = load_module().build(run_tests=False)

    assert report["audit_status"] == "PASS_WITH_FOUNDATION_PHYSICS_BLOCKED"
    assert report["status"] == "PROGRAM_CONTROL_CLOSED_FOUNDATION_PHYSICS_NOT_CLOSED"
    assert report["wave_count"] == 12
    assert report["failed_evidence_paths"] == []
    assert all(report["checks"].values())
    assert report["foundation_boundary"]["status"] == "BLOCKED"
    assert report["foundation_boundary"]["physical_promotion_allowed"] is False

    for wave in report["waves"]:
        assert wave["evidence_present"] is True, wave["wave"]
        assert wave["evidence_hashes_current"] is True, wave["wave"]
        assert wave["boundary_complete"] is True, wave["wave"]


if __name__ == "__main__":
    test_all_wave_completion_packet_is_closed_without_physics_promotion()
