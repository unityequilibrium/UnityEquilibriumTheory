import numpy as np

from docs.core.uet_shear_symmetry import constraints, e2_group, pump_doublet, rotation


def test_no_invariant_linear_force():
    linear, _ = constraints()
    assert np.linalg.matrix_rank(linear, tol=1e-10) == 2
    np.testing.assert_allclose(sum(e2_group())/12, 0, atol=1e-14)


def test_unique_isotropic_quadratic():
    _, quadratic = constraints()
    assert np.linalg.matrix_rank(quadratic, tol=1e-10) == 2
    np.testing.assert_allclose(quadratic @ [1., 1., 0.], 0, atol=1e-14)
    h = np.array([[3., 2.], [2., 7.]])
    average = sum(g.T @ h @ g for g in e2_group())/12
    np.testing.assert_allclose(average, np.trace(h)*np.eye(2)/2, atol=1e-14)


def test_basis_gauge_invariance():
    change = rotation(.41)
    group = [change @ g @ change.T for g in e2_group()]
    linear = np.vstack([g.T-np.eye(2) for g in group])
    assert np.linalg.matrix_rank(linear, tol=1e-10) == 2
    np.testing.assert_allclose(sum(group)/12, 0, atol=1e-14)


def test_quadratic_phi_coupling_survives():
    s = np.array([.3, -.2])
    phi, eta = .7, .13
    potential = -.5*eta*phi*np.dot(s, s)
    for g in e2_group():
        np.testing.assert_allclose(-.5*eta*phi*np.dot(g @ s, g @ s), potential)
    # This coupling changes curvature, not a force independent of displacement.
    np.testing.assert_array_equal(eta*phi*np.zeros(2), np.zeros(2))


def test_polarized_source_covariance_and_intensity():
    field = np.array([.4, .8])
    for angle in np.linspace(0, 2*np.pi, 13):
        np.testing.assert_allclose(pump_doublet(rotation(angle) @ field),
                                   rotation(2*angle) @ pump_doublet(field), atol=1e-14)
    rotated = rotation(np.pi/2) @ field
    np.testing.assert_allclose(np.dot(rotated, rotated), np.dot(field, field))
    np.testing.assert_allclose(pump_doublet(rotated), -pump_doublet(field), atol=1e-14)


def test_anisotropic_source_allows_linear_pairing():
    source, s = np.array([.1, -.3]), np.array([.5, .2])
    for g in e2_group():
        np.testing.assert_allclose(np.dot(g @ source, g @ s), np.dot(source, s))


def test_coherent_mean_not_thermal_variance():
    points = np.array([[1., 0], [-1., 0], [0., 1.], [0., -1.]])
    np.testing.assert_allclose(points.mean(axis=0), 0)
    assert np.mean(np.sum(points**2, axis=1)) == 1
    for g in e2_group():
        np.testing.assert_allclose(np.mean(np.sum((points @ g.T)**2, axis=1)), 1)
