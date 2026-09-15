"""Unit checks for Wave 5 spatial-coupling candidate operators."""

from __future__ import annotations

import sys
from docs.core.core_paths import repo_root

import numpy as np


def _bootstrap():
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


_bootstrap()

from docs.core.uet_master_equation import (  # noqa: E402
    CONSERVED_ORDER_OPERATOR_MODE,
    CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    LEGACY_OPERATOR_MODE,
    SPATIAL_COUPLED_OPERATOR_MODE,
    SPATIAL_COUPLED_V2_OPERATOR_MODE,
    conserved_laplacian,
    dynamics_step_complete,
    game_theory_force,
    game_theory_potential,
    gradient_magnitude_squared,
    information_coupling,
    information_dynamics_source,
    screened_nonlocal_field,
    spatial_interface_activity,
    spatial_memory_contrast,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


def _compare_state(left, right) -> None:
    if isinstance(left, tuple):
        assert isinstance(right, tuple)
        assert len(left) == len(right)
        for a, b in zip(left, right):
            np.testing.assert_allclose(a, b)
    else:
        np.testing.assert_allclose(left, right)


def test_legacy_information_coupling_matches_historical_form() -> None:
    params = UETParameters(beta=0.25, operator_mode=LEGACY_OPERATOR_MODE)
    C = np.array([1.0, 2.0, 3.0])
    I = np.array([0.5, -1.0, 2.0])
    dx = 0.2
    expected = params.beta * np.sum(C * I) * dx
    got = information_coupling(C, I, dx, params)
    np.testing.assert_allclose(got, expected)


def test_spatial_information_source_zero_gates() -> None:
    params = UETParameters(beta=0.25, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE)
    C = np.array([0.0, 1.0, 2.0])
    I = np.array([1.0, 0.0, -1.0])
    source = information_dynamics_source(C, I, params)
    expected = -params.beta * params.spatial_information_coupling * C * I
    np.testing.assert_allclose(source, expected)
    np.testing.assert_allclose(information_dynamics_source(np.zeros_like(C), I, params), 0.0)
    np.testing.assert_allclose(information_dynamics_source(C, np.zeros_like(I), params), 0.0)


def test_spatial_game_operator_is_interface_sensitive() -> None:
    params = UETParameters(beta=0.05, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE)
    uniform = np.ones(32)
    interface = np.concatenate([np.zeros(16), np.ones(16)])
    uniform_game = game_theory_potential(
        uniform, params.SIGMA_CRIT, params=params, dx=1.0, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE
    )
    interface_game = game_theory_potential(
        interface, params.SIGMA_CRIT, params=params, dx=1.0, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE
    )
    np.testing.assert_allclose(uniform_game, 0.0)
    assert float(np.linalg.norm(interface_game)) > 0.0


def test_spatial_game_operator_preserves_2d_shape() -> None:
    params = UETParameters(beta=0.05, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE)
    C = np.zeros((8, 8))
    C[:, 4:] = 1.0
    grad_sq = gradient_magnitude_squared(C, 1.0)
    force = game_theory_force(
        C,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=1.0,
        params=params,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
    )
    assert grad_sq.shape == C.shape
    assert force.shape == C.shape
    assert float(np.linalg.norm(force)) > 0.0


def test_spatial_v2_memory_contrast_zero_uniform_and_shape_safe() -> None:
    params = UETParameters(operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE)
    uniform_1d = np.ones(16)
    uniform_2d = np.ones((6, 8))
    interface_2d = np.zeros((6, 8))
    interface_2d[:, 4:] = 1.0

    np.testing.assert_allclose(spatial_memory_contrast(uniform_1d, 1.0, params), 0.0, atol=1e-12)
    np.testing.assert_allclose(spatial_memory_contrast(uniform_2d, 1.0, params), 0.0, atol=1e-12)
    assert screened_nonlocal_field(interface_2d, 1.0, params.spatial_v2_memory_length).shape == interface_2d.shape
    assert spatial_interface_activity(interface_2d, 1.0, params).shape == interface_2d.shape
    assert float(np.linalg.norm(spatial_interface_activity(interface_2d, 1.0, params))) > 0.0


def test_spatial_v2_information_source_zero_and_interface_gates() -> None:
    params = UETParameters(beta=0.25, operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE)
    uniform = np.ones(16)
    interface = np.concatenate([np.zeros(8), np.ones(8)])
    I = np.ones_like(interface)

    np.testing.assert_allclose(information_dynamics_source(uniform, I, params, dx=1.0), 0.0, atol=1e-12)
    np.testing.assert_allclose(information_dynamics_source(np.zeros_like(interface), I, params, dx=1.0), 0.0)
    np.testing.assert_allclose(information_dynamics_source(interface, np.zeros_like(I), params, dx=1.0), 0.0)
    assert float(np.linalg.norm(information_dynamics_source(interface, I, params, dx=1.0))) > 0.0


def test_spatial_v2_game_force_is_conserved_and_interface_active() -> None:
    params = UETParameters(beta=0.05, operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE)
    uniform = np.ones(32)
    interface = np.concatenate([np.zeros(16), np.ones(16)])

    uniform_force = game_theory_force(
        uniform,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=1.0,
        params=params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )
    interface_force = game_theory_force(
        interface,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=1.0,
        params=params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )

    np.testing.assert_allclose(uniform_force, 0.0, atol=1e-12)
    assert float(np.linalg.norm(interface_force)) > 0.0
    np.testing.assert_allclose(np.sum(interface_force), 0.0, atol=1e-10)
    np.testing.assert_allclose(np.sum(conserved_laplacian(interface, 1.0)), 0.0, atol=1e-12)


def test_spatial_v2_dynamics_preserves_shape() -> None:
    params = UETParameters(
        beta=0.05,
        kappa=0.1,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )
    C = np.zeros((8, 8))
    C[:, 4:] = 1.0
    I = np.ones_like(C)
    updated = dynamics_step_complete(
        C,
        I=I,
        dx=1.0,
        dt=0.01,
        params=params,
        density=params.SIGMA_CRIT,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )
    C_updated, I_updated = updated
    assert C_updated.shape == C.shape
    assert I_updated.shape == I.shape


def test_conserved_order_mode_preserves_mass_and_shape_2d() -> None:
    params = UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.1,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
    )
    C = np.zeros((8, 8))
    C[:, 4:] = 0.2
    initial_mean = float(np.mean(C))
    updated = dynamics_step_complete(
        C,
        dx=1.0,
        dt=0.01,
        params=params,
        operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
    )
    assert updated.shape == C.shape
    np.testing.assert_allclose(float(np.mean(updated)), initial_mean, atol=1e-12)


