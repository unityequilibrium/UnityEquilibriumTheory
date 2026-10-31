from __future__ import annotations

import hashlib
import importlib
import json

import numpy as np
import pytest
from docs.core.core_paths import repo_root


BOUNDARY = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_linear_boundary"
)
PROJECTORS = importlib.import_module(
    "docs.core.02_equations.covariant.uet_curved_3p1_gh_boundary_projectors"
)
AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_uet_curved_3p1_gh_linear_boundary"
)
ROOT = repo_root()
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_linear_boundary_residual_audit.json"
)


def _symmetric(rng: np.random.Generator, prefix: tuple[int, ...] = ()) -> np.ndarray:
    raw = rng.normal(size=prefix + (4, 4))
    return 0.5 * (raw + np.swapaxes(raw, -1, -2))


def _random_jet(seed: int = 17):
    rng = np.random.default_rng(seed)
    return {
        "metric_perturbation": _symmetric(rng),
        "pi_perturbation": _symmetric(rng),
        "phi_perturbation": _symmetric(rng, (3,)),
        "metric_gradient": _symmetric(rng, (3,)),
        "pi_gradient": _symmetric(rng, (3,)),
        "phi_gradient": _symmetric(rng, (3, 3)),
    }


def _rotate_jet(jet, rotation: np.ndarray):
    spacetime = np.eye(4)
    spacetime[1:, 1:] = rotation

    def rotate_tensor(value):
        return np.einsum("ac,...cd,bd->...ab", spacetime, value, spacetime)

    return {
        "metric_perturbation": rotate_tensor(jet["metric_perturbation"]),
        "pi_perturbation": rotate_tensor(jet["pi_perturbation"]),
        "phi_perturbation": np.einsum(
            "ij,jab->iab", rotation, rotate_tensor(jet["phi_perturbation"])
        ),
        "metric_gradient": np.einsum(
            "ij,jab->iab", rotation, rotate_tensor(jet["metric_gradient"])
        ),
        "pi_gradient": np.einsum(
            "ij,jab->iab", rotation, rotate_tensor(jet["pi_gradient"])
        ),
        "phi_gradient": np.einsum(
            "ij,kl,jlab->ikab",
            rotation,
            rotation,
            rotate_tensor(jet["phi_gradient"]),
        ),
    }


def _literal_rinne_axis_x_reference(jet, gamma2: float):
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    time_up = np.array([1.0, 0.0, 0.0, 0.0])
    time_down = eta @ time_up
    normal_up = np.array([0.0, 1.0, 0.0, 0.0])
    k_up = (time_up - normal_up) / np.sqrt(2.0)
    k_down = eta @ k_up

    def trace(tensor):
        return float(np.einsum("ab,ab->", eta, tensor))

    dmetric = jet["metric_gradient"]
    dpi = jet["pi_gradient"]
    dphi = jet["phi_gradient"]
    d_u1_minus = dpi[0] - dphi[0, 0] - gamma2 * dmetric[0]
    constraint = np.sqrt(2.0) * (
        k_up @ d_u1_minus - 0.5 * k_down * trace(d_u1_minus)
    )
    for tangent_component in (2, 3):
        derivative_axis = tangent_component - 1
        constraint[tangent_component] += 0.5 * trace(dpi[derivative_axis])
        constraint -= dpi[derivative_axis, tangent_component]
        constraint -= dphi[
            derivative_axis, tangent_component - 1, 0
        ]
        constraint += 0.5 * time_down * trace(
            dphi[derivative_axis, tangent_component - 1]
        )
        constraint += gamma2 * (
            dmetric[derivative_axis, tangent_component]
            - 0.5 * np.eye(4)[tangent_component] * trace(dmetric[derivative_axis])
        )
        constraint += dphi[derivative_axis, 0, tangent_component]
        constraint -= 0.5 * np.eye(4)[tangent_component] * trace(
            dphi[derivative_axis, 0]
        )

    raw = np.zeros((2, 2))
    for a_index, a in enumerate((2, 3)):
        derivative_axis = a - 1
        for b_index, b in enumerate((2, 3)):
            value = dpi[0, a, b] - dphi[0, 0, a, b]
            for spatial_i in (1, 2, 3):
                value += 2.0 * dphi[derivative_axis, spatial_i - 1, spatial_i, b]
                value -= dphi[derivative_axis, b - 1, spatial_i, spatial_i]
            for c in (2, 3):
                value -= dphi[c - 1, c - 1, a, b]
            value += dphi[derivative_axis, 0, b, 0]
            value -= dpi[derivative_axis, b, 1]
            value -= dphi[derivative_axis, b - 1, 1, 0]
            raw[a_index, b_index] = value
    physical = 0.5 * (raw + raw.T)
    physical -= 0.5 * np.trace(physical) * np.eye(2)
    return constraint, physical


