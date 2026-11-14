"""Independent action derivatives, Bose-series and stationary thermodynamics."""
from dataclasses import replace
from math import pi
import numpy as np
import pytest
from scipy.special import kve
from docs.scripts.audit import audit_topic13_normal_thermal_background as a

CFG=a.MixtureInputs()


@pytest.mark.parametrize("m2,T,mu,charges",[(1.,.25,.2,(-1,1)),(.5,.5,0.,(0,)),(2.4,1.,.1,(-1,1))])
def test_thermal_integrals_against_bessel_series(m2,T,mu,charges):
    r=a.thermal_terms(m2,T,mu,charges,order=256,cutoff_factor=80.)
    m=np.sqrt(m2); ell=np.arange(1,513,dtype=float); z=ell*m/T
    pressure=tadpole=second=0.
    for q in charges:
        factor=np.exp(-ell*(m-q*mu)/T)
        pressure+=m2*T*T/(2*pi*pi)*np.sum(factor*kve(2,z)/ell**2)
        tadpole+=m*T/(4*pi*pi)*np.sum(factor*kve(1,z)/ell)
        second+=-1/(8*pi*pi)*np.sum(factor*kve(0,z))
    assert -r["omega"]==pytest.approx(pressure,rel=1e-10)
    assert r["tadpole"]==pytest.approx(tadpole,rel=1e-10)
    assert r["mass_second"]==pytest.approx(second,rel=1e-10)


@pytest.mark.parametrize("x",[0.,.03,.2])
@pytest.mark.parametrize("z,k,eps",[(1.,1.,1.),(.25,4.,.5),(4.,9.,4.)])
def test_background_hessian_and_induced_cubic_from_production(x,z,k,eps):
    cfg=replace(CFG,z=z,mass_squared=z,quartic=CFG.coupling*z*z,
        epsilon=eps,response_kinetic=k,response_mass_squared=.5*k,
        response_coupling=CFG.cubic*z*np.sqrt(k/eps),
        response_quartic=CFG.neutral_quartic*eps*k*k)
    b=a.canonical_background(x,cfg)
    h=.01; v=lambda y:a.production_potential(y,[0.,0.],cfg)
    first=(v(x-2*h)-8*v(x-h)+8*v(x+h)-v(x+2*h))/(12*h)
    second=(-v(x+2*h)+16*v(x+h)-30*v(x)+16*v(x-h)-v(x-2*h))/(12*h*h)
    third=(v(x+2*h)-2*v(x+h)+2*v(x-h)-v(x-2*h))/(2*h**3)
    assert first==pytest.approx(b["tree_force"],abs=1e-12)
    assert second==pytest.approx(b["response_tree_mass_squared"],abs=1e-10)
    assert third==pytest.approx(b["response_tree_cubic"],abs=1e-9)
    w=lambda y:a.production_potential(x,[y,0.],cfg)
    matter_second=(-w(2*h)+16*w(h)-30*w(0)+16*w(-h)-w(-2*h))/(12*h*h)
    assert matter_second==pytest.approx(b["matter_mass_squared"],abs=1e-10)


@pytest.mark.parametrize("x,T",[(.01,.25),(.2,.5),(-.03,1.)])
def test_effective_force_and_hessian_are_derivatives(x,T):
    h=1e-4
    f=lambda y:a.effective_state(y,T)
    first=(f(x-2*h)["omega"]-8*f(x-h)["omega"]+8*f(x+h)["omega"]-f(x+2*h)["omega"])/(12*h)
    second=(f(x+h)["force"]-f(x-h)["force"])/(2*h)
    assert first==pytest.approx(f(x)["force"],rel=1e-8,abs=1e-11)
    assert second==pytest.approx(f(x)["static_response_curvature"],rel=1e-6)


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
def test_stationarity_and_envelope(T):
    s=a.stationary_state(T)
    assert s["phi_c"]>0 and s["unshifted_force"]<0
    assert abs(s["force"])<1e-10
    assert s["static_response_curvature"]>0
    assert s["normal_gap"]>0
    assert s["pressure_shift"]>0
    assert s["susceptibility_backreaction"]>0
    w=a.derivative_witness(s)
    for key in ("charge_envelope_relative_error","entropy_envelope_relative_error",
                "susceptibility_relative_error","dphi_dmu_relative_error"):
        assert w[key]<1e-4
    assert w["independent_minimum_success"]
    assert w["independent_minimum_relative_error"]<1e-3
    assert abs(w["energy_identity_residual"])<1e-10


def test_zero_temperature_and_decoupled_response():
    cold=a.stationary_state(T=0.)
    assert cold["phi_c"]==0 and cold["pressure"]==0
    assert cold["entropy_density"]==0 and cold["charge_density"]==0
    detached=a.stationary_state(cfg=replace(CFG,response_coupling=0.))
    assert detached["phi_c"]==0 and detached["unshifted_force"]==0
    assert detached["susceptibility_backreaction"]==0
    assert detached["static_response_curvature"]>CFG.response_mass_sq


