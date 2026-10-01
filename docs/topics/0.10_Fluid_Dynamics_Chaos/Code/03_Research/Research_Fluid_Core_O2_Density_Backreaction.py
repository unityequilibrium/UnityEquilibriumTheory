"""Leading mean condensate density/source and fixed-domain Gaussian bookkeeping."""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_density_backreaction_contract.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_core_o2_density_backreaction_audit.json"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_density_backreaction_addendum.json"

def load(path,name):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def rel(x,y):return float(abs(x-y)/max(abs(x),abs(y),1e-300))
def conditioned(x,y,scale):return float(abs(x-y)/max(abs(x),abs(y),abs(scale),1e-300))

def densities(a,m):
    E,pol,n=m["E"],m["polarization"],m["action_per_amplitude_squared"]
    rho=np.sqrt(a["r"]/a["lambda_c"])
    shift=-(3*pol*pol+1)/(4*rho)
    qr=a["mu"]*(pol*pol+1)/2+pol*E
    qc=2*a["mu"]*rho*shift
    # Stable corrected charge is compared to an independently differentiated root.
    qt=pol*(E-a["mu"]*pol)
    er=(E*E+a["k"]**2+a["mu"]**2+a["m2"])*(pol*pol+1)/4+a["mu"]*pol*E+a["r"]*(3*pol*pol+1)/4
    ec=a["mu"]*qc
    return {"rho":float(rho),"shift_per_amplitude_squared":float(shift),"q_raw_coefficient":float(qr),
        "q_condensate_coefficient":float(qc),"q_corrected_coefficient":float(qt),"e_raw_coefficient":float(er),
        "e_condensate_coefficient":float(ec),"e_corrected_coefficient":float(n*E+a["mu"]*qt),
        "grand_coefficient":float(n*E),"q_per_action":float(qt/n),"e_per_action":float(E+a["mu"]*qt/n),
        "radial_force_coefficient":float(-a["lambda_c"]*rho*(3*pol*pol+1)/2),
        "charge_cancellation_condition":float(max(abs(qr),abs(qc))/max(abs(qt),1e-300))}

def field_average(ns,a,m,amplitude,phase,order,shifted):
    """Original field action/EOM/current/stress with independently computed box."""
    rho=np.sqrt(a["r"]/a["lambda_c"]);pol=m["polarization"];E=m["E"];k=a["k"]
    rho_b=rho-(3*pol*pol+1)*amplitude**2/(4*rho) if shifted else rho
    conf=SimpleNamespace(matter_kinetic=a["Z"],matter_mass_sq=a["m2"]*a["Z"],matter_quartic=a["lambda_c"]*a["Z"]**2,response_coupling=0.)
    response=SimpleNamespace(epsilon_nc=0.,phi_equilibrium=0.)
    g=np.diag([-1.,1.,1.,1.]);rot=np.array([[np.cos(phase),np.sin(phase)],[-np.sin(phase),np.cos(phase)]])
    means=np.zeros(6)
    for angle in 2*np.pi*np.arange(order)/order:
        for sign in (-1,1):
            u=sign*amplitude*pol*np.cos(angle);v=sign*amplitude*np.sin(angle)
            ut=-sign*amplitude*pol*E*np.sin(angle);vt=sign*amplitude*E*np.cos(angle)
            uz=sign*amplitude*pol*k*np.sin(angle);vz=-sign*amplitude*k*np.cos(angle)
            f=rot@np.array([rho_b+u,-v])/np.sqrt(a["Z"])
            gradients=np.zeros((2,4));gradients[:,0]=rot@np.array([ut-a["mu"]*v,-vt-a["mu"]*(rho_b+u)])/np.sqrt(a["Z"])
            gradients[:,3]=rot@np.array([uz,-vz])/np.sqrt(a["Z"])
            box=rot@np.array([(E*E-k*k+a["mu"]**2)*u+2*a["mu"]*vt+a["mu"]**2*rho_b,
                             (-E*E+k*k-a["mu"]**2)*v+2*a["mu"]*ut])/np.sqrt(a["Z"])
            j=ns["matter_noether_current"](g,f,gradients,conf)
            stress=ns["coupled_matter_stress_tensor"](g,g,f,gradients,a["Phi"],response,conf)
            action=ns["coupled_matter_lagrangian_scalar"](g,gradients,f,a["Phi"],response,conf)
            eom=ns["matter_eom_residual"](box,f,a["Phi"],response,conf)
            radial=(rot.T@eom)[0]/np.sqrt(a["Z"])
            raised=g@stress@g
            means+=np.array([j[0],raised[0,0],action,radial,j[3],raised[3,0]])/(2*order)
    return means

