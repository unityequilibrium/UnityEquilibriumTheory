import numpy as np
from docs.scripts.audit.audit_topic13_channel_error_attribution import attribute


def test_signed_contributions_reconstruct_matrix_and_witness():
    a=np.array([[1.,0.],[0.,1.],[1.,1.]])
    b=np.array([[.5,0.],[0.,1.5],[1.,.8]])
    r=attribute(a,b,[1.,2.,3.])
    expected=b.T@np.diag([1/6,2/6,3/6])@b-a.T@np.diag([1/6,2/6,3/6])@a
    np.testing.assert_allclose(r["delta"].sum(axis=0),expected,atol=1e-14)
    assert r["reconstruction_residual"]<1e-14


def test_common_rate_scaling_does_not_change_normalized_attribution():
    a=np.eye(2); b=2*a
    r=attribute(a,b,[1.,3.]); scaled=attribute(a,b,[1e-20,3e-20])
    np.testing.assert_allclose(r["contributions"],scaled["contributions"])
    assert abs(r["rate_concentration_inverse_sum_squares"]-1.6)<1e-14
