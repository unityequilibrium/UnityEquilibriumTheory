"""Tests for the conditional anisotropic thermoelastic response bridge."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_anisotropic_thermoelastic_response_bridge import (
    anisotropic_thermoelastic_bridge_contract,
    anisotropic_thermoelastic_response,
    hexagonal_normal_stiffness,
)
from docs.core.uet_scalar_thermoelastic_response_bridge import (
    scalar_thermoelastic_response,
)


def _hex_witness(**overrides):
    values = {
        "temperature": 0.8,
        "alpha_tensor": [-0.03, -0.03, 0.18],
        "stiffness": hexagonal_normal_stiffness(
            c11=8.0, c12=2.0, c13=1.0, c33=4.0
        ),
        "c_strain_vol": 2.4,
        "coupling_tensor": [0.2, 0.2, 0.5],
        "response_residue": 1.3,
        "response_curvature": 0.8,
        "delta_phi": 0.02,
    }
    values.update(overrides)
    return anisotropic_thermoelastic_response(**values)


def test_tensor_linear_system_matches_closed_form_and_constraints():
    witness = _hex_witness()
    assert witness.stress_residual_norm <= 1.0e-14
    assert abs(witness.entropy_residual) <= 1.0e-14
    assert abs(witness.heat_capacity_identity_residual) <= 1.0e-14
    assert witness.temperature_map_relative_residual <= 1.0e-14
    assert witness.c_stress_vol > witness.c_strain_vol


def test_hexagonal_contractions_match_explicit_formulas():
    alpha_a, alpha_c = -0.03, 0.18
    g_a, g_c = 0.2, 0.5
    c11, c12, c13, c33 = 8.0, 2.0, 1.0, 4.0
    witness = _hex_witness()
    expected_numerator = 2.0 * alpha_a * g_a + alpha_c * g_c
    expected_thermoelastic = (
        2.0 * (c11 + c12) * alpha_a**2
        + 4.0 * c13 * alpha_a * alpha_c
        + c33 * alpha_c**2
    )
    assert witness.coupling_contraction == pytest.approx(expected_numerator)
    assert witness.thermoelastic_contraction == pytest.approx(
        expected_thermoelastic
    )


def test_basal_axis_permutation_is_covariant():
    stiffness = hexagonal_normal_stiffness(c11=8.0, c12=2.0, c13=1.0, c33=4.0)
    base = _hex_witness(stiffness=stiffness)
    permutation = np.asarray([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    permuted = _hex_witness(
        alpha_tensor=permutation @ np.asarray([-0.03, -0.03, 0.18]),
        coupling_tensor=permutation @ np.asarray([0.2, 0.2, 0.5]),
        stiffness=permutation @ stiffness @ permutation.T,
    )
    assert permuted.delta_temperature == pytest.approx(base.delta_temperature)
    assert permuted.stability_margin == pytest.approx(base.stability_margin)


def test_scalar_one_axis_reduction_matches_scalar_parent():
    temperature = 0.8
    alpha = 0.12
    modulus = 5.0
    c_v = 2.4
    coupling = 0.7
    residue = 1.3
    curvature = 0.8
    delta_phi = 0.02
    tensor = anisotropic_thermoelastic_response(
        temperature=temperature,
        alpha_tensor=[alpha, 0.0, 0.0],
        stiffness=np.diag([modulus, 7.0, 9.0]),
        c_strain_vol=c_v,
        coupling_tensor=[coupling, 0.0, 0.0],
        response_residue=residue,
        response_curvature=curvature,
        delta_phi=delta_phi,
    )
    scalar = scalar_thermoelastic_response(
        temperature=temperature,
        alpha_v=alpha,
        bulk_modulus=modulus,
        c_v_vol=c_v,
        coupling=coupling,
        response_residue=residue,
        response_curvature=curvature,
        delta_phi=delta_phi,
    )
    assert tensor.delta_temperature == pytest.approx(scalar.delta_temperature)
    assert tensor.c_stress_vol == pytest.approx(scalar.c_p_vol)
    assert tensor.stability_margin == pytest.approx(
        scalar.stability_margin / modulus
    )


def test_invalid_stiffness_fails_closed():
    with pytest.raises(ValueError):
        _hex_witness(stiffness=np.diag([1.0, 1.0, -1.0]))
    with pytest.raises(ValueError):
        _hex_witness(stiffness=[[2.0, 1.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])


def test_coupling_stability_margin_detects_unstable_tensor():
    assert _hex_witness().stability_margin > 0.0
    assert _hex_witness(coupling_tensor=[2.0, 2.0, 3.0]).stability_margin < 0.0


def test_natural_unit_contract_closes():
    units = anisotropic_thermoelastic_bridge_contract()["natural_unit_exponents"]
    assert units["stiffness"] + 2 * units["strain"] == units[
        "free_energy_density"
    ]
    assert (
        units["coupling_tensor"] + units["Phi_E"] + units["strain"]
        == units["free_energy_density"]
    )
    assert units["response_curvature"] + 2 * units["Phi_E"] == units[
        "free_energy_density"
    ]


def test_generated_anisotropic_artifact_is_scoped_and_hash_linked():
    root = Path(__file__).resolve().parents[3]
    artifact_path = root / (
        "docs/core/artifacts/t13_anisotropic_thermoelastic_response_bridge_audit.json"
    )
    registry_path = root / (
        "docs/core/artifacts/"
        "uet_equation_correspondence_registry_topic13_anisotropic_thermoelastic_bridge_addendum.json"
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
    for relative, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    evidence = registry["equation_entries"][0]["evidence_artifacts"][0]
    assert evidence["path"] == artifact_path.relative_to(root).as_posix()
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == evidence["sha256"]
