import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_composite_alpha_design import design, log_alpha_variance, TARGET


def test_product_identified_without_individual_factors():
    A=np.array([[0,0,0,1],[1,1,1,0]])
    r=design(A)
    assert r["alpha_magnitude_identifiable"]
    assert not r["individual_factors_identifiable"]
    np.testing.assert_allclose(np.array(r["null_directions"])@TARGET,0,atol=1e-12)
    np.testing.assert_allclose(A.T@r["measurement_combination"],TARGET,atol=1e-12)


def test_missing_chi_and_normalized_shape_do_not_identify_alpha():
    assert not design([[0,0,0,1],[0,1,1,0]])["alpha_magnitude_identifiable"]
    assert not design([[0,0,0,0]])["alpha_magnitude_identifiable"]


def test_correlated_uncertainty_not_independent_default():
    covariance=np.array([[.04,.015],[.015,.01]])
    assert log_alpha_variance([-1,1],covariance)==pytest.approx(.02)
    assert log_alpha_variance([-1,1],np.diag([.04,.01]))==pytest.approx(.05)
    with pytest.raises(ValueError):
        log_alpha_variance([-1,1],[[1,2],[2,1]])
