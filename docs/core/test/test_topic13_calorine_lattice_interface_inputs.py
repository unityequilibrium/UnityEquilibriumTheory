"""Tests for the Calorine material-lattice interface input boundary."""
import hashlib
import json
from pathlib import Path

from docs.scripts.audit.audit_topic13_calorine_lattice_interface_inputs import (
    inspect_local_inputs,
)


def test_source_locked_mode_fields_are_present_and_finite():
    witness = inspect_local_inputs()
    assert set(witness["required_comparator_keys"]) <= set(witness["available_keys"])
    assert all(row["finite"] for row in witness["field_rows"].values())
    assert witness["kappa_sha256"] == witness["expected_kappa_sha256"]
    assert witness["kappa_size_bytes"] == witness["expected_kappa_size_bytes"]


def test_total_gamma_cannot_be_promoted_to_resistive_umklapp_rate():
    witness = inspect_local_inputs()
    assert witness["field_rows"]["gamma"]["minimum"] >= 0.0
    assert not witness["normal_umklapp_decomposition_available"]
    assert not witness["collision_matrix_available"]
    assert not witness["collision_eigenvectors_available"]
    assert witness["collision_eigenvalue_files"]
    assert witness["full_lbte_status"] == "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN"


def test_generated_boundary_is_strict_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = root / "docs/core/artifacts/t13_calorine_lattice_interface_input_boundary.json"
    registry_path = root / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_calorine_lattice_inputs_addendum.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == evidence["sha256"]