def test_normal_derivative_maps_have_source_projector_ranks_and_kernels() -> None:
    directions = (
        np.array(value, dtype=float) / np.linalg.norm(value)
        for value in __import__("itertools").product((-1.0, 0.0, 1.0), repeat=3)
        if value != (0.0, 0.0, 0.0)
    )
    for normal in directions:
        maps = BOUNDARY.gh_boundary_normal_maps(normal)
        assert maps["constraint"].shape == (4, 10)
        assert maps["physical"].shape == (2, 10)
        assert np.linalg.matrix_rank(maps["constraint"], tol=1.0e-10) == 4
        assert np.linalg.matrix_rank(maps["physical"], tol=1.0e-10) == 2
        assert np.max(
            np.abs(maps["constraint"] @ (np.eye(10) - maps["constraint_projector"]))
        ) < 1.0e-12
        assert np.max(
            np.abs(maps["physical"] @ (np.eye(10) - maps["physical_projector"]))
        ) < 1.0e-12


def test_zero_jet_satisfies_homogeneous_boundary_data_in_both_shift_regimes() -> None:
    zero_tensor = np.zeros((4, 4))
    jet = {
        "metric_perturbation": zero_tensor,
        "pi_perturbation": zero_tensor,
        "phi_perturbation": np.zeros((3, 4, 4)),
        "metric_gradient": np.zeros((3, 4, 4)),
        "pi_gradient": np.zeros((3, 4, 4)),
        "phi_gradient": np.zeros((3, 3, 4, 4)),
    }
    for shift, regime in ((-0.2, "U1_ONLY_INCOMING_SUBLUMINAL"), (0.2, "U1_AND_U2_INCOMING_SUBLUMINAL")):
        result = BOUNDARY.gh_linear_boundary_residuals(
            **jet, normal=(1.0, 2.0, -1.0), normal_shift=shift
        )
        assert result.boundary_regime == regime
        assert np.allclose(result.constraint_incoming, 0.0)
        assert np.allclose(result.physical_weyl_incoming, 0.0)
        assert np.allclose(result.gauge_incoming, 0.0)
        assert np.allclose(result.u2_curl_incoming, 0.0)


def test_physical_and_gauge_boundary_data_are_subtracted_in_their_own_sectors() -> None:
    normal = np.array([1.0, 0.0, 0.0])
    projectors = PROJECTORS.build_gh_boundary_projectors(normal)
    raw = np.arange(16, dtype=float).reshape(4, 4)
    symmetric = 0.5 * (raw + raw.T)
    gauge_data = PROJECTORS.apply_gh_boundary_projector(symmetric, projectors.gauge)
    physical_data = PROJECTORS.apply_gh_boundary_projector(symmetric, projectors.physical)

    jet = _random_jet(23)
    jet["metric_perturbation"] = np.zeros((4, 4))
    jet["pi_perturbation"] = gauge_data.copy()
    jet["phi_perturbation"] = np.zeros((3, 4, 4))
    jet["metric_gradient"] = np.zeros((3, 4, 4))
    jet["pi_gradient"] = np.zeros((3, 4, 4))
    jet["phi_gradient"] = np.zeros((3, 3, 4, 4))
    jet["pi_gradient"][0] = physical_data

    result = BOUNDARY.gh_linear_boundary_residuals(
        **jet,
        normal=normal,
        physical_data=physical_data,
        gauge_data=gauge_data,
    )
    assert np.max(np.abs(result.physical_weyl_incoming)) < 1.0e-12
    assert np.max(np.abs(result.gauge_incoming)) < 1.0e-12


