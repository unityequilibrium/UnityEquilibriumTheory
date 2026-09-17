import numpy as np
import pytest
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state


@pytest.fixture(scope="module")
def small_state():
    return covariant_entropy_heat_flux_balance_state(.22,.35,.15,natural_bridge_config(),
        thermal_force_covariant=np.array([0.,1.e-9,0.,0.]))


def test_current_outputs_are_distinct_and_frame_consistent(small_state):
    d=small_state.frame_current_decomposition
    q=np.array(d["energy_flux_contravariant"])
    v=np.array(d["charge_diffusion_contravariant"])
    heat=np.array(d["invariant_heat_contravariant"])
    assert np.linalg.norm(q) < 1.e-10*np.linalg.norm(heat)
    assert np.linalg.norm(heat-q+small_state.enthalpy_per_charge*v)<1.e-20
    assert d["entropy_frame_identity_residual"]<1.e-15
    canonical=np.array(d["landau_entropy_current_contravariant"])
    assert canonical[1] == pytest.approx(-small_state.chemical_potential*v[1]/small_state.temperature)
    assert not np.allclose(canonical,small_state.entropy_current_contravariant,atol=1.e-10)


def test_small_probe_is_not_a_certified_finite_velocity_state(small_state):
    d=small_state.frame_current_decomposition
    assert d["frame_shift_spatial_norm"]<.001
    assert d["finite_velocity_state_validated"] is False
    assert "NOT_CANONICAL" in d["legacy_entropy_current_role"]


def test_unit_response_is_not_a_physical_frame_velocity():
    state=covariant_entropy_heat_flux_balance_state(.22,.35,.15,natural_bridge_config())
    d=state.frame_current_decomposition
    assert d["frame_shift_spatial_norm"]>1.
    assert d["finite_velocity_state_validated"] is False
