import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_state,
    quasiparticle_pressure,
)


def test_normal_and_condensed_branches_have_finite_thermodynamics() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(quadrature_order=96, cutoff_factor=50.0)
    normal = finite_temperature_o2_state(0.25, 0.4, 0.1, config)
    condensed = finite_temperature_o2_state(0.15, 1.2, 0.1, config)
    assert normal.branch == "normal"
    assert condensed.branch == "condensed"
    assert normal.pressure > 0.0 and condensed.pressure > 0.0
    assert normal.entropy_density > 0.0 and condensed.entropy_density > 0.0
    assert condensed.goldstone_energy_at_zero_momentum <= 1.0e-8


def test_condensed_quasiparticle_spectrum_is_ordered_and_nonnegative() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(quadrature_order=96, cutoff_factor=50.0)
    for momentum in (0.0, 0.1, 1.0, 5.0):
        upper, lower = condensed_quasiparticle_energies(momentum, 1.2, 0.1, config)
        assert np.isfinite(upper) and np.isfinite(lower)
        assert upper >= lower >= 0.0


def test_pressure_is_even_and_charge_is_odd_in_chemical_potential() -> None:
    config = FiniteTemperatureO2QuasiparticleConfig(quadrature_order=96, cutoff_factor=50.0)
    positive = finite_temperature_o2_state(0.15, 1.2, 0.1, config)
    negative = finite_temperature_o2_state(0.15, -1.2, 0.1, config)
    np.testing.assert_allclose(
        quasiparticle_pressure(0.15, -1.2, 0.1, config),
        quasiparticle_pressure(0.15, 1.2, 0.1, config),
        rtol=2.0e-7,
        atol=2.0e-10,
    )
    assert np.isclose(
        positive.charge_density,
        -negative.charge_density,
        rtol=2.0e-5,
        atol=2.0e-8,
    )
