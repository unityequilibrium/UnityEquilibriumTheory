"""Tests for the conditional scalar thermoelastic response bridge."""
import hashlib
import json
from pathlib import Path

import pytest

from docs.core.uet_scalar_thermoelastic_response_bridge import (
    scalar_thermoelastic_bridge_contract,
    scalar_thermoelastic_response,
)


def _witness(**overrides):
    values = {
        "temperature": 0.8,
        "alpha_v": 0.12,
        "bulk_modulus": 5.0,
        "c_v_vol": 2.4,
        "coupling": 0.7,
        "response_residue": 1.3,
        "response_curvature": 0.8,
        "delta_phi": 0.02,
    }
    values.update(overrides)
    return scalar_thermoelastic_response(**values)


def test_linear_system_matches_closed_form_and_thermodynamic_constraints():
    witness = _witness()
    assert abs(witness.stress_residual) <= 1.0e-14
    assert abs(witness.entropy_residual) <= 1.0e-14
    assert abs(witness.cp_cv_identity_residual) <= 1.0e-14
    assert witness.temperature_map_relative_residual <= 1.0e-14
    assert witness.c_p_vol > witness.c_v_vol


def test_material_factor_reproduces_conditional_alpha_product():
    witness = _witness()
    product = (
        witness.chi_u_theta
        * witness.coupling
        * witness.response_residue
        / witness.c_v_vol
    )
    assert product == pytest.approx(witness.alpha_phi_temperature_natural)


@pytest.mark.parametrize(
    ("overrides", "expected_zero"),
    [
        ({"alpha_v": 0.0}, True),
        ({"coupling": 0.0}, True),
        ({"response_residue": 0.0}, True),
        ({"delta_phi": 0.0}, True),
    ],
)
def test_decoupling_limits_have_zero_temperature_response(overrides, expected_zero):
    witness = _witness(**overrides)
    assert (witness.delta_temperature == pytest.approx(0.0)) is expected_zero


def test_static_stability_margin_detects_allowed_and_disallowed_coupling():
    assert _witness(coupling=0.7).stability_margin > 0.0
    assert _witness(coupling=2.1).stability_margin < 0.0


def test_natural_unit_contract_closes_all_declared_relations():
    units = scalar_thermoelastic_bridge_contract()["natural_unit_exponents"]
    assert units["bulk_modulus"] + 2 * units["theta"] == units[
        "free_energy_density"
    ]
    assert (
        units["bulk_modulus"]
        + units["alpha_v"]
        + units["theta"]
        + units["temperature"]
        == units["free_energy_density"]
    )
    assert (
        units["g_Phi_theta"] + units["Phi_E"] + units["theta"]
        == units["free_energy_density"]
    )
    assert units["a_Phi"] + 2 * units["Phi_E"] == units[
        "free_energy_density"
    ]
    assert units["chi_u_theta"] == 0


@pytest.mark.parametrize(
    "field",
    ["temperature", "bulk_modulus", "c_v_vol", "response_curvature"],
)
def test_nonpositive_stability_input_fails_closed(field):
    with pytest.raises(ValueError):
        _witness(**{field: 0.0})


def test_generated_thermoelastic_artifact_is_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = (
        root / "docs/core/artifacts/t13_scalar_thermoelastic_response_bridge_audit.json"
    )
    registry_path = root / (
        "docs/core/artifacts/"
        "uet_equation_correspondence_registry_topic13_scalar_thermoelastic_bridge_addendum.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    json.dumps(artifact, allow_nan=False)
    json.dumps(registry, allow_nan=False)
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["source_combination_admitted"] is False
    assert artifact["full_core_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["parameter_fitting_performed"] is False
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == evidence["sha256"]
