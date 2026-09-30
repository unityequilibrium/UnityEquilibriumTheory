"""Leading 3D Goldstone 1->2 decay and triad balance; no thermalization admission."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_goldstone_collision_contract.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_core_o2_goldstone_collision_audit.json"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_goldstone_collision_addendum.json"


def relative(a,b):
    return float(np.linalg.norm(np.asarray(a)-np.asarray(b))/max(np.linalg.norm(a),np.linalg.norm(b),1e-300))


def parameters(mu,m2,lam):
    r=mu*mu-m2;B=3*mu*mu-m2
    if min(r,B,lam)<=0:raise ValueError("positive condensed weak-coupling parameters required")
    c=np.sqrt(r/B);g=mu*np.sqrt(lam)/B**1.5
    return {"mu":mu,"m2":m2,"lambda_c":lam,"r":r,"B":B,"c":c,"g3":g,
      "g4":lam/(4*B*B),"curvature":mu**4/(np.sqrt(r)*B**2.5),
      "leading_occupation_coefficient":3*lam*mu**6/(20*np.pi*r*B**4)}


def velocity(q,E,a):
    root=np.sqrt(a["B"]**2+4*a["mu"]**2*q*q)
    return q/E*(1-2*a["mu"]**2/root)


def energy_inverse(target,k,energy):
    lo,hi=0.,k
    for _ in range(60):
        mid=(lo+hi)*.5
        if energy(mid)<target:lo=mid
        else:hi=mid
    return .5*(lo+hi)


def triad(k,p,energy,a,azimuth=0.):
    Ek,Ep=energy(k),energy(p)
    q=energy_inverse(Ek-Ep,k,energy);Eq=energy(q)
    cosine=(k*k+p*p-q*q)/(2*k*p)
    if not -1<=cosine<=1:raise ValueError("no interior curved on-shell triad; clipping prohibited")
    # Place the soft daughter directly. Heron's factored area avoids loss from
    # subtracting two nearly equal large longitudinal parent/daughter vectors.
    qz=((k-p)*(k+p)+q*q)/(2*k)
    area_factors=(p+q-k,p+q+k,k-p+q,k+p-q)
    if min(area_factors)<=0:raise ValueError("non-interior triangle; clipping prohibited")
    transverse=np.sqrt(np.prod(area_factors))/(2*k)
    K=np.array([0.,0.,k]);Q=np.array([-transverse*np.cos(azimuth),-transverse*np.sin(azimuth),qz]);P=K-Q
    vertex=a["g3"]*(6*Ek*Ep*Eq-2*(Ek*(P@Q)+Ep*(K@Q)+Eq*(K@P)))
    return {"k":k,"p":p,"q":q,"energies":[Ek,Ep,Eq],"momenta":[K.tolist(),P.tolist(),Q.tolist()],
      "cosine":cosine,"vertex":float(vertex),"energy_error":relative(Ek,Ep+Eq),
      "momentum_error":relative(K,P+Q),"triangle_error":max(relative(np.linalg.norm(Q),q),relative(np.linalg.norm(P),p))}


def polarized_cubic(row,a):
    # Recover the mixed coefficient by polarization of the reduced pressure:
    # delta X=2mu theta_t+(theta_t^2-grad theta^2), P_cubic=mu/lambda_c theta_t*(theta_t^2-grad theta^2).
    energies=np.array(row["energies"]);momenta=np.array(row["momenta"])
    incoming=np.column_stack((energies,momenta));incoming[0]*=-1
    scale=np.sqrt(a["lambda_c"]/a["B"])
    coefficient=0.
    for s0 in (-1.,1.):
        for s1 in (-1.,1.):
            for s2 in (-1.,1.):
                t,*space=scale*(np.array([s0,s1,s2])@incoming)
                coefficient+=s0*s1*s2*(a["mu"]/a["lambda_c"])*t*(t*t-np.dot(space,space))/8
    return float(coefficient)


def decay(k,order,energy,a):
    x,w=np.polynomial.legendre.leggauss(order);momenta=.5*k*(x+1);weights=.5*k*w
    total=0.;errors=[];cosines=[]
    for p,weight in zip(momenta,weights):
        row=triad(k,float(p),energy,a);Ek,Ep,Eq=row["energies"];q=row["q"]
        v=velocity(q,Eq,a)
        total+=weight*p*q/(Ep*Eq*v)*row["vertex"]**2
        errors.append(max(row["energy_error"],row["momentum_error"],row["triangle_error"]))
        cosines.append(row["cosine"])
    rate=float(total/(32*np.pi*energy(k)*k))
    return {"order":order,"occupation_rate":rate,"pole_amplitude_damping":rate/2,
      "rate_over_k5":rate/k**5,"rate_over_energy":rate/energy(k),
      "max_on_shell_error":max(errors),"cosine_interval":[min(cosines),max(cosines)]}


def balance(row,T):
    energies=np.array(row["energies"])
    N=1/np.expm1(energies/T)
    forward=N[0]*(1+N[1])*(1+N[2]);reverse=(1+N[0])*N[1]*N[2]
    # Off-shell control: change one energy, not the invariant momenta.
    shifted=energies.copy();shifted[1]*=1.05;Nb=1/np.expm1(shifted/T)
    wrong=relative(Nb[0]*(1+Nb[1])*(1+Nb[2]),(1+Nb[0])*Nb[1]*Nb[2])
    return {"forward":float(forward),"reverse":float(reverse),"relative_error":relative(forward,reverse),
       "off_shell_relative_defect":wrong,"weight":float(forward*row["vertex"]**2)}


def audit(p,path):
    spec=importlib.util.spec_from_file_location("goldstone_base",ROOT/p["source_adapter"])
    base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    original=json.loads((ROOT/p["source_contract"]).read_text(encoding="utf-8"))
    ns,AST=base.source_functions(original);rules=p["verification"];checks={}
    def flag(name,v):checks[name]={"pass":bool(v)}
    def close(name,v,t):checks[name]={"metric":float(v),"threshold":t,"pass":bool(np.isfinite(v) and v<=t)}
    def greater(name,v,t=0.):checks[name]={"metric":float(v),"minimum":t,"pass":bool(np.isfinite(v) and v>t)}
    flag("scope",p["record_role"]=="LOW_ENERGY_TREE_GOLDSTONE_CHANNEL_NOT_THERMALIZATION")
    flag("source_state_unchanged",p["configuration"]==original["configuration"])
    flag("locked_nonempty_parameters",p["exploratory_couplings"]==[.01,.001] and
      p["momenta"]==[.02,.01,.005] and p["mu"]==1.28)
    flag("locked_rules",rules["locked_before_first_execution"] is True and rules["orders"]==[48,96,192] and
      rules["leading_coefficient_relative_tolerance"]==.001 and rules["order_relative_tolerance"]==1e-7 and
      rules["energy_relative_tolerance"]==1e-11)
    for name,value in p["admission"].items():flag("boundary/"+name,value is False)
    rows=[]
    for lam in p["exploratory_couplings"]:
        c=p["configuration"];mu=p["mu"];local=json.loads(json.dumps(original));local["configuration"]["lambda"]=lam
        cfg=base.configuration(local,128,70)
        m2=ns["finite_density"]["effective_mass_sq"](c["Phi_fixed"],cfg.eos)/c["Z"]
        a=parameters(mu,m2,lam/c["Z"]**2)
        def energy(k):return ns["EOS"]["condensed_quasiparticle_energies"](float(k),mu,c["Phi_fixed"],cfg)[1]
        gap=ns["EOS"]["condensed_quasiparticle_energies"](0.,mu,c["Phi_fixed"],cfg)[0]
        rates=[]
        for k in p["momenta"]:
            label=str(lam)+"/"+str(k);sweep=[decay(k,o,energy,a) for o in rules["orders"]];ref=sweep[-1]
            greater(label+"/positive_rate",ref["occupation_rate"])
            close(label+"/order_refinement",relative(sweep[-1]["occupation_rate"],sweep[-2]["occupation_rate"]),rules["order_relative_tolerance"])
            close(label+"/on_shell",ref["max_on_shell_error"],rules["energy_relative_tolerance"])
            close(label+"/leading_k5_coefficient",relative(ref["rate_over_k5"],a["leading_occupation_coefficient"]),rules["leading_coefficient_relative_tolerance"])
            close(label+"/pole_vs_occupation",relative(2*ref["pole_amplitude_damping"],ref["occupation_rate"]),rules["algebra_relative_tolerance"])
            curvature=(energy(k)/k-a["c"])/(k*k)
            close(label+"/source_curvature",relative(curvature,a["curvature"]),rules["curvature_relative_tolerance"])
            h=k*rules["velocity_step_fraction"];finite=(energy(k+h)-energy(k-h))/(2*h)
            close(label+"/group_velocity",relative(finite,velocity(k,energy(k),a)),rules["finite_velocity_relative_tolerance"])
            greater(label+"/weak_width",.001-ref["rate_over_energy"])
            greater(label+"/low_energy_scale",.01-k/gap)
            probes=[];floor=rules["negative_control_floor"]
            for i,fraction in enumerate(rules["triad_fractions"]):
                row=triad(k,k*fraction,energy,a,.7*i);b=balance(row,rules["equilibrium_balance_temperature"])
                close(label+"/vertex_polarization/"+str(fraction),relative(abs(row["vertex"]),abs(polarized_cubic(row,a))),rules["algebra_relative_tolerance"])
                close(label+"/detailed_balance/"+str(fraction),b["relative_error"],rules["energy_relative_tolerance"])
                greater(label+"/off_shell_detected/"+str(fraction),b["off_shell_relative_defect"],floor)
                probes.append({**row,"balance":b})
            rates.append({"k":k,"order_sweep":sweep,"final":ref,"curvature_from_source":float(curvature),"triads":probes})
        flag(str(lam)+"/positive_curvature",a["curvature"]>0)
        rows.append({"lambda_exploratory":lam,"parameters":a,"radial_gap":gap,"rates":rates})
    if len(rows)==2:
        for i,k in enumerate(p["momenta"]):
            ratio=rows[0]["rates"][i]["final"]["occupation_rate"]/rows[1]["rates"][i]["final"]["occupation_rate"]
            close("coupling_scaling/"+str(k),relative(ratio,p["exploratory_couplings"][0]/p["exploratory_couplings"][1]),rules["algebra_relative_tolerance"])
    else:flag("coupling_scaling_available",False)
    nr=[]
    for delta in rules["nr_relative_mu"]:
        # m=1, leading NR density; no assignment to a measured material.
        a=parameters(1+delta,1,.01);nNR=2*delta/.01
        expected=3/(640*np.pi*nNR);derived=a["leading_occupation_coefficient"]/2
        nr.append({"mu_NR_over_m":delta,"pole_coefficient":derived,"NR_leading_coefficient":expected,
            "relative_error":relative(derived,expected)})
    close("NR_pole_coefficient_limit",nr[-1]["relative_error"],rules["nr_coefficient_relative_tolerance"])
    greater("factor_two_error_detected",relative(nr[-1]["pole_coefficient"]*2,nr[-1]["NR_leading_coefficient"]),rules["negative_control_floor"])
    # A full zero external derivative kills the cubic vertex; constant contact does not.
    if rows:
        a=rows[0]["parameters"];r0=rows[0]["rates"][-1]["triads"][0]
        soft={**r0,"energies":[r0["energies"][0],0.,r0["energies"][2]],
              "momenta":[r0["momenta"][0],[0.,0.,0.],r0["momenta"][2]]}
        close("full_four_momentum_soft_vertex",abs(polarized_cubic(soft,a)),rules["algebra_relative_tolerance"])
        greater("constant_contact_soft_error_detected",a["lambda_c"],rules["negative_control_floor"])
        chosen=rows[0]["rates"][1]["triads"];size=3*len(chosen)
        incidence=np.zeros((len(chosen),size));energies=[];momenta=[];weights=[]
        for i,row in enumerate(chosen):
            incidence[i,3*i:3*i+3]=[1.,-1.,-1.]
            energies.extend(row["energies"]);momenta.extend(row["momenta"]);weights.append(row["balance"]["weight"])
        weights=np.array(weights)/max(weights) # normalized diagnostic, not a physical spectral operator.
        C=incidence.T@np.diag(weights)@incidence;eigen=np.linalg.eigvalsh(C)
        close("triad_energy_invariant",np.linalg.norm(incidence@energies)/np.linalg.norm(energies),rules["energy_relative_tolerance"])
        close("triad_momentum_invariant",np.linalg.norm(incidence@momenta)/np.linalg.norm(momenta),rules["energy_relative_tolerance"])
        close("triad_operator_symmetry",relative(C,C.T),rules["algebra_relative_tolerance"])
        greater("triad_entropy_PSD",float(min(eigen))+rules["algebra_relative_tolerance"])
        greater("phonon_number_not_invariant",np.linalg.norm(incidence@np.ones(size)),rules["negative_control_floor"])
        phi=np.linspace(-.8,.9,size);lhs=float(phi@C@phi);rhs=float(np.sum(weights*(incidence@phi)**2))
        close("entropy_form_independent",relative(lhs,rhs),rules["algebra_relative_tolerance"])
        nulls=int(np.sum(abs(eigen)<rules["algebra_relative_tolerance"]))
        flag("extra_disconnected_null_modes_retained",nulls==2*len(chosen) and nulls>4)
        graph={"incidence":incidence.tolist(),"normalized_operator":C.tolist(),"eigenvalues":eigen.tolist(),
            "null_mode_count":nulls,"expected_conservation_invariants":4,"normalization":"maximum triad weight scaled to one; no physical rate/gap",
            "connected_continuum":False,"transport_time":None}
    else:
        graph=None;flag("nonempty_triad_graph",False)
    paths=[path,ROOT/p["card"],REGISTRY,Path(__file__).resolve(),ROOT/p["source_adapter"],ROOT/p["source_contract"]]+[
      ROOT/v for v in original["core_sources"].values()]+[ROOT/v for v in p["reused_inputs"]]
    archive=TOPIC/"Result/previews/fluid_core_o2_goldstone_collision_first_execution.json"
    archive_source=TOPIC/"Result/previews/core_o2_goldstone_collision_first_execution_verifier.py.txt"
    paths.extend([archive,archive_source])
    hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
    passed=all(q["pass"] for q in checks.values())
    return {"schema_version":"t010-core-o2-goldstone-collision-audit-v1","date":p["date"],
      "status":"PASS_LEADING_GOLDSTONE_CHANNEL_ONLY" if passed else "LEADING_GOLDSTONE_CHANNEL_FAIL",
      "check_count":len(checks),"passing_check_count":sum(q["pass"] for q in checks.values()),"checks":checks,
      "input_hashes":hashes,"source_AST_definition_hashes":AST,"locked_verification":rules,
      "state_results":rows,"nonrelativistic_coefficient_controls":nr,"disconnected_triad_diagnostic":graph,
      "candidate_controller":p["passed_reference_next_controller"] if passed else p["previous_candidate_controller"],
      "physical_controller":p["physical_controller"],"leading_tree_cubic_channel_checked":bool(rows),
      "finite_temperature_rate_emitted":False,"thermalization_derived":False,"collision_spectral_gap_established":False,
      "physical_frequency_window_established":False,"collective_two_fluid_sound_damping_assigned":False,
      "whole_Core_runtime_executed":False,"live_Phi_executed":False,"complete_nonlinear_operator_derived":False,
      "physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,"physical_prediction_executed":False,
      "physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,
      "claim_promotion":False,"dependency_unlock":False,"thresholds_relaxed":False,"parameters_fitted":False,
      "first_execution_record":{"artifact":archive.relative_to(ROOT).as_posix(),
        "verifier_source_archive":archive_source.relative_to(ROOT).as_posix(),
        "status":"LEADING_GOLDSTONE_CHANNEL_FAIL","passing_checks":153,"check_count":159,
        "repair":"factored triangle/soft-daughter placement replaces cancellation-sensitive cosine reconstruction; no threshold or rate formula change",
        "role":"immutable historical diagnostic, not current-source evidence"},
      "remaining_blockers":["connected_condensed_collision_vector_heat_current_projection_and_convergence",
        "interacting_finite_temperature_state_and_hydrodynamic_frequency_window",
        "nonlinear_live_response_and_material_SI_independent_source_admission"],
      "notes":["Leading vertex plus exact source tree kinematics is only an asymptotic channel diagnostic.",
        "Exploratory .01/.001 couplings do not recalibrate the previous lambda=1 ideal state.",
        "Positive disconnected triads and single-mode decay do not derive entropy conservation or transport thermalization.",
        "Historical Topic13 lane-specific Kubo/contact evidence is preserved; rates are not mapped to hydrodynamic normal/super velocities."]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(a,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"])
    for row in a["state_results"]:
        print("lambda",row["lambda_exploratory"],"rates",[(r["k"],r["final"]["occupation_rate"]) for r in row["rates"]])
    failed=[(n,v) for n,v in a["checks"].items() if not v["pass"]]
    if failed:print("FAIL",failed)
    return 0 if not failed else 1


if __name__=="__main__":
    raise SystemExit(main())
