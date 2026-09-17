"""Independent action, counting and symmetry tests for the elastic pilot."""
from dataclasses import replace
from math import pi
import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs, amplitude, differential_cross_section, tagged_loss_rates,
    cubic_from_production_potential,
)


@pytest.mark.parametrize("z,k,eps", [(1.,1.,1.),(.25,4.,.5),(4.,9.,4.)])
def test_canonical_field_covariance_and_production_cubic(z,k,eps):
    base=ActionInputs()
    other=replace(base,z=z,mass_squared=z,quartic=base.coupling*z*z,
                  epsilon=eps,response_kinetic=k,response_mass_squared=.5*k,
                  response_coupling=base.cubic*z*np.sqrt(k/eps))
    assert cubic_from_production_potential(other)==pytest.approx(base.cubic,rel=1e-12)
    for charges in ((1,1,1,1),(1,-1,1,-1)):
        np.testing.assert_allclose(amplitude(8.,np.array([-.8,0.,.6]),charges,other),
                                   amplitude(8.,np.array([-.8,0.,.6]),charges,base),rtol=1e-12)


@pytest.mark.parametrize("charges", [(1,1,1,1),(-1,-1,-1,-1),(1,-1,1,-1),(-1,1,-1,1)])
def test_contact_amplitude_and_phase_space(charges):
    cfg=ActionInputs(response_coupling=0.)
    x,w=np.polynomial.legendre.leggauss(24)
    np.testing.assert_allclose(amplitude(8.,x,charges,cfg),4*cfg.coupling,rtol=1e-12)
    sigma=2*pi*np.dot(w,differential_cross_section(8.,x,charges,cfg))
    divisor=2 if charges[2]==charges[3] else 1
    # Invariant two-body phase space / incident flux at s=8, m=1.
    beta=np.sqrt(1-4*cfg.mass**2/8.)
    phase_space=beta/(8*pi)
    flux=2*8.*beta
    expected=(4*cfg.coupling)**2*phase_space/(flux*divisor)
    assert sigma==pytest.approx(expected,rel=1e-12)


@pytest.mark.parametrize("x", [-.9,0.,.7])
def test_crossing_and_charge_conjugation(x):
    cfg=ActionInputs()
    original=amplitude(8.,x,(1,-1,1,-1),cfg)
    assert amplitude(8.,-x,(1,-1,-1,1),cfg)==pytest.approx(original)
    assert amplitude(8.,x,(-1,1,-1,1),cfg)==pytest.approx(original)
    assert amplitude(8.,x,(1,1,-1,-1),cfg)==0.


def test_exchange_interference_matches_static_elimination_limit():
    cfg=ActionInputs()
    expected=4*cfg.coupling-2*cfg.cubic**2/cfg.response_mass_sq
    assert amplitude(4*cfg.mass**2+1e-9,0.,(1,1,1,1),cfg)==pytest.approx(expected,rel=1e-8)


def test_no_ad_hoc_resonant_regularization():
    with pytest.raises(ValueError,match="resummed"):
        amplitude(8.,0.,(1,-1,1,-1),ActionInputs(response_mass_squared=8.))


def test_incoming_and_outgoing_geometry_agree_with_explicit_boost():
    from docs.core.uet_o2_action_derived_transition_kernel import _boost_from_center_of_mass
    m,k,p,c=1.,1.,.8,.3
    e1,e2=np.sqrt(k*k+m*m),np.sqrt(p*p+m*m)
    v1=np.array([0.,0.,k]); v2=np.array([p*np.sqrt(1-c*c),0.,p*c])
    total=e1+e2; beta=(v1+v2)/total
    s=total*total-np.dot(v1+v2,v1+v2); ps=np.sqrt(s/4-m*m); gamma=total/np.sqrt(s)
    _, incoming_star=_boost_from_center_of_mass(e1,v1,-beta)
    axis=incoming_star/ps
    transverse=beta-np.dot(beta,axis)*axis
    transverse=transverse/np.linalg.norm(transverse)
    side=np.cross(axis,transverse)
    out_cos,az=.4,.7
    direction=out_cos*axis+np.sqrt(1-out_cos*out_cos)*(np.cos(az)*transverse+np.sin(az)*side)
    energy3,momentum3=_boost_from_center_of_mass(np.sqrt(s)/2,ps*direction,beta)
    energy4,momentum4=_boost_from_center_of_mass(np.sqrt(s)/2,-ps*direction,beta)
    bpar=gamma*(beta[2]*k-np.dot(beta,beta)*e1)/ps
    btrans=abs(beta[0]*k)/ps
    analytic=total/2+gamma*ps*(bpar*out_cos+btrans*np.sqrt(1-out_cos*out_cos)*np.cos(az))
    assert energy3==pytest.approx(analytic,rel=1e-12)
    assert energy3+energy4==pytest.approx(total)
    np.testing.assert_allclose(momentum3+momentum4,v1+v2,rtol=1e-12,atol=1e-12)
    assert energy3**2-np.dot(momentum3,momentum3)==pytest.approx(m*m)


@pytest.mark.parametrize("quantum", [False,True])
def test_tagged_rates_charge_conjugation_and_detailed_balance(quantum):
    controls=dict(radial_order=12,incoming_order=8,outgoing_order=8,azimuth_order=8,cutoff=10.,final_bose=quantum)
    positive=tagged_loss_rates(mu=.2,**controls)
    negative=tagged_loss_rates(mu=-.2,**controls)
    np.testing.assert_allclose(positive["rates"],negative["rates"][::-1],rtol=1e-12)
    assert positive["max_detailed_balance_relative_error"]<1e-10
    assert all(value>0 for value in positive["rates"])


def test_contact_mu_zero_rate_is_twelve_times_legacy_comparator():
    from docs.core.uet_o2_kinetic_collision_kubo import _collision_width
    cfg=ActionInputs(response_coupling=0.)
    r,w=np.polynomial.legendre.leggauss(24); r,w=6*(r+1),6*w
    x,xw=np.polynomial.legendre.leggauss(16)
    old=_collision_width(1.,1.,.25,cfg.mass,0.,cfg.coupling,r,w,x,xw)
    new=tagged_loss_rates(cfg,mu=0.,radial_order=24,incoming_order=16,
                         outgoing_order=8,azimuth_order=8,cutoff=12.,final_bose=False)
    np.testing.assert_allclose(new["rates"],12*old,rtol=1e-12)


def test_quartic_derivative_tracks_production_potential(monkeypatch):
    from docs.scripts.audit import audit_topic13_action_normalized_elastic_scattering as audit
    cfg=ActionInputs()
    assert audit.quartic_from_production_potential(cfg)==pytest.approx(cfg.coupling)
    original=audit.matter_potential
    monkeypatch.setattr(audit,"matter_potential",lambda field,mc:2*original(field,mc))
    assert audit.quartic_from_production_potential(cfg)==pytest.approx(2*cfg.coupling)
