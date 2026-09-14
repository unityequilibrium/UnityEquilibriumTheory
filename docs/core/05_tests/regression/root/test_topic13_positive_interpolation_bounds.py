import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_positive_interpolation_bounds import positive_bounds


def inputs():
    p=np.array([[-1.,0.,0.],[1.,0.,0.]])
    return np.full((2,2),.5),p,np.full(2,np.sqrt(2)),np.array([[0.,0.,0.],[.2,.1,0.]]),np.array([1.,np.sqrt(1.05)])


def test_local_and_signed_channel_bounds():
    r=positive_bounds(*inputs(),1.,np.array([[1.,-1.],[2.,1.]]),[1.,3.])
    assert r["max_leg_bound_violation"]==0
    assert r["max_channel_bound_violation"]==0
    assert np.all(np.array(r["rate_weighted_channel_error_rms"])<=r["rate_weighted_channel_bound_rms"])


def test_bound_rejects_signed_interpolation():
    s,p,e,tp,te=inputs();s[:,0]=[-1.,2.]
    with pytest.raises(ValueError,match="positive normalized"):
        positive_bounds(s,p,e,tp,te,1.,[[1.,-1.]],[1.])


def test_exact_nodes_have_zero_radius_and_error():
    _,p,e,_,_=inputs()
    r=positive_bounds(np.eye(2),p,e,p,e,1.,[[1.,-1.]],[1.])
    assert r["radius_max"]==0
    np.testing.assert_array_equal(r["leg_error_rms"],[0.,0.])


def test_nearly_normalized_weights_include_constant_defect():
    _,p,e,_,_=inputs()
    r=positive_bounds(np.eye(2)*(1+5e-14),p,e,p,e,1.,[[1.,-1.]],[1.])
    assert r["normalization_defect_max"]>0
    assert r["leg_bound_rms"][1]>0
    assert r["max_leg_bound_violation"]<1e-15
