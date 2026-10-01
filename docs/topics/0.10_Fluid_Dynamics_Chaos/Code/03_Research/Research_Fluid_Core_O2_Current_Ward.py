"""Source-verbatim tree spatial Noether/stress and rotating-generator current correspondence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_current_ward_contract.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_current_ward_audit.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_current_ward_addendum.json"

def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def relative(a, b):
    return float(abs(a-b)/max(abs(a), abs(b), 1e-300))

def mode(k, a, branch):
    S = np.sqrt(a["B"]**2+4*a["mu"]**2*k*k)
    E = np.sqrt(k*k*(k*k+2*a["r"])/(k*k+a["B"]+S)) if branch == "lower" else np.sqrt(k*k+a["B"]+S)
    if branch not in ("lower", "upper") or not k > 0:
        raise ValueError("positive momentum and declared mode branch required")
    x = E*E-k*k
    A = -S if branch == "lower" else S
    pol = (k*k-E*E)/(2*a["mu"]*E)
    action = E*(pol*pol+1)/2+a["mu"]*pol
    if not action > 0:
        raise ValueError("positive action norm required")
    return {"E":float(E),"polarization":float(pol),"action_per_amplitude_squared":float(action),
            "group_velocity":float(k*(x-a["r"])/(E*A)),"E_h":float(2*a["mu"]*k/A),
            "E_mu":float(a["mu"]*(3*E*E-k*k)/(E*A)),
            "charge_flux":float(pol*k/action),"grand_flux":float(E*k*(pol*pol+1)/(2*action)),
            "physical_energy_flux":float(k*(E*(pol*pol+1)/2+a["mu"]*pol)/action)}

def field_flux(ns, a, m, amplitude, phase, order, reflected=False):
    """Execute original Core functions with covariant gradients; raise source T indices."""
    rho=np.sqrt(a["r"]/a["lambda_c"])
    Z=a["Z"]
    conf=SimpleNamespace(matter_kinetic=Z,matter_mass_sq=a["m2"]*Z,
                         matter_quartic=a["lambda_c"]*Z**2,response_coupling=0.)
    response=SimpleNamespace(epsilon_nc=0.,phi_equilibrium=0.)
    g=np.diag([-1.,1.,1.,1.])
    rot=np.array([[np.cos(phase),np.sin(phase)],[-np.sin(phase),np.cos(phase)]])
    E,k,pol=m["E"],a["k"],m["polarization"]
    sums=np.zeros(4)
    for angle in 2*np.pi*np.arange(order)/order:
        pair=np.zeros(4)
        for sign in (-1,1):
            u=sign*amplitude*pol*np.cos(angle);v=sign*amplitude*np.sin(angle)
            ut=-sign*amplitude*pol*E*np.sin(angle);vt=sign*amplitude*E*np.cos(angle)
            uz=sign*amplitude*pol*k*np.sin(angle);vz=-sign*amplitude*k*np.cos(angle)
            fields=rot@np.array([rho+u,-v])/np.sqrt(Z)
            gradients=np.zeros((2,4));gradients[:,0]=rot@np.array([ut-a["mu"]*v,-vt-a["mu"]*(rho+u)])/np.sqrt(Z)
            gradients[:,3]=rot@np.array([uz,-vz])/np.sqrt(Z)
            if reflected:
                fields[1]*=-1;gradients[1]*=-1
            current=ns["matter_noether_current"](g,fields,gradients,conf)
            cov=ns["coupled_matter_stress_tensor"](g,g,fields,gradients,a["Phi"],response,conf)
            raised=g@cov@g
            pair+=np.array([current[3],raised[3,0],raised[0,3],cov[3,0]])/2
        sums+=pair/order
    N=amplitude*amplitude*m["action_per_amplitude_squared"]
    return {"charge_flux":float(sums[0]/N),"physical_energy_flux":float(sums[1]/N),
            "momentum_density_weight":float(sums[2]/N),"unraised_stress_weight":float(sums[3]/N),
            "grand_flux":float((sums[1]-a["mu"]*sums[0])/N),"wave_action_density":float(N)}

def derivative(function, step):
    return float((function(-2*step)-8*function(-step)+8*function(step)-function(2*step))/(12*step))

def projection(a, order):
    xs,ws=np.polynomial.legendre.leggauss(order)
    k=a["K"]*(xs+1)/2;dk=a["K"]*ws/2
    modes=[mode(float(v),a,"lower") for v in k]
    E=np.array([m["E"] for m in modes]);N=1/np.expm1(E/a["T"])
    measure=dk*k*k*N*(1+N)/(6*np.pi**2)
    gram=float(np.sum(measure*k*k))
    def project(values):return values-k*np.sum(measure*k*values)/gram
    JE=np.array([m["physical_energy_flux"] for m in modes])
    JN=np.array([m["charge_flux"] for m in modes]);JG=np.array([m["grand_flux"] for m in modes])
    S=np.sqrt(a["B"]**2+4*a["mu"]**2*k*k)
    d=8*a["mu"]**4*k*k/(a["B"]*S*(S+a["B"]))
    dbar=float(np.sum(measure*k*k*d)/gram)
    old=k*(d-dbar)
    pg,pn,pe=project(JG),project(JN),project(JE)
    norm=lambda v:float(np.sum(measure*v*v))
    return {"order":order,"source_G":norm(pg),"old_source_G":norm(old),
        "old_source_correspondence_error":float(np.sqrt(norm(pg-old)/norm(old))),
        "projected_charge_grand_identity_error":float(np.sqrt(norm(pg+a["mu"]*pn)/norm(old))),
        "total_energy_projected_relative_norm":float(np.sqrt(norm(pe)/norm(JE))),
        "total_energy_misidentification_error":float(np.sqrt(norm(JG-JE)/norm(JE))),
        "momentum_Gram":gram,"dbar":dbar}

def audit(p,path):
    checks,rows,errors,identities={},[],[],{}
    def flag(n,v):checks[n]={"pass":bool(v)}
    def close(n,v,t):checks[n]={"metric":float(v),"threshold":t,"pass":bool(np.isfinite(v) and v<=t)}
    def greater(n,v,t=0):checks[n]={"metric":float(v),"minimum":t,"pass":bool(np.isfinite(v) and v>t)}
    rules=p["verification"]
    flag("scope",p["record_role"]=="TREE_SPATIAL_NOETHER_GRANDCANONICAL_CURRENT_REFERENCE_ONLY")
    flag("locked_states",p["mu"]==1.28 and p["temperatures"]==[.002,.004] and p["lambda_exploratory"]==.01)
    controls={"locked_before_first_execution":True,"cutoff_factor":60,"parent_over_thermal_k":[.1,1.,10.,60.],
        "branches":["lower","upper"],"phase_orders":[8,16,32],"amplitude_over_rho":[.001,.002,.004],
        "background_phases":[0.,.37],"flow_parent_over_thermal_k":[1.,10.,60.],"flow_relative_steps":[.001,.0003,.0001],
        "current_orders":[64,128,256],"algebra_relative_tolerance":1e-8,"derivative_relative_tolerance":1e-5,
        "refinement_relative_tolerance":.01,"negative_control_floor":.001,"energy_scale":2}
    flag("locked_controls",rules==controls)
    flag("locked_configuration",p["configuration"]=={"Z":1.,"mass_squared":1.,"response_coupling":0.,"epsilon_nc":0.,"Phi_fixed":.15,"phi_equilibrium":0.})
    required={"full_charge_density_backreaction","interacting_Noether_current","physical_heat_current","physical_material_frame",
        "SI_charge_atom_mapping","all_channel_collision","physical_frequency_window","physical_UET_operator","physical_HeII_state",
        "physical_J04_executed","physical_J05_executed","physical_J06_executed","formal_verification","external_math_review",
        "interval_certificate","useful_relative_error_certificate","claim_promotion","dependency_unlock"}
    flag("boundary_fields",set(p["admission"])==required)
    for key in sorted(required):flag("boundary/"+key,p["admission"].get(key) is False)
    prior=json.loads((ROOT/p["current_bound_artifact"]).read_text(encoding="utf-8"))
    flag("prior_sources_fresh",all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==s for n,s in prior["input_hashes"].items()))
    flag("prior_conditional_bound_only",prior["status"]=="PASS_CONDITIONAL_SELECTED_CURRENT_BOUND_ONLY" and
         prior["selected_current_finiteness_internal_derivation_supported"] and not prior["physical_heat_current_matched"])
    flag("preregistered_card",hashlib.sha256((ROOT/p["card"]).read_bytes()).hexdigest()=="2679190ef730d41212c570a3b962c351bc45f9eb3c879cf3a35617617a3bbc8a")
    flag("preregistered_registry",hashlib.sha256(REGISTRY.read_bytes()).hexdigest()=="4c31a8065e9317f5a15daefafd9e0b4a3fb44367eb24808e9e7863d95e08d4f8")
    def finish():
        paths=[path,ROOT/p["card"],REGISTRY,Path(__file__).resolve()]+[ROOT/p[k] for k in
               ("current_bound_contract","current_bound_verifier","current_bound_artifact","flow_verifier","source_adapter","core_matter_source","core_response_source")]
        paths.extend(ROOT/n for n in prior["input_hashes"])
        hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
        passed=len(rows)==2 and all(c["pass"] for c in checks.values()) and not errors
        return {"schema_version":"t010-current-ward-audit-v1","date":p["date"],
            "status":"PASS_TREE_SPATIAL_CURRENT_WARD_REFERENCE_ONLY" if passed else "TREE_CURRENT_WARD_REFERENCE_FAIL",
            "check_count":len(checks),"passing_check_count":sum(c["pass"] for c in checks.values()),"checks":checks,
            "input_hashes":hashes,"source_AST_definition_hashes":identities,"locked_verification":rules,"state_results":rows,"execution_errors":errors,
            "selected_tree_grandcanonical_flux_correspondence_supported":bool(passed),"selected_tree_spatial_Noether_Ward_supported":bool(passed),
            "physical_heat_current_matched":False,"physical_material_frame_admitted":False,"charge_density_backreaction_completed":False,
            "interacting_Noether_current_completed":False,"useful_relative_error_certified":False,"full_continuum_inverse_executed":False,
            "formal_verification":False,"external_math_review":False,"interval_certified":False,"whole_Core_runtime_executed":False,
            "physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,"physical_frequency_window":None,
            "physical_relaxation_time":None,"live_Phi_executed":False,"physical_J04_executed":False,"physical_J05_executed":False,
            "physical_J06_executed":False,"claim_promotion":False,"dependency_unlock":False,"thresholds_relaxed":False,"parameters_fitted":False,
            "unit_powers":{"Nwave":3,"j_N":3,"T_flux":4,"J_N":0,"J_E":1,"J_G":1,"source_G":5},
            "physical_controller":p["physical_controller"],"controlling_measured_blocker":p["candidate_controller"],
            "notes":["Core stress source with covariant gradients is raised in both indices before energy/momentum comparison.",
                "Tree spatial mode flux is not a complete interacting charge/energy-density/tadpole or material heat-current derivation.",
                "J_G is H-mu Q energy flux; omitting mu*J_N misidentifies it as total energy flux.",
                "Momentum projection does not select zero material mass/charge flow or an experimental He-II frame."]}
    if not all(c["pass"] for c in checks.values()):return finish()
    base=load(ROOT/p["source_adapter"],"ward_source_adapter")
    response,ids=base.selected_namespace(ROOT/p["core_response_source"],p["AST_selected_response_definitions"])
    identities["response"]=ids
    matter,ids=base.selected_namespace(ROOT/p["core_matter_source"],p["AST_selected_matter_definitions"],
                                     {"response_displacement":response["response_displacement"],"validate_lorentz_metric":response["validate_lorentz_metric"]})
    identities["matter"]=ids
    flow=load(ROOT/p["flow_verifier"],"ward_flow_source")
    bound=load(ROOT/p["current_bound_verifier"],"ward_bound_source")
    bc=json.loads((ROOT/p["current_bound_contract"]).read_text(encoding="utf-8"))
    continuum=load(ROOT/bc["continuum_verifier"],"ward_continuum_source")
    cc=p["configuration"];tol=rules["algebra_relative_tolerance"]
    try:
        for T in p["temperatures"]:
            a=continuum.parameters(T,p["mu"],cc["mass_squared"]/cc["Z"],p["lambda_exploratory"]/cc["Z"]**2,60)
            a.update(lambda_c=p["lambda_exploratory"],m2=cc["mass_squared"],Z=cc["Z"],Phi=cc["Phi_fixed"])
            points=[]
            for branch in rules["branches"]:
                for multiple in rules["parent_over_thermal_k"]:
                    k=multiple*T/a["c"];a["k"]=k;m=mode(k,a,branch)
                    key=str(T)+"/"+branch+"/"+str(multiple)
                    maxima={n:0. for n in ("field_charge","field_energy","field_momentum","field_grand","Ward","phase_order")}
                    final=None;executions=0
                    for amp in rules["amplitude_over_rho"]:
                        amplitude=amp*np.sqrt(a["r"]/a["lambda_c"])
                        for phase in rules["background_phases"]:
                            seq=[field_flux(matter,a,m,amplitude,phase,n) for n in rules["phase_orders"]]
                            executions+=len(seq)
                            for v in seq:
                                for metric,target in (("field_charge","charge_flux"),("field_energy","physical_energy_flux"),("field_grand","grand_flux")):
                                    maxima[metric]=max(maxima[metric],relative(v[target],m[target]))
                                maxima["field_momentum"]=max(maxima["field_momentum"],relative(v["momentum_density_weight"],k))
                                maxima["Ward"]=max(maxima["Ward"],relative(v["physical_energy_flux"],v["grand_flux"]+a["mu"]*v["charge_flux"]))
                            maxima["phase_order"]=max(maxima["phase_order"],max(relative(seq[-1][n],seq[-2][n]) for n in ("charge_flux","physical_energy_flux","grand_flux")))
                            if amp==.001 and phase==0:final=seq[-1]
                    for name,value in maxima.items():close(key+"/"+name,value,tol)
                    close(key+"/group_flux",relative(m["grand_flux"],m["E"]*m["group_velocity"]),tol)
                    close(key+"/phase_current",relative(m["charge_flux"],-m["E_h"]),tol)
                    greater(key+"/action_norm",m["action_per_amplitude_squared"])
                    greater(key+"/omitted_charge_negative_control",relative(m["grand_flux"],k),rules["negative_control_floor"])
                    greater(key+"/unraised_index_negative_control",relative(final["unraised_stress_weight"],k),rules["negative_control_floor"])
                    wrong=field_flux(matter,a,m,.001*np.sqrt(a["r"]/a["lambda_c"]),0,32,reflected=True)
                    greater(key+"/charge_convention_negative_control",relative(wrong["charge_flux"],m["charge_flux"]),rules["negative_control_floor"])
                    root_sweep=[]
                    if multiple in rules["flow_parent_over_thermal_k"]:
                        for step in rules["flow_relative_steps"]:
                            index=0 if branch=="lower" else 1
                            dh=derivative(lambda h:flow.positive_roots(k,a["mu"],h,1.,a["m2"],1e-9)[0][index],a["mu"]*step)
                            close(key+"/finite_flow/"+str(step),relative(dh,m["E_h"]),rules["derivative_relative_tolerance"])
                            root_sweep.append({"h_over_mu":step,"E_h_finite":dh,"relative_error":relative(dh,m["E_h"])})
                    qtherm=-m["E_mu"];advective=qtherm*m["group_velocity"]
                    if branch=="lower" and multiple==.1:
                        greater(key+"/naive_charge_advection_negative_control",relative(advective,m["charge_flux"]),rules["negative_control_floor"])
                    points.append({"branch":branch,"parent_over_thermal_k":multiple,"k":k,"mode":m,"maximum_source_errors":maxima,
                                   "source_control_count":executions,"source_final":final,"flow_derivative_sweep":root_sweep,
                                   "thermodynamic_mode_charge":qtherm,"naive_advective_charge_flux":advective,
                                   "complete_density_backreaction":False})
            sweep=[projection(a,n) for n in rules["current_orders"]]
            for v in sweep:
                key=str(T)+"/projection/"+str(v["order"])
                for n in ("old_source_correspondence_error","projected_charge_grand_identity_error","total_energy_projected_relative_norm"):
                    close(key+"/"+n,v[n],tol)
                greater(key+"/source_G",v["source_G"])
                greater(key+"/total_energy_misidentification",v["total_energy_misidentification_error"],rules["negative_control_floor"])
            close(str(T)+"/projection_refinement",relative(sweep[-1]["source_G"],sweep[-2]["source_G"]),rules["refinement_relative_tolerance"])
            rows.append({"T":T,"parameters":dict(a),"mode_points":points,"projection_sweep":sweep})
        a=rows[-1]["parameters"];scale=rules["energy_scale"]
        scaled=continuum.parameters(a["T"]*scale,a["mu"]*scale,a["m2"]*scale**2,a["lambda_c"],60)
        scaled.update(lambda_c=a["lambda_c"],m2=a["m2"]*scale**2,Z=a["Z"],Phi=a["Phi"]*scale)
        for branch in rules["branches"]:
            m=mode(a["k"],a,branch);sm=mode(a["k"]*scale,scaled,branch);scaled["k"]=a["k"]*scale
            for name,power in (("E",1),("charge_flux",0),("grand_flux",1),("physical_energy_flux",1),("action_per_amplitude_squared",1)):
                close("scale/"+branch+"/"+name,relative(sm[name],m[name]*scale**power),tol)
            one=field_flux(matter,a,m,.001*np.sqrt(a["r"]/a["lambda_c"]),0,32)
            two=field_flux(matter,scaled,sm,.001*np.sqrt(scaled["r"]/scaled["lambda_c"]),0,32)
            close("scale/"+branch+"/Nwave",relative(two["wave_action_density"],one["wave_action_density"]*scale**3),tol)
        other=projection(scaled,256)
        close("scale/source_G",relative(other["source_G"],rows[-1]["projection_sweep"][-1]["source_G"]*scale**5),tol)
    except (ValueError,FloatingPointError) as exc:
        errors.append({"type":type(exc).__name__,"message":str(exc)});flag("requested_controls_completed",False)
    flag("complete_states",len(rows)==2)
    return finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT);args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(a,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"],flush=True)
    failed=[(k,v) for k,v in a["checks"].items() if not v["pass"]]
    if failed:print("FAIL",failed,flush=True)
    return 0 if a["status"]=="PASS_TREE_SPATIAL_CURRENT_WARD_REFERENCE_ONLY" else 1

if __name__=="__main__":raise SystemExit(main())
