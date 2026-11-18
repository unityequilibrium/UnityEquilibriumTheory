"""Tests for the Calorine material-lattice interface input boundary."""
from core.core_paths import canonical_existing_path
from docs.core.core_paths import repo_root
import hashlib
import json
from pathlib import Path

from docs.scripts.audit.audit_topic13_calorine_lattice_interface_inputs import (
    inspect_local_inputs,
)


def test_payload_and_collision_scan_share_one_physical_tree(tmp_path, monkeypatch):
    """A migrated directory must not hide an available legacy payload tree."""
    import h5py
    import numpy as np
    from docs.scripts.audit import audit_topic13_calorine_lattice_interface_inputs as audit

    for selected in ("legacy", "current"):
        root = tmp_path / selected
        legacy = root / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
        current = root / "topics/0.13_Thermodynamic_Bridge/Data/03_Research"
        for base in (legacy, current):
            (base / "reproduction").mkdir(parents=True)
        physical = legacy if selected == "legacy" else current
        suffix = Path("reproduction/t13_calorine_pbte/mesh_12x12x6/kappa-m12126.hdf5")
        payload = physical / suffix
        payload.parent.mkdir(parents=True)
        with h5py.File(payload, "w") as handle:
            for key in audit.REQUIRED_COMPARATOR_KEYS:
                handle.create_dataset(key, data=np.ones(1))
        collision = physical / "reproduction/other_run/collision.hdf5"
        collision.parent.mkdir()
        with h5py.File(collision, "w") as handle:
            handle.create_dataset("collision_eigenvalues", data=np.ones(2))
        summary = {
            "output_artifacts": {"kappa_hdf5": {
                "size_bytes": payload.stat().st_size,
                "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
            }},
            "source": {"structure": {"path": "synthetic_fixture"}},
            "run": {"transport_solver": "fixture", "holdout_accessed": False, "fit_performed": False},
        }
        (current / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        full = root / "full.json"
        full.write_text(json.dumps({
            "status": "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN",
            "major_result": {"open_blockers": ["synthetic_fixture_not_physical_validation"]},
        }), encoding="utf-8")

        def resolve(path):
            path = Path(path)
            try:
                relocated = root / "topics" / path.relative_to(root / "docs/topics")
            except ValueError:
                return path
            return relocated if relocated.exists() else path

        with monkeypatch.context() as mp:
            mp.setattr(audit, "ROOT", root)
            mp.setattr(audit, "BASE", legacy)
            mp.setattr(audit, "KAPPA", legacy / suffix)
            mp.setattr(audit, "SUMMARY", legacy / "summary.json")
            mp.setattr(audit, "FULL_LBTE", full)
            mp.setattr(audit, "canonical_existing_path", resolve)
            witness = audit.inspect_local_inputs()
        assert witness["raw_payload_available"] is True
        assert witness["hdf5_file_count_scanned"] == 2
        assert witness["collision_eigenvalue_files"] == [collision.relative_to(root).as_posix()]
        assert witness["kappa_sha256"] == summary["output_artifacts"]["kappa_hdf5"]["sha256"]
        assert witness["collision_matrix_available"] is False
        assert witness["collision_eigenvectors_available"] is False


def test_source_locked_mode_fields_are_present_and_finite():
    witness = inspect_local_inputs()
    if witness["raw_payload_available"]:
        assert set(witness["required_comparator_keys"]) <= set(witness["available_keys"])
        assert all(row["finite"] for row in witness["field_rows"].values())
        assert witness["kappa_sha256"] == witness["expected_kappa_sha256"]
        assert witness["kappa_size_bytes"] == witness["expected_kappa_size_bytes"]
    else:
        assert witness["input_mode"] == "METADATA_ONLY_PUBLIC_BOUNDARY"
        assert witness["available_keys"] == []
        assert witness["field_rows"] == {}
        assert witness["kappa_sha256"] is None
        assert witness["kappa_size_bytes"] is None
        assert len(witness["expected_kappa_sha256"]) == 64
        assert witness["expected_kappa_size_bytes"] > 0


def test_total_gamma_cannot_be_promoted_to_resistive_umklapp_rate():
    witness = inspect_local_inputs()
    if witness["raw_payload_available"]:
        assert witness["field_rows"]["gamma"]["minimum"] >= 0.0
        assert witness["collision_eigenvalue_files"]
    else:
        assert witness["collision_structure_matches"] == {}
        assert witness["collision_eigenvalue_files"] == []
    assert not witness["normal_umklapp_decomposition_available"]
    assert not witness["collision_matrix_available"]
    assert not witness["collision_eigenvectors_available"]
    assert witness["full_lbte_status"] == "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN"


def test_generated_boundary_is_strict_scoped_and_hash_linked():
    root = repo_root()
    artifact_path = root / 'core/07_artifacts/topic13/t13_calorine_lattice_interface_input_boundary.json'
    registry_path = root / 'core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_calorine_lattice_inputs_addendum.json'
    artifact = json.loads(canonical_existing_path(artifact_path).read_text(encoding="utf-8"))
    registry = json.loads(canonical_existing_path(registry_path).read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((canonical_existing_path(root / relative)).read_bytes()).hexdigest() == digest
    for relative, declaration in artifact["locked_source_declarations"].items():
        assert len(declaration["sha256"]) == 64
        assert declaration["size_bytes"] > 0
        if declaration["exists"]:
            assert hashlib.sha256((canonical_existing_path(root / relative)).read_bytes()).hexdigest() == declaration["sha256"]
            assert (root / relative).stat().st_size == declaration["size_bytes"]
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(canonical_existing_path(artifact_path).read_bytes()).hexdigest() == evidence["sha256"]