def test_charge_conjugation():
    positive=a.stationary_state(mu=.2); negative=a.stationary_state(mu=-.2)
    for key in ("phi_c","pressure","entropy_density","energy_density","stationary_charge_susceptibility"):
        assert positive[key]==pytest.approx(negative[key],rel=1e-12)
    assert positive["charge_density"]==pytest.approx(-negative["charge_density"])
    assert positive["dphi_dmu"]==pytest.approx(-negative["dphi_dmu"])


def test_energy_dimension_covariance():
    scale=2.
    cfg=replace(CFG,mass_squared=CFG.mass_squared*scale**2,
        response_mass_squared=CFG.response_mass_squared*scale**2,response_coupling=CFG.response_coupling*scale)
    base=a.stationary_state(); new=a.stationary_state(T=.25*scale,mu=.2*scale,cfg=cfg)
    for key,dimension in (("phi_c",1),("pressure",4),("charge_density",3),("entropy_density",3),
                          ("static_response_curvature",2),("stationary_charge_susceptibility",2)):
        assert new[key]==pytest.approx(base[key]*scale**dimension,rel=1e-10)


def test_canonical_field_rescaling():
    cfg=replace(CFG,z=4.,mass_squared=4.,quartic=CFG.coupling*16.,
        epsilon=.5,response_kinetic=9.,response_mass_squared=4.5,
        response_coupling=CFG.cubic*4*np.sqrt(9/.5),response_quartic=CFG.neutral_quartic*.5*81)
    base=a.stationary_state(); new=a.stationary_state(cfg=cfg)
    for key in ("phi_c","pressure","charge_density","static_response_curvature"):
        assert new[key]==pytest.approx(base[key],rel=1e-11)
    assert new["Phi_natural_displacement"]==pytest.approx(base["phi_c"]/np.sqrt(.5*9))


def test_quadrature_and_cutoff_convergence():
    values=[a.stationary_state(order=n,cutoff_factor=c)["phi_c"] for n,c in a.GRIDS]
    assert max(abs(b/aa-1) for aa,b in zip(values,values[1:]))<1e-5


@pytest.mark.parametrize("kwargs",[{"T":-1},{"T":float("nan")},{"mu":1.},{"mu":float("nan")},
                                   {"order":3},{"order":True},{"cutoff_factor":1}])
def test_invalid_normal_domain_rejected(kwargs):
    with pytest.raises(ValueError):
        a.stationary_state(**kwargs)


def test_positive_bose_gap_is_not_clipped():
    with pytest.raises(ValueError,match="gap"):
        a.effective_state(6.)


@pytest.mark.parametrize("T",[.25,.5,1.])
def test_shifted_tree_vertices_and_mass_only_omission(T):
    state=a.stationary_state(T)
    b=state["background"]; G=CFG.cubic; H=b["response_tree_cubic"]
    m2,M2=b["matter_mass_squared"],b["response_tree_mass_squared"]
    s,t,u=8.,-.7,-2.
    expected=G*G*(1/(t-m2)+1/(u-m2))-G*H/(s-M2)
    assert a.shifted_tree_amplitude(s,t,u,(1,-1,0,0),state)==pytest.approx(expected)
    expected=6*CFG.neutral_quartic+H*H*(1/(s-M2)+1/(t-M2)+1/(u-M2))
    assert a.shifted_tree_amplitude(s,t,u,(0,0,0,0),state)==pytest.approx(expected)
    assert a.shifted_tree_amplitude(s,t,u,(1,1,0,0),state)==0
    witness=a.shifted_vertex_witness(state)
    assert len(witness["rows"])==9
    assert all(row["analytic_relative_error"]<1e-10 for row in witness["rows"])
    assert all(row["missing_exchange_term"]!=0 for row in witness["rows"])


def test_zero_shift_reproduces_preceding_collision_amplitudes():
    from docs.scripts.audit.audit_topic13_coupled_gain_loss_operator import CHANNELS,channel_amplitude
    state=a.stationary_state(T=0.)
    for _,q in CHANNELS:
        assert a.shifted_tree_amplitude(8.,-.5,-2.,q,state)==pytest.approx(channel_amplitude(8.,-.5,-2.,q,CFG))


def test_shifted_pole_is_not_regularized():
    state=a.stationary_state()
    with pytest.raises(ValueError,match="pole"):
        a.shifted_tree_amplitude(state["background"]["response_tree_mass_squared"],-.5,-2.,(1,-1,0,0),state)


def test_small_coupling_response_from_implicit_function():
    at_zero=a.effective_state(0.,cfg=replace(CFG,response_coupling=0.))
    analytic=at_zero["matter"]["tadpole"]/at_zero["static_response_curvature"]
    values=[a.stationary_state(cfg=replace(CFG,response_coupling=g))["phi_c"]/g for g in (.2,.1,.05)]
    errors=[abs(v/analytic-1) for v in values]
    assert errors[2]<errors[1]<errors[0]
    assert errors[-1]<1e-5
    state=a.stationary_state()
    assert state["linearized_background_estimate"]==pytest.approx(state["phi_c"],rel=1e-5)
