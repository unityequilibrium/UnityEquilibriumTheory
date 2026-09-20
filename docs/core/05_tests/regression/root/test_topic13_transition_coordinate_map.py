import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_transition_coordinate_map import coordinate_rows, manufactured_case


def test_manufactured_weight_change_is_not_physical_change():
    r=manufactured_case()
    assert r["coordinate_amplitude"] == pytest.approx(r["expected_channel_amplitude"])
    assert r["legacy_amplitude"] != pytest.approx(r["expected_channel_amplitude"])
    assert r["coordinate_constant_defect"] == pytest.approx(0,abs=1e-14)
    assert abs(r["legacy_constant_defect"]) > .1


def test_rectangular_pullback_preserves_transition_quadratic_form():
    s=np.array([[.2,.5],[.3,.1],[.5,.4]])
    we=np.array([2.,7.]); wb=np.array([3.,5.,11.])
    v=np.array([[2.,-1.],[1.,3.]])
    rates=np.diag([.4,2.])
    z=np.array([1.,-2.,3.])
    exact_z=np.sqrt(we)*(s.T@(z/np.sqrt(wb)))
    rows=coordinate_rows(v,s,we,wb)
    np.testing.assert_allclose(rows@z,v@exact_z,rtol=1e-14)
    assert z@rows.T@rates@rows@z == pytest.approx(exact_z@v.T@rates@v@exact_z)


def test_exact_weight_reparameterization_cancels():
    incidence=np.array([[1.,1.,-1.,-1.]])
    wb=np.array([1.,4.,9.,16.])
    results=[]
    for we in (wb,wb*100):
        results.append(coordinate_rows(incidence/np.sqrt(we),np.eye(4),we,wb))
    np.testing.assert_allclose(*results,rtol=1e-14)


def test_invalid_weights_rejected():
    with pytest.raises(ValueError):
        coordinate_rows(np.ones((1,2)),np.eye(2),[1.,0.],[1.,2.])
