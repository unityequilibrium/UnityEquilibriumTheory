from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    chemical_potential_from_charge_density,
    effective_mass_sq,
    o2_eos_derivatives,
    o2_equilibrium_state,
    o2_finite_density_eos_contract,
    o2_helmholtz_state,
)


def _config(*, epsilon: float = 0.2) -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.3,
            matter_mass_sq=0.7,
            matter_quartic=0.9,
            response_coupling=0.4,
        ),
        response=CovariantResponseConfig(
            epsilon_nc=epsilon,
            phi_equilibrium=0.1,
        ),
    )


def test_condensed_eos_is_stationary_and_matches_closed_form() -> None:
    config = _config()
    mu = 1.4
    phi = 0.35
    state = o2_equilibrium_state(mu, phi, config)
    q = config.matter.matter_kinetic * mu**2 - effective_mass_sq(phi, config)
    assert state.branch == "condensed"
    assert state.amplitude**2 == pytest.approx(q / config.matter.matter_quartic)
    assert state.pressure == pytest.approx(q**2 / (4.0 * config.matter.matter_quartic))
    assert state.charge_density == pytest.approx(
        config.matter.matter_kinetic * mu * q / config.matter.matter_quartic
    )
    stationarity = (
        (state.effective_mass_sq - config.matter.matter_kinetic * mu**2)
        * state.amplitude
        + config.matter.matter_quartic * state.amplitude**3
    )
    assert abs(stationarity) <= 1.0e-12
    assert state.energy_density == pytest.approx(mu * state.charge_density - state.pressure)
    assert state.susceptibility is not None and state.susceptibility > 0.0
    assert state.sound_speed_sq is not None
    assert 0.0 <= state.sound_speed_sq <= 1.0


def test_pressure_derivatives_and_response_reciprocity() -> None:
    config = _config()
    mu = 1.35
    phi = 0.2
    state = o2_equilibrium_state(mu, phi, config)
    derivatives = o2_eos_derivatives(mu, phi, config)
    h_mu = 1.0e-5
    p_plus = o2_equilibrium_state(mu + h_mu, phi, config).pressure
    p_minus = o2_equilibrium_state(mu - h_mu, phi, config).pressure
    fd_density = (p_plus - p_minus) / (2.0 * h_mu)
    fd_chi = (
        o2_equilibrium_state(mu + h_mu, phi, config).charge_density
        - o2_equilibrium_state(mu - h_mu, phi, config).charge_density
    ) / (2.0 * h_mu)
    h_phi = 1.0e-6
    fd_response = (
        o2_equilibrium_state(mu, phi + h_phi, config).pressure
        - o2_equilibrium_state(mu, phi - h_phi, config).pressure
    ) / (2.0 * h_phi)
    assert fd_density == pytest.approx(state.charge_density, rel=1.0e-9, abs=1.0e-9)
    assert fd_chi == pytest.approx(state.susceptibility, rel=1.0e-9, abs=1.0e-9)
    assert fd_response == pytest.approx(state.response_source, rel=1.0e-8, abs=1.0e-9)
    assert derivatives["dp_dphi_at_fixed_mu"] == pytest.approx(state.response_source)
    assert derivatives["df_dphi_at_fixed_n"] == pytest.approx(-state.response_source)


@pytest.mark.parametrize("density", [-2.0, -0.3, -0.01, 0.01, 0.3, 2.0])
def test_canonical_inversion_is_signed_unique_and_legendre_closed(density: float) -> None:
    config = _config()
    phi = 0.25
    mu = chemical_potential_from_charge_density(density, phi, config)
    state = o2_helmholtz_state(density, phi, config)
    assert np.sign(mu) == np.sign(density)
    assert state.branch == "condensed"
    assert state.charge_density == pytest.approx(density, rel=1.0e-11, abs=1.0e-12)
    assert state.helmholtz_free_energy == pytest.approx(
        mu * density - state.pressure, rel=1.0e-12, abs=1.0e-12
    )
    assert state.energy_density == pytest.approx(state.helmholtz_free_energy)
    assert state.helmholtz_response_derivative == pytest.approx(-state.response_source)


def test_helmholtz_derivatives_recover_mu_and_inverse_susceptibility() -> None:
    config = _config()
    density = 0.8
    phi = 0.2
    state = o2_helmholtz_state(density, phi, config)
    step = 1.0e-5
    plus = o2_helmholtz_state(density + step, phi, config)
    minus = o2_helmholtz_state(density - step, phi, config)
    df_dn = (plus.helmholtz_free_energy - minus.helmholtz_free_energy) / (2.0 * step)
    dmu_dn = (plus.chemical_potential - minus.chemical_potential) / (2.0 * step)
    assert df_dn == pytest.approx(state.chemical_potential, rel=1.0e-8, abs=1.0e-9)
    assert dmu_dn == pytest.approx(1.0 / state.susceptibility, rel=1.0e-8, abs=1.0e-9)


def test_signed_symmetry_and_response_null_limit() -> None:
    config = _config()
    plus = o2_equilibrium_state(1.4, 0.6, config)
    minus = o2_equilibrium_state(-1.4, 0.6, config)
    assert plus.pressure == pytest.approx(minus.pressure)
    assert plus.charge_density == pytest.approx(-minus.charge_density)

    null = _config(epsilon=0.0)
    left = o2_equilibrium_state(1.4, -20.0, null)
    right = o2_equilibrium_state(1.4, 30.0, null)
    assert left == right.__class__(**{**right.__dict__, "space_response": left.space_response})
    assert left.response_source == 0.0


def test_normal_and_critical_branches_are_explicit() -> None:
    config = _config()
    phi = 0.1
    normal = o2_equilibrium_state(0.0, phi, config)
    assert normal.branch == "normal"
    assert normal.pressure == 0.0
    critical_mu = np.sqrt(effective_mass_sq(phi, config) / config.matter.matter_kinetic)
    critical = o2_equilibrium_state(critical_mu, phi, config)
    assert critical.branch == "critical_boundary"
    assert critical.susceptibility is None
    with pytest.raises(ValueError, match="one-sided"):
        o2_eos_derivatives(critical_mu, phi, config)


def test_contract_preserves_claim_boundary() -> None:
    contract = o2_finite_density_eos_contract()
    assert contract["pressure_origin"] == "tree_level_stationary_O2_grand_potential"
    assert contract["symmetric_double_well"] == "CONSTITUTIVE_COMPARATOR_NOT_DERIVED"
    assert contract["finite_temperature_normal_component"] == "NOT_DERIVED"
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
