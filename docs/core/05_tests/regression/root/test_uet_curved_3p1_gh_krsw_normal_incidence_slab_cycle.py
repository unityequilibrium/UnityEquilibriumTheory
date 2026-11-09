from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AUDIT_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_krsw_normal_incidence_slab_cycle.py"
SPEC = importlib.util.spec_from_file_location("krsw_normal_incidence_slab_cycle_audit", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load audit module: {AUDIT_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)

ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_normal_incidence_slab_cycle.json"


def test_both_round_trip_maps_are_weighted_orthogonal_projections() -> None:
    artifact = AUDIT.build_artifact()
    for cycle in artifact["cycles"].values():
        assert all(cycle["checks"].values())
        assert cycle["rank"] == 4
        assert cycle["energy_defect_rank"] == 6


def test_exact_normal_incidence_pulse_energy_cannot_grow_per_cycle() -> None:
    artifact = AUDIT.build_artifact()
    assert all(artifact["checks"].values())
    assert "E[Pp]=E[p]" in artifact["major_result"]["equation_or_mapping"]["pulse_energy"]
    assert artifact["major_result"]["dependency_unlocked"] == "none"
    assert artifact["claim_promotion"] is False
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False


def test_artifact_rebuild_and_source_hashes_match() -> None:
    recorded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rebuilt = AUDIT.build_artifact()
    assert recorded["checks"] == rebuilt["checks"]
    assert recorded["cycles"] == rebuilt["cycles"]
    for relative_path, expected_hash in recorded["source_hashes"].items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash


def run_tests() -> None:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
