import numpy as np
from docs.scripts.audit.audit_topic13_e2g_nonlinear_symmetry import cubic,invariant_dimension,e2_group,rotation


def test_counts():
    assert [invariant_dimension(d,e2_group()) for d in range(1,7)]==[0,1,1,1,1,2]
    assert [invariant_dimension(d,[rotation(np.sqrt(2.))]) for d in range(1,7)]==[0,1,0,1,0,1]


def test_cubic_and_noncontinuous_rotation():
    p=np.array([[1.,0.],[.3,.8]])
    for g in e2_group():
        np.testing.assert_allclose(cubic(p@g.T),cubic(p),atol=1e-13)
    assert np.max(abs(cubic(p@rotation(np.pi/6).T)-cubic(p)))>.1


def test_torque_derivative():
    theta=.27; h=1e-5
    V=lambda t:.4*.6**3*np.cos(3*t)
    np.testing.assert_allclose(-(V(theta+h)-V(theta-h))/(2*h),3*.4*.6**3*np.sin(3*theta),rtol=1e-8)
