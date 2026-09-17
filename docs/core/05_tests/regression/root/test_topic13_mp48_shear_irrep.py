import numpy as np
import pytest

from docs.scripts.audit.audit_topic13_mp48_shear_irrep import gamma_action, expected_e2g_character


def test_inversion_includes_atom_swap():
    pos = np.array([[0, 0, .25], [0, 0, .75]])
    action, _, perm, error = gamma_action(np.eye(3), pos, [1, 1], -np.eye(3), np.zeros(3))
    assert perm == [1, 0] and error == 0
    shear = np.array([1., 0, 0, -1, 0, 0])
    np.testing.assert_array_equal(action @ shear, shear)
    np.testing.assert_array_equal(action @ action, np.eye(6))


def test_unequal_mass_swap_rejected():
    with pytest.raises(ValueError):
        gamma_action(np.eye(3), np.array([[0, 0, .25], [0, 0, .75]]),
                     [1, 2], -np.eye(3), np.zeros(3))


def test_false_translation_rejected():
    with pytest.raises(ValueError):
        gamma_action(np.eye(3), np.array([[0, 0, 0]]), [1], np.eye(3), [.1, 0, 0])


def test_character_distinguishes_vector_and_doublet():
    angle = np.pi/3
    r = np.array([[np.cos(angle), -np.sin(angle), 0],
                  [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
    np.testing.assert_allclose(expected_e2g_character(r), -1)
    np.testing.assert_allclose(np.trace(r[:2, :2]), 1)
    assert expected_e2g_character(-np.eye(3)) == 2
    assert expected_e2g_character(np.diag([1., -1., -1.])) == 0
