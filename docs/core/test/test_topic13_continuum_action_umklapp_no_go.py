"""Tests for the current-action direct-Umklapp structural boundary."""
import hashlib
import json
from pathlib import Path

from docs.scripts.audit.audit_topic13_continuum_action_umklapp_no_go import (
    build_boundary_witness,
)


def test_current_action_surfaces_have_no_reciprocal_lattice_structure():
    witness = build_boundary_witness()
    assert not any(witness["lattice_fields"].values())
    assert not witness["amplitude_absolute_position_or_reciprocal_input"]


def test_current_collision_events_enforce_exact_continuum_momentum():
    witness = build_boundary_witness()
    assert witness["maximum_event_energy_residual"] <= 1.0e-12
    assert witness["maximum_event_momentum_residual"] <= 1.0e-12
    assert witness["event_contract"] == "p1+p2-p3-p4=0"
    assert "G!=0" in witness["required_umklapp_contract"]


def test_generated_no_go_artifact_is_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = root / "docs/core/artifacts/t13_continuum_action_umklapp_direct_route_no_go.json"
    registry_path = root / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_umklapp_no_go_addendum.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_disposition"] == "CLOSED_AS_NO_GO"
    assert all(artifact["checks"].values())
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["admissible_routes"]["recommended_near_term"]["id"] == "external_material_lattice_sector_interface"
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == evidence["sha256"]
