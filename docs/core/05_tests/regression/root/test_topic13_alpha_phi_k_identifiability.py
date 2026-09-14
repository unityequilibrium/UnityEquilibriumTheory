"""Regression tests for the Topic 13 Phi-normalization boundary."""

from __future__ import annotations

from docs.scripts.audit.audit_topic13_alpha_phi_k_identifiability import (
    action_coordinate_reparameterization,
)


def test_action_coordinate_reparameterization_preserves_declared_observables() -> None:
    witness = action_coordinate_reparameterization()
    assert witness["potential_residual"] <= 1.0e-15
    assert witness["derivative_covariance_residual"] <= 1.0e-15
    assert witness["effective_mass_sq_residual"] <= 1.0e-15


def test_coordinate_reparameterization_does_not_emit_an_absolute_calibration() -> None:
    witness = action_coordinate_reparameterization()
    assert witness["alpha_scale_rule"] == "alpha_Phi_prime_K=alpha_Phi_K/s"
    assert witness["physical_observable_invariance"] == (
        "Delta_Tq=alpha_Phi_K*Delta_Phi is unchanged"
    )
