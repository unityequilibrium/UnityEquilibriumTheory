"""Tests for the carrier-neutral comparator contract boundary."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


def test_carrier_comparator_has_three_declared_lanes_and_stays_blocked() -> None:
    path = canonical_artifact_path("carrier_neutral_comparator_contract.json")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["contract_verification"] == "PASS"
    assert artifact["dependency_status"] == "BLOCKED"
    assert {lane["lane_id"] for lane in artifact["lanes"]} == {
        "photon", "neutrino", "electron_positron_reaction"
    }


def test_carrier_comparator_does_not_promote_trace_or_transition_identity() -> None:
    path = canonical_artifact_path("carrier_neutral_comparator_contract.json")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    policy = artifact["comparison_policy"]
    assert policy["parameter_fitting"] is False
    assert policy["external_validation"] is False
    assert policy["I_trace_is_any_lane"] is False
    assert policy["massless_transition_is_automatic"] is False
    neutrino = next(lane for lane in artifact["lanes"] if lane["lane_id"] == "neutrino")
    assert "LEGACY_PURE_I_FIELD" in neutrino["uet_identity_status"]
