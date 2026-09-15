from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import pytest

from docs.core.uet_o2_finite_temperature_sunset_vacuum_match import (
    finite_temperature_sunset_vacuum_match_contract,
    finite_temperature_sunset_vacuum_match_state,
)


@pytest.fixture(scope="module")
def vacuum_match_state():
    root = repo_root()
    artifact = json.loads(
        (root / "docs/core/artifacts/t13_uet_o2_action_1pi_sunset_retarded_audit.json").read_text(
            encoding="utf-8-sig"
        )
    )
    reference = tuple(artifact["state"]["reference"]["euclidean_reference_response"])
    return finite_temperature_sunset_vacuum_match_state(0.05, 0.5, 0.8, reference)


def test_low_temperature_sunset_matches_vacuum_spectral_and_retarded_sign(vacuum_match_state):
    state = vacuum_match_state
    assert state.matched_invariant_and_normalization_witness
    assert state.vacuum_match_completed
    assert state.vacuum_retarded_imaginary_part < 0.0
    assert state.thermal_retarded_imaginary_part < 0.0
    assert state.spectral_relative_residual <= 1.0e-3
    assert state.retarded_imaginary_relative_residual <= 1.0e-3


def test_low_temperature_sunset_matches_vacuum_pv_and_removes_scattering_channel(vacuum_match_state):
    state = vacuum_match_state
    assert state.principal_value_relative_residual <= 1.0e-3
    assert state.two_to_two_fraction <= 1.0e-3
    assert state.one_to_three_relative_residual <= 1.0e-3


def test_vacuum_match_contract_keeps_physical_renormalization_open():
    contract = finite_temperature_sunset_vacuum_match_contract()
    assert contract["included"]["low_temperature_spectral_match"]
    assert contract["included"]["low_temperature_principal_value_match"]
    assert contract["excluded"]["physical_renormalization_scheme_match"]
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["alpha_Phi_K"]
