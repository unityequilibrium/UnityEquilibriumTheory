"""Tests for the same-kernel tagged and spectral width."""
import numpy as np
import pytest

from docs.core.uet_o2_same_kernel_tagged_width import (
    same_kernel_tagged_width_contract,
    same_kernel_tagged_width_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config
from docs.scripts.audit import audit_topic13_same_kernel_tagged_width as audit


def test_tagged_width_is_positive_resolved_and_spectral():
    state = same_kernel_tagged_width_state(0.25, 0.1, 0.0, config())
    contract = same_kernel_tagged_width_contract()
    widths = np.asarray(state.total_widths_by_tag_momentum)
    spectral = np.asarray(state.retarded_self_energy_imaginary_by_tag_momentum)
    energies = np.asarray(state.tagged_energies)
    assert contract["unit_contract"]["Gamma"] == 1
    assert np.all(widths > 0.0)
    assert np.allclose(spectral, -2.0 * energies[None, :] * widths, rtol=1.0e-14)
    assert state.maximum_event_energy_residual <= 1.0e-12
    assert state.maximum_event_momentum_residual <= 1.0e-12
    assert state.maximum_detailed_balance_residual <= 1.0e-10
    assert not state.dressed_self_consistent_width_completed
    assert not state.xie_2026_accessed


def test_charge_conjugation_swaps_tagged_widths():
    positive_mu = same_kernel_tagged_width_state(
        0.25, 0.1, 0.0, config(), tagged_momenta=(1.0,)
    )
    negative_mu = same_kernel_tagged_width_state(
        0.25, -0.1, 0.0, config(), tagged_momenta=(1.0,)
    )
    assert np.asarray(positive_mu.total_widths_by_tag_momentum)[:, 0] == pytest.approx(
        np.asarray(negative_mu.total_widths_by_tag_momentum)[::-1, 0], rel=1.0e-12
    )


@pytest.mark.parametrize("scale", [1.5, 2.0, 3.0])
def test_whole_action_width_scaling(scale):
    row = audit.scale_witness(scale)
    assert row["energy_exponents_by_tag"] == pytest.approx([1.0, 1.0], abs=1.0e-10)


@pytest.mark.parametrize("momenta", [(), (0.0,), (1.0, 0.5), (1.0, 1.0)])
def test_invalid_tagged_momentum_grid(momenta):
    with pytest.raises(ValueError):
        same_kernel_tagged_width_state(
            0.25, 0.1, 0.0, config(), tagged_momenta=momenta
        )
