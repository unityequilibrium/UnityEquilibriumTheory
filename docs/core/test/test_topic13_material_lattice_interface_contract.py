"""Tests for the conditional UET-material lattice interface."""
import hashlib
import json
from pathlib import Path

import pytest

from docs.core.uet_material_lattice_interface_contract import (
    exchange_ledger_witness,
    interface_rescaling_witness,
    material_lattice_interface_contract,
)


def test_interface_ontology_keeps_uet_and_material_states_separate():
    contract = material_lattice_interface_contract()
    assert contract["state_ownership"]["UET"] == ["C", "Phi", "Pi"]
    assert "u_i" in contract["state_ownership"]["material_lattice"]
    assert "R_gen" in contract["state_ownership"]["excluded_from_state"]
    assert "not temperature" in contract["ontology"]["Phi"]


def test_interface_units_close_in_natural_lane():
    units = material_lattice_interface_contract()["natural_unit_exponents"]
    assert units["derivative"] + units["displacement_u"] == units["strain_theta"]
    assert units["g_Phi_theta"] + units["Phi_E"] + units["strain_theta"] == units["interaction_energy_density"]
    assert units["interaction_energy_density"] == units["phonon_energy_density"]
    assert units["exchange_rate_density"] == units["phonon_energy_density"] + units["derivative"]
    assert units["Phi_E"] + units["g_Phi_theta"] - units["C_src_natural"] == units["alpha_per_normalized_Phi_natural"]


@pytest.mark.parametrize("scale", [0.25, 0.5, 2.0, 4.0])
def test_field_residue_coupling_rescaling_is_unidentifiable(scale):
    witness = interface_rescaling_witness(scale=scale)
    assert witness.interaction_relative_residual <= 1.0e-15
    assert witness.alpha_product_relative_residual <= 1.0e-15


def test_exchange_ledger_sources_cancel_exactly():
    witness = exchange_ledger_witness(0.7)
    assert witness["uet_energy_source"] == -witness["lattice_energy_source"]
    assert witness["total_energy_source"] == 0.0


@pytest.mark.parametrize("scale", [0.0, -1.0])
def test_invalid_rescaling_fails_closed(scale):
    with pytest.raises(ValueError):
        interface_rescaling_witness(scale=scale)


def test_contract_keeps_physical_inputs_open():
    contract = material_lattice_interface_contract()
    admitted = contract["admitted_current_evidence"]
    assert admitted["calorine_mode_source_fields"]
    assert not admitted["normal_umklapp_collision_split"]
    assert not admitted["physical_Z_Phi"]
    assert not admitted["physical_g_Phi_theta"]
    assert not admitted["physical_alpha_Phi_K"]


def test_generated_interface_artifact_is_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = root / "docs/core/artifacts/t13_uet_material_lattice_interface_contract_audit.json"
    registry_path = root / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_material_lattice_interface_addendum.json"
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
