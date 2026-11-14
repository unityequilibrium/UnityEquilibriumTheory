"""Independent enriched and smooth vector trials; no continuum or physical admission."""
from __future__ import annotations
import argparse
import ast
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_infrared_trials_contract.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_core_o2_infrared_trials_audit.json"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_infrared_trials_addendum.json"
PRIOR_SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Vector_Refinement.py"

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

v=load(PRIOR_SCRIPT,"infrared_prior_vector")
relative=v.relative

def build_basis(k,w,T,K,N,family):
    if not isinstance(family,tuple):
        return v.build_basis(k,w,T,K,N,family)
    name,epsilon=family
    even,seed_basis=v.build_basis(k,w,T,K,N-1,"EVEN")
    soft=np.full_like(k,T) if name=="HYBRID" else T*k/np.sqrt(k*k+epsilon*epsilon)
    seeds=np.column_stack([k,soft,even[:,1:]])
    G0=seed_basis["G0"];C=np.zeros((N,N));C[0,0]=1.;A=[k.copy()]
    for j in range(1,N):
        column=np.zeros(N);column[j]=1.;trial=seeds[:,j].copy()
        for _ in range(2):
            correction=np.array([np.sum(w*trial*f)/G0 for f in A])
            trial-=np.array(A).T@correction;column-=C[:,:j]@correction
        beta=float(np.sqrt(np.sum(w*trial*trial)/G0))
        if not np.isfinite(beta) or beta<=0:raise ValueError("unresolved seed norm")
        C[:,j]=column/beta;A.append(trial/beta)
    return np.array(A).T,{"family":name,"T":T,"K":K,"G0":G0,
                          "epsilon":epsilon,"seed_even":seed_basis,"transform":C.tolist()}

def evaluate_basis(k,basis):
    if basis["family"] not in ("HYBRID","SMOOTH"):
        return v.evaluate_basis(k,basis)
    k=np.asarray(k);even=v.evaluate_basis(k,basis["seed_even"])
    soft=np.full_like(k,basis["T"]) if basis["family"]=="HYBRID" else basis["T"]*k/np.sqrt(k*k+basis["epsilon"]**2)
    return np.column_stack([k,soft,even[:,1:]])@np.array(basis["transform"])

def stable_geometry(k,p,q,a):
    # Exact d-form Heron identity, with high precision ONLY for an unresolved
    # positive excess. This never modifies the float event weights or occupations.
    consistency=abs(a["B"]-(a["r"]+2*a["mu"]**2))/a["B"]
    if consistency>128*np.finfo(float).eps:
        raise ValueError("inconsistent tree parameters for precision geometry")
    gap=p+q-k
    mask=gap<=128*np.finfo(float).eps*k
    repaired=int(np.sum(mask))
    if repaired:
        with localcontext() as context:
            context.prec=60
            kd=Decimal.from_float(float(k))
            rd=Decimal.from_float(float(a["r"]))
            mud=Decimal.from_float(float(a["mu"]));mu2=mud*mud
            Bd=rd+2*mu2
            def E(z):
                z2=z*z
                return z*((z2+2*rd)/(z2+Bd+(Bd*Bd+4*mu2*z2).sqrt())).sqrt()
            ek=E(kd)
            for index in np.flatnonzero(mask):
                pd=Decimal.from_float(float(p[index]));e=ek-E(pd)
                qd=e*(1+4*mu2/((rd*rd+4*mu2*e*e).sqrt()+rd)).sqrt()
                gap[index]=float(qd-(kd-pd))
    factors=np.stack([gap,2*k+gap,2*(k-p)+gap,2*p-gap],axis=1)
    if np.any(factors<=0):raise ValueError("non-interior high-precision triangle; clipping prohibited")
    pz=p-gap*(2*(k-p)+gap)/(2*k)
    transverse=np.sqrt(np.prod(factors,axis=1))/(2*k)
    PP=np.column_stack((transverse,np.zeros_like(p),pz))
    QQ=np.array([0.,0.,k])-PP
    return factors,PP,QQ,repaired

def collision_tail_ast(source):
    function=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="make_bank")
    loop=next(n for n in function.body if isinstance(n,ast.For))
    start=next(j for j,n in enumerate(loop.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="velocity" for t in n.targets))
    return hashlib.sha256(ast.dump(ast.Module(body=loop.body[start:],type_ignores=[]),include_attributes=False).encode()).hexdigest()

