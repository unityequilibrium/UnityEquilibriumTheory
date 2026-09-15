"""Regression tests for the all-wave closure evidence snapshot."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import importlib.util
from pathlib import Path

ROOT = repo_root()
SCRIPT = ROOT / "docs/scripts/audit/audit_uet_all_waves_closure.py"


def load_module():
    spec = importlib.util.spec_from_file_location("uet_all_waves_closure", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load closure script: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_wave_evidence_hashes_are_current_and_complete():
    report = load_module().build()
    assert report["audit_status"] == "PASS"
    assert report["wave_count"] == 12
    assert report["checks"]["all_planned_waves_present"] is True
    assert report["checks"]["all_waves_have_closure_status"] is True
    assert report["checks"]["all_waves_have_claim_ceiling"] is True
    assert report["checks"]["all_blocked_waves_have_controller"] is True
    assert report["checks"]["no_physical_promotion"] is True

    for wave in report["waves"]:
        assert wave["evidence"], wave["wave"]
        for item in wave["evidence"]:
            path = ROOT / item["path"]
            assert item["exists"] is True, (wave["wave"], item["path"])
            assert item["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), (
                wave["wave"],
                item["path"],
            )


if __name__ == "__main__":
    test_all_wave_evidence_hashes_are_current_and_complete()
