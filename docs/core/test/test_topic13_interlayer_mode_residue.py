"""Independent kinematic and spectral checks, not material validation."""

import numpy as np
import pytest

from docs.core.uet_interlayer_mode_residue import (
    cell_phase, pair_character, projected_resolvent, shear_basis,
)


def setup_basis():
    masses = np.array([2., 3., 5., 7.])
    layers = np.array([0, 1, 0, 1])
    basis, mu = shear_basis(masses, layers, [0, 0, 1], [1, 0, 0])
    return masses, layers, basis, mu


def test_centroid_and_translation():
    masses, layers, basis, mu = setup_basis()
    np.testing.assert_allclose(basis.T @ basis, np.eye(2), atol=1e-14)
    displacement = np.arange(12.).reshape(4, 3)
    centroids = [np.average(displacement[layers == j], axis=0,
                            weights=masses[layers == j]) for j in (0, 1)]
    actual = basis.T @ (np.sqrt(masses)[:, None]*displacement).ravel()/np.sqrt(mu)
    np.testing.assert_allclose(actual, (centroids[0]-centroids[1])[:2])
    translation = (np.sqrt(masses)[:, None]*np.array([2., 3., 4.])).ravel()
    np.testing.assert_allclose(basis.T @ translation, 0, atol=1e-14)


def test_rigid_kinetic_energy():
    masses, layers, _, mu = setup_basis()
    ma, mb = [masses[layers == j].sum() for j in (0, 1)]
    speed = np.array([.3, -.4, 0])
    velocities = np.where((layers == 0)[:, None], mb/(ma+mb)*speed,
                          -ma/(ma+mb)*speed)
    np.testing.assert_allclose(.5*np.sum(masses[:, None]*velocities**2),
                               .5*mu*np.dot(speed, speed))


def test_atom_permutation_and_rotation():
    masses, layers, basis, mu = setup_basis()
    perm = np.array([2, 0, 3, 1])
    rotated = np.array([[0., 0, 1], [1, 0, 0], [0, 1, 0]])
    other, other_mu = shear_basis(masses[perm], layers[perm],
                                  rotated @ [0, 0, 1], rotated @ [1, 0, 0])
    expected = np.einsum('ab,nbc->nac', rotated, basis.reshape(4, 3, 2)[perm])
    np.testing.assert_allclose(other, expected.reshape(12, 2), atol=1e-14)
    assert mu == other_mu


def test_degenerate_pair_gauge_and_phase():
    _, _, basis, _ = setup_basis()
    vectors = np.linalg.qr(basis, mode='complete')[0].astype(complex)
    original = pair_character(vectors, basis)
    mix = np.array([[1, 1j], [1j, 1]])/np.sqrt(2)
    vectors[:, :2] = vectors[:, :2] @ mix
    phase = cell_phase([.02, 0, .01], np.arange(12.).reshape(4, 3)/12)
    changed = pair_character(vectors/phase[:, None], basis, phase)
    np.testing.assert_allclose(changed['weight_matrix'], original['weight_matrix'], atol=1e-14)
    np.testing.assert_allclose(changed['principal_weights'], [1, 1], atol=1e-14)


def test_spectral_sum_and_residue_sum_rule():
    _, _, basis, mu = setup_basis()
    rng = np.random.default_rng(17)
    vectors = np.linalg.qr(rng.normal(size=(12, 12)))[0]
    values = np.linspace(.1, 9, 12)
    matrix = (vectors*values) @ vectors.T
    s = .7+1.3j
    overlaps = basis.T @ vectors
    spectral = (overlaps/(values+s*s)) @ overlaps.T/mu
    np.testing.assert_allclose(projected_resolvent(matrix, basis, mu, s), spectral,
                               rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(overlaps @ overlaps.T, np.eye(2), atol=1e-14)


@pytest.mark.parametrize('masses,layers,normal,tangent', [
    ([0, 1], [0, 1], [0, 0, 1], [1, 0, 0]),
    ([1, 1], [0, 0], [0, 0, 1], [1, 0, 0]),
    ([1, 1], [0, 1], [0, 0, 1], [0, 0, 2]),
    ([1, np.nan], [0, 1], [0, 0, 1], [1, 0, 0]),
])
def test_invalid_mass_basis(masses, layers, normal, tangent):
    with pytest.raises(ValueError):
        shear_basis(masses, layers, normal, tangent)


def test_nonhermitian_rejected():
    _, _, basis, mu = setup_basis()
    matrix = np.eye(12)
    matrix[0, 1] = .1
    with pytest.raises(ValueError):
        projected_resolvent(matrix, basis, mu, 1.)
