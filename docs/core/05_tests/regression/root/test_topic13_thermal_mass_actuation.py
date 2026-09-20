import pytest
from docs.scripts.audit.audit_topic13_thermal_mass_actuation import equilibrium,response


def test_implicit_response_and_refinement():
    r=response()
    errors=[]
    for h in (.01,.005,.0025):
        value=(equilibrium(h)-equilibrium(-h))/(2*h)
        errors.append(abs(value/r["mass_gain"]-1))
    assert errors[2]<errors[1]<errors[0]
    assert errors[2]<1e-5
    assert equilibrium(0.)==pytest.approx(0.,abs=1e-13)


def test_thermal_variance_drive_and_zero_coupling():
    h=.0025
    gain=(equilibrium(0.,h)-equilibrium(0.,-h))/(2*h)
    assert gain==pytest.approx(response()["temperature_gain"],rel=1e-4)
    assert response(eta=0.)["mass_gain"]==0.
    assert equilibrium(.01,eta=0.)==0.


def test_unstable_reference_rejected():
    with pytest.raises(ValueError):
        response(curvature=1e-8)
