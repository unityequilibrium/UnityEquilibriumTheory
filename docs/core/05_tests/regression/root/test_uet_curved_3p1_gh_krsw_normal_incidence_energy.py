from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AUDIT_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_krsw_normal_incidence_energy.py"
SPEC = importlib.util.spec_from_file_location("krsw_normal_incidence_energy_audit", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load audit module: {AUDIT_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)

ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_normal_incidence_energy.json"


def test_exact_face_maps_and_quadratic_forms() -> None:
    artifact = AUDIT.build_artifact()
    assert all(artifact["checks"].values())
    assert artifact["face_maps"]["right"]["map_rank"] == 4
    assert artifact["face_maps"]["left"]["map_squared_rank"] == 1
    assert artifact["face_maps"]["right"]["quadratic_flux_identity_exact"] is True


def test_two_face_fixed_amplitude_is_not_promoted_to_a_slab_mode() -> None:
    artifact = AUDIT.build_artifact()
    assert artifact["two_face"]["fixed_vector_residual_exact"] == "0"
    assert "not a physical eigenmode" in artifact["two_face"]["interpretation"]
    assert artifact["major_result"]["dependency_unlocked"] == "none"
    assert artifact["claim_promotion"] is False


def test_artifact_matches_recomputed_exact_result_and_source_hashes() -> None:
    recorded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    recomputed = AUDIT.build_artifact()
    assert recorded["checks"] == recomputed["checks"]
    assert recorded["face_maps"] == recomputed["face_maps"]
    assert recorded["two_face"] == recomputed["two_face"]
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
