import numpy as np
from docs.scripts.audit.audit_topic13_finiteq_scattering_geometry import mode_geometry
from docs.scripts.audit.audit_topic13_gamma_scattering_geometry import pair_weight


def test_gamma_limit_matches_existing_geometry():
    p = np.array([[0., 0, 0], [.2, .3, .5]])
    m = [1., 2.]
    q = 2*np.pi*np.array([1., 2., 0.])
    e = np.eye(6)
    weights = mode_geometry(q, [1, 2, 0], p, m, e)
    np.testing.assert_allclose(weights.sum(), pair_weight(q, p, m, e))


def test_eigenvector_phase_does_not_change_column():
    rng = np.random.default_rng(12)
    e, _ = np.linalg.qr(rng.normal(size=(6, 6))+1j*rng.normal(size=(6, 6)))
    args = ([1., 2., 0], [1, 0, 0], [[0., 0, 0], [.2, .3, .5]], [1., 2.])
    np.testing.assert_allclose(mode_geometry(*args, e), mode_geometry(*args, e*np.exp(1j*np.arange(6))))


def test_atomic_gauge_and_phase_must_change_together():
    rng = np.random.default_rng(3)
    e, _ = np.linalg.qr(rng.normal(size=(6, 6))+1j*rng.normal(size=(6, 6)))
    p = np.array([[0., 0, 0], [.2, .3, .5]])
    reduced = np.array([.12, .07, 0])
    G = np.array([1., 0, 0])
    phase = np.repeat(np.exp(2j*np.pi*(p @ reduced)), 3)
    # Equivalent cell gauge has phase Q.x and transformed conjugate eigenvector.
    np.testing.assert_allclose(mode_geometry([1, 2, 0], G, p, [1, 2], e),
                              mode_geometry([1, 2, 0], G+reduced, p, [1, 2], phase[:, None]*e))
