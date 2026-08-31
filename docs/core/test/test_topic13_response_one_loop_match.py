"""Independent one-loop vacuum, Matsubara, spectral and thermal witnesses."""
from dataclasses import replace
from math import pi, sqrt
import mpmath as mp
import numpy as np
import pytest
from scipy.integrate import quad
from docs.scripts.audit import audit_topic13_response_one_loop_match as a

CFG=a.CFG


@pytest.mark.parametrize("degree",[2,4])
@pytest.mark.parametrize("r",[-.8,-.2,-.01,-1e-8,1e-8,.01,.2,1.])
def test_remainder_against_high_precision_derivatives(r,degree):
    with mp.workdps(100):
        x=mp.mpf(r)
        f=lambda z:(1+z)**2*mp.log(1+z)
        polynomial=mp.taylor(f,0,degree)
        remainder=lambda z:f(z)-sum(c*z**n for n,c in enumerate(polynomial))
        expected=[float(mp.diff(remainder,x,n)) for n in range(3)]
    assert a.vacuum_remainder(r,degree)==pytest.approx(expected,rel=2e-11,abs=1e-65)


@pytest.mark.parametrize("x",[-.3,-.01,.01,.3])
@pytest.mark.parametrize("reference_scale",[.3,2.])
def test_vacuum_axis_against_independent_cw_taylor(x,reference_scale):
    with mp.workdps(90):
        m2=mp.mpf(CFG.mass**2); M2=mp.mpf(CFG.response_mass_sq)
        G=mp.mpf(CFG.cubic); lam=mp.mpf(CFG.neutral_quartic)
        scale=mp.mpf(reference_scale)
        def cw(y):
            charged=m2-G*y; neutral=M2+3*lam*y*y
            term=lambda z:z*z*(mp.log(z/scale**2)-mp.mpf("1.5"))
            return (2*term(charged)+term(neutral))/(64*mp.pi**2)
        coeffs=mp.taylor(cw,0,4)
        ren=lambda y:cw(y)-sum(c*y**n for n,c in enumerate(coeffs))
        expected=[float(mp.diff(ren,mp.mpf(x),n)) for n in range(3)]
    actual=a.vacuum_axis(x)
    assert [actual[k] for k in ("potential","force","curvature")]==pytest.approx(expected,rel=2e-10,abs=1e-30)


@pytest.mark.parametrize("s",[-2.,-.1,.01,.5,2.,3.8])
def test_vacuum_retarded_independent_radial_and_spectral_dispersion(s):
    m=CFG.mass; G=CFG.cubic
    def radial(p):
        E=sqrt(p*p+m*m); d=4*E*E
        return -G*G*p*p/(2*pi*pi)*s*s/(E*d*d*(d-s))
    # Twice-subtracted causal dispersion: Im Pi(s') = -rho(s')/2.
    def spectral(t):
        rho=G*G/(8*pi)*sqrt(1-4*m*m/t)
        return -rho/(2*pi)*s*s/(t*t*(t-s))
    momentum=quad(radial,0,np.inf,epsabs=1e-14,epsrel=1e-10)[0]
    dispersion=quad(spectral,4*m*m,np.inf,epsabs=1e-14,epsrel=1e-10)[0]
    value,derivative=a.vacuum_retarded(s)
    assert value==pytest.approx(momentum,rel=2e-9,abs=1e-14)
    assert value==pytest.approx(dispersion,rel=2e-9,abs=1e-14)
    h=1e-5
    fd=(a.vacuum_retarded(s+h)[0]-a.vacuum_retarded(s-h)[0])/(2*h)
    assert derivative==pytest.approx(fd,rel=1e-7,abs=1e-13)


