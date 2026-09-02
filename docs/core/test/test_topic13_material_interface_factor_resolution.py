"""Tests for Topic 13 material-interface factor resolution."""
import hashlib
import json
from pathlib import Path

import pytest

from docs.core.uet_material_interface_factor_resolution import (
    conditional_alpha_witness,
    material_interface_factor_resolution,
)


def test_existing_matter_coupling_cannot_be_relabelled_as_strain_coupling():
    no_go = material_interface_factor_resolution()["operator_substitution_no_go"]
    assert no_go["implemented_coefficient_mass_dimension"] == 1
    assert no_go["required_coefficient_mass_dimension"] == 3
    assert no_go["missing_mass_dimension"] == 2
    assert "theta" not in no_go["implemented_operator_fields"]
    assert "chi_1" not in no_go["required_operator_fields"]


def test_factor_matrix_keeps_physical_inputs_and_composite_alpha_open():
    factors = material_interface_factor_resolution()["factor_matrix"]
    assert factors["Z_Phi"]["resolution_status"] == (
        "OPEN_PHYSICAL_RESIDUE_NONIDENTIFIABLE"
    )
    assert factors["g_Phi_theta"]["resolution_status"] == (
        "ABSENT_FROM_CURRENT_ACTION"
    )
    assert factors["C_src"]["resolution_status"] == (
        "COMPARATOR_AVAILABLE_ACCEPTED_INPUT_OPEN"
    )
    assert factors["alpha_Phi_T_natural"]["resolution_status"] == (
        "DERIVED_DIFFERENT_LANE_NOT_SI_ALPHA"
    )
    assert factors["alpha_Phi_K"]["resolution_status"] == (
        "OPEN_COMPOSITE_COEFFICIENT"
    )


def test_conditional_alpha_and_independent_uncertainty_algebra():
    witness = conditional_alpha_witness(
        chi_u_theta=0.8,
        g_phi_theta=2.5,
        z_phi=1.2,
        c_src=4.0,
        standard_uncertainties={
            "chi_u_theta": 0.08,
            "g_phi_theta": 0.25,
            "z_phi": 0.12,
            "c_src": 0.4,
        },
    )
    assert witness.alpha_natural == pytest.approx(0.6)
    assert witness.relative_standard_uncertainty == pytest.approx(0.2)
    assert witness.standard_uncertainty_natural == pytest.approx(0.12)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "chi_u_theta": 0.0,
            "g_phi_theta": 1.0,
            "z_phi": 1.0,
            "c_src": 1.0,
            "standard_uncertainties": {
                "chi_u_theta": 0.0,
                "g_phi_theta": 0.0,
                "z_phi": 0.0,
                "c_src": 0.0,
            },
        },
        {
            "chi_u_theta": 1.0,
            "g_phi_theta": 1.0,
            "z_phi": 1.0,
            "c_src": 1.0,
            "standard_uncertainties": {
                "chi_u_theta": -0.1,
                "g_phi_theta": 0.0,
                "z_phi": 0.0,
                "c_src": 0.0,
            },
        },
    ],
)
def test_invalid_factor_or_uncertainty_fails_closed(kwargs):
    with pytest.raises(ValueError):
        conditional_alpha_witness(**kwargs)


def test_missing_uncertainty_factor_fails_closed():
    with pytest.raises(ValueError):
        conditional_alpha_witness(
            chi_u_theta=1.0,
            g_phi_theta=1.0,
            z_phi=1.0,
            c_src=1.0,
            standard_uncertainties={
                "chi_u_theta": 0.1,
                "g_phi_theta": 0.1,
                "z_phi": 0.1,
            },
        )


def test_generated_factor_artifact_is_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = (
        root / "docs/core/artifacts/t13_material_interface_factor_resolution_audit.json"
    )
    registry_path = root / (
        "docs/core/artifacts/"
        "uet_equation_correspondence_registry_topic13_material_interface_factor_resolution_addendum.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["closure_disposition"] == (
        "CLOSED_AS_NO_GO_EXISTING_MATTER_COUPLING_SUBSTITUTION"
    )
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
