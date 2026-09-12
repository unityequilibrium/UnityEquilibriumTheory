import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_variance_mesh_shift import shifted_grid


def test_uniform_grid_cardinality_and_fourier_cancellation():
    q = shifted_grid(8, (.25, .5, .75))
    assert q.shape == (512, 3)
    assert len(np.unique(q, axis=0)) == 512
    assert np.all(abs(q) < .5)
    for axis in range(3):
        np.testing.assert_allclose(np.mean(np.exp(2j*np.pi*q[:, axis])), 0, atol=1e-14)


def test_complement_shifts_are_inversion_pairs():
    a = shifted_grid(8, (.25, .25, .25))
    b = shifted_grid(8, (.75, .75, .75))
    np.testing.assert_allclose(a, -b[::-1], atol=0, rtol=0)


def test_invalid_grid_rejected():
    for n, s in [(1, [.5]*3), (2, [0]*3), (2, [np.nan]*3), (2, [.5]*2)]:
        with pytest.raises(ValueError):
            shifted_grid(n, s)
