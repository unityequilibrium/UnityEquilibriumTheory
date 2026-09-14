import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_quadratic_source_averaging import source_average


def test_zero_mean_does_not_remove_local_source():
    r=source_average([[1.,0.],[-1.,0.]],[.5,.5])
    assert r['source_of_mean']==0
    assert r['local_source_average']==pytest.approx(.2)
    assert r['identity_error']<1e-14


def test_uniform_null_and_allowed_coupling():
    for eps in (0.,.5,1.):
        r=source_average([[.3,.2],[-.4,.8]],[.2,.8],epsilon=eps)
        assert r['identity_error']<1e-14
    r=source_average([[.3,.2],[.3,.2]],[.2,.8])
    assert r['unresolved_variance']<1e-30


def test_component_rotation_invariance():
    chi=np.array([[.2,.3],[-.4,.1],[.6,-.2]])
    rotation=np.array([[0.,-1.],[1.,0.]])
    a=source_average(chi,[.2,.3,.5]); b=source_average(chi@rotation,[.2,.3,.5])
    assert a['local_source_average']==pytest.approx(b['local_source_average'])
    assert a['unresolved_variance']==pytest.approx(b['unresolved_variance'])


def test_invalid_weight_rejected_not_renormalized():
    for weights in ([.4,.4],[-.2,1.2],[np.nan,.5]):
        with pytest.raises(ValueError):source_average([[1.,0.],[-1.,0.]],weights)
    with pytest.raises(ValueError):source_average([[1.,0.],[-1.,0.]],[.5,.5],epsilon=-.5)
