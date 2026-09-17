"""Tests for the condensed dissipative transport identifiability boundary."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_condensed_dissipative_transport_identifiability_no_go import (
    condensed_dissipative_transport_boundary,
    condensed_dissipative_transport_contract,
    entropy_production_quadratic,
    is_positive_semidefinite_2x2,
)


def test_two_witnesses_are_positive_and_identical_on_static_state() -> None:
    boundary = condensed_dissipative_transport_boundary(0.2, 0.35)

    assert boundary.witness_a_positive_semidefinite is True
    assert boundary.witness_b_positive_semidefinite is True
    assert boundary.static_force == (0.0, 0.0)
    assert boundary.static_entropy_production_a == 0.0
    assert boundary.static_entropy_production_b == 0.0
    assert boundary.static_state_identical is True


def test_nonzero_probe_separates_the_two_responses() -> None:
    boundary = condensed_dissipative_transport_boundary(0.2, 0.35)

    assert boundary.probe_responses_distinct is True
    assert boundary.probe_response_a != boundary.probe_response_b


def test_non_positive_matrix_is_rejected_by_psd_boundary() -> None:
    matrix = ((1.0, 0.0), (0.0, -0.1))

    assert is_positive_semidefinite_2x2(matrix) is False
    assert entropy_production_quadratic(matrix, (0.0, 1.0)) < 0.0


def test_contract_keeps_physical_promotion_open() -> None:
    contract = condensed_dissipative_transport_contract()

    assert "not a physical Kubo coefficient" in contract["unit_contract"]["onsager_matrix"]
    assert "a physical Kubo/Onsager coefficient" in contract["excluded_scope"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "derived history trace" in contract["unit_contract"]["R_gen"]
    assert "separate observer" in contract["unit_contract"]["R_obs"]


def test_temperature_must_be_positive() -> None:
    with pytest.raises(ValueError, match="temperature must be positive"):
        condensed_dissipative_transport_boundary(0.0, 0.35)
