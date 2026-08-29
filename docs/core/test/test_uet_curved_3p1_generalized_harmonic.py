from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_generalized_harmonic import (
    GHParameters,
    compute_linear_gh_reduction_damped_rhs,
    generalized_harmonic_contract,
    gh_characteristic_fields,
    gh_curl_constraint,
    gh_gauge_constraint,
    gh_principal_symbol,
    gh_reduction_constraint,
    reconstruct_gh_state,
)
from docs.core.uet_curved_3p1_geometry import periodic_central_derivative


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "docs/core/artifacts/curved_3p1_gh_principal_system_verification.json"
FORMULA = ROOT / "docs/core/artifacts/curved_3p1_gh_principal_system_formula_audit.json"
GATE = ROOT / "docs/core/artifacts/curved_3p1_gh_branch_gate.json"


def test_preregistered_parameter_domain_is_enforced() -> None:
    parameters = GHParameters(gamma2=0.7, symmetrizer_lambda=1.2)
    assert parameters.gamma1 == -1.0
    assert parameters.gamma3 == -0.7
    with pytest.raises(ValueError):
        GHParameters(gamma1=0.0)
    with pytest.raises(ValueError):
        GHParameters(gamma2=1.0, symmetrizer_lambda=1.0)
    with pytest.raises(ValueError):
        GHParameters(gamma0=0.0)


@pytest.mark.parametrize(
    "direction",
    [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 1.0), (0.254, -0.381, 0.889)],
)
def test_principal_symbol_has_complete_source_matched_characteristics(direction) -> None:
    parameters = GHParameters(
        lapse=0.8, shift=(0.1, -0.05, 0.03), gamma2=0.7, symmetrizer_lambda=1.2
    )
    result = gh_principal_symbol(direction, parameters)
    beta_normal = float(np.asarray(parameters.shift) @ result.normal)
    assert result.eigenvector_rank == 5
    assert result.characteristic_residual < 1e-12
    assert result.transform_condition_number < 20.0
    assert np.allclose(
        result.characteristic_speeds,
        [0.0, -beta_normal + parameters.lapse, -beta_normal - parameters.lapse, -beta_normal, -beta_normal],
        atol=1e-12,
        rtol=0.0,
    )
    assert np.allclose(
        (result.characteristic_speeds[1:3] + beta_normal) / parameters.lapse,
        [1.0, -1.0],
        atol=1e-12,
        rtol=0.0,
    )


def test_analytic_symmetrizer_is_positive_and_symmetrizes_symbol() -> None:
    result = gh_principal_symbol(
        (1.0, 2.0, -1.0),
        GHParameters(lapse=1.3, shift=(-0.2, 0.1, 0.04), gamma2=1.0, symmetrizer_lambda=1.5),
    )
    assert result.minimum_symmetrizer_eigenvalue > 0.0
    assert result.symmetrizer_residual < 1e-12


def test_characteristic_transform_roundtrips_state() -> None:
    parameters = GHParameters(gamma2=0.6, symmetrizer_lambda=1.0)
    state = np.array([0.2, -0.4, 0.6, -0.1, 0.3])
    fields = gh_characteristic_fields(state[0], state[1], state[2:], (1.0, 1.0, 0.0), parameters)
    reconstructed = reconstruct_gh_state(fields, (1.0, 1.0, 0.0), parameters)
    assert np.allclose(reconstructed, state, atol=1e-12, rtol=0.0)


def test_flat_harmonic_gauge_constraint_is_zero_and_source_is_visible() -> None:
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    pi = np.zeros((4, 4))
    phi = np.zeros((3, 4, 4))
    normal = np.array([1.0, 0.0, 0.0, 0.0])
    assert np.allclose(gh_gauge_constraint(metric, pi, phi, np.zeros(4), normal), 0.0)
    source = np.array([0.1, -0.2, 0.3, -0.4])
    assert np.allclose(gh_gauge_constraint(metric, pi, phi, source, normal), source)


def test_reduction_and_curl_constraints_vanish_for_discrete_gradient() -> None:
    n = 12
    spacing = (2.0 * np.pi / n,) * 3
    x = np.arange(n) * spacing[0]
    xx, yy, zz = np.meshgrid(x, x, x, indexing="ij")
    metric = np.zeros((n, n, n, 4, 4))
    metric[..., 1, 1] = np.sin(xx) + 0.3 * np.cos(yy) + 0.2 * np.sin(zz)
    phi = np.stack(
        [periodic_central_derivative(metric, axis=i, spacing=spacing[i]) for i in range(3)],
        axis=3,
    )
    assert np.max(np.abs(gh_reduction_constraint(metric, phi, spacing))) == 0.0
    assert np.max(np.abs(gh_curl_constraint(phi, spacing))) < 1e-12


def test_constant_reduction_violation_has_declared_damping_rate() -> None:
    n = 8
    spacing = (1.0 / n,) * 3
    metric = np.zeros((n, n, n, 4, 4))
    pi = np.zeros_like(metric)
    phi = np.zeros((n, n, n, 3, 4, 4))
    phi[..., 0, 1, 1] = 0.125
    parameters = GHParameters(
        lapse=0.9, shift=(0.1, -0.02, 0.03), gamma2=0.6, symmetrizer_lambda=1.0
    )
    constraint = gh_reduction_constraint(metric, phi, spacing)
    rhs = compute_linear_gh_reduction_damped_rhs(metric, pi, phi, spacing, parameters)
    constraint_rate = -rhs.spatial_derivative_rhs
    assert np.max(
        np.abs(constraint_rate + parameters.lapse * parameters.gamma2 * constraint)
    ) < 1e-12
    assert rhs.diagnostics["gauge_constraint_gamma0_damping_rhs"] == "NOT_IMPLEMENTED"


def test_contract_preserves_uet_ontology_and_open_evolution_boundary() -> None:
    contract = generalized_harmonic_contract()
    assert "UET Phi" in contract["excluded_state"]
    assert "R_gen" in contract["excluded_state"]
    assert "complete nonlinear vacuum GH algebraic right-hand sides for declared H_a and nabla_a H_b" in contract["implemented"]
    assert "time integration and CFL policy" in contract["not_implemented"]
    assert "not a time-integrated numerical-relativity solver" in contract["claim_boundary"]


def test_generated_artifacts_are_hash_linked_and_keep_parent_work_partial() -> None:
    verification = json.loads(VERIFY.read_text(encoding="utf-8"))
    formula = json.loads(FORMULA.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    assert verification["status"] == "PASS_GH_PRINCIPAL_CHARACTERISTIC_SYSTEM"
    assert verification["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert formula["status"] == "PASS_SOURCE_LOCKED_GH_PRINCIPAL_FORMULAS"
    assert gate["status"] == "PARTIAL_GH_PRINCIPAL_SYSTEM_READY"
    assert gate["requirements"]["complete_nonlinear_gh_rhs"] == "OPEN"
    assert gate["requirements"]["time_integration_and_cfl"] == "OPEN"
    for relative_path, expected_hash in verification["source_hashes"].items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
    for evidence in gate["evidence_artifacts"]:
        assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]
