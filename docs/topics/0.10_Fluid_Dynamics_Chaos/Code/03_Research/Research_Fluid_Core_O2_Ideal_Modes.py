"""Local scalar-pressure current/stress and conditional ideal two-fluid modes."""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_ideal_modes_contract.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_core_o2_ideal_modes_audit.json"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_ideal_modes_addendum.json"
ETA=np.diag([1.,-1.,-1.,-1.])


def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def norm_error(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return float(np.linalg.norm(a-b)/max(np.linalg.norm(a),np.linalg.norm(b),1e-30))


def eos_state(p,base,flow,ns,T,mu,order,factor):
    cfg=base.configuration(p,order,factor)
    k,w=flow.quadrature(order,flow.cutoff_value(p,T,mu,factor))
    E=np.array([ns["EOS"]["condensed_quasiparticle_energies"](float(v),mu,p["configuration"]["Phi_fixed"],cfg) for v in k])
    kk=k[:,None]**2;mc2=p["configuration"]["mass_squared"]/p["configuration"]["Z"]
    x=E**2-kk;r=mu*mu-mc2;D=x-r-2*mu*mu
    FE=4*E*D;FEE=4*(D+2*E**2)
    Fmu=-4*mu*(3*E**2-kk);Fmm=-4*(3*E**2-kk);FEmu=-24*mu*E
    Em=-Fmu/FE
    Emm=-(Fmm+2*FEmu*Em+FEE*Em**2)/FE
    N=flow.bose(E,T);measure=w[:,None]*kk/(2*np.pi**2)
    Pth=float(T*np.sum(measure*flow.thermal_log(E,T)))
    nth=float(-np.sum(measure*N*Em))
    s=float(np.sum(measure*(flow.thermal_log(E,T)+(E/T)*N)))
    Hmm=float(np.sum(measure*(N*(1+N)*Em**2/T-N*Emm)))
    HmT=float(-np.sum(measure*N*(1+N)*E*Em/T**2))
    HTT=float(np.sum(measure*N*(1+N)*E**2/T**3))
    c=p["configuration"];q=c["Z"]*mu*mu-c["mass_squared"]
    Ptree=q*q/(4*c["lambda"]);ntree=c["Z"]*mu*q/c["lambda"]
    Htree=c["Z"]*(3*c["Z"]*mu*mu-c["mass_squared"])/c["lambda"]
    phase=flow.implicit_phase(p,base,ns,T,mu,order,factor)
    n=ntree+nth;f=phase["flow_phase_stiffness"];nn=n-mu*f
    chi=mu*nn+T*s
    return {"T":T,"mu":mu,"order":order,"cutoff_factor":factor,"pressure":Ptree+Pth,
      "n":n,"s":s,"thermal_charge_sector_derivative":nth,"phase_curvature":f,
      "ideal_normal_charge_coefficient":nn,"ideal_normal_inertia":chi,
      "H":[[Htree+Hmm,HmT],[HmT,HTT]],"H_thermal":[[Hmm,HmT],[HmT,HTT]],
      "thermal_pressure":Pth,"thermal_charge":nth,"H_tree":Htree,"phase_details":phase}


def finite_thermal_derivatives(p,base,flow,ns,T,mu,order,factor,step):
    cfg=base.configuration(p,order,factor)
    # Fixed bounds isolate derivatives; separate cutoff refinements test truncation.
    k,w=flow.quadrature(order,flow.cutoff_value(p,T,mu,factor))
    measure=w[:,None]*k[:,None]**2/(2*np.pi**2)
    @lru_cache(maxsize=None)
    def modes(m):
        return np.array([ns["EOS"]["condensed_quasiparticle_energies"](float(v),m,p["configuration"]["Phi_fixed"],cfg) for v in k])
    def pressure(t,m):return float(t*np.sum(measure*flow.thermal_log(modes(m),t)))
    hm=step*max(1.,abs(mu));ht=step*max(1.,abs(T))
    def first(values,h):return (values[0]-8*values[1]+8*values[3]-values[4])/(12*h)
    def second(values,h):return (-values[4]+16*values[3]-30*values[2]+16*values[1]-values[0])/(12*h*h)
    shifts=[-2,-1,0,1,2]
    grid=np.array([[pressure(T+i*ht,mu+j*hm) for j in shifts] for i in shifts])
    coefficient=np.array([1.,-8.,0.,8.,-1.])
    cross=float(coefficient@grid@coefficient/(144*ht*hm))
    return {"step":step,"thermal_charge":first(grid[2,:],hm),"s":first(grid[:,2],ht),
      "H_thermal":[[second(grid[2,:],hm),cross],[cross,second(grid[:,2],ht)]]}


def pressure_local(ref,metric,beta,phase):
    inverse=np.linalg.inv(metric)
    T=float((beta@metric@beta)**(-.5));u=T*beta
    y=float(u@phase);x=float(phase@inverse@phase)
    change=np.array([y-ref["mu"],T-ref["T"]])
    H=np.asarray(ref["H"])
    P=ref["pressure"]+ref["n"]*change[0]+ref["s"]*change[1]+.5*change@H@change+.5*ref["phase_curvature"]*(x-y*y)
    PT=ref["s"]+float(H[1]@change)
    Py=ref["n"]+float(H[0]@change)-ref["phase_curvature"]*y
    return float(P),T,u,y,x,float(PT),float(Py)


def current_stress_local(ref,metric,beta,phase):
    P,T,u,y,x,s,nn=pressure_local(ref,metric,beta,phase)
    inverse=np.linalg.inv(metric);pp=inverse@phase;f=ref["phase_curvature"]
    chi=T*s+y*nn
    current=f*pp+nn*u
    stress=f*np.outer(pp,pp)+chi*np.outer(u,u)-P*inverse
    entropy=s*u
    theta=-(nn/s)*pp+(chi/s)*u
    entrainment=np.array([[1/f,-nn/(s*f)],[-nn/(s*f),nn*nn/(s*s*f)+chi/(s*s)]])
    conjugates=entrainment@np.vstack([current,entropy])
    return {"P":P,"T":T,"y":y,"x":x,"current":current,"stress":stress,"entropy":entropy,"theta":theta,
       "phase_contravariant":pp,"entrainment":entrainment,"conjugates":conjugates,
       "two_current_stress":-P*inverse+np.outer(current,pp)+np.outer(entropy,theta)}


def five_point_scalar(function,h):
    return (function(-2*h)-8*function(-h)+8*function(h)-function(2*h))/(12*h)


def source_metric_derivatives(ref,beta,phase,step):
    current=[]
    for i in range(4):
        direction=np.eye(4)[i]
        current.append(five_point_scalar(lambda e:pressure_local(ref,ETA,beta,phase+e*direction)[0],step))
    tensor=np.zeros((4,4))
    for i in range(4):
        for j in range(i,4):
            direction=np.zeros((4,4));direction[i,j]=1.
            if i!=j:direction[j,i]=1.
            def density(e):
                metric=ETA+e*direction
                return float(np.sqrt(-np.linalg.det(metric))*pressure_local(ref,metric,beta,phase)[0])
            value=-(2. if i==j else 1.)*five_point_scalar(density,step)
            tensor[i,j]=tensor[j,i]=value
    return np.array(current),tensor


def boost(speed,direction):
    d=np.array(direction,dtype=float);d/=np.linalg.norm(d);gamma=1/np.sqrt(1-speed*speed)
    B=np.eye(4);B[0,0]=gamma;B[0,1:]=B[1:,0]=gamma*speed*d
    B[1:,1:]+=(gamma-1)*np.outer(d,d)
    return B


def ideal_operator(ref):
    mu,n,s,f=ref["mu"],ref["n"],ref["s"],ref["phase_curvature"]
    nn,chi=ref["ideal_normal_charge_coefficient"],ref["ideal_normal_inertia"]
    rs=mu*mu*f;H=np.array(ref["H"]);K=np.linalg.inv(H)
    A=np.zeros((4,4))
    A[0,2:]=[nn/chi,mu*f-nn*rs/chi]
    A[1,2:]=[s/chi,-s*rs/chi]
    A[2,:2]=np.array([n,s])@K
    A[3,:2]=K[0,:]/mu
    S=np.zeros((4,4));S[:2,:2]=K
    S[2:,2:]=[[1/chi,-rs/chi],[-rs/chi,rs+rs*rs/chi]]
    # Independent generalized system in (delta mu,delta T,v_n,v_s).
    M=np.zeros((4,4));M[:2,:2]=H
    M[2,2:]=[chi,rs];M[3,3]=mu
    L=np.zeros((4,4))
    L[0,2:]=[nn,mu*f];L[1,2]=s;L[2,:2]=[n,s];L[3,0]=1.
    R=M.copy();R[3,3]=1.
    generalized=np.linalg.solve(M,L)
    transformed=R@generalized@np.linalg.inv(R)
    values,vectors=np.linalg.eig(A)
    chol=np.linalg.cholesky(S)
    whitened=chol.T@A@np.linalg.inv(chol.T)
    modes=[]
    for i,value in enumerate(values):
        q=vectors[:,i];q=q/np.sqrt(np.vdot(q,S@q).real)
        vn=(q[2]-rs*q[3])/chi
        modes.append({"speed_real":float(value.real),"speed_imag":float(value.imag),
           "state_real":q.real.tolist(),"state_imag":q.imag.tolist(),
           "normal_velocity_real":float(vn.real),"super_velocity_real":float(q[3].real),
           "entropy_current_real":float((s*vn).real),
           "relative_velocity_magnitude":float(abs(vn-q[3])),
           "eigen_residual":norm_error(A@q,value*q)})
    modes.sort(key=lambda q:q["speed_real"])
    return A,S,M,L,transformed,whitened,modes


def local_work(ref,state,gradient):
    mu,n,s,f=ref["mu"],ref["n"],ref["s"],ref["phase_curvature"]
    nn,chi=ref["ideal_normal_charge_coefficient"],ref["ideal_normal_inertia"];rs=mu*mu*f
    K=np.linalg.inv(np.array(ref["H"]))
    chemical=K@state[:2];chemical_dx=K@gradient[:2]
    vn=(state[2]-rs*state[3])/chi;vn_dx=(gradient[2]-rs*gradient[3])/chi
    j=nn*vn+mu*f*state[3];j_dx=nn*vn_dx+mu*f*gradient[3]
    entropy=s*vn;entropy_dx=s*vn_dx
    density_dot=-chemical[0].conjugate()*j_dx-chemical[1].conjugate()*entropy_dx
    kinetic_dot=-vn.conjugate()*(n*chemical_dx[0]+s*chemical_dx[1])-rs*(state[3]-vn).conjugate()*chemical_dx[0]/mu
    flux_dx=chemical_dx[0].conjugate()*j+chemical[0].conjugate()*j_dx+chemical_dx[1].conjugate()*entropy+chemical[1].conjugate()*entropy_dx
    residual=float((density_dot+kinetic_dot+flux_dx).real)
    scale=max(abs(density_dot)+abs(kinetic_dot)+abs(flux_dx),1e-30)
    return {"signed_residual":residual,"relative_residual":float(abs(residual)/scale)}


def audit(p,path):
    base=load_module(ROOT/p["source_adapter"],"ideal_source_adapter")
    flow=load_module(ROOT/p["phase_verifier"],"ideal_phase_adapter")
    original=json.loads((ROOT/p["source_contract"]).read_text(encoding="utf-8"))
    phase_contract=json.loads((ROOT/p["phase_contract"]).read_text(encoding="utf-8"))
    ns,AST=base.source_functions(original);rules=p["verification"];checks={}
    def flag(n,v):checks[n]={"pass":bool(v)}
    def close(n,v,t):checks[n]={"metric":float(v),"threshold":t,"pass":bool(np.isfinite(v) and v<=t)}
    def greater(n,v,t=0.):checks[n]={"metric":float(v),"minimum":t,"pass":bool(np.isfinite(v) and v>t)}
    flag("record_scope",p["record_role"]=="FIXED_PHI_LOCAL_IDEAL_TWO_FLUID_REFERENCE_NOT_ADMISSION")
    flag("configuration_matches_source",p["configuration"]==original["configuration"]==phase_contract["configuration"])
    flag("three_locked_states",p["states"]==phase_contract["states"] and len(p["states"])==3)
    flag("ideal_thermalization_assumption_explicit",p["assumptions"]["ideal_local_equilibrium_entropy_conservation"] is True and
         p["assumptions"]["thermalization_derived"] is False and p["assumptions"]["physical_hydrodynamic_frequency_window_known"] is False)
    flag("thresholds_locked",rules["locked_before_first_execution"] is True and rules["radial_orders"]==[128,256,384] and
         rules["cutoffs"]==[45,70,100] and rules["thermal_derivative_steps"]==[.001,.0003,.0001] and
         rules["derivative_relative_tolerance"]==1e-5 and rules["algebra_covariance_work_pole_tolerance"]==1e-8)
    for k,v in p["admission"].items():flag("boundary/"+k,v is False)
    rows=[];tol=rules["algebra_covariance_work_pole_tolerance"];floor=rules["positive_and_negative_floor"]
    for point in p["states"]:
        T,mu=point["T"],point["mu"];label=str(T)
        orders=[eos_state(p,base,flow,ns,T,mu,o,rules["order_sweep_cutoff"]) for o in rules["radial_orders"]]
        cutoffs=[eos_state(p,base,flow,ns,T,mu,rules["cutoff_sweep_order"],f) for f in rules["cutoffs"]]
        ref=cutoffs[-1]
        for kind,sweep in [("order",orders),("cutoff",cutoffs)]:
            error=max(norm_error(sweep[-1][key],sweep[-2][key]) for key in
              ("H_thermal","s","thermal_charge","phase_curvature","ideal_normal_inertia"))
            close(label+"/"+kind+"_refinement",error,rules["implicit_refinement_relative_tolerance"])
        finite=[finite_thermal_derivatives(p,base,flow,ns,T,mu,rules["radial_orders"][-1],rules["cutoffs"][-1],h)
                for h in rules["thermal_derivative_steps"]]
        for key in ("H_thermal","s","thermal_charge"):
            close(label+"/finite_derivative/"+key,norm_error(finite[-1][key],ref[key]),rules["derivative_relative_tolerance"])
            close(label+"/finite_step/"+key,norm_error(finite[-1][key],finite[-2][key]),rules["finite_difference_refinement_relative_tolerance"])
        source=base.state(original,ns,point,rules["radial_orders"][-1],rules["cutoffs"][-1],.0001)
        close(label+"/source_pressure",norm_error(ref["pressure"],source["pressure"]),tol)
        close(label+"/source_charge",norm_error(ref["n"],source["charge_density"]),tol)
        close(label+"/source_entropy",norm_error(ref["s"],source["entropy_density"]),tol)
        close(label+"/separate_static_proxy",norm_error(ref["ideal_normal_inertia"],source["static_Doppler_momentum_proxy"]),
              rules["proxy_correspondence_relative_tolerance"])
        for key in ("s","phase_curvature","ideal_normal_charge_coefficient","ideal_normal_inertia"):
            greater(label+"/positive/"+key,ref[key])
        greater(label+"/EOS_Hessian_positive",float(np.min(np.linalg.eigvalsh(ref["H"]))),floor)
        normal=np.array(rules["normal_velocity_probe"]);u=np.r_[1.,normal]/np.sqrt(1-normal@normal)
        beta=u/T;phase=np.r_[mu,np.array(rules["phase_spatial_probe"])]
        analytic=current_stress_local(ref,ETA,beta,phase)
        derivative_rows=[]
        for step in rules["source_metric_steps"]:
            jc,tc=source_metric_derivatives(ref,beta,phase,step)
            ej,et=norm_error(jc,analytic["current"]),norm_error(tc,analytic["stress"])
            close(label+"/source_current/"+str(step),ej,rules["source_metric_relative_tolerance"])
            close(label+"/metric_stress/"+str(step),et,rules["source_metric_relative_tolerance"])
            derivative_rows.append({"step":step,"current_relative_error":ej,"stress_relative_error":et})
        close(label+"/stress_symmetric",norm_error(analytic["stress"],analytic["stress"].T),tol)
        close(label+"/two_current_stress",norm_error(analytic["stress"],analytic["two_current_stress"]),tol)
        close(label+"/conjugate_phase",norm_error(analytic["conjugates"][0],analytic["phase_contravariant"]),tol)
        close(label+"/conjugate_thermal",norm_error(analytic["conjugates"][1],analytic["theta"]),tol)
        greater(label+"/entrainment_positive",float(np.min(np.linalg.eigvalsh(analytic["entrainment"]))),floor)
        close(label+"/entrainment_inverse",norm_error(np.linalg.solve(analytic["entrainment"],analytic["conjugates"]),
              np.vstack([analytic["current"],analytic["entropy"]])),tol)
        for speed in rules["lorentz_boosts"]:
            B=boost(speed,rules["boost_direction"])
            changed=current_stress_local(ref,ETA,B@beta,ETA@B@ETA@phase)
            close(label+"/boost_metric/"+str(speed),norm_error(B.T@ETA@B,ETA),tol)
            close(label+"/boost_current/"+str(speed),norm_error(changed["current"],B@analytic["current"]),tol)
            close(label+"/boost_stress/"+str(speed),norm_error(changed["stress"],B@analytic["stress"]@B.T),tol)
        angle=rules["rotation_angle"];rotation=np.eye(4)
        rotation[1:3,1:3]=[[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]
        rotated=current_stress_local(ref,ETA,rotation@beta,ETA@rotation@ETA@phase)
        close(label+"/rotation_current",norm_error(rotated["current"],rotation@analytic["current"]),tol)
        close(label+"/rotation_stress",norm_error(rotated["stress"],rotation@analytic["stress"]@rotation.T),tol)
        A,S,M,L,alternative,white,modes=ideal_operator(ref)
        greater(label+"/energy_positive",float(np.min(np.linalg.eigvalsh(S))),floor)
        close(label+"/work_symmetry",norm_error(S@A,A.T@S),tol)
        close(label+"/independent_operator_coordinates",norm_error(A,alternative),tol)
        close(label+"/whitened_operator_symmetric",norm_error(white,white.T),tol)
        native=np.sort_complex(np.linalg.eigvals(A))
        independent=np.sort_complex(np.linalg.eigvals(np.linalg.solve(M,L)))
        close(label+"/independent_poles",norm_error(native,independent),tol)
        close(label+"/real_poles",float(np.max(abs(native.imag))),tol)
        real=native.real
        close(label+"/opposite_acoustic_pairs",norm_error(real,-real[::-1]),tol)
        greater(label+"/two_distinct_positive_acoustic_speeds",min(real[2],real[3]-real[2]),floor)
        close(label+"/subluminal_reference_speeds",max(0.,float(max(abs(real)))-1.),tol)
        close(label+"/mode_residuals",max(m["eigen_residual"] for m in modes),tol)
        samples=[(np.array([.1,-.2,.3,-.1]),np.array([-.2,.15,.1,.4])),
                 (np.array([.1,-.2,.3,-.1])+1j*np.array([.2,.1,-.15,.3]),
                  np.array([-.2,.15,.1,.4])+1j*np.array([.05,-.25,.2,.1]))]
        work=[local_work(ref,x,g) for x,g in samples]
        close(label+"/local_real_and_complex_work",max(q["relative_residual"] for q in work),tol)
        wrong_entropy=A.copy();wrong_entropy[1,:]=[0.,0.,0.,ref["s"]]
        wrong_phase=A.copy();wrong_phase[3,:]*=-1
        entropy_defect=norm_error(S@wrong_entropy,wrong_entropy.T@S)
        phase_growth=float(np.max(abs(np.linalg.eigvals(wrong_phase).imag)))
        omit_heat=norm_error(ref["ideal_normal_inertia"],mu*ref["ideal_normal_charge_coefficient"])
        greater(label+"/super_velocity_entropy_error_detected",entropy_defect,floor)
        greater(label+"/wrong_Josephson_instability_detected",phase_growth,floor)
        greater(label+"/omit_Ts_inertia_error_detected",omit_heat,floor)
        rows.append({"point":point,"reference":ref,"order_sweep":orders,"cutoff_sweep":cutoffs,
           "finite_derivative_sweep":finite,"source_zero_flow":source,"source_metric_derivative_controls":derivative_rows,
           "local_current":analytic["current"].tolist(),"local_stress":analytic["stress"].tolist(),
           "local_thermal_conjugate":analytic["theta"].tolist(),"entrainment_matrix":analytic["entrainment"].tolist(),
           "linear_operator":A.tolist(),"energy_Hessian":S.tolist(),"generalized_M":M.tolist(),"generalized_L":L.tolist(),
           "modes":modes,"local_work_controls":work,
           "negative_controls":{"entropy_velocity_work_defect":entropy_defect,"wrong_Josephson_growth":phase_growth,
              "omit_Ts_inertia_relative_defect":omit_heat},
           "mode_role":"conditional ideal local-equilibrium acoustic eligibility; no physical He-II speed"})
    passed=all(q["pass"] for q in checks.values())
    phase_result=json.loads((ROOT/p["phase_artifact"]).read_text(encoding="utf-8"))
    flag("prior_phase_scalar_gate_passed",phase_result["scalar_correspondence_gate"]["target_pass"] is True)
    passed=all(q["pass"] for q in checks.values())
    paths=[path,ROOT/p["card"],REGISTRY,Path(__file__).resolve(),ROOT/p["source_adapter"],ROOT/p["source_contract"],
      ROOT/p["phase_verifier"],ROOT/p["phase_contract"],ROOT/p["phase_artifact"]]+[ROOT/f for f in original["core_sources"].values()]+[ROOT/f for f in p["reused_inputs"]]
    hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
    return {"schema_version":"t010-core-o2-ideal-modes-audit-v1","date":p["date"],
       "status":"PASS_LOCAL_IDEAL_REFERENCE_ONLY" if passed else "LOCAL_IDEAL_REFERENCE_FAIL",
       "check_count":len(checks),"passing_check_count":sum(q["pass"] for q in checks.values()),"checks":checks,
       "input_hashes":hashes,"source_AST_definition_hashes":AST,"state_results":rows,
       "candidate_controller":p["passed_reference_next_controller"] if passed else p["previous_candidate_controller"],
       "physical_controller":p["physical_controller"],"locked_verification":rules,"assumptions":p["assumptions"],
       "local_pressure_current_stress_entrainment_checked":True,
       "conditional_ideal_acoustic_pairs_checked":bool(rows),
       "microscopic_entropy_conservation_derived":False,"thermalization_derived":False,
       "physical_frequency_window_established":False,"complete_nonlinear_operator_derived":False,
       "whole_Core_runtime_executed":False,"live_Phi_executed":False,
       "physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,"physical_normal_density_assigned":False,
       "physical_prediction_executed":False,"physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,
       "claim_promotion":False,"dependency_unlock":False,"thresholds_relaxed":False,"mode_coefficients_fitted":False,
       "notes":["Metric/current variation is of a declared local second-order scalar Taylor action, not arbitrary nonlinear thermal microphysics.",
          "EOS derivatives and phase curvature use independent source-mode integrals, not fitted sound speeds.",
          "Entropy conservation is an explicit ideal local-equilibrium assumption, not derived thermalization.",
          "Natural charge/current coefficients and acoustic speeds are not material SI densities or He-II observables.",
          "Prior tree-only FAIL and independent phase-Hessian PASS artifacts remain unchanged."]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"])
    for row in a["state_results"]:
        print(row["point"],"speeds",[m["speed_real"] for m in row["modes"]],
              "normal coefficient",row["reference"]["ideal_normal_charge_coefficient"])
    if a["passing_check_count"]!=a["check_count"]:
        print("FAIL:",[(n,v) for n,v in a["checks"].items() if not v["pass"]])
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
