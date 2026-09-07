from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_curved_3p1_generalized_harmonic import (
    GHNonlinearParameters,
    compute_nonlinear_vacuum_gh_rhs,
    derive_gh_kinematics,
    generalized_harmonic_contract,
    gh_gamma0_damping_term,
)


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "docs/core/artifacts/curved_3p1_gh_nonlinear_vacuum_rhs_verification.json"
FORMULA = ROOT / "docs/core/artifacts/curved_3p1_gh_nonlinear_vacuum_formula_audit.json"
GATE = ROOT / "docs/core/artifacts/curved_3p1_gh_nonlinear_vacuum_gate.json"


def _flat_state(n: int = 5) -> tuple[np.ndarray, ...]:
    shape = (n, n, n)
    metric = np.broadcast_to(np.diag([-1.0, 1.0, 1.0, 1.0]), shape + (4, 4)).copy()
    return (
        metric,
        np.zeros_like(metric),
        np.zeros(shape + (3, 4, 4)),
        np.zeros(shape + (4,)),
        np.zeros(shape + (4, 4)),
    )


def test_nonlinear_parameter_domain_is_enforced() -> None:
    parameters = GHNonlinearParameters(gamma0=0.4, gamma2=0.7)
    assert parameters.gamma1 == -1.0
    assert parameters.gamma3 == -0.7
    with pytest.raises(ValueError):
        GHNonlinearParameters(gamma0=0.0)
    with pytest.raises(ValueError):
        GHNonlinearParameters(gamma2=0.0)
    with pytest.raises(ValueError):
        GHNonlinearParameters(gamma1=0.0)


def test_minkowski_is_exact_fixed_point() -> None:
    result = compute_nonlinear_vacuum_gh_rhs(*_flat_state(), (1.0, 1.0, 1.0))
    assert np.max(np.abs(result.metric_rhs)) == 0.0
    assert np.max(np.abs(result.normal_derivative_rhs)) == 0.0
    assert np.max(np.abs(result.spatial_derivative_rhs)) == 0.0
    assert np.max(np.abs(result.gauge_constraint)) == 0.0


def test_metric_kinematics_recovers_declared_lapse_and_shift() -> None:
    lapse = 0.8
    shift = np.array([0.1, -0.04, 0.02])
    spatial = np.diag([1.2, 0.9, 1.1])
    metric = np.zeros((4, 4))
    metric[1:, 1:] = spatial
    metric[0, 1:] = spatial @ shift
    metric[1:, 0] = metric[0, 1:]
    metric[0, 0] = -lapse**2 + shift @ spatial @ shift
    kinematics = derive_gh_kinematics(metric)
    assert np.isclose(kinematics.lapse, lapse)
    assert np.allclose(kinematics.shift, shift)
    assert np.isclose(kinematics.unit_normal @ metric @ kinematics.unit_normal, -1.0)


def test_gamma0_term_is_isolated_and_scales_linearly() -> None:
    metric, pi, phi, source, derivative = _flat_state()
    source[..., 0] = 0.1
    low = compute_nonlinear_vacuum_gh_rhs(
        metric, pi, phi, source, derivative, (1.0, 1.0, 1.0), GHNonlinearParameters(gamma0=0.4)
    )
    high = compute_nonlinear_vacuum_gh_rhs(
        metric, pi, phi, source, derivative, (1.0, 1.0, 1.0), GHNonlinearParameters(gamma0=0.8)
    )
    direct = gh_gamma0_damping_term(metric, low.gauge_constraint, low.kinematics, 0.4)
    assert np.allclose(low.normal_derivative_rhs, direct)
    assert np.allclose(high.normal_derivative_rhs, 2.0 * low.normal_derivative_rhs)


def test_invalid_metric_shape_and_grid_are_rejected() -> None:
    with pytest.raises(ValueError):
        derive_gh_kinematics(np.eye(4))
    metric, pi, phi, source, derivative = _flat_state(4)
    with pytest.raises(ValueError):
        compute_nonlinear_vacuum_gh_rhs(metric, pi, phi, source, derivative, (1.0, 1.0, 1.0))


def test_contract_keeps_time_matter_and_external_claims_open() -> None:
    contract = generalized_harmonic_contract()
    assert "complete nonlinear vacuum GH algebraic right-hand sides for declared H_a and nabla_a H_b" in contract["implemented"]
    assert "periodic vacuum RK4 time integration" in " ".join(contract["implemented"])
    assert "matter stress-energy wiring and detector observable map" in contract["not_implemented"]
    assert "not a production numerical-relativity solver" in contract["claim_boundary"]


def test_generated_artifacts_are_hash_linked_and_parent_remains_partial() -> None:
    verification = json.loads(VERIFY.read_text(encoding="utf-8"))
    formula = json.loads(FORMULA.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    assert verification["status"] == "PASS_GH_NONLINEAR_VACUUM_RHS"
    assert verification["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert verification["checks"]["independent_variable_grid_reference"] is True
    assert formula["status"] == "PASS_SOURCE_LOCKED_GH_NONLINEAR_VACUUM_FORMULAS"
    assert gate["status"] == "PARTIAL_GH_NONLINEAR_VACUUM_RHS_READY"
    assert gate["requirements"]["time_integration_and_cfl"] == "OPEN"
    assert gate["requirements"]["matter_stress_energy_wiring"] == "OPEN"
    for relative_path, expected_hash in verification["source_hashes"].items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
    for evidence in gate["evidence_artifacts"]:
        assert hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest() == evidence["sha256"]
