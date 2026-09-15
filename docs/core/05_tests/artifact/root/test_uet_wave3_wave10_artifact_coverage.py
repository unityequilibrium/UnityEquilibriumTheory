"""Completion-audit coverage for the named Wave 3--10 deliverables."""

from __future__ import annotations

import json
from pathlib import Path

from docs.core.core_paths import canonical_artifact_path, repo_root


ROOT = repo_root()
PROGRAM = ROOT / "docs/core/artifacts/uet_wave3_wave10_research_program.json"


REQUIRED = (
    "docs/core/artifacts/matter_space_causal_lane_comparison.json",
    "docs/core/artifacts/matter_space_variational_verification.json",
    canonical_artifact_path("matter_space_energy_ledger_verification.json", "verification"),
    "docs/core/artifacts/matter_space_phase_pilot.json",
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json",
    "docs/core/artifacts/o2_finite_density_eos_verification.json",
    "docs/core/artifacts/covariant_superfluid_transport_verification.json",
    "docs/core/artifacts/carrier_observer_thought_experiment.json",
    "docs/core/artifacts/orbit_cosmology_correspondence_gate.json",
    "docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json",
    "docs/topics/0.26_Cosmic_Dynamic_Frame/Result/artifacts/0_26_cosmic_dynamic_frame_verification.json",
)


def read() -> dict:
    return json.loads(PROGRAM.read_text(encoding="utf-8"))


def test_named_wave_deliverables_exist() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    assert missing == []


def test_named_deliverables_are_represented_in_the_program_gate() -> None:
    artifact = read()
    referenced = {item["path"] for wave in artifact["waves"] for item in wave["inputs"]}
    assert "docs/core/artifacts/matter_space_phase_pilot.json" in referenced
    assert "docs/core/artifacts/orbit_cosmology_correspondence_gate.json" in referenced
    assert artifact["status"] == "BLOCKED"