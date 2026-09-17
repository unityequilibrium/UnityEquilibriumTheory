"""Independent witnesses for charged/neutral one-loop thermal matching."""
from dataclasses import replace
from math import pi,sqrt
import mpmath as mp
import numpy as np
import pytest
from scipy.integrate import quad
from docs.scripts.audit import audit_topic13_charged_one_loop_match as a

CFG=a.CFG


@pytest.mark.parametrize("E,W,mu",[(1.2,.8,.2),(1.2,.8,-.2),(1.,1.,0.),(1.,.8,.2),(1.,.8,0.)])
@pytest.mark.parametrize("T",[.1,.25,1.])
def test_complex_matsubara_sum(E,W,mu,T):
    r=a.matsubara_witness(E,W,T,mu)
    assert max(x["relative_error"] for x in r["rows"])<1e-9


@pytest.mark.parametrize("ea,eb",[(1.,1.),(1.+1e-12,1.),(.1,2.),(.8,1.)])
def test_bose_divided_difference_high_precision(ea,eb):
    with mp.workdps(70):
        x=mp.mpf(ea); y=mp.mpf(eb); T=mp.mpf(".25")
        n=lambda z:1/mp.expm1(z/T)
        expected=mp.diff(n,x) if x==y else (n(x)-n(y))/(x-y)
    actual=float(a.divided_occupation(ea,eb,.25))
    assert actual==pytest.approx(float(expected),rel=1e-13)
    assert actual<0


@pytest.mark.parametrize("frequency",[0.,.3,2.])
@pytest.mark.parametrize("mu",[0.,.2])
def test_static_hessian_from_independent_three_field_determinant(frequency,mu):
    p=.4; E2=p*p+CFG.mass**2; W2=p*p+CFG.response_mass_sq
    lam=CFG.coupling; G=CFG.cubic
    def determinant(r):
        d=frequency**2+E2-mu*mu
        H=np.array([[d+3*lam*r*r,2*mu*frequency,-G*r],
                    [-2*mu*frequency,d+lam*r*r,0.],
                    [-G*r,0.,frequency**2+W2]])
        return np.linalg.det(H)
    h=1e-3
    f=lambda r:.5*np.log(determinant(r))
    fd=(-f(2*h)+16*f(h)-30*f(0)+16*f(-h)-f(-2*h))/(12*h*h)
    d=frequency**2+E2-mu*mu
    diagonal_propagator=d/(d*d+4*mu*mu*frequency**2)
    analytic=4*lam*diagonal_propagator-G*G*diagonal_propagator/(frequency**2+W2)
    assert fd==pytest.approx(analytic,rel=1e-7,abs=1e-9)


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
def test_thermal_static_curvature_from_gaussian_eigenvalues(T):
    # At mu=0, the full three-field fluctuation Hessian has real mass eigenvalues.
    def determinant_free_energy(r):
        H=np.array([[CFG.mass**2+3*CFG.coupling*r*r,0.,-CFG.cubic*r],
                    [0.,CFG.mass**2+CFG.coupling*r*r,0.],
                    [-CFG.cubic*r,0.,CFG.response_mass_sq]])
        eigenvalues=np.linalg.eigvalsh(H)
        return sum(a.thermal.thermal_terms(m2,T,0.,(0,))["omega"] for m2 in eigenvalues)
    h=.003
    f=determinant_free_energy
    fd=(-f(2*h)+16*f(h)-30*f(0)+16*f(-h)-f(-2*h))/(12*h*h)
    s=a.charged_self_energy(0.,T,mu=0.,static=True)
    expected=s["quartic_tadpole"]+s["mixed_thermal_bubble"]
    assert fd==pytest.approx(expected,rel=2e-5,abs=1e-10)


@pytest.mark.parametrize("Omega",[-.5,.5,1.,1.6])
def test_unequal_mass_vacuum_spectral_dispersion(Omega):
    m=CFG.mass; M=sqrt(CFG.response_mass_sq); s=Omega*Omega
    def integrand(t):
        phase=CFG.cubic**2/(8*pi)*sqrt((t-(m+M)**2)*(t-(m-M)**2))/t
        return -phase*s*s/(2*pi*t*t*(t-s))
    expected=quad(integrand,(m+M)**2,np.inf,epsabs=1e-14,epsrel=1e-10)[0]
    value,derivative=a.vacuum_kernel(s)
    assert value==pytest.approx(expected,rel=1e-9,abs=1e-13)
    h=1e-6
    fd=(a.vacuum_kernel(s+h)[0]-a.vacuum_kernel(s-h)[0])/(2*h)
    assert derivative==pytest.approx(fd,rel=1e-7,abs=1e-12)