@pytest.mark.parametrize("T,mu",[(.1,.2),(.25,.2),(.25,-.2),(1.,.8)])
def test_matsubara_nonzero_and_static_occupation_term(T,mu):
    result=a.matsubara_witness(E=1.3,T=T,mu=mu,cutoff=8192)
    assert max(r["relative_error"] for r in result["rows"])<1e-9
    zero=result["rows"][0]
    E=1.3
    fplus=1/np.expm1((E-mu)/T); fminus=1/np.expm1((E+mu)/T)
    pair_only=(1+fplus+fminus)/(4*E**3)
    assert zero["analytic"]>pair_only
    population=(fplus*(1+fplus)+fminus*(1+fminus))/(4*T*E*E)
    assert zero["analytic"]-pair_only==pytest.approx(population,rel=1e-10)


def test_matsubara_tail_converges_without_adjusting_tolerance():
    coarse=a.matsubara_witness(cutoff=64)
    fine=a.matsubara_witness(cutoff=256)
    for c,f in zip(coarse["rows"],fine["rows"]):
        assert f["relative_error"]<c["relative_error"]/30


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
def test_static_dynamic_match_and_strict_pole(T):
    pole=a.response_pole(T)
    assert pole["static_dynamic_gap"]==pytest.approx(pole["population_term"],rel=1e-8,abs=1e-15)
    assert pole["population_term"]>0
    strict=CFG.response_mass_sq+pole["kernel_at_tree_pole"]["self_energy"]
    assert pole["strict_one_loop_pole_squared"]==strict
    root=pole["partial_Dyson_pole_squared"]
    assert root-CFG.response_mass_sq-pole["kernel_at_Dyson_pole"]["self_energy"]==pytest.approx(0,abs=1e-12)
    assert 0<pole["pole_residue"]<=1
    assert pole["one_loop_on_shell_width"]==0


@pytest.mark.parametrize("T,mu",[(.1,.2),(.25,-.2),(1.,.8)])
def test_pair_cut_kms_charge_symmetry_and_optical_phase_space(T,mu):
    omega=3.
    result=a.pair_cut(omega,T,mu)
    flipped=a.pair_cut(omega,T,-mu)
    for key in ("spectral","greater","lesser","noise"):
        assert result[key]==pytest.approx(flipped[key],rel=1e-14,abs=0.)
    assert result["log_kms_error"]<1e-10
    assert result["fdt_relative_error"]<1e-10
    assert result["greater"]-result["lesser"]==pytest.approx(result["spectral"])
    assert result["imag_retarded_self_energy"]==-.5*result["spectral"]
    cold=a.pair_cut(omega,0.)
    # Two distinguishable charged final particles; no identical-state 1/2.
    integrated_phase_space=sqrt(1-4*CFG.mass**2/omega**2)/(8*pi)
    decay_width=CFG.cubic**2*integrated_phase_space/(2*omega)
    assert -cold["imag_retarded_self_energy"]/omega==pytest.approx(decay_width)
    assert cold["lesser"]==0 and cold["noise"]==cold["spectral"]


def test_pair_cut_cold_underflow_has_finite_log_kms():
    with np.errstate(over="raise",divide="raise",invalid="raise"):
        r=a.pair_cut(3.,T=1e-4)
    assert r["support"] and r["spectral"]>0
    assert r["lesser"]==0
    assert r["log_kms_error"]<1e-8
    assert r["fdt_relative_error"]<1e-12
    assert r["lesser_underflow"]


