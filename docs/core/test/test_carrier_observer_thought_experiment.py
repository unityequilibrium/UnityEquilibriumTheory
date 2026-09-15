"""Boundary tests for the Wave 8 observer thought-experiment artifact."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/carrier_observer_thought_experiment.json"


def read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_event_order_and_past_record_are_explicit() -> None:
    artifact = read()
    events = artifact["events"]
    assert artifact["status"] == "SIMULATION_ONLY"
    assert events["arrival_event"]["time"] > events["source_event"]["time"]
    assert events["arrival_event"]["delay"] > 0.0
    assert artifact["checks"]["detector_receives_past_source_state"] is True


def test_observer_record_does_not_become_particle_or_trace() -> None:
    artifact = read()
    text = " ".join(artifact["interpretation"].values())
    assert "R_gen particle identity" in text
    assert "Lorentz-covariant UET derivation" in text
    assert artifact["interpretation"]["observer_layer"].startswith("R_obs")