def test_definition_constraint_u2_curl_vanishes_for_a_symmetric_hessian() -> None:
    rng = np.random.default_rng(31)
    hessian = rng.normal(size=(3, 3))
    hessian = 0.5 * (hessian + hessian.T)
    tensor = _symmetric(rng)
    phi_gradient = np.einsum("ij,ab->ijab", hessian, tensor)
    jet = _random_jet(37)
    jet["phi_gradient"] = phi_gradient

    result = BOUNDARY.gh_linear_boundary_residuals(
        **jet, normal=(1.0, -2.0, 2.0), normal_shift=0.15
    )
    assert result.boundary_regime == "U1_AND_U2_INCOMING_SUBLUMINAL"
    assert np.max(np.abs(result.u2_curl_incoming)) < 1.0e-12


def test_positive_shift_u2_boundary_residual_controls_all_twenty_incoming_components() -> None:
    rank, residual = AUDIT._u2_normal_map_control()
    assert rank == 20
    assert residual < 1.0e-12


def test_residuals_are_covariant_under_spatial_orthogonal_changes_of_frame() -> None:
    normal = np.array([1.0, 2.0, -1.0], dtype=float)
    normal /= np.linalg.norm(normal)
    angle = 0.73
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    jet = _random_jet(41)
    base = BOUNDARY.gh_linear_boundary_residuals(**jet, normal=normal, normal_shift=-0.1)
    rotated_jet = _rotate_jet(jet, rotation)
    rotated = BOUNDARY.gh_linear_boundary_residuals(
        **rotated_jet, normal=rotation @ normal, normal_shift=-0.1
    )
    spacetime = np.eye(4)
    spacetime[1:, 1:] = rotation

    assert np.allclose(rotated.constraint_incoming, spacetime @ base.constraint_incoming, atol=1e-11, rtol=0.0)
    assert np.allclose(
        rotated.physical_weyl_incoming,
        spacetime @ base.physical_weyl_incoming @ spacetime.T,
        atol=1e-11,
        rtol=0.0,
    )
    assert np.allclose(
        rotated.gauge_incoming,
        spacetime @ base.gauge_incoming @ spacetime.T,
        atol=1e-11,
        rtol=0.0,
    )


def test_constraint_and_weyl_residuals_match_literal_rinne_equations_for_axis_x() -> None:
    jet = _random_jet(43)
    gamma2 = 0.7
    result = BOUNDARY.gh_linear_boundary_residuals(
        **jet, normal=(1.0, 0.0, 0.0), normal_shift=0.0, gamma2=gamma2
    )
    expected_constraint, expected_physical = _literal_rinne_axis_x_reference(
        jet, gamma2
    )
    assert np.allclose(result.constraint_incoming, expected_constraint, atol=1e-12, rtol=0.0)
    assert np.allclose(
        result.physical_weyl_incoming[2:4, 2:4],
        expected_physical,
        atol=1e-12,
        rtol=0.0,
    )


@pytest.mark.parametrize("shift", [-1.0, 1.0, 1.1])
def test_sonic_or_superluminal_boundary_shift_is_rejected(shift: float) -> None:
    jet = _random_jet(47)
    with pytest.raises(ValueError, match="strictly subluminal"):
        BOUNDARY.gh_linear_boundary_residuals(**jet, normal=(1.0, 0.0, 0.0), normal_shift=shift)


def test_invalid_physical_and_gauge_boundary_data_are_rejected() -> None:
    jet = _random_jet(53)
    with pytest.raises(ValueError, match="transverse and trace-free"):
        BOUNDARY.gh_linear_boundary_residuals(
            **jet, normal=(1.0, 0.0, 0.0), physical_data=np.eye(4)
        )
    with pytest.raises(ValueError, match="gauge-projector subspace"):
        BOUNDARY.gh_linear_boundary_residuals(
            **jet, normal=(1.0, 0.0, 0.0), gauge_data=np.eye(4)
        )


def test_boundary_audit_artifact_is_source_hashed_and_does_not_claim_ibvp_closure() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    rebuilt = AUDIT.build_artifact()
    assert artifact["status"] == "PASS_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["scope"]["boundary_operator_applied_to_evolution"] is False
    assert artifact["claim_promotion"] is False
    assert all(artifact["checks"].values())
    assert artifact["metrics"]["incoming_count_cases"] == 78
    assert artifact["metrics"]["incoming_counts_by_shift"] == {
        "negative": [10],
        "zero": [10],
        "positive": [30],
    }
    assert artifact["metrics"]["maximum_incoming_condition_count_mismatch"] == 0
    assert rebuilt["source_hashes"] == artifact["source_hashes"]
    for source, digest in artifact["source_hashes"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest
