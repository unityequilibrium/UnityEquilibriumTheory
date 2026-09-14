from __future__ import annotations

import numpy as np

from docs.core.uet_o2_equilibrium_kms import equilibrium_kms_contract, equilibrium_kms_state


def test_kms_ratio_and_spectral_difference() -> None:
    state = equilibrium_kms_state(temperature=0.25, mode_energy=1.1, spectral_weight=1.4)

    assert np.isclose(state.greater_weight - state.lesser_weight, state.spectral_weight)
    assert np.isclose(state.log_kms_ratio, state.mode_energy / state.temperature)
    assert np.isclose(
        state.greater_weight / state.lesser_weight,
        np.exp(state.mode_energy / state.temperature),
    )


def test_fdt_noise_and_entropy() -> None:
    state = equilibrium_kms_state(temperature=0.25, mode_energy=1.1, spectral_weight=1.4)

    assert np.isclose(
        state.noise_weight,
        state.spectral_weight / np.tanh(state.mode_energy / (2.0 * state.temperature)),
    )
    assert state.mode_entropy >= 0.0
    assert state.entropy_production == 0.0


def test_contract_preserves_ontology_and_open_boundary() -> None:
    contract = equilibrium_kms_contract()

    assert "not a charge" in contract["ontology"]["C"]
    assert "not temperature" in contract["ontology"]["Phi"]
    assert "not an equilibrium state" in contract["ontology"]["R_gen"]
    assert "physical Kubo coefficients" in contract["scope"]["open"]
    assert "alpha_Phi_K" in contract["scope"]["open"]