def test_threshold_and_decoupled_cut_are_not_zero_over_zero():
    for omega,cfg in [(1.,CFG),(2.,CFG),(3.,replace(CFG,response_coupling=0.))]:
        r=a.pair_cut(omega,cfg=cfg)
        assert not r["support"]
        assert r["spectral"]==0 and r["log_kms_error"] is None


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
def test_stationary_renormalized_envelope_and_energy(T):
    h=1e-4
    s=a.stationary_axis(T)
    assert abs(s["force"])<1e-10 and s["phi_c"]>0
    assert s["static_response_curvature"]>0
    p_mu=(a.stationary_axis(T,mu=.2+h)["pressure"]-a.stationary_axis(T,mu=.2-h)["pressure"])/(2*h)
    p_T=(a.stationary_axis(T+h)["pressure"]-a.stationary_axis(T-h)["pressure"])/(2*h)
    assert p_mu==pytest.approx(s["charge_density"],rel=2e-5)
    assert p_T==pytest.approx(s["entropy_density"],rel=2e-5)
    assert s["energy_density"]==pytest.approx(-s["pressure"]+T*s["entropy_density"]+.2*s["charge_density"],abs=1e-12)
    strict=-a.renormalized_axis_state(0.,T)["force"]/CFG.response_mass_sq
    assert s["strict_one_loop_mean_shift"]==strict


def test_cold_and_uncoupled_stationary_limits():
    assert a.stationary_axis(T=0.)["phi_c"]==0
    assert a.stationary_axis(cfg=replace(CFG,response_coupling=0.))["phi_c"]==0
    assert a.vacuum_axis(0.)==dict(potential=0.,force=0.,curvature=0.)
    assert a.vacuum_retarded(0.)==(0.,0.)


def test_energy_scale_covariance():
    scale=2.5
    cfg=replace(CFG,mass_squared=CFG.mass_squared*scale**2,
        response_mass_squared=CFG.response_mass_squared*scale**2,
        response_coupling=CFG.response_coupling*scale)
    base=a.stationary_axis(); new=a.stationary_axis(T=.25*scale,mu=.2*scale,cfg=cfg)
    for key,dim in (("phi_c",1),("omega",4),("static_response_curvature",2),("charge_density",3)):
        assert new[key]==pytest.approx(base[key]*scale**dim,rel=1e-9)
    p=a.response_pole(); q=a.response_pole(.25*scale,.2*scale,cfg)
    for key in ("strict_one_loop_pole_squared","static_dynamic_gap"):
        assert q[key]==pytest.approx(p[key]*scale**2,rel=1e-9)
    assert q["pole_residue"]==pytest.approx(p["pole_residue"],rel=1e-12)


def test_canonical_field_rescaling_does_not_change_response():
    z,k,eps=.25,4.,.5
    cfg=replace(CFG,z=z,mass_squared=z,quartic=CFG.coupling*z*z,
        epsilon=eps,response_kinetic=k,response_mass_squared=.5*k,
        response_coupling=CFG.cubic*z*sqrt(k/eps),
        response_quartic=CFG.neutral_quartic*eps*k*k)
    p=a.response_pole(cfg=cfg); q=a.response_pole()
    for key in ("strict_one_loop_pole_squared","population_term","pole_residue"):
        assert p[key]==pytest.approx(q[key],rel=1e-14,abs=0.)
    assert a.vacuum_axis(.2,cfg)==pytest.approx(a.vacuum_axis(.2),rel=1e-14,abs=0.)


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
def test_thermal_and_vacuum_dispersion_agree_with_retarded_kernel(T):
    r=a.dispersion_witness(T=T)
    assert r["vacuum_absolute_error"]<1e-12
    assert r["thermal_absolute_error"]<1e-12


@pytest.mark.parametrize("kwargs",[{"T":0.},{"T":-.1},{"E":0.},{"mu":1.3},{"cutoff":0},{"cutoff":True},{"cutoff":2.5}])
def test_invalid_matsubara_domain(kwargs):
    with pytest.raises(ValueError):
        a.matsubara_witness(**kwargs)


@pytest.mark.parametrize("s",[4.,5.,float("nan")])
def test_no_subthreshold_formula_above_cut(s):
    with pytest.raises(ValueError):
        a.vacuum_retarded(s)


@pytest.mark.parametrize("r,degree",[(-1.,2),(-2.,4),(float("nan"),2),(.1,3)])
def test_invalid_vacuum_domain(r,degree):
    with pytest.raises(ValueError):
        a.vacuum_remainder(r,degree)
