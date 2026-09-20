"""Tests for the condensed retarded-dissipation identifiability no-go."""

from __future__ import annotations

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_condensed_retarded_dissipation_no_go import (
    condensed_retarded_dissipation_boundary,
    condensed_retarded_dissipation_contract,
    retarded_memory_kernel,
    retarded_memory_kernel_time,
)


def _config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def test_causal_witnesses_match_at_zero_and_separate_at_finite_frequency() -> None:
    boundary = condensed_retarded_dissipation_boundary(0.2, 1.3, 0.2, _config())

    assert boundary.condensate_control > 0.0
    assert boundary.witness_a_causal is True
    assert boundary.witness_b_causal is True
    assert boundary.zero_frequency_match is True
    assert boundary.finite_frequency_distinct is True
    assert boundary.physical_transport_coefficients_emitted is False


def test_memory_witness_has_retarded_support_and_positive_dissipative_part() -> None:
    assert retarded_memory_kernel_time(-1.0, 0.8, 1.0) == 0.0
    assert retarded_memory_kernel_time(0.5, 0.8, 1.0) > 0.0
    assert retarded_memory_kernel(0.7, 0.8, 1.0).real >= 0.0
    assert retarded_memory_kernel(0.7, 0.8, 4.0).real >= 0.0


def test_contract_keeps_physical_transport_open() -> None:
    contract = condensed_retarded_dissipation_contract()

    assert "physical coefficient" in contract["claim_boundary"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "derived history trace" in contract["unit_contract"]["R_gen"]
    assert "separate observer" in contract["unit_contract"]["R_obs"]
