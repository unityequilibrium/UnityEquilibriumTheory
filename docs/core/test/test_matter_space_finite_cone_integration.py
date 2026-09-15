"""Tests for selected finite-cone shared-ledger integration boundary."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/matter_space_finite_cone_shared_ledger_integration.json"


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_selected_lane_integrates_without_promoting_full_candidate() -> None:
    artifact = load()
    assert artifact["audit_status"] == "PASS"
    assert artifact["operator_mode"] == "matter_space_characteristic_cone_v1"
    assert artifact["unit_lane"] == "normalized_only_v1"
    assert artifact["checks"]["characteristic_compact_support"] is True
    assert artifact["checks"]["normalized_observable_contract"] is True
    assert artifact["checks"]["full_default_candidate_blocker_preserved"] is True
    assert artifact["checks"]["si_mapping_remains_open"] is True
    assert artifact["checks"]["mass_density_mapping_remains_undefined"] is True
