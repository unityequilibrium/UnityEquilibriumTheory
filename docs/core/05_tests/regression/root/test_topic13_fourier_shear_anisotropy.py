import numpy as np
from docs.scripts.audit.audit_topic13_fourier_shear_anisotropy import potential,gradient,scan,K


def test_stationary_hessian_and_gradient():
    np.testing.assert_allclose(gradient(0.,0.),0,atol=1e-14)
    h=1e-5
    for x,y in ((.02,.03),(-.01,.04)):
        numeric=[(potential(x+h,y)-potential(x-h,y))/(2*h),(potential(x,y+h)-potential(x,y-h))/(2*h)]
        np.testing.assert_allclose(gradient(x,y),numeric,rtol=1e-7)
    np.testing.assert_allclose((gradient(h,0)-gradient(-h,0))/(2*h),[3*K*K,0],atol=1e-8)


def test_cubic_remainder_scaling():
    a,b=scan(.002),scan(.001)
    assert 3.9<a["sampled_after_cubic_ratio"]/b["sampled_after_cubic_ratio"]<4.1
    assert abs(b["sampled_full_force_ratio"]/b["leading_force_ratio"]-1)<.01
