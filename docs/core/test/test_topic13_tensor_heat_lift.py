import numpy as np
import pytest
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    _covariant_tensor_entropy_heat_flux, lorentz_boost_x,
)


def inputs():
    tensor=np.zeros((4,4))
    tensor[1:,1:]=[[2.,.3,0.],[.3,5.,.2],[0.,.2,3.]]
    return np.diag([-1.,1.,1.,1.]),np.array([1.,0.,0.,0.]),tensor,np.array([0.,.4,-.2,.7])


def test_anisotropic_response_is_not_scalar_average():
    metric,u,k,x=inputs()
    result=_covariant_tensor_entropy_heat_flux(metric,u,.22,1.,k,x)
    np.testing.assert_allclose(result["heat_flux_contravariant"],k@x)
    assert result["entropy_production"]==pytest.approx(x@k@x/.22)
    assert not np.allclose(k@x,np.trace(k)/3*x)


@pytest.mark.parametrize("speed",[-.6,.37,.7])
def test_anisotropic_tensor_boost(speed):
    metric,u,k,x=inputs()
    base=_covariant_tensor_entropy_heat_flux(metric,u,.22,1.,k,x)
    boost=lorentz_boost_x(speed)
    other=_covariant_tensor_entropy_heat_flux(metric,boost@u,.22,1.,boost@k@boost.T,np.linalg.inv(boost).T@x)
    np.testing.assert_allclose(other["heat_flux_contravariant"],boost@base["heat_flux_contravariant"],atol=1.e-12)
    assert other["entropy_production"]==pytest.approx(base["entropy_production"])


def test_invalid_tensor_is_rejected_not_clipped():
    metric,u,k,x=inputs()
    for invalid in (np.diag([0.,-1.,1.,1.]),np.eye(4),np.ones((3,3))):
        with pytest.raises(ValueError):
            _covariant_tensor_entropy_heat_flux(metric,u,.22,1.,invalid,x)
