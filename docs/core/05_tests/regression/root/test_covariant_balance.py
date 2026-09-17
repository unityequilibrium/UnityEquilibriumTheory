"""Focused tests for covariant Noether/Bianchi and exchange balance."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_balance import (
    balance_contract,
    canonical_response_stress_divergence,
    compact_metric_residual_divergence,
    evaluate_balance_identity,
    exchange_completed_ledger,
    matter_number_balance_residual,
    sourced_on_shell_metric_divergence,
)
from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    response_scalar_equation_residual,
)


def _config(epsilon: float = .3) -> CovariantResponseConfig:
    return CovariantResponseConfig(
        epsilon_nc=epsilon,
        einstein_coupling=.62,
        cosmological_constant=.014,
        phi_equilibrium=.1,
        response_kinetic=1.2,
        response_mass_sq=.8,
        response_quartic=.4,
        curvature_coupling=.06,
    )


def test_expanded_and_compact_bianchi_identity_agree() -> None:
    cfg = _config()
    result = evaluate_balance_identity(
        matter_stress_divergence=np.array([.04, -.02, .01, .03]),
        gradient_phi=np.array([.12, -.07, .03, .09]),
        curvature_scalar=.11,
        box_phi=-.06,
        phi=.32,
        config=cfg,
    )
    np.testing.assert_allclose(result["expanded"], result["compact"], atol=1e-14)
    assert result["max_abs_difference"] <= 1e-14


def test_canonical_response_stress_divergence_has_expected_factor() -> None:
    cfg = _config()
    gradient = np.array([.2, -.1, .04, .03])
    actual = canonical_response_stress_divergence(gradient, .08, .31, cfg)
    delta = .31 - cfg.phi_equilibrium
    expected_bracket = (
        cfg.response_kinetic * .08
        - cfg.response_mass_sq * delta
        - cfg.response_quartic * delta**3
    )
    np.testing.assert_allclose(actual, expected_bracket * gradient, atol=1e-14)


def test_exchange_ledger_closes_and_sourced_metric_shell_is_zero() -> None:
    cfg = _config()
    gradient = np.array([.1, -.04, .03, .08])
    ledger = exchange_completed_ledger(.27, gradient, cfg)
    assert ledger.full_scalar_source == pytest.approx(cfg.epsilon_nc * .27)
    np.testing.assert_allclose(
        ledger.matter_exchange, -ledger.response_exchange, atol=0.0
    )
    np.testing.assert_allclose(ledger.total_exchange, 0.0, atol=0.0)
    assert ledger.closed
    np.testing.assert_allclose(
        sourced_on_shell_metric_divergence(.27, gradient, cfg), 0.0, atol=1e-15
    )


def test_exchange_source_and_balance_vanish_exactly_in_gr_limit() -> None:
    cfg = _config(0.0)
    gradient = np.full(4, 1e100)
    ledger = exchange_completed_ledger(1e100, gradient, cfg)
    assert ledger.full_scalar_source == 0.0
    assert np.array_equal(ledger.matter_exchange, np.zeros(4))
    assert np.array_equal(ledger.response_exchange, np.zeros(4))
    assert np.array_equal(
        compact_metric_residual_divergence(np.zeros(4), gradient, 0.0, cfg),
        np.zeros(4),
    )


def test_exchange_current_transforms_as_a_covector() -> None:
    cfg = _config()
    gradient = np.array([.11, -.05, .07, .02])
    ledger = exchange_completed_ledger(.19, gradient, cfg)
    transform = np.array(
        [[1, .06, 0, 0], [.03, .97, .04, 0], [0, .01, 1.05, .03], [0, 0, .02, .95]],
        dtype=float,
    )
    transformed = exchange_completed_ledger(.19, transform.T @ gradient, cfg)
    np.testing.assert_allclose(
        transformed.matter_exchange,
        transform.T @ ledger.matter_exchange,
        rtol=1e-14,
        atol=1e-14,
    )


def test_sourced_shell_uses_full_nested_scalar_equation() -> None:
    cfg = _config()
    gradient = np.array([.08, .03, -.02, .06])
    reduced_source = .22
    full_source = cfg.epsilon_nc * reduced_source
    matter_exchange = -full_source * gradient
    residual = compact_metric_residual_divergence(
        matter_exchange, gradient, full_source, cfg
    )
    np.testing.assert_allclose(residual, 0.0, atol=1e-15)
    assert response_scalar_equation_residual(.2, -.1, .4, cfg) != 0.0


def test_matter_number_equation_remains_independent() -> None:
    assert matter_number_balance_residual(0.0) == 0.0
    assert matter_number_balance_residual(.2) == .2
    with pytest.raises(ValueError):
        matter_number_balance_residual(float("nan"))
    contract = balance_contract()
    assert contract["matter_number_equation_independent"] is True
    assert contract["derived_trace_imported"] is False
    assert contract["causal_kernel_implemented"] is False
