import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_heat_charge_frame_map import linear_frame_entropy


def test_linear_entropy_frame_identity_needs_convective_shift():
    t,mu,n,s=.5,.2,.7,.8
    h=mu+t*s/n
    row=linear_frame_entropy(t,mu,n,s,h,[1.e-5,2.e-5,0.])
    assert row["relative_entropy_frame_residual"]<1.e-12
    assert not np.allclose(row["raw_heat_over_T_is_not_landau_entropy"],row["landau_entropy_spatial"],atol=1.e-12)


def test_wrong_enthalpy_breaks_identity():
    row=linear_frame_entropy(.5,.2,.7,.8,2.,[1.e-5,0.,0.])
    assert row["relative_entropy_frame_residual"]>.1


def test_zero_charge_has_no_eckart_map():
    with pytest.raises(ValueError):
        linear_frame_entropy(.5,.2,0.,.8,2.,[1.e-5,0.,0.])