def make_bank(g,T,mu,m2,lam,order,factor,N,family):
    r=mu*mu-m2;B=3*mu*mu-m2;c=np.sqrt(r/B)
    a={"r":r,"B":B,"mu":mu,"g3":mu*np.sqrt(lam)/B**1.5}
    K=factor*T/c;xs,ws=np.polynomial.legendre.leggauss(order)
    k=.5*K*(xs+1);dk=.5*K*ws;fraction=.5*(xs+1);dw=.5*ws
    E=g.energy(k,a);occ=1/np.expm1(E/T)
    w=k*k*dk*occ*(1+occ)/(6*np.pi**2)
    A,basis=build_basis(k,w,T,K,N,family)
    actual=evaluate_basis(k,basis);G=actual.T@(w[:,None]*actual)
    evaluation_error=relative(actual,A)
    root=np.sqrt(B*B+4*mu*mu*k*k)
    da=8*mu**4*k*k/(B*root*(root+B))
    a0=float(np.sum(w*k*k*da)/np.sum(w*k*k));J=k*(da-a0)
    b=actual.T@(w*J);D=float(np.sum(w*J*J))
    lin=(c*k)*c;lin_mean=float(np.sum(w*k*lin)/np.sum(w*k*k))
    lin_D=float(np.sum(w*(lin-lin_mean*k)**2));lin_norm=float(np.sum(w*lin*lin))
    precision_events=0;Q=np.zeros((N,N));max_energy=max_geom=max_balance=max_factor=0.;minimum_triangle=float("inf")
    for parent,Ek,nk,dparent in zip(k,E,occ,dk):
        p=parent*fraction;Ep=g.energy(p,a);q=g.inverse_energy(Ek-Ep,a);Eq=g.energy(q,a)
        factors,PP,QQ,repaired=stable_geometry(parent,p,q,a)
        precision_events+=repaired
        minimum_triangle=min(minimum_triangle,float(np.min(factors)))
        KK=np.array([0.,0.,parent])
        max_energy=max(max_energy,float(np.max(abs(Ek-Ep-Eq)/Ek)))
        max_geom=max(max_geom,float(np.max(abs(np.linalg.norm(QQ,axis=1)-q)/q)),
                     float(np.max(abs(np.linalg.norm(PP,axis=1)-p)/p)))
        velocity=q/Eq*(1-2*mu*mu/np.sqrt(B*B+4*mu*mu*q*q))
        vertex=a["g3"]*(6*Ek*Ep*Eq-2*(Ek*np.einsum("ij,ij->i",PP,QQ)+Ep*(QQ@KK)+Eq*(PP@KK)))
        dgamma=parent*dw*p*q/(Ep*Eq*velocity)*vertex**2/(32*np.pi*Ek*parent)
        npop=1/np.expm1(Ep/T);qpop=1/np.expm1(Eq/T)
        forward=nk*(1+npop)*(1+qpop);reverse=(1+nk)*npop*qpop
        max_balance=max(max_balance,float(np.max(abs(forward-reverse)/np.maximum(forward,reverse))))
        lhs=(1+npop)*(1+qpop)/(1+nk);rhs=1+npop+qpop
        max_factor=max(max_factor,float(np.max(abs(lhs-rhs)/rhs)))
        Ak=evaluate_basis(np.array([parent]),basis)[0];Ap=evaluate_basis(p,basis);Aq=evaluate_basis(q,basis)
        delta=np.array([0.,0.,1.])[None,None,:]*Ak[None,:,None]-Ap[:,:,None]*(PP/p[:,None])[:,None,:]-Aq[:,:,None]*(QQ/q[:,None])[:,None,:]
        weight=parent*parent*dparent/(2*np.pi**2)*dgamma*forward/3
        Q+=np.einsum("a,aij,alj->il",weight,delta,delta,optimize=True)
    return {"T":T,"mu":mu,"m2":m2,"lambda":lam,"order":order,"factor":factor,"family":family,"N":N,
      "basis":basis,"G":G.tolist(),"Q":Q.tolist(),"b":b.tolist(),"D":D,
      "recurrence_evaluation_error":evaluation_error,"Gram_orthogonality_error":relative(G,np.eye(N)*basis["G0"]),
      "raw_momentum_error":float(np.linalg.norm(Q[:,0])/max(np.linalg.norm(Q),1e-300)),
      "source_momentum_error":float(abs(b[0])/max(np.sqrt(G[0,0]*D),1e-300)),
      "linear_current_relative_squared_norm":lin_D/lin_norm,
      "max_event_energy_error":max_energy,"max_event_geometry_error":max_geom,
      "max_detailed_balance_error":max_balance,"max_parent_factor_error":max_factor,
      "minimum_triangle_factor":minimum_triangle,"event_count":order*order,
      "cutoff_E_over_gap":float(g.energy(K,a)/np.sqrt(2*B)),"cutoff_k_over_gap":float(K/np.sqrt(2*B)),
      "collision_kernel_changed":False,"interpolation_used":False,"posterior_collision_projection_used":False,
      "basis_coefficients_fitted_to_response":False,"high_precision_gap_events":precision_events,"source_tree_relation_error":abs(B-(r+2*mu*mu))/B}

