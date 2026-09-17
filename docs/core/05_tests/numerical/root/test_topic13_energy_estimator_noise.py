import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_energy_estimator_noise import energy_estimator


def test_inverse_variance_weighted_mean():
    w, var, _ = energy_estimator([[1], [1]], [1], np.diag([1, 4]))
    np.testing.assert_allclose(w, [.8, .2])
    np.testing.assert_allclose(var, .8)


def test_identifiable_sum_without_full_state():
    w, var, _ = energy_estimator([[1, 1]], [1, 1], [[2]])
    np.testing.assert_allclose(w, [1])
    np.testing.assert_allclose(var, 2)
    with pytest.raises(ValueError):
        energy_estimator([[1, 1]], [1, 2], [[2]])


def test_covariance_rescaling_and_null_perturbation():
    a = np.array([[1., 0], [0, 1], [1, 1]])
    cov = np.diag([1., 2, 3])
    w, var, _ = energy_estimator(a, [1, 2], cov)
    w2, var2, _ = energy_estimator(a, [1, 2], 4*cov)
    np.testing.assert_allclose(w, w2)
    np.testing.assert_allclose(var2, 4*var)
    altered = w+np.array([-1., -1, 1])
    assert altered @ cov @ altered > var
