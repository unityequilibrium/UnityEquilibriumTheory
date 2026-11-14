"""Ideal standard two-fluid/EOS comparator; no UET or He-II material prediction."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_two_fluid_eos_reference_contract.json"
INPUTS=TOPIC/"Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json"
CARD=TOPIC/"TWO_FLUID_STATE_EOS_REFERENCE.md"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_two_fluid_eos_reference.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_two_fluid_eos_reference_audit.json"


def rms(a):
    return float(np.sqrt(np.mean(np.abs(np.asarray(a))**2)))


def relative(a,b):
    return rms(np.asarray(a)-np.asarray(b))/max(1,rms(a),rms(b))


def match(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return float(min(max(abs(a[i]-b[j]) for i,j in enumerate(order))
                     for order in itertools.permutations(range(len(b))))/
                 max(1,np.max(abs(a)),np.max(abs(b))))


def operator(c):
    r,rs,sg=c["rho"],c["rho_s"],c["sigma"];rn=r-rs
    A,B,D=c["A"],c["B"],c["D"]
    if not (r>rs>0 and sg>0 and c["T"]>0 and A>0 and D>0 and A*D>B*B):
        raise ValueError("Positive components, temperature, entropy and EOS Hessian required")
    M=np.array([[0,0,1,0],[0,0,sg/rn,-sg*rs/rn],
                [r*A+sg*B,r*B+sg*D,0,0],[A,B,0,0]],float)
    H=np.zeros((4,4));H[:2,:2]=[[A,B],[B,D]]
    H[2:,2:]=[[1/rn,-rs/rn],[-rs/rn,rs*r/rn]]
    return M,H


def thermodynamics(c):
    r,rs,sg,T=c["rho"],c["rho_s"],c["sigma"],c["T"]
    A,B,D=c["A"],c["B"],c["D"];rn=r-rs
    ct=r*(A-B*B/D);cs=r*A+2*sg*B+sg*sg*D/r
    cv=T/(r*D);cp=cv*cs/ct;v=rs/rn*T*(sg/r)**2/cv
    roots=np.sort(np.roots([1,-(cs+v),ct*v]).real)
    return dict(c_T_squared=ct,c_S_squared=cs,c_v=cv,c_p=cp,
                v_entropy_squared=v,speed_squared=roots.tolist(),
                slow_reduced_estimate_squared=rs/rn*T*(sg/r)**2/cp,
                pressure_entropy_derivative=r*B+sg*D)


def potentials(r,sg,c):
    dr,ds=r-c["rho"],sg-c["sigma"]
    A,B,D,T=c["A"],c["B"],c["D"],c["T"]
    e=T*ds+.5*(A*dr*dr+2*B*dr*ds+D*ds*ds)
    mu=A*dr+B*ds;temp=T+B*dr+D*ds
    return e,mu,temp,r*mu+sg*temp-e


def path_eos(w,kappa,omit_heat_correction=False):
    r,T=w["rho"],w["T"];sg=r*w["s"]
    alpha=w["alpha_path"]+kappa*w["p_path_prime"]
    cp=w["c_sat"] if omit_heat_correction else w["c_sat"]+T*alpha*w["p_path_prime"]/r
    cv=cp-T*alpha*alpha/(r*kappa)
    D=T/(r*cv);B=D/r*(alpha/kappa-sg)
    A=1/(r*r*kappa)+B*B/D
    return dict(rho=r,rho_s=w["rho_s"],sigma=sg,T=T,A=A,B=B,D=D),dict(
        kappa_T=kappa,alpha_p=alpha,c_p=cp,c_v=cv)


def audit(contract):
    rules=contract["verification"];c=rules["base"]
    tol=rules["identity_tolerance"];floor=rules["negative_control_floor"]
    checks={}
    def check(name,value,limit=tol):
        checks[name]=dict(metric=float(value),threshold=float(limit),
                          pass_=bool(np.isfinite(value) and value<=limit))
    def positive(name,value,minimum=0.):
        checks[name]=dict(metric=float(value),minimum=float(minimum),
                          pass_=bool(np.isfinite(value) and value>minimum))
    M,H=operator(c);th=thermodynamics(c)
    positive("positive_quadratic_availability",np.min(np.linalg.eigvalsh(H)))
    check("reciprocal_flux_symmetry",rms(H@M-(H@M).T))
    check("four_real_characteristic_speeds",rms(np.linalg.eigvals(M).imag))
    speed=np.sqrt(th["speed_squared"])
    check("two_acoustic_pairs_from_quartic",match(np.linalg.eigvals(M),np.r_[-speed,speed]))
    S=c["rho"]*c["A"]+2*c["sigma"]*c["B"]+c["sigma"]**2*c["D"]/(c["rho"]-c["rho_s"])
    P=c["sigma"]**2*c["rho_s"]/(c["rho"]-c["rho_s"])*(c["A"]*c["D"]-c["B"]**2)
    check("quartic_thermodynamic_sum",relative(S,th["c_S_squared"]+th["v_entropy_squared"]))
    check("quartic_thermodynamic_product",relative(P,th["c_T_squared"]*th["v_entropy_squared"]))
    positive("distinct_positive_sound_branches",speed[1]-speed[0])
    derivative=[]
    r,sg=c["rho"],c["sigma"]
    target=np.array([[0,c["T"]],[c["A"],c["B"]],[c["B"],c["D"]],
                    [r*c["A"]+sg*c["B"],r*c["B"]+sg*c["D"]]])
    jac=np.array([[c["B"],c["D"]],target[3]])
    constant_p=np.linalg.solve(jac,[1,0])
    for eps in rules["steps"]:
        columns=[]
        for axis in range(2):
            delta=np.eye(2)[axis]*eps
            columns.append((np.asarray(potentials(r+delta[0],sg+delta[1],c))-
                            np.asarray(potentials(r-delta[0],sg-delta[1],c)))/(2*eps))
        numeric=np.column_stack(columns)
        plus=(sg+eps*constant_p[1])/(r+eps*constant_p[0])
        minus=(sg-eps*constant_p[1])/(r-eps*constant_p[0])
        cp_numeric=c["T"]*(plus-minus)/(2*eps)
        derivative.append(dict(step=eps,EOS_derivative_error=relative(numeric,target),
                               c_p_derivative_error=relative(cp_numeric,th["c_p"])))
    check("EOS_potentials_and_Gibbs_pressure_derivatives",derivative[-1]["EOS_derivative_error"],rules["derivative_tolerance"])
    check("constant_pressure_specific_heat_derivative",derivative[-1]["c_p_derivative_error"],rules["derivative_tolerance"])
    # Independent periodic local conservation test; flux uses quadratic work.
    n=rules["periodic_grid"];x=2*np.pi*np.arange(n)/n
    fields=np.array([.1*np.sin(x)+.04*np.cos(2*x),.08*np.cos(x)+.03*np.sin(3*x),
                     .12*np.sin(2*x)+.07*np.cos(x),.09*np.cos(2*x)+.05*np.sin(3*x)])
    kx=np.fft.fftfreq(n,1/n)
    def dx(a):return np.fft.ifft(1j*kx*np.fft.fft(a,axis=-1),axis=-1).real
    rate=-M@dx(fields)
    flux=.5*np.einsum("in,ij,jn->n",fields,H@M,fields)
    work=np.einsum("in,ij,jn->n",fields,H,rate)
    check("local_quadratic_work_flux_balance",rms(work+dx(flux)))
    check("global_periodic_quadratic_work_balance",abs(np.mean(work)))
    check("periodic_mass_entropy_momentum_mean_balance",rms(np.mean(rate[:3],axis=1)))
    rn=c["rho"]-c["rho_s"];vn=(fields[2]-c["rho_s"]*fields[3])/rn
    check("normal_velocity_entropy_transport",rms(rate[1]+sg*dx(vn)))
    kinetic=(fields[2]-c["rho_s"]*fields[3])**2/(2*rn)+c["rho_s"]*fields[3]**2/2
    w=vn-fields[3]
    barycentric=fields[2]**2/(2*r)+rn*c["rho_s"]*w*w/(2*r)
    check("common_relative_kinetic_decomposition",relative(kinetic,barycentric))
    wrong_entropy=M.copy();wrong_entropy[1]=[0,0,sg/r,0]
    positive("common_velocity_entropy_error_work_detected",
             rms(H@wrong_entropy-(H@wrong_entropy).T),floor)
    positive("common_velocity_entropy_error_local_flux_detected",
             rms(np.einsum("in,ij,jn->n",fields,H,-wrong_entropy@dx(fields))+dx(flux)),floor)
    wrong_sign=M.copy();wrong_sign[3]*=-1
    positive("superfluid_sign_error_work_detected",rms(H@wrong_sign-(H@wrong_sign).T),floor)
    positive("superfluid_sign_error_instability_detected",
             np.max(np.linalg.eigvals(-1j*rules["wavenumbers"][-1]*wrong_sign).real),floor)
    # A finite expansion pressure drive invalidates silently clamped j=0.
    positive("finite_expansion_clamped_mass_current_local_defect",abs(M[2,1]),floor)
    positive("finite_expansion_reduced_speed_is_not_exact",
             abs(th["speed_squared"][0]-th["slow_reduced_estimate_squared"]),floor)
    zero=dict(c,B=-sg*c["D"]/r);M0,H0=operator(zero);tz=thermodynamics(zero)
    check("zero_expansion_counterflow_subspace_invariant",abs(M0[2,1]))
    check("zero_expansion_heat_capacities_equal",relative(tz["c_p"],tz["c_v"]))
    check("zero_expansion_exact_counterflow_branch",
          relative(tz["speed_squared"][0],tz["v_entropy_squared"]))
    check("zero_expansion_reciprocal_work",rms(H0@M0-(H0@M0).T))
    modes=[]
    for k in rules["wavenumbers"]:
        L=-1j*k*M
        check(str(k)+"/complex_work_conservation",rms(H@L+L.conj().T@H))
        check(str(k)+"/acoustic_dispersion",match(np.linalg.eigvals(L),np.r_[1j*k*speed,-1j*k*speed]))
        modes.append(dict(k=k,modes=[dict(real=float(v.real),imag=float(v.imag))
                                    for v in np.linalg.eigvals(L)]))
    # Same path tangent, distinct transverse EOS: no numerical He-II input.
    witness=rules["path_witness"];records=[]
    dr=-witness["rho"]*witness["alpha_path"]
    ds=witness["c_sat"]/witness["T"]
    dsg=dr*witness["s"]+witness["rho"]*ds
    for kappa in witness["kappa_T"]:
        cc,props=path_eos(witness,kappa);MM,HH=operator(cc);tt=thermodynamics(cc)
        temp_tangent=cc["B"]*dr+cc["D"]*dsg
        p_tangent=(cc["rho"]*cc["A"]+cc["sigma"]*cc["B"])*dr+(cc["rho"]*cc["B"]+cc["sigma"]*cc["D"])*dsg
        prefix=str(kappa)+"/"
        check(prefix+"same_path_temperature_tangent",abs(temp_tangent-1))
        check(prefix+"same_path_pressure_tangent",relative(p_tangent,witness["p_path_prime"]))
        check(prefix+"path_heat_to_fixed_pressure_heat",relative(tt["c_p"],props["c_p"]))
        positive(prefix+"positive_EOS_and_inertia",np.min(np.linalg.eigvalsh(HH)))
        bad,badprops=path_eos(witness,kappa,omit_heat_correction=True)
        badtemp=bad["B"]*dr+bad["D"]*dsg
        positive(prefix+"omitted_saturation_heat_correction_detected",abs(badtemp-1),floor)
        records.append(dict(EOS=cc,properties=props,thermodynamics=tt,
                            common_path=dict(rho_prime=dr,s_prime=ds,T_prime=temp_tangent,
                                             p_prime=p_tangent),
                            omitted_heat_correction_temperature_tangent=badtemp))
    positive("same_path_distinct_isothermal_compressibility_speed",
             abs(records[0]["thermodynamics"]["c_T_squared"]-records[1]["thermodynamics"]["c_T_squared"]),floor)
    positive("same_path_distinct_second_sound_pole",
             abs(records[0]["thermodynamics"]["speed_squared"][0]-records[1]["thermodynamics"]["speed_squared"][0]),floor)
    for name,bad in [("nonpositive_entropy",dict(c,sigma=0)),
                     ("zero_normal_component",dict(c,rho_s=c["rho"])),
                     ("indefinite_EOS",dict(c,A=-1))]:
        rejected=False
        try:operator(bad)
        except ValueError:rejected=True
        check(name+"/input_rejected",0 if rejected else 1)
    # SI dimension closure independent of normalized matrix numbers.
    rho=np.array([1,-3,0,0]);sig=np.array([1,-1,-2,-1]);energy=np.array([1,-1,-2,0])
    temp=np.array([0,0,0,1]);vel=np.array([0,1,-1,0])
    da,db,dd=energy-2*rho,energy-rho-sig,energy-2*sig
    cp=np.array([0,2,-2,-1]);kap=-energy;exp=-temp;pprime=energy-temp
    for name,left,right in [
        ("density_sound_stiffness",rho+da,2*vel),
        ("entropy_sound_stiffness",sig+db,2*vel),
        ("entropy_curvature_sound_stiffness",2*sig+dd-rho,2*vel),
        ("c_v",temp-rho-dd,cp),
        ("path_heat_correction",temp+exp+pprime-rho,cp),
        ("heat_capacity_difference",temp+2*exp-rho-kap,cp)]:
        check("SI/"+name,rms(left-right),0)
    for item in checks.values():item["pass"]=item.pop("pass_")
    return dict(pass_=all(v["pass"] for v in checks.values()),checks=checks,
                reference_check_count=len(checks),thermodynamics=th,
                EOS_derivative_controls=derivative,mode_records=modes,
                finite_expansion_clamped_momentum_coefficient=float(M[2,1]),
                zero_expansion_control=dict(EOS=zero,thermodynamics=tz),
                path_EOS_witnesses=records,operator=M.tolist(),availability_weight=H.tolist())


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    result=audit(contract);ok=result.pop("pass_")
    paths=[Path(__file__),CONTRACT,INPUTS,CARD,REGISTRY,
           TOPIC/"Data/03_Research/fluid_second_sound_mode_eligibility_contract.json",
           TOPIC/"Result/artifacts/fluid_second_sound_mode_eligibility_audit.json",
           ROOT/"docs/topics/0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md"]
    result.update(schema_version="t10-two-fluid-EOS-reference-audit-v1",pass_=ok,
                  status="PASS_STANDARD_TWO_FLUID_AND_PATH_UNDERDETERMINATION_REFERENCE_ONLY" if ok else "FAIL_TWO_FLUID_EOS_REFERENCE",
                  controlling_blocker=contract["controlling_blocker"],
                  coupled_input_blocker=contract["coupled_input_blocker"],
                  reference_disposition="REFERENCE_STATE_AND_FIXED_PRESSURE_INPUT_OBLIGATIONS_IDENTIFIED" if ok else "UNRESOLVED_AUDIT_FAILED",
                  claim_promotion=False,dependency_unlock=False,physical_uet_operator_admitted=False,
                  physical_prediction_executed=False,numerical_HeII_data_ingested=False,
                  thresholds=contract["verification"],scope=contract["assumptions"],
                  input_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  excludes=["UET state derivation/admission","material EOS/He-II prediction","nonlinear entropy/FDT closure",
                            "attenuation/transport tensor","source independence","PDE trajectory","formal proof","Core unlock"])
    result["pass"]=result.pop("pass_")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(dict(status=result["status"],checks=result["reference_check_count"],
                         failed=[name for name,v in result["checks"].items() if not v["pass"]])))
    return 0 if ok else 1


if __name__=="__main__":raise SystemExit(main())
