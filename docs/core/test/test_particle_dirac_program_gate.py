"""Tests for the explicit deferred particle-program boundary."""

from __future__ import annotations
from docs.core.core_paths import core_root

import json
from pathlib import Path


ROOT = core_root()


def test_particle_program_is_explicitly_deferred_without_particle_claims() -> None:
    artifact = json.loads((ROOT / "artifacts/particle_dirac_program_gate.json").read_text(encoding="utf-8"))
    assert artifact["audit_status"] == "PASS"
    assert artifact["status"] == "DEFERRED_BLOCKED"
    assert len(artifact["prerequisites"]) == 6
    assert all(item["status"] == "MISSING" for item in artifact["prerequisites"])
    assert artifact["checks"]["no_particle_identity_assigned_to_trace"] is True
