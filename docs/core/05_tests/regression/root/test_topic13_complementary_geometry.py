import numpy as np
from docs.scripts.audit.audit_topic13_complementary_geometry import reciprocal_design
from docs.scripts.audit.audit_topic13_energy_identifiability import observable_null_test


def test_design_is_nested_and_has_no_duplicate_rows():
    a, b = reciprocal_design([0]), reciprocal_design([0, 1])
    assert len(a) == 24 and len(b) == 49
    assert set(map(tuple, a)) < set(map(tuple, b))
    assert len(set(map(tuple, b))) == len(b)


def test_complementary_not_duplicate_row_resolves_energy():
    assert not observable_null_test([[1, 1], [2, 2]], [1, 2])['identifiable_at_numerical_tolerance']
    assert observable_null_test([[1, 1], [1, 2]], [1, 2])['identifiable_at_numerical_tolerance']


def test_positive_row_rescaling_preserves_exact_row_space():
    a = np.array([[1., 1, 0], [0, 1, 1]])
    c = [1, 2, 1]
    assert observable_null_test(a, c)['identifiable_at_numerical_tolerance']
    assert observable_null_test(a*np.array([2, 3])[:, None], c)['identifiable_at_numerical_tolerance']
