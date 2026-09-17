import numpy as np
from docs.scripts.audit.audit_topic13_energy_identifiability import observable_null_test


def test_rank_deficiency_does_not_prevent_sum_observation():
    result = observable_null_test([[1, 1]], [1, 1])
    assert result['rank'] == 1
    assert result['identifiable_at_numerical_tolerance']


def test_energy_witness_is_positive_and_indistinguishable():
    a = np.array([[1., 1.]])
    result = observable_null_test(a, [1, 2])
    w = result['synthetic_witness']
    assert min(w['n_plus']+w['n_minus']) >= .75
    np.testing.assert_allclose(a @ np.array(w['n_plus']), a @ np.array(w['n_minus']))
    assert w['energy_difference'] > 0


def test_invisible_mode_energy_and_full_rank():
    assert not observable_null_test([[1, 0]], [1, 1])['identifiable_at_numerical_tolerance']
    assert observable_null_test(np.eye(2), [1, 2])['identifiable_at_numerical_tolerance']
