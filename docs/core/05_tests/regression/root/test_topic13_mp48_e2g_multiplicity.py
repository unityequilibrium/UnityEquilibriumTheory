import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_mp48_e2g_multiplicity import frequency_groups, representation_errors


def test_same_symmetry_does_not_merge_different_frequencies():
    assert frequency_groups([50., 1., 1.+1e-8, 50.+1e-8]) == [[1, 2], [0, 3]]


def test_grouping_does_not_chain_unresolved_neighbors():
    assert frequency_groups([0., .75, 1.5], tolerance=1.) == [[0, 1], [2]]
    with pytest.raises(ValueError):
        frequency_groups([np.nan])


def test_character_and_leakage_are_basis_invariant():
    action = np.diag([1., -1., 2.])
    pair = np.eye(3)[:, :2]
    q, _ = np.linalg.qr(np.array([[1., 2.], [3., 4.]]))
    assert max(representation_errors(pair @ q, [action], [0.])) < 1e-12
    assert representation_errors(pair, [action], [2.])[1] == 2.
