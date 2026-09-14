import numpy as np
from docs.scripts.audit.audit_topic13_gamma_scattering_geometry import pair_weight


def test_destructive_interference_requires_position_phase():
    vectors = np.zeros((6, 1)); vectors[0, 0] = vectors[3, 0] = 1/np.sqrt(2)
    assert pair_weight([np.pi, 0, 0], [[0, 0, 0], [1, 0, 0]], [1, 1], vectors) < 1e-25
    assert pair_weight([np.pi, 0, 0], [[0, 0, 0], [0, 0, 0]], [1, 1], vectors) > 1


def test_pair_gauge_and_origin_invariance():
    e = np.eye(3)[:, :2]
    rotation = np.array([[1, 1], [-1, 1]])/np.sqrt(2)
    a = pair_weight([1, 2, 0], [[0, 0, 0]], [2], e)
    b = pair_weight([1, 2, 0], [[3, 4, 5]], [2], e @ rotation)
    np.testing.assert_allclose(a, b)


def test_out_of_plane_displacement_invisible_for_basal_q():
    assert pair_weight([1, 2, 0], [[0, 0, 0]], [1], np.eye(3)[:, 2:]) == 0