@pytest.mark.parametrize("T,mu",[(.1,.2),(.25,.2),(.5,-.2)])
def test_mixed_thermal_kernel_from_both_signed_spectral_cuts(T,mu):
    Omega=1.; m=CFG.mass; M=sqrt(CFG.response_mass_sq)
    def spectral(w,chemical,kind):
        E=(w*w+m*m-M*M)/(2*w)
        if kind=="PAIR":
            W=w-E
            weights=float(a.occupation(E-chemical,T)+a.occupation(W,T))
        else:
            W=E-w
            weights=float(a.occupation(W,T)-a.occupation(E-chemical,T))
        phase=CFG.cubic**2*sqrt((w*w-(m+M)**2)*(w*w-(m-M)**2))/(8*pi*w*w)
        return phase*weights
    def integrand(w,kind):
        return -(spectral(w,mu,kind)/(w-Omega)+spectral(w,-mu,kind)/(w+Omega))/(2*pi)
    expected=quad(lambda w:integrand(w,"PAIR"),m+M,np.inf,epsabs=1e-13)[0]
    expected+=quad(lambda w:integrand(w,"LANDAU"),0,m-M,epsabs=1e-13)[0]
    actual=a.charged_self_energy(Omega,T,mu)["mixed_thermal_bubble"]
    assert actual==pytest.approx(expected,rel=1e-8,abs=1e-12)


@pytest.mark.parametrize("T",[.1,.25,.5,1.])
@pytest.mark.parametrize("q",[-1,1])
def test_charged_pole_mean_counting_and_temporal_ward_derivative(T,q):
    pole=a.charged_pole(T,q=q)
    kernel=pole["kernel_at_tree"]
    expected_mean=a.response.stationary_axis(T)["strict_one_loop_mean_shift"]
    assert kernel["strict_response_mean_shift"]==pytest.approx(expected_mean,rel=1e-13)
    assert kernel["mean_mass_shift"]==-CFG.cubic*kernel["strict_response_mean_shift"]
    assert pole["strict_energy"]==CFG.mass+kernel["self_energy"]/(2*CFG.mass)
    assert pole["strict_grand_energy"]>0 and pole["static_grand_curvature"]>0
    z=pole["partial_Dyson_energy"]; h=1e-5
    inverse=lambda x:x*x-CFG.mass**2-a.charged_self_energy(x,T,q=q)["self_energy"]
    fd=q*(inverse(z+h)-inverse(z-h))/(2*h)
    assert pole["temporal_Ward_required_vertex"]==pytest.approx(fd,rel=1e-9)
    assert inverse(z)==pytest.approx(0.,abs=1e-10)
    assert pole["one_loop_on_shell_width"]==0
    assert "transverse" in pole["boundary"]


@pytest.mark.parametrize("Omega",[.1,.2,.25,2.,3.])
@pytest.mark.parametrize("q",[-1,1])
def test_charged_kms_and_landau_sign(Omega,q):
    cut=a.mixed_cut(Omega,q=q)
    assert cut["greater"]>=0 and cut["lesser"]>=0
    assert cut["kms_log_error"]<1e-10
    assert cut["fdt_cross_relative_error"]<1e-10
    assert cut["spectral"]==pytest.approx(cut["greater"]-cut["lesser"],abs=1e-16)
    assert cut["spectral"]*cut["grand_frequency"]>=-1e-16
    E=cut["charged_energy"]; W=cut["neutral_energy"]; p=cut["momentum"]
    jacobian=p*Omega/(E*W)
    phase_from_delta=CFG.cubic**2/(4*pi)*p*p/(E*W*jacobian)
    if cut["kind"]=="PAIR":
        n=float(a.occupation(E-q*.2,.25)+a.occupation(W,.25))
        assert cut["spectral"]==pytest.approx(phase_from_delta*(1+n))
    else:
        n=float(a.occupation(W,.25)-a.occupation(E-q*.2,.25))
        assert cut["spectral"]==pytest.approx(phase_from_delta*n)


