"""Independent SD04 integrand/source checks; no material or thermal state solve."""
import importlib.util
import json
import math
from pathlib import Path
import mpmath as mp
import pytest
from scipy.integrate import quad

SOURCE=Path(__file__).with_name("Research_Fluid_Core_O2_Matrix_Tadpole.py")
spec=importlib.util.spec_from_file_location("sd04_matrix_tadpole",SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
C=json.loads(m.CONTRACT.read_text())

def controls():
    return [float(mp.mpf(v)) for v in [C["synthetic_integrand_control"][k] for k in ["k","Y","D","mu","T"]]]

def test_inverse_frequency_and_finite_temperature_sum():
    k,Y,D,mu,T=controls();a=k*k+Y+D-mu*mu;b=k*k+Y-D-mu*mu
    high,low,r11,r22=m.mode_data(k,Y,D,mu)
    for numerator,weights in [(b,r11),(a,r22)]:
        # Direct inversion followed by frequency integration, not pole integration.
        def inverse_diagonal(w):
            return (w*w+numerator)/((w*w+a)*(w*w+b)+4*mu*mu*w*w)
        value,error=quad(inverse_diagonal,-math.inf,math.inf,epsabs=1e-12,epsrel=1e-12)
        expected=sum(v/(2*e) for v,e in zip(weights,(high,low)))
        assert abs(value/(2*math.pi)-expected)<C["numerical_controls"]["frequency_quadrature_abs_tol"]
        assert error/(2*math.pi)<C["numerical_controls"]["frequency_quadrature_abs_tol"]
        with mp.workdps(40):
            total=T*mp.nsum(lambda n: inverse_diagonal(2*mp.pi*n*T),[-mp.inf,mp.inf])
            thermal=sum(v*mp.coth(e/(2*T))/(2*e) for v,e in zip(weights,(high,low)))
            assert abs(total-thermal)<C["numerical_controls"]["frequency_quadrature_abs_tol"]
    for args in [(0,Y,D,mu),(k,1,D,mu),(k,5,0,0)]:
        with pytest.raises(ValueError):m.mode_data(*args)

def test_trace_log_variations_against_direct_matrix_frequency_derivatives():
    k,Y,D,mu,T=controls();a=k*k+Y+D-mu*mu;b=k*k+Y-D-mu*mu
    step=C["numerical_controls"]["derivative_step"]
    expected=[]
    for variable in ["Y","D","mu"]:
        def direct(w):
            det=(w*w+a)*(w*w+b)+4*mu*mu*w*w
            if variable=="Y":ddet=2*w*w+a+b
            elif variable=="D":ddet=b-a
            else:ddet=-2*mu*(2*w*w+a+b)+8*mu*w*w
            return ddet/(2*det)
        value,_=quad(direct,-math.inf,math.inf,epsabs=1e-12,epsrel=1e-12)
        expected.append(value/(2*math.pi))
    for i,value in enumerate(expected):
        params=[Y,D,mu];plus=params.copy();minus=params.copy();plus[i]+=step;minus[i]-=step
        difference=(m.zero_point(k,*plus)-m.zero_point(k,*minus))/(2*step)
        assert abs(difference-value)<C["numerical_controls"]["derivative_abs_tol"]
    assert abs(expected[2])>1e-5  # Mixed vacuum is source dependent at D!=0.
    # Independent expanded auxiliary form detects old traceless-sign reuse.
    x,lam,m2=1.5,.125,2.
    ell=m.zero_point(k,Y,D,mu)
    expanded=ell-(Y-m2)**2/(8*lam)+D*D/(4*lam)+x*(Y-D-mu*mu)/2
    assert abs(m.auxiliary(ell,x,Y,D,mu,m2,lam)-expanded)<1e-12
    assert abs((m.auxiliary(ell,x+step,Y,D,mu,m2,lam)-m.auxiliary(ell,x-step,Y,D,mu,m2,lam))/(2*step)-(Y-D-mu*mu)/2)<1e-7


def test_high_precision_matrix_UV_and_Goldstone_IR_limits():
    with mp.workdps(C["synthetic_UV_control"]["decimal_precision"]):
        _,Y,D,mu,_=map(mp.mpf,[C["synthetic_integrand_control"][k] for k in ["k","Y","D","mu","T"]])
        Y0=mp.mpf(C["synthetic_UV_control"]["Y0"])
        def ell(k,y=Y,d=D,chemical=mu):
            a=k*k+y+d-chemical*chemical;b=k*k+y-d-chemical*chemical
            # Independent pole-sum identity from trace and determinant, no eH-eL subtraction.
            return mp.sqrt((k*k+y+chemical*chemical+mp.sqrt(a*b))/2)
        c5=((Y-Y0)**3+3*(Y-Y0)*D*D-2*mu*mu*D*D)/16
        for token in C["synthetic_UV_control"]["k"]:
            k=mp.mpf(token);e0=mp.sqrt(k*k+Y0)
            ren=ell(k)-e0-(Y-Y0)/(2*e0)+((Y-Y0)**2+D*D)/(8*e0**3)
            assert abs(k**5*ren-c5)<C["numerical_controls"]["UV_scaled_remainder_abs_tol"]
            scalar=ren-D*D/(8*e0**3)
            assert abs(k**3*scalar+D*D/8)<C["numerical_controls"]["UV_scaled_remainder_abs_tol"]
            charge=mp.diff(lambda c:ell(k,chemical=c),mu)
            assert abs(k**5*charge+mu*D*D/4)<C["numerical_controls"]["UV_scaled_remainder_abs_tol"]
        f=C["synthetic_IR_control"];mu,D,T,k=[mp.mpf(f[v]) for v in ["mu","D","T","k"]]
        a=k*k+2*D;b=k*k;R=mp.sqrt((D+2*mu*mu)**2+4*mu*mu*k*k)
        high2=k*k+D+2*mu*mu+R;low2=a*b/high2;low=mp.sqrt(low2)
        wl22=(a-low2)/(2*R);wl11=(b-low2)/(2*R)
        radial22=k*k*wl22/(low*mp.expm1(low/T));radial11=k*k*wl11/(low*mp.expm1(low/T))
        assert abs(radial22-T)<C["numerical_controls"]["IR_abs_tol"]
        assert abs(radial11)<C["numerical_controls"]["IR_abs_tol"]


def test_fresh_evidence_archives_and_fail_closed_scope(tmp_path,monkeypatch):
    a=m.audit();b=m.audit();assert a==b
    assert a["passing_check_count"]==a["check_count"]==58
    assert len(a["input_hashes"])==123
    first=json.loads(m.FIRST_RESULT.read_text());assert first["passing_check_count"]==53 and first["check_count"]==55
    assert {k for k,v in first["checks"].items() if not v}=={"divergent_coefficients_no_explicit_mu","finite_vacuum_mu_derivative"}
    assert all(v is None for v in a["physical_scales"].values())
    assert all(v is False for v in a["admission"].values())
    for key in ["condensed_state_solver_authorized","new_benchmark_expansions_authorized","full_2PI_renormalization_admitted"]:
        changed=dict(C);changed[key]=True;path=tmp_path/(key+".json");path.write_text(json.dumps(changed))
        rejected=m.audit(path);assert not rejected["checks"]["supplied_contract_exact"] and rejected["expressions"]=={}
    original=m.sha;path=m.ROOT/next(iter(C["prelocked_input_hashes"]))
    monkeypatch.setattr(m,"sha",lambda p:"0"*64 if p==path else original(p))
    rejected=m.audit();assert not rejected["checks"]["all_prelocked_inputs_fresh"] and rejected["expressions"]=={}
