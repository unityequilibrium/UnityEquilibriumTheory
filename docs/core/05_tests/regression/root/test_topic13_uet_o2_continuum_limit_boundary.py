"""Tests for the scoped continuum-limit acceptance boundary."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_continuum_limit_boundary import (
    CONTINUUM_ACCEPTANCE_THRESHOLD,
    assess_continuum_limit,
    continuum_limit_boundary_contract,
)


def test_nonconverged_sequence_is_rejected_without_extrapolation() -> None:
    boundary = assess_continuum_limit(
        (8, 10, 12, 14),
        (64, 96, 128, 160),
        (83.4, 43.7, 33.2, 31.8),
        (0.475, 0.242, 0.040),
    )
    assert boundary.current_scheme_continuum_no_go is True
    assert boundary.acceptance_threshold == CONTINUUM_ACCEPTANCE_THRESHOLD
    assert boundary.extrapolated_response_emitted is False


def test_converged_sequence_is_not_called_no_go() -> None:
    boundary = assess_continuum_limit(
        (8, 10, 12),
        (64, 96, 128),
        (10.0, 10.05, 10.06),
        (0.005, 0.001),
    )
    assert boundary.current_scheme_continuum_no_go is False


def test_invalid_sequence_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="equal length"):
        assess_continuum_limit((8, 10), (64,), (1.0, 1.1), (0.1,))


def test_contract_keeps_ontology_and_scope_boundaries() -> None:
    contract = continuum_limit_boundary_contract()
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "mathematical no-go for every future discretization" in contract["excluded_scope"]