def coefficient(ns,a,m,phase,order,amplitudes,shifted):
    # Exact rational interpolation weights for coefficient of A^2. Full source
    # after a mean shift is a degree-eight amplitude polynomial, not a wave solve.
    xs=[Fraction(str(v))**2 for v in amplitudes];weights=[]
    for i,x in enumerate(xs):
        w=Fraction(1)
        for j,y in enumerate(xs):
            if i!=j:w*=y/(y-x)
        weights.append(float(w))
    rho=np.sqrt(a["r"]/a["lambda_c"])
    baseline=field_average(ns,a,m,0.,phase,order,shifted)
    result=np.zeros(6)
    for v,w in zip(amplitudes,weights):
        amp=v*rho
        result+=w*(field_average(ns,a,m,amp,phase,order,shifted)-baseline)/(amp*amp)
    return result

def thermal(a,ward,order,T=None,mu=None):
    # Central physical momentum domain is held fixed during source variations.
    T=a["T"] if T is None else T;mu=a["mu"] if mu is None else mu
    b=dict(a);b.update(T=T,mu=mu,r=mu*mu-a["m2"],B=3*mu*mu-a["m2"])
    if b["r"]<=0:raise ValueError("positive condensed state required")
    rho=np.sqrt(b["r"]/b["lambda_c"])
    nodes,weights=np.polynomial.legendre.leggauss(order)
    k=a["K"]*(nodes+1)/2;D=weights*a["K"]/2*k*k/(2*np.pi**2)
    qraw=qcond=qtotal=U=P=delta=entropy=0.
    for v,w in zip(k,D):
        b["k"]=float(v);m=ward.mode(float(v),b,"lower");d=densities(b,m);E=m["E"];n=m["action_per_amplitude_squared"]
        z=np.exp(-E/T);f=z/(-np.expm1(-E/T));log=np.log1p(-z)
        P-=w*T*log;U+=w*f*E;entropy+=w*(E*f/T-log)
        qraw+=w*f*d["q_raw_coefficient"]/n;qcond+=w*f*d["q_condensate_coefficient"]/n
        qtotal+=w*f*d["q_per_action"];delta+=w*f*d["shift_per_amplitude_squared"]/n
    return {"order":order,"P":float(P),"q_raw":float(qraw),"q_condensate":float(qcond),"q_corrected":float(qtotal),
        "U_grand":float(U),"energy_correction":float(U+mu*qtotal),"entropy":float(entropy),
        "mean_shift":float(delta),"background_charge":float(2*mu*rho*delta),"fixed_K":float(a["K"])}