def test_charge_conjugation_and_zero_density_degeneracy():
    for q in (-1,1):
        plus=a.charged_pole(mu=.2,q=q); minus=a.charged_pole(mu=-.2,q=-q)
        for key in ("strict_energy","strict_grand_energy","static_grand_curvature"):
            assert plus[key]==pytest.approx(minus[key],rel=1e-13)
    plus=a.charged_pole(mu=0.,q=1); minus=a.charged_pole(mu=0.,q=-1)
    assert plus["strict_energy"]==minus["strict_energy"]
    assert a.charged_pole(q=1)["strict_energy"]!=a.charged_pole(q=-1)["strict_energy"]


def test_zero_coupling_and_cold_limits():
    cfg=replace(CFG,response_coupling=0.)
    s=a.charged_self_energy(1.,cfg=cfg)
    assert s["mixed_thermal_bubble"]==0 and s["mean_mass_shift"]==0 and s["vacuum_subtracted"]==0
    assert s["self_energy"]==s["quartic_tadpole"]
    cold=a.charged_self_energy(1.,T=0.)
    assert cold["mean_mass_shift"]==0 and cold["quartic_tadpole"]==0 and cold["mixed_thermal_bubble"]==0
    assert cold["vacuum_subtracted"]<0
    assert a.mixed_cut(.25,T=0.)["spectral"]==0
    assert a.mixed_cut(1.)["kind"]=="NO_CUT_SUPPORT"


def test_cold_cut_no_exponential_overflow():
    with np.errstate(over="raise",divide="raise",invalid="raise"):
        for Omega in (.25,2.):
            c=a.mixed_cut(Omega,T=1e-4)
            assert c["kms_log_error"]<1e-8


def test_energy_covariance():
    scale=2.
    cfg=replace(CFG,mass_squared=CFG.mass_squared*scale**2,
        response_mass_squared=CFG.response_mass_squared*scale**2,response_coupling=CFG.response_coupling*scale)
    p=a.charged_pole(); s=a.charged_pole(T=.25*scale,mu=.2*scale,cfg=cfg)
    for key,dim in (("strict_energy",1),("static_grand_curvature",2),("residue",0)):
        assert s[key]==pytest.approx(p[key]*scale**dim,rel=1e-10)


def test_canonical_field_covariance():
    z,k,eps=.25,4.,.5
    cfg=replace(CFG,z=z,mass_squared=z,quartic=CFG.coupling*z*z,
        epsilon=eps,response_kinetic=k,response_mass_squared=CFG.response_mass_sq*k,
        response_coupling=CFG.cubic*z*sqrt(k/eps),
        response_quartic=CFG.neutral_quartic*eps*k*k)
    p=a.charged_pole(); r=a.charged_pole(cfg=cfg)
    for key in ("strict_energy","static_grand_curvature","residue","temporal_Ward_required_vertex"):
        assert r[key]==pytest.approx(p[key],rel=1e-13)


def test_static_limit_is_charge_even_and_not_a_dynamic_pole():
    positive=a.charged_pole(q=1); negative=a.charged_pole(q=-1)
    assert positive["static_grand_curvature"]==pytest.approx(negative["static_grand_curvature"],rel=1e-13)
    with pytest.raises(ValueError):
        a.charged_self_energy(1.,static=True)


@pytest.mark.parametrize("kwargs",[{"T":0.},{"T":-.1},{"E":0.},{"mu":1.2},{"cutoff":0},{"cutoff":True}])
def test_invalid_matsubara_parameters(kwargs):
    with pytest.raises(ValueError):
        a.matsubara_witness(**kwargs)


@pytest.mark.parametrize("Omega",[0.,.1,.2,2.,float("nan")])
def test_real_pole_kernel_rejects_cut_region(Omega):
    with pytest.raises(ValueError):
        a.charged_self_energy(Omega)


@pytest.mark.parametrize("kwargs",[{"T":-.1},{"mu":1.},{"q":0},{"order":True},{"cutoff_factor":1.}])
def test_invalid_kernel_parameters(kwargs):
    with pytest.raises(ValueError):
        a.charged_self_energy(1.,**kwargs)
