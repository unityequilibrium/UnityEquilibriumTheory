import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_variance_directional_grid import directional_grid
from docs.scripts.audit.audit_topic13_variance_mesh_shift import shifted_grid


def test_isotropic_reference_and_inversion():
    q = directional_grid((8,8,8))
    np.testing.assert_array_equal(q, shifted_grid(8, (.5,.5,.5)))
    np.testing.assert_array_equal(q, -q[::-1])


def test_anisotropic_cardinality_and_marginals():
    q = directional_grid((4,6,8))
    assert q.shape == (192,3)
    for axis,n in enumerate((4,6,8)):
        values,counts = np.unique(q[:,axis], return_counts=True)
        np.testing.assert_array_equal(values, (np.arange(n)+.5)/n-.5)
        assert np.all(counts == len(q)//n)


def test_invalid_shape():
    for shape in ((1,2,2), (2.,3.,4.), (2,3)):
        with pytest.raises(ValueError):
            directional_grid(shape)
