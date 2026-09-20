import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_moment_interpolation import moment_correct


def test_mass_shell_moments_reproduced_with_signed_coefficients():
    axes=np.r_[np.eye(3),-np.eye(3)]
    p=np.r_[axes,2*axes]; e=np.sqrt(1+np.sum(p*p,axis=1))
    b=np.column_stack((np.ones(12),e,p)); t=np.array([[1.,1.,0.,0.,0.]])
    seed=np.full((12,1),1/12)
    s,report=moment_correct(seed,b,t)
    np.testing.assert_allclose(s.T@b,t,atol=1e-14)
    assert report["minimum_coefficient"]<0
    # Minimum-norm correction lies in the row space; no nullspace component.
    delta=(s-seed)[:,0]
    np.testing.assert_allclose(delta,b@np.linalg.lstsq(b,delta,rcond=None)[0],atol=1e-14)


def test_rank_deficiency_rejected_without_expanding_support():
    with pytest.raises(ValueError,match="rank-deficient"):
        moment_correct(np.full((3,1),1/3),np.ones((3,5)),np.ones((1,5)))


def test_existing_exact_mapping_unchanged():
    b=np.array([[1.,0.],[1.,1.],[1.,2.]])
    seed=np.array([[.25],[.5],[.25]])
    s,_=moment_correct(seed,b,seed.T@b)
    np.testing.assert_array_equal(s,seed)
