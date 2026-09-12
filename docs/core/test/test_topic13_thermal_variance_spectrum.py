import numpy as np
import pytest
from scipy.constants import c
from docs.scripts.audit.audit_topic13_thermal_variance_spectrum import partition_trace
from docs.scripts.audit.audit_topic13_interlayer_thermal_variance import modal_covariance


def test_partition_reconstructs_total_and_handles_empty_bins():
    omega = 2*np.pi*c*100*np.array([5., 20., 1500.])
    overlap = np.array([[1., 2j, .3], [.4j, .2, 1.]])
    bins = partition_trace(overlap, omega, 300, 2.)
    np.testing.assert_allclose(bins.sum(), np.trace(modal_covariance(overlap, omega, 300, 2.)).real, rtol=1e-14, atol=0)
    assert np.all(bins[[2, 3, 4]] == 0)


def test_degenerate_subspace_invariance():
    omega = np.full(2, 2*np.pi*c*100*20)
    overlap = np.array([[1., .3j], [.2, .4]])
    unitary = np.array([[1, 1j], [1j, 1]])/np.sqrt(2)
    np.testing.assert_allclose(partition_trace(overlap, omega, 200, 3.), partition_trace(overlap@unitary, omega, 200, 3.), rtol=1e-14, atol=0)


def test_unstable_frequency_and_invalid_mass_rejected():
    with pytest.raises(ValueError):
        partition_trace(np.ones((2, 1)), [0.], 300, 1.)
    with pytest.raises(ValueError):
        partition_trace(np.ones((2, 1)), [1.], 300, -1.)
