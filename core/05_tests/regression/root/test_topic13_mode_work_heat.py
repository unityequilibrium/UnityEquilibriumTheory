import numpy as np
import pytest
from scipy.constants import Boltzmann as KB

from docs.core.uet_mode_work_heat import equilibrium, protocol_response


def fixture():
    return KB*np.array([60., 180., 400.]), 200., KB*np.array([15., -20., 35.]), np.array([2., 1., 3.])


def test_energy_entropy_derivatives_independently():
    e, t, de, w = fixture()
    result = protocol_response(e, t, de, w)
    h = 1e-4
    plus, minus = equilibrium(e+h*de, t), equilibrium(e-h*de, t)
    for field, expected in [('energy', 'isothermal_energy_derivative'),
                            ('entropy', 'isothermal_entropy_derivative')]:
        numeric = np.dot(w, plus[field]-minus[field])/(2*h)
        np.testing.assert_allclose(numeric, result[expected], rtol=1e-7, atol=1e-35)


def test_isentropic_tangent():
    e, t, de, w = fixture()
    gain = protocol_response(e, t, de, w)['equilibrium_isentropic_temperature_derivative']
    h = 1e-4
    plus = np.dot(w, equilibrium(e+h*de, t+h*gain)['entropy'])
    minus = np.dot(w, equilibrium(e-h*de, t-h*gain)['entropy'])
    assert abs(plus-minus)/(KB*h) < 1e-8


def test_uniform_gap_scale_preserves_canonical_occupation():
    e, t, _, w = fixture()
    gain = protocol_response(e, t, e, w)['equilibrium_isentropic_temperature_derivative']
    np.testing.assert_allclose(gain, t)
    np.testing.assert_allclose(equilibrium(1.3*e, 1.3*t)['occupation'], equilibrium(e, t)['occupation'])


def test_nonuniform_frozen_modes_have_no_common_temperature():
    e, t, _, _ = fixture()
    scale = np.array([1.1, 1.2, .9])
    inferred_temperatures = scale*t
    assert np.ptp(inferred_temperatures) > 0
    n = equilibrium(e, t)['occupation']
    np.testing.assert_allclose(scale*e/(KB*np.log1p(1/n)), inferred_temperatures)


def test_heat_is_not_total_energy_change():
    e = KB*np.array([60.])
    result = protocol_response(e, 200., e, [1.])
    assert result['isothermal_work_derivative'] > 0
    assert result['isothermal_heat_derivative'] < 0
    assert result['isothermal_energy_derivative'] > 0
    assert result['frozen_occupation_heat_derivative'] == 0


def test_derivative_not_determined_by_unperturbed_spectrum():
    e, t, de, w = fixture()
    first = protocol_response(e, t, de, w)
    second = protocol_response(e, t, 2*de, w)
    assert first['capacity'] == second['capacity']
    np.testing.assert_allclose(second['equilibrium_isentropic_temperature_derivative'],
                               2*first['equilibrium_isentropic_temperature_derivative'])


@pytest.mark.parametrize('gap', [0., -1., np.nan])
def test_invalid_mode_not_clipped(gap):
    with pytest.raises(ValueError):
        equilibrium([gap], 200.)
