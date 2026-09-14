import numpy as np
from docs.scripts.audit.audit_topic13_matter_actuation_harmonics import measure


def test_zero_background_quadratic_source():
    a=measure(0.,.1); b=measure(0.,.05)
    assert abs(a["dc_fundamental_second_harmonic"][1])<1e-16
    np.testing.assert_allclose(np.array(a["dc_fundamental_second_harmonic"])[[0,2]],
                               4*np.array(b["dc_fundamental_second_harmonic"])[[0,2]],rtol=1e-13)


def test_background_linear_and_nonlinear_harmonics():
    for b in (-.4,.4):
        r=measure(b,.1)
        np.testing.assert_allclose(r["dc_fundamental_second_harmonic"],r["expected"],atol=1e-15)


def test_gr_null_kept_regular():
    r=measure(.4,.1,epsilon=0.)
    assert r["dc_fundamental_second_harmonic"]==[0.,0.,0.]