def test_conserved_order_mode_preserves_mass_1d_over_steps() -> None:
    params = UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.1,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
    )
    C = np.linspace(-0.2, 0.2, 16)
    initial_mean = float(np.mean(C))
    for _ in range(12):
        C = dynamics_step_complete(
            C,
            dx=1.0,
            dt=0.005,
            params=params,
            operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
        )
    np.testing.assert_allclose(float(np.mean(C)), initial_mean, atol=1e-12)


def test_conserved_order_uniform_field_is_stationary() -> None:
    params = UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.1,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
    )
    C = np.ones((5, 7)) * 0.2
    updated = dynamics_step_complete(
        C,
        dx=1.0,
        dt=0.01,
        params=params,
        operator_mode=CONSERVED_ORDER_OPERATOR_MODE,
    )
    np.testing.assert_allclose(updated, C, atol=1e-12)


def test_conserved_order_spectral_mode_preserves_mass_under_wave13_settings() -> None:
    params = UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.002,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    )
    rng = np.random.default_rng(1601)
    nx = 16
    C = rng.normal(0.0, 0.01, (nx, nx))
    initial_mean = float(np.mean(C))
    for _ in range(25):
        C = dynamics_step_complete(
            C,
            dx=1.0 / nx,
            dt=0.01,
            params=params,
            operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        )
    assert C.shape == (nx, nx)
    assert np.all(np.isfinite(C))
    np.testing.assert_allclose(float(np.mean(C)), initial_mean, atol=1e-12)


def test_conserved_order_spectral_uniform_field_is_stationary() -> None:
    params = UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.002,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    )
    C = np.ones((5, 7)) * 0.2
    updated = dynamics_step_complete(
        C,
        dx=1.0 / 7.0,
        dt=0.01,
        params=params,
        operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    )
    np.testing.assert_allclose(updated, C, atol=1e-12)


def test_default_and_explicit_legacy_dynamics_match() -> None:
    params = UETParameters(beta=0.05, kappa=0.1, W_N=0.0, a0_viscosity=0.0)
    C = np.linspace(-0.2, 0.2, 16)
    I = np.linspace(0.1, 0.2, 16)
    default_state = dynamics_step_complete(C, I=I, dx=0.1, dt=0.01, params=params)
    explicit_legacy_state = dynamics_step_complete(
        C,
        I=I,
        dx=0.1,
        dt=0.01,
        params=params,
        operator_mode=LEGACY_OPERATOR_MODE,
    )
    _compare_state(default_state, explicit_legacy_state)


if __name__ == "__main__":
    test_legacy_information_coupling_matches_historical_form()
    test_spatial_information_source_zero_gates()
    test_spatial_game_operator_is_interface_sensitive()
    test_spatial_game_operator_preserves_2d_shape()
    test_spatial_v2_memory_contrast_zero_uniform_and_shape_safe()
    test_spatial_v2_information_source_zero_and_interface_gates()
    test_spatial_v2_game_force_is_conserved_and_interface_active()
    test_spatial_v2_dynamics_preserves_shape()
    test_conserved_order_mode_preserves_mass_and_shape_2d()
    test_conserved_order_mode_preserves_mass_1d_over_steps()
    test_conserved_order_uniform_field_is_stationary()
    test_conserved_order_spectral_mode_preserves_mass_under_wave13_settings()
    test_conserved_order_spectral_uniform_field_is_stationary()
    test_default_and_explicit_legacy_dynamics_match()
    print("Wave 5/11/14/16 spatial and conserved-order unit checks passed")