def audit(p,path):
    checks,rows,errors,ids={},[],[],{}
    def flag(n,v):checks[n]={"pass":bool(v)}
    def close(n,v,t):checks[n]={"metric":float(v),"threshold":t,"pass":bool(np.isfinite(v) and v<=t)}
    def greater(n,v,t):checks[n]={"metric":float(v),"minimum":t,"pass":bool(np.isfinite(v) and v>t)}
    rules=p["verification"]
    locked={"locked_before_first_execution":True,"cutoff_factor":60,"branches":["lower","upper"],"parent_over_thermal_k":[.1,1.,10.,60.],"phase_orders":[8,16,32],"background_phases":[0.,.37],"coefficient_amplitudes_over_rho":[.01,.02,.04,.08],"mu_relative_steps":[.001,.0003,.0001],"thermal_orders":[64,128,256],"thermal_relative_steps":[.001,.0003,.0001],"source_conditioned_tolerance":1e-8,"derivative_relative_tolerance":1e-5,"refinement_relative_tolerance":.01,"negative_control_floor":.001,"energy_scale":2,"thermal_branch":"lower","derivative_domain":"fixed_central_K"}
    flag("scope",p["record_role"]=="TREE_MEAN_DENSITY_BACKREACTION_GAUSSIAN_SUBSET_ONLY")
    flag("locked_states",p["temperatures"]==[.002,.004] and p["mu"]==1.28 and p["lambda_exploratory"]==.01)
    flag("locked_controls",rules==locked)
    flag("configuration",p["configuration"]=={"Z":1.,"mass_squared":1.,"response_coupling":0.,"epsilon_nc":0.,"Phi_fixed":.15,"phi_equilibrium":0.})
    required={"full_nonlinear_wave","full_interacting_density_backreaction","interacting_Noether_current","self_consistent_thermal_gap","paper_low_T_accuracy","physical_heat_current","physical_material_frame","SI_charge_atom_mapping","all_channel_collision","physical_frequency_window","physical_UET_operator","physical_HeII_state","physical_J04_executed","physical_J05_executed","physical_J06_executed","formal_verification","external_math_review","interval_certificate","useful_relative_error_certificate","claim_promotion","dependency_unlock"}
    flag("boundary_fields",set(p["admission"])==required)
    for n in sorted(required):flag("boundary/"+n,p["admission"].get(n) is False)
    prior=json.loads((ROOT/p["prior_ward_artifact"]).read_text(encoding="utf-8"))
    flag("prior_source_fresh",all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==s for n,s in prior["input_hashes"].items()))
    flag("prior_scope",prior["status"]=="PASS_TREE_SPATIAL_CURRENT_WARD_REFERENCE_ONLY" and not prior["charge_density_backreaction_completed"] and not prior["physical_heat_current_matched"])
    flag("card_locked",hashlib.sha256((ROOT/p["card"]).read_bytes()).hexdigest()=="be95e3f2131d08507afe4179514a4d63740f11b52a0440b8135caba917fc5171")
    flag("registry_locked",hashlib.sha256(REGISTRY.read_bytes()).hexdigest()=="524d1c3530ab3e875ad9aeac5a0227db7d3e6460197425fe19aea892b14315ef")
    flag("source_binding_name",p["AST_selected_matter_definitions"][-2:]==["coupled_matter_lagrangian_scalar","matter_eom_residual"])
    flag("binding_repair_card_identity",hashlib.sha256((ROOT/p["binding_repair_card"]).read_bytes()).hexdigest()=="6bb3ede2263c626f4fc2906d838ad6c61cc25033b742d731dc5109655900f1cc")
    flag("first_binding_failure_identity",hashlib.sha256((ROOT/p["first_binding_failure"]).read_bytes()).hexdigest()=="25a6a09a48977ed5bd1c00c61c15ce0eaf8e2a70dc707098dab21b18328868aa")
    flag("first_contract_archive_identity",hashlib.sha256((ROOT/p["first_contract_archive"]).read_bytes()).hexdigest()=="60a4941244e4dcbaeb882f1fcf58034cf6b3ec040238ec180d578da42333d537")
    flag("first_verifier_archive_identity",hashlib.sha256((ROOT/p["first_verifier_archive"]).read_bytes()).hexdigest()=="3458fbf3f9db4e58b65f3e6c6f44715bdc8f9458aa21e76b0f44f53d8ff8fe46")
    flag("derivative_center_repair_card_identity",hashlib.sha256((ROOT/p["derivative_center_repair_card"]).read_bytes()).hexdigest()=="f3ee71c8fbf0773f272823577aafcacbf0dd29d05b3d0d12acae96ad7de7780b")
    flag("uncentered_verifier_archive_identity",hashlib.sha256((ROOT/p["uncentered_verifier_archive"]).read_bytes()).hexdigest()=="a641ae467b13c7d40c0a091cdfeddf3f8ab4bae536e1242955bec2b72fec2cc7")
    flag("uncentered_failure_identity",hashlib.sha256((ROOT/p["uncentered_failure"]).read_bytes()).hexdigest()=="542dba0017723653e0bb6607c4e43e5f041da45d8eafca90f2a190e2b8600a0b")
    def finish():
        paths=[path,Path(__file__).resolve(),REGISTRY,ROOT/p["card"]]+[ROOT/p[k] for k in ("prior_ward_contract","prior_ward_verifier","prior_ward_artifact","source_adapter","core_matter_source","core_response_source","binding_repair_card","first_binding_failure","first_contract_archive","first_verifier_archive","derivative_center_repair_card","uncentered_verifier_archive","uncentered_failure")]+[ROOT/n for n in prior["input_hashes"]]
        hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
        passed=len(rows)==2 and all(c["pass"] for c in checks.values()) and not errors
        return {"schema_version":"t010-density-backreaction-audit-v1","date":p["date"],"status":"PASS_LEADING_MEAN_DENSITY_GAUSSIAN_SUBSET_ONLY" if passed else "LEADING_MEAN_DENSITY_DIAGNOSTIC_FAIL",
            "check_count":len(checks),"passing_check_count":sum(v["pass"] for v in checks.values()),"checks":checks,"input_hashes":hashes,
            "source_AST_definition_hashes":ids,"locked_verification":rules,"state_results":rows,"execution_errors":errors,
            "leading_mean_density_backreaction_supported":bool(passed),"fixed_domain_Gaussian_density_Legendre_supported":bool(passed),
            "full_interacting_density_backreaction_completed":False,"full_nonlinear_wave_solved":False,"interacting_Noether_current_completed":False,
            "self_consistent_thermal_gap_solved":False,"paper_low_T_accuracy_admitted":False,"physical_heat_current_matched":False,
            "physical_material_frame_admitted":False,"physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,
            "formal_verification":False,"external_math_review":False,"interval_certified":False,"whole_Core_runtime_executed":False,
            "physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,"physical_frequency_window":None,
            "physical_relaxation_time":None,"live_Phi_executed":False,"useful_relative_error_certified":False,"claim_promotion":False,
            "dependency_unlock":False,"parameters_fitted":False,"thresholds_relaxed":False,
            "unit_powers":{"mean_shift":1,"q_density":3,"e_density":4,"Nwave":3,"q_per_action":0,"e_per_action":1,"thermal_P":4,"thermal_q":3},
            "physical_controller":p["physical_controller"],"controlling_measured_blocker":p["candidate_controller"],
            "notes":["Mean radial response is order-A^2 only; no full nonlinear wave or interacting EOS.","Source errors report cancellation conditioning; no interval certification.","Thermal derivatives hold the central physical K fixed.","Paper T^2>>lambda*mu^2 regime is not admitted for the selected states."]}
    if not all(v["pass"] for v in checks.values()):return finish()
    ward=load(ROOT/p["prior_ward_verifier"],"density_ward_source")
    base=load(ROOT/p["source_adapter"],"density_ast_adapter")
    response,h=base.selected_namespace(ROOT/p["core_response_source"],p["AST_selected_response_definitions"]);ids["response"]=h
    ns,h=base.selected_namespace(ROOT/p["core_matter_source"],p["AST_selected_matter_definitions"],{n:response[n] for n in ("response_displacement","validate_lorentz_metric")});ids["matter"]=h
    wc=json.loads((ROOT/p["prior_ward_contract"]).read_text(encoding="utf-8"))
    bc=json.loads((ROOT/wc["current_bound_contract"]).read_text(encoding="utf-8"))
    continuum=load(ROOT/bc["continuum_verifier"],"density_continuum_source")
    cc=p["configuration"];tol=rules["source_conditioned_tolerance"]
    try:
        for T in p["temperatures"]:
            a=continuum.parameters(T,p["mu"],cc["mass_squared"],p["lambda_exploratory"],60)
            a.update(m2=cc["mass_squared"],lambda_c=p["lambda_exploratory"],Z=cc["Z"],Phi=cc["Phi_fixed"])
            points=[]
            ratio=T*T/(p["lambda_exploratory"]*p["mu"]**2)
            flag(str(T)+"/paper_regime_not_satisfied",ratio<1)
            for branch in rules["branches"]:
                for multiple in rules["parent_over_thermal_k"]:
                    k=multiple*T/a["c"];a["k"]=k;m=ward.mode(k,a,branch);d=densities(a,m);key=str(T)+"/"+branch+"/"+str(multiple)
                    maximum={n:0. for n in ("raw_charge","raw_energy","corrected_charge","corrected_energy","grand_density","tadpole_raw","tadpole_corrected","action","spatial_charge","spatial_energy","phase_order")}
                    final=None;count=0
                    for phase in rules["background_phases"]:
                        last=None
                        for order in rules["phase_orders"]:
                            raw=coefficient(ns,a,m,phase,order,rules["coefficient_amplitudes_over_rho"],False)
                            cor=coefficient(ns,a,m,phase,order,rules["coefficient_amplitudes_over_rho"],True);count+=2
                            targets={"raw_charge":(raw[0],d["q_raw_coefficient"],d["q_raw_coefficient"]),"raw_energy":(raw[1],d["e_raw_coefficient"],d["e_raw_coefficient"]),
                                "corrected_charge":(cor[0],d["q_corrected_coefficient"],d["q_raw_coefficient"]),"corrected_energy":(cor[1],d["e_corrected_coefficient"],d["e_raw_coefficient"]),
                                "grand_density":(cor[1]-a["mu"]*cor[0],d["grand_coefficient"],d["e_raw_coefficient"]),
                                "tadpole_raw":(raw[3],d["radial_force_coefficient"],d["radial_force_coefficient"]),"tadpole_corrected":(cor[3],0.,d["radial_force_coefficient"]),
                                "action":(cor[2],0.,d["e_raw_coefficient"]),"spatial_charge":(cor[4],m["charge_flux"]*m["action_per_amplitude_squared"],m["charge_flux"]*m["action_per_amplitude_squared"]),
                                "spatial_energy":(cor[5],k*m["action_per_amplitude_squared"],k*m["action_per_amplitude_squared"])}
                            for name,(x,y,s) in targets.items():maximum[name]=max(maximum[name],conditioned(x,y,s))
                            if last is not None:maximum["phase_order"]=max(maximum["phase_order"],conditioned(cor[0],last[0],d["q_raw_coefficient"]),conditioned(cor[1],last[1],d["e_raw_coefficient"]))
                            last=cor
                            if phase==0 and order==32:final={"raw":raw.tolist(),"corrected":cor.tolist()}
                    for name,value in maximum.items():close(key+"/"+name,value,tol)
                    close(key+"/charge_root_identity",rel(d["q_per_action"],-m["E_mu"]),tol)
                    close(key+"/raw_plus_condensate",conditioned(d["q_raw_coefficient"]+d["q_condensate_coefficient"],d["q_corrected_coefficient"],d["q_raw_coefficient"]),tol)
                    close(key+"/energy_Legendre",conditioned(d["e_raw_coefficient"]+d["e_condensate_coefficient"],d["e_corrected_coefficient"],d["e_raw_coefficient"]),tol)
                    greater(key+"/omitted_mean_shift_negative",conditioned(d["q_raw_coefficient"],d["q_corrected_coefficient"],d["q_raw_coefficient"]),rules["negative_control_floor"])
                    sweep=[]
                    for step in rules["mu_relative_steps"]:
                        def energy(mu):
                            b=dict(a);b.update(mu=mu,r=mu*mu-a["m2"],B=3*mu*mu-a["m2"])
                            return ward.mode(k,b,branch)["E"]
                        derivative=ward.derivative(lambda offset:energy(a["mu"]+offset),a["mu"]*step)
                        close(key+"/mu_derivative/"+str(step),rel(-derivative,d["q_per_action"]),rules["derivative_relative_tolerance"])
                        sweep.append({"relative_step":step,"q_finite":-derivative,"relative_error":rel(-derivative,d["q_per_action"])})
                    points.append({"branch":branch,"parent_over_thermal_k":multiple,"k":k,"mode":m,"density":d,"source_coefficient_sets":count,"maximum_conditioned_errors":maximum,"source_final":final,
                        "corrected_charge_source_actual_relative_error":rel(final["corrected"][0],d["q_corrected_coefficient"]),"mu_derivative_sweep":sweep})
            ts=[thermal(a,ward,n) for n in rules["thermal_orders"]]
            for v in ts:
                key=str(T)+"/thermal/"+str(v["order"])
                close(key+"/charge_sum",conditioned(v["q_raw"]+v["q_condensate"],v["q_corrected"],v["q_raw"]),tol)
                close(key+"/mean_shift_charge",rel(v["background_charge"],v["q_condensate"]),tol)
                close(key+"/entropy_Legendre",rel(T*v["entropy"]-v["P"],v["U_grand"]),tol)
                greater(key+"/P_positive",v["P"],0);greater(key+"/U_G_positive",v["U_grand"],0)
            for name in ("P","q_corrected","U_grand","mean_shift"):
                close(str(T)+"/thermal_refinement/"+name,rel(ts[-1][name],ts[-2][name]),rules["refinement_relative_tolerance"])
            derivatives=[]
            for step in rules["thermal_relative_steps"]:
                q=ward.derivative(lambda offset:thermal(a,ward,256,mu=a["mu"]+offset)["P"],a["mu"]*step)
                s=ward.derivative(lambda offset:thermal(a,ward,256,T=T+offset)["P"],T*step)
                close(str(T)+"/thermal_mu/"+str(step),rel(q,ts[-1]["q_corrected"]),rules["derivative_relative_tolerance"])
                close(str(T)+"/thermal_T/"+str(step),rel(s,ts[-1]["entropy"]),rules["derivative_relative_tolerance"])
                derivatives.append({"relative_step":step,"fixed_K":a["K"],"q_finite":q,"s_finite":s})
            rows.append({"T":T,"parameters":dict(a),"paper_T_squared_over_lambda_mu_squared":ratio,"mode_points":points,"thermal_sweep":ts,"thermal_derivatives":derivatives})
        a=rows[-1]["parameters"];scale=rules["energy_scale"];b=dict(a)
        b.update(T=a["T"]*scale,mu=a["mu"]*scale,m2=a["m2"]*scale**2,r=a["r"]*scale**2,B=a["B"]*scale**2,K=a["K"]*scale,k=a["k"]*scale,Phi=a["Phi"]*scale)
        for branch in rules["branches"]:
            d=densities(a,ward.mode(a["k"],a,branch));sd=densities(b,ward.mode(b["k"],b,branch))
            for name,power in (("rho",1),("shift_per_amplitude_squared",-1),("q_raw_coefficient",1),("q_corrected_coefficient",1),("e_corrected_coefficient",2),("q_per_action",0),("e_per_action",1)):
                close("scale/"+branch+"/"+name,rel(sd[name],d[name]*scale**power),tol)
        tt=thermal(b,ward,256)
        for name,power in (("P",4),("q_corrected",3),("U_grand",4),("mean_shift",1),("entropy",3)):
            close("scale/thermal/"+name,rel(tt[name],rows[-1]["thermal_sweep"][-1][name]*scale**power),tol)
    except (ValueError,FloatingPointError) as exc:
        errors.append({"type":type(exc).__name__,"message":str(exc)});flag("requested_controls_completed",False)
    flag("complete_states",len(rows)==2)
    return finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--contract-json",type=Path,default=CONTRACT);parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();path=args.contract_json.resolve();a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(a,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"],flush=True)
    failed=[(n,v) for n,v in a["checks"].items() if not v["pass"]]
    if failed:print("FAIL",failed,flush=True)
    return 0 if a["status"]=="PASS_LEADING_MEAN_DENSITY_GAUSSIAN_SUBSET_ONLY" else 1

if __name__=="__main__":raise SystemExit(main())
