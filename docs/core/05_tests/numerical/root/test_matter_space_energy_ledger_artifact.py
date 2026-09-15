"""Schema and claim-boundary checks for the focused matter-space ledger artifact."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


def test_energy_ledger_artifact_keeps_normalized_and_blocked_boundaries() -> None:
    path = canonical_artifact_path("matter_space_energy_ledger_verification.json")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["artifact"] == "matter_space_energy_ledger_verification"
    assert artifact["status"] in {"PASS", "FAIL"}
    assert artifact["dependency_status"] == "BLOCKED"
    assert artifact["no_loss_language"]["normalized_ledger_only"] is True
    assert artifact["no_loss_language"]["joule_claim"] is False
    assert artifact["no_loss_language"]["trace_is_energy_reservoir"] is False
    assert artifact["upstream_core_controller"] == "prearrival_leakage"