def kernel_ast(source):
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="make_bank")
    return hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()

def audit(p,path):
    rules=p["verification"];checks={};banks=[];rows=[];gates=[];cache={};errors=[]
    def flag(name,value):checks[name]={"pass":bool(value)}
    def close(name,value,tolerance):checks[name]={"metric":float(value),"threshold":tolerance,"pass":bool(np.isfinite(value) and value<=tolerance)}
    def positive(name,value):checks[name]={"metric":float(value),"pass":bool(np.isfinite(value) and value>0)}
    flag("scope",p["record_role"]=="INDEPENDENT_ENRICHED_AND_SMOOTH_TRIAL_DIAGNOSTIC_NOT_CONTINUUM_OR_TRANSPORT")
    flag("locked_state",p["mu"]==1.28 and p["lambda_exploratory"]==.01 and p["temperatures"]==[.002,.004])
    flag("locked_sweeps",rules["locked_before_first_execution"] is True and rules["orders"]==[96,192,384] and
         rules["cutoff_factors"]==[40,50,60] and rules["hybrid_feature_orders"]==[6,10,14,18] and
         rules["smooth_deltas"]==[.1,.03,.01,.003] and rules["soft_feature_order"]==35 and
         rules["even_feature_order"]==17 and rules["default_order"]==384 and rules["default_cutoff_factor"]==60)
    flag("locked_targets",rules["refinement_relative_tolerance"]==.01 and
         rules["source_representation_relative_tolerance"]==.01 and rules["algebra_relative_tolerance"]==1e-8 and
         rules["event_relative_tolerance"]==1e-9 and rules["relative_eigenvalue_tolerance"]==1e-9 and
         rules["correspondence_relative_tolerance"]==1e-8 and rules["max_cutoff_energy_over_radial_gap"]==.1)
    required={"continuum_collision_form_domain","continuum_current_upper_bound","physical_heat_current",
       "full_interacting_transport","continuum_spectral_gap","thermalization","physical_frequency_window",
       "collective_sound_damping","live_Phi","physical_UET_operator","physical_HeII_state",
       "physical_J04_executed","physical_J05_executed","physical_J06_executed","claim_promotion","dependency_unlock"}
    flag("admission_fields",set(p["admission"])==required)
    for key in sorted(required):flag("boundary/"+key,p["admission"].get(key) is False)
    old=json.loads((ROOT/p["vector_artifact"]).read_text(encoding="utf-8"))
    flag("historical_failed_targets_retained",old["status"]=="PASS_STABLE_VECTOR_DIAGNOSTIC_ONLY" and old["refinement_gate"]["target_pass"] is False)
    old_kernel_hash=kernel_ast(PRIOR_SCRIPT.read_text(encoding="utf-8"))
    new_kernel_hash=kernel_ast(Path(__file__).read_text(encoding="utf-8"))
    old_tail=collision_tail_ast(PRIOR_SCRIPT.read_text(encoding="utf-8"))
    new_tail=collision_tail_ast(Path(__file__).read_text(encoding="utf-8"))
    flag("unchanged_velocity_vertex_measure_Bose_gain_loss_AST",old_tail==new_tail)
    first_path=TOPIC/"Result/previews/fluid_core_o2_infrared_trials_first_execution.json"
    first_source=TOPIC/"Result/previews/core_o2_infrared_trials_first_execution_verifier.py.txt"
    first=json.loads(first_path.read_text(encoding="utf-8"))
    flag("first_failure_source_identity",hashlib.sha256(first_source.read_bytes()).hexdigest()==first["input_hashes"][Path(__file__).resolve().relative_to(ROOT).as_posix()])
    flag("first_failure_targets_preserved",first["locked_verification"]==rules)
    flag("first_failure_not_relabelled",first["status"]=="ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_FAIL" and bool(first["execution_errors"]))
    source=json.loads((ROOT/p["vector_contract"]).read_text(encoding="utf-8"))
    flag("same_scientific_controls",p["mu"]==source["mu"] and p["lambda_exploratory"]==source["lambda_exploratory"] and p["temperatures"]==source["temperatures"])
    header_pass=all(q["pass"] for q in checks.values())
    def finish():
        paths=[path,ROOT/p["card"],REGISTRY,Path(__file__).resolve(),ROOT/p["vector_contract"],ROOT/p["vector_verifier"],ROOT/p["vector_artifact"]]
        paths += [ROOT/f for f in old["input_hashes"]]
        paths += [first_path,first_source,TOPIC/"CORE_O2_GOLDSTONE_INFRARED_GEOMETRY_REPAIR.md",
                  ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_infrared_geometry_addendum.json"]
        hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
        passed=bool(rows) and all(q["pass"] for q in checks.values()) and not errors
        target_pass=bool(gates) and all(q["pass"] for q in gates)
        return {"schema_version":"t010-core-o2-infrared-trials-audit-v1","date":p["date"],
         "status":"PASS_ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_ONLY" if passed else "ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_FAIL",
         "check_count":len(checks),"passing_check_count":sum(q["pass"] for q in checks.values()),"checks":checks,
         "input_hashes":hashes,"locked_verification":rules,"kernel_AST_hashes":{"prior":old_kernel_hash,"current":new_kernel_hash,
             "full_function_unchanged":old_kernel_hash==new_kernel_hash,
             "prior_collision_tail":old_tail,"current_collision_tail":new_tail},
         "first_execution_record":{"artifact":first_path.relative_to(ROOT).as_posix(),
             "verifier_source_archive":first_source.relative_to(ROOT).as_posix(),
             "status":first["status"],"passing_check_count":first["passing_check_count"],
             "check_count":first["check_count"],"execution_errors":first["execution_errors"]},
         "basis_banks":banks,"state_results":rows,"execution_errors":errors,
         "previous_failed_package":{"artifact":p["vector_artifact"],"sha256":hashes[p["vector_artifact"]],
             "status":old["status"],"refinement_gate":old["refinement_gate"]},
         "refinement_gate":{"status":"PASS_DECLARED_ENRICHED_SMOOTH_TARGETS_ONLY" if target_pass else "MEASURED_ENRICHED_SMOOTH_TARGETS_OPEN",
             "target_pass":target_pass,"state_targets":gates,"physical_admission":False,
             "historical_unenriched_target_pass":False,"continuum_current_closed":False},
         "candidate_controller":p["candidate_controller"],"physical_controller":p["physical_controller"],
         "controlling_measured_blocker":"infrared_collision_form_domain_continuum_current_and_physical_heat_current_admission_open" if target_pass else
            "independent_enriched_or_smooth_infrared_trial_response_not_converged",
         "shared_enriched_smooth_vector_trials_evaluated":bool(rows),
         "Gram_norm_smooth_approximation_lemma":"finite_cutoff_dominated_convergence_only",
         "continuum_collision_form_domain_established":False,"continuum_current_upper_bound_established":False,
         "physical_heat_current_matched":False,"full_interacting_collision_completed":False,
         "continuum_spectral_gap_established":False,"thermalization_derived":False,
         "physical_frequency_window_established":False,"collective_sound_damping_assigned":False,
         "physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,
         "physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,
         "whole_Core_runtime_executed":False,"live_Phi_executed":False,"claim_promotion":False,
         "dependency_unlock":False,"thresholds_relaxed":False,"parameters_fitted":False,
         "notes":["Trial epsilon changes only a vector seed, never kernel/occupation/integration limits.",
                  "Finite quadrature variational ordering is not a rigorous continuum error upper bound.",
                  "Prior EVEN and cross-family failures are retained; no retroactive status promotion.",
                  "Scalar block reused, not rerun; no material heat-current or interacting admission."]}
    if not header_pass:return finish()
    gal=json.loads((ROOT/source["galerkin_contract"]).read_text(encoding="utf-8"))
    core=json.loads((ROOT/gal["core_source_contract"]).read_text(encoding="utf-8"))
    cfg=core["configuration"];mu=p["mu"];m2=cfg["mass_squared"]/cfg["Z"];lam=p["lambda_exploratory"]/cfg["Z"]**2
    g=load(ROOT/source["galerkin_verifier"],"infrared_prior_galerkin")
    c=np.sqrt((mu*mu-m2)/(3*mu*mu-m2));tol=rules["algebra_relative_tolerance"]
    def bank(T,order,factor,family,delta=0.):
        key=(T,order,factor,family,delta)
        if key not in cache:
            N=rules["hybrid_feature_orders"][-1] if family in ("HYBRID","SMOOTH") else rules["soft_feature_order"] if family=="SOFT" else rules["even_feature_order"]
            kind=(family,delta*T/c) if family in ("HYBRID","SMOOTH") else family
            b=make_bank(g,T,mu,m2,lam,order,factor,N,kind);b["family"]=family;b["delta"]=delta;b["bank_id"]=len(banks)
            cache[key]=b;banks.append(b);label=str(key)
            for name in ("recurrence_evaluation_error","Gram_orthogonality_error","raw_momentum_error","source_momentum_error","linear_current_relative_squared_norm"):
                close(label+"/"+name,b[name],tol)
            for name in ("max_event_energy_error","max_event_geometry_error","max_detailed_balance_error","max_parent_factor_error"):
                close(label+"/"+name,b[name],rules["event_relative_tolerance"])
            close(label+"/energy_cutoff",b["cutoff_E_over_gap"],rules["max_cutoff_energy_over_radial_gap"])
            positive(label+"/positive_source",b["D"])
            close(label+"/source_tree_relation",b["source_tree_relation_error"],128*np.finfo(float).eps)
            flag(label+"/no_kernel_patch",not any(b[k] for k in ("collision_kernel_changed","interpolation_used","posterior_collision_projection_used","basis_coefficients_fitted_to_response")))
        return cache[key]
    def summary(b,N=None):
        N=N or b["N"];s=v.response(b,N,rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"]);s["bank_id"]=b["bank_id"]
        label=str((b["T"],b["order"],b["factor"],b["family"],b["delta"],N))
        close(label+"/Gram_condition",s["Gram_condition"]-1,tol)
        close(label+"/DC_spectral",s["DC_spectral_error"],tol)
        close(label+"/frequency_spectral",max(q["spectral_error"] for q in s["frequency_response"]),tol)
        close(label+"/operator_symmetry",s["operator_symmetry_error"],tol)
        flag(label+"/conservation_rank",s["full_spectrum"]["nulls"]==1 and s["full_spectrum"]["negative_resolved"]==0 and s["full_spectrum"]["positive_resolved"]==N-1)
        positive(label+"/positive_R",s["R"]);return s
    def target(targets,name,error):
        targets[name]={"relative_change":float(error),"threshold":.01,"pass":bool(np.isfinite(error) and error<=rules["refinement_relative_tolerance"])}
    try:
        for T in p["temperatures"]:
            targets={};correspond={}
            for family in ("EVEN","SOFT"):
                current=bank(T,192,60,family)
                previous=next(b for b in old["basis_banks"] if b["T"]==T and b["order"]==192 and b["factor"]==60 and b["family"]==family)
                for name in ("G","Q","b","D"):
                    error=relative(current[name],previous[name]);correspond[family+"/"+name]=error
                    close(str(T)+"/immutable_same_family/"+family+"/"+name,error,rules["correspondence_relative_tolerance"])
                fresh=summary(current)
                old_r=next(row for row in old["state_results"] if row["T"]==T)["families"][family]["final"]["R"]
                error=relative(fresh["R"],old_r);correspond[family+"/R"]=error
                close(str(T)+"/immutable_same_family/"+family+"/R",error,rules["correspondence_relative_tolerance"])
            order_rows=[summary(bank(T,o,60,"HYBRID")) for o in rules["orders"]]
            cutoff_rows=[summary(bank(T,rules["default_order"],f,"HYBRID")) for f in rules["cutoff_factors"]]
            hybrid=bank(T,rules["default_order"],60,"HYBRID")
            basis_rows=[summary(hybrid,n) for n in rules["hybrid_feature_orders"]]
            for name,sweep in (("hybrid_order",order_rows),("hybrid_cutoff",cutoff_rows),("hybrid_basis",basis_rows)):
                target(targets,name,max(relative(sweep[-1][k],sweep[-2][k]) for k in ("R","tau_basis")))
            flag(str(T)+"/nested_hybrid",all(basis_rows[j+1]["R"]>=basis_rows[j]["R"]*(1-tol) for j in range(len(basis_rows)-1)))
            even=summary(bank(T,rules["default_order"],60,"EVEN"));soft=summary(bank(T,rules["default_order"],60,"SOFT"));hybrid_r=basis_rows[-1]
            flag(str(T)+"/discrete_variational_ordering",even["R"]<=hybrid_r["R"]*(1+tol) and hybrid_r["R"]<=soft["R"]*(1+tol))
            target(targets,"enriched_cross_family",relative(hybrid_r["R"],soft["R"]))
            target(targets,"hybrid_source",abs(hybrid_r["source_representation_relative_squared_error"]))
            smooth_rows=[summary(bank(T,rules["default_order"],60,"SMOOTH",d)) for d in rules["smooth_deltas"]]
            smooth_order=[summary(bank(T,o,60,"SMOOTH",rules["smooth_deltas"][-1])) for o in rules["orders"]]
            target(targets,"smooth_order",max(relative(smooth_order[-1][k],smooth_order[-2][k]) for k in ("R","tau_basis")))
            target(targets,"smooth_delta",max(relative(smooth_rows[-1][k],smooth_rows[-2][k]) for k in ("R","tau_basis")))
            target(targets,"smooth_to_hybrid",relative(smooth_rows[-1]["R"],hybrid_r["R"]))
            target(targets,"smooth_source",abs(smooth_rows[-1]["source_representation_relative_squared_error"]))
            rows.append({"T":T,"immutable_correspondence":correspond,"hybrid_order_sweep":order_rows,
                "hybrid_cutoff_sweep":cutoff_rows,"hybrid_basis_sweep":basis_rows,"EVEN":even,"HYBRID":hybrid_r,"SOFT":soft,
                "smooth_delta_sweep":smooth_rows,"smooth_order_sweep":smooth_order,"measured_targets":targets})
            gates.append({"T":T,"pass":all(q["pass"] for q in targets.values()),"targets":targets})
        if rows:
            T=p["temperatures"][-1];ref=bank(T,rules["default_order"],60,"SMOOTH",rules["smooth_deltas"][-1]);scale=rules["energy_scale"]
            other=make_bank(g,T*scale,mu*scale,m2*scale**2,lam,ref["order"],60,ref["N"],("SMOOTH",ref["basis"]["epsilon"]*scale))
            for key,power in (("G",5),("Q",6),("b",5),("D",5)):
                close("scale/"+key,relative(np.array(other[key]),np.array(ref[key])*scale**power),tol)
            old_r=summary(ref);new_r=v.response(other,other["N"],rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"])
            for key,power in (("R",4),("tau_basis",-1)):
                close("scale/"+key,relative(new_r[key],old_r[key]*scale**power),tol)
    except (ValueError,np.linalg.LinAlgError) as exc:
        errors.append({"type":type(exc).__name__,"message":str(exc)})
        flag("all_requested_banks_executed",False)
    flag("nonempty_complete_states",len(rows)==len(p["temperatures"]) and bool(rows))
    return finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT);args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"],a["refinement_gate"]["status"],flush=True)
    for row in a["state_results"]:print("T",row["T"],row["measured_targets"],flush=True)
    print("errors",a["execution_errors"],flush=True)
    failed=[(k,v) for k,v in a["checks"].items() if not v["pass"]]
    if failed:print("FAIL",failed,flush=True)
    return 0 if a["status"]=="PASS_ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_ONLY" else 1

if __name__=="__main__":raise SystemExit(main())
