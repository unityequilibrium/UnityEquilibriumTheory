"""Stable shared vector recurrences and soft trial-space refinement; no transport admission."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_vector_refinement_contract.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_core_o2_vector_refinement_audit.json"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_vector_refinement_addendum.json"


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def relative(a,b):
    return float(np.linalg.norm(np.asarray(a)-np.asarray(b))/max(np.linalg.norm(a),np.linalg.norm(b),1e-300))


def build_basis(k,w,T,K,N,family):
    G0=float(np.sum(w*k*k));A=[k.copy()];rows=[]
    x=(k/K)**(2 if family=="EVEN" else 1)
    for j in range(1,N):
        trial=np.full_like(k,T) if family=="SOFT" and j==1 else x*A[-1]
        coefficient=np.zeros(j)
        for _ in range(2):
            correction=np.array([np.sum(w*trial*v)/G0 for v in A])
            coefficient+=correction;trial=trial-np.array(A).T@correction
        beta=float(np.sqrt(np.sum(w*trial*trial)/G0))
        if not np.isfinite(beta) or beta<=0:raise ValueError("unresolved positive recurrence norm")
        A.append(trial/beta);rows.append({"projection":coefficient.tolist(),"beta":beta})
    return np.array(A).T,{"family":family,"T":T,"K":K,"G0":G0,"rows":rows}


def evaluate_basis(k,basis):
    k=np.asarray(k);A=[k.copy()];x=(k/basis["K"])**(2 if basis["family"]=="EVEN" else 1)
    for j,row in enumerate(basis["rows"],1):
        trial=np.full_like(k,basis["T"]) if basis["family"]=="SOFT" and j==1 else x*A[-1]
        A.append((trial-np.array(A).T@np.array(row["projection"]))/row["beta"])
    return np.array(A).T


def coordinate_even(basis,N):
    C=np.zeros((N,N));C[0,0]=1.
    for j,row in enumerate(basis["rows"][:N-1],1):
        trial=np.r_[0.,C[:-1,j-1]]-C[:,:j]@np.array(row["projection"])
        C[:,j]=trial/row["beta"]
    return C


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
    Q=np.zeros((N,N));max_energy=max_geom=max_balance=max_factor=0.;minimum_triangle=float("inf")
    for parent,Ek,nk,dparent in zip(k,E,occ,dk):
        p=parent*fraction;Ep=g.energy(p,a);q=g.inverse_energy(Ek-Ep,a);Eq=g.energy(q,a)
        qz=((parent-p)*(parent+p)+q*q)/(2*parent)
        factors=np.stack([p+q-parent,p+q+parent,parent-p+q,parent+p-q],axis=1)
        minimum_triangle=min(minimum_triangle,float(np.min(factors)))
        if np.any(factors<=0):raise ValueError("non-interior triangle; clipping prohibited")
        transverse=np.sqrt(np.prod(factors,axis=1))/(2*parent)
        KK=np.array([0.,0.,parent]);QQ=np.column_stack((-transverse,np.zeros_like(q),qz));PP=KK-QQ
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
      "basis_coefficients_fitted_to_response":False}


def response(bank,N,tol,ratios):
    G=np.array(bank["G"])[:N,:N];Q=np.array(bank["Q"])[:N,:N];b=np.array(bank["b"])[:N]
    Gr=G[1:,1:]-np.outer(G[1:,0],G[0,1:])/G[0,0]
    Qr=Q[1:,1:];br=b[1:]-G[1:,0]*b[0]/G[0,0]
    chol=np.linalg.cholesky(Gr);inverse=np.linalg.inv(chol);C=inverse@Qr@inverse.T
    eig,V=np.linalg.eigh(C)
    if np.min(eig)<=0:raise ValueError("unresolved positive reduced basis; no clipping or regulator")
    amplitudes=V.T@(inverse@br)
    R=float(br@np.linalg.solve(Qr,br));spectral=float(np.sum(amplitudes**2/eig))
    represented=float(br@np.linalg.solve(Gr,br));freq=[]
    for ratio in ratios:
        omega=float(np.min(eig))*ratio
        direct=br@np.linalg.solve(Qr-1j*omega*Gr,br)
        other=np.sum(amplitudes**2/(eig-1j*omega))
        freq.append({"ratio":ratio,"real":float(direct.real),"imag":float(direct.imag),"spectral_error":relative(direct,other)})
    full=g_spectrum(G,Q,tol)
    return {"N":N,"R":R,"tau_basis":R/bank["D"],"Gram_condition":float(np.linalg.cond(G)),
      "source_representation_relative_squared_error":float((bank["D"]-represented)/bank["D"]),
      "DC_spectral_error":relative(R,spectral),"operator_symmetry_error":relative(C,C.T),
      "reduced_rates":eig.tolist(),"full_spectrum":full,"frequency_response":freq,
      "physical_time":None}


def g_spectrum(G,Q,tol):
    inverse=np.linalg.inv(np.linalg.cholesky(G));C=inverse@Q@inverse.T;v=np.linalg.eigvalsh(C)
    threshold=float(max(abs(v)))*tol
    return {"rates":v.tolist(),"nulls":int(np.sum(abs(v)<=threshold)),
      "negative_resolved":int(np.sum(v < -threshold)),"positive_resolved":int(np.sum(v>threshold))}


def audit(p,path):
    rules=p["verification"];checks={}
    def flag(name,v):checks[name]={"pass":bool(v)}
    def close(name,v,t):checks[name]={"metric":float(v),"threshold":t,"pass":bool(np.isfinite(v) and v<=t)}
    def greater(name,v,t=0.):checks[name]={"metric":float(v),"minimum":t,"pass":bool(np.isfinite(v) and v>t)}
    flag("scope",p["record_role"]=="STABLE_VECTOR_AND_SOFT_VARIATIONAL_REFINEMENT_NOT_TRANSPORT")
    flag("locked_state",p["temperatures"]==[.002,.004] and p["mu"]==1.28 and p["lambda_exploratory"]==.01)
    flag("locked_targets",rules["locked_before_first_execution"] is True and rules["orders"]==[96,144,192] and
         rules["cutoff_factors"]==[40,50,60] and rules["even_feature_orders"]==[5,9,13,17] and
         rules["soft_feature_orders"]==[5,9,17,25,35] and rules["refinement_relative_tolerance"]==.01)
    for k,v in p["admission"].items():flag("boundary/"+k,v is False)
    prior=json.loads((ROOT/p["galerkin_contract"]).read_text(encoding="utf-8"))
    old=json.loads((ROOT/p["galerkin_artifact"]).read_text(encoding="utf-8"))
    flag("prior_failure_retained",old["status"]=="PASS_FINITE_GALERKIN_DIAGNOSTIC_ONLY" and old["refinement_gate"]["target_pass"] is False)
    flag("same_scientific_controls",p["temperatures"]==prior["temperatures"] and p["mu"]==prior["mu"] and p["lambda_exploratory"]==prior["lambda_exploratory"])
    g=load(ROOT/p["galerkin_verifier"],"stable_prior_galerkin")
    core=json.loads((ROOT/prior["core_source_contract"]).read_text(encoding="utf-8"))
    config=core["configuration"];mu=p["mu"];m2=config["mass_squared"]/config["Z"];lam=p["lambda_exploratory"]/config["Z"]**2
    cache={};banks=[];rows=[];tol=rules["algebra_relative_tolerance"];etol=rules["event_relative_tolerance"]
    def bank(T,order,factor,family):
        key=(T,order,factor,family)
        if key not in cache:
            N=rules["even_feature_orders"][-1] if family=="EVEN" else rules["soft_feature_orders"][-1]
            b=make_bank(g,T,mu,m2,lam,order,factor,N,family);cache[key]=b;b["bank_id"]=len(banks);banks.append(b)
            label=str(key)
            for name in ("recurrence_evaluation_error","Gram_orthogonality_error","raw_momentum_error","source_momentum_error","linear_current_relative_squared_norm"):
                close(label+"/"+name,b[name],tol)
            for name in ("max_event_energy_error","max_event_geometry_error","max_detailed_balance_error","max_parent_factor_error"):
                close(label+"/"+name,b[name],etol)
            close(label+"/energy_cutoff",b["cutoff_E_over_gap"],rules["max_cutoff_energy_over_radial_gap"])
            greater(label+"/positive_source",b["D"])
            flag(label+"/no_kernel_patch",not any(b[k] for k in ("collision_kernel_changed","interpolation_used","posterior_collision_projection_used","basis_coefficients_fitted_to_response")))
        return cache[key]
    def summarize(b,N):
        v=response(b,N,rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"]);v["bank_id"]=b["bank_id"]
        label=str((b["T"],b["order"],b["factor"],b["family"],N))
        close(label+"/Gram_condition",v["Gram_condition"]-1,tol)
        close(label+"/DC_spectral",v["DC_spectral_error"],tol)
        close(label+"/frequency_spectral",max(q["spectral_error"] for q in v["frequency_response"]),tol)
        close(label+"/operator_symmetry",v["operator_symmetry_error"],tol)
        flag(label+"/expected_momentum_null",v["full_spectrum"]["nulls"]==1)
        flag(label+"/positive_resolved",v["full_spectrum"]["negative_resolved"]==0 and v["full_spectrum"]["positive_resolved"]==N-1)
        greater(label+"/positive_R",v["R"]);return v
    gates=[]
    for T in p["temperatures"]:
        results={};targets={}
        for family,ns in [("EVEN",rules["even_feature_orders"]),("SOFT",rules["soft_feature_orders"])]:
            order_rows=[summarize(bank(T,o,rules["default_cutoff_factor"],family),ns[-1]) for o in rules["orders"]]
            cutoff_rows=[summarize(bank(T,rules["default_order"],f,family),ns[-1]) for f in rules["cutoff_factors"]]
            refbank=bank(T,rules["default_order"],rules["default_cutoff_factor"],family)
            basis_rows=[summarize(refbank,n) for n in ns]
            flag(str(T)+"/"+family+"/nested_R",all(basis_rows[i+1]["R"]>=basis_rows[i]["R"]*(1-tol) for i in range(len(basis_rows)-1)))
            for kind,sweep in [("order",order_rows),("cutoff",cutoff_rows),("basis",basis_rows)]:
                error=max(relative(sweep[-1][k],sweep[-2][k]) for k in ("R","tau_basis"))
                targets[family+"/"+kind]={"relative_change":error,"threshold":.01,"pass":error<=rules["refinement_relative_tolerance"]}
            error=abs(basis_rows[-1]["source_representation_relative_squared_error"])
            targets[family+"/source"]={"relative_squared_error":error,"threshold":.01,"pass":error<=rules["source_representation_relative_tolerance"]}
            results[family]={"order_sweep":order_rows,"cutoff_sweep":cutoff_rows,"basis_sweep":basis_rows,"final":basis_rows[-1]}
        even,soft=results["EVEN"]["final"],results["SOFT"]["final"]
        flag(str(T)+"/soft_superset_variational_bound",soft["R"]>=even["R"]*(1-tol))
        cross=relative(soft["R"],even["R"]);targets["cross_family"]={"relative_change":cross,"threshold":.01,"pass":cross<=rules["refinement_relative_tolerance"]}
        # Independent same-span coordinate comparison with the immutable raw implementation.
        reference_bank=bank(T,72,40,"EVEN");N=5;C=coordinate_even(reference_bank["basis"],N)
        raw=g.state(T,mu,m2,lam,72,40,N,rules["relative_eigenvalue_tolerance"])
        new=response(reference_bank,N,rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"])
        correspond={}
        for key,oldkey in [("G","Gram_vector"),("Q","collision_vector")]:
            error=relative(np.array(reference_bank[key])[:N,:N],C.T@np.array(raw[oldkey])@C)
            correspond[key]=error;close(str(T)+"/same_span/"+key,error,rules["same_span_relative_tolerance"])
        error=relative(np.array(reference_bank["b"])[:N],C.T@np.array(raw["source_vector"]))
        correspond["source"]=error;close(str(T)+"/same_span/source",error,rules["same_span_relative_tolerance"])
        error=relative(new["R"],raw["current_response"]);correspond["R"]=error
        close(str(T)+"/same_span/R",error,rules["same_span_relative_tolerance"])
        rows.append({"T":T,"families":results,"measured_targets":targets,"same_span_correspondence":correspond})
        gates.append({"T":T,"pass":all(q["pass"] for q in targets.values()),"targets":targets})
    if rows:
        T=p["temperatures"][-1];ref=bank(T,rules["default_order"],rules["default_cutoff_factor"],"SOFT");scale=rules["energy_scale"]
        scaled=make_bank(g,T*scale,mu*scale,m2*scale**2,lam,ref["order"],ref["factor"],ref["N"],"SOFT")
        for key,power in [("G",5),("Q",6),("b",5),("D",5)]:
            close("scale/"+key,relative(np.array(scaled[key]),np.array(ref[key])*scale**power),tol)
        original_r=response(ref,ref["N"],rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"])
        scaled_r=response(scaled,ref["N"],rules["relative_eigenvalue_tolerance"],rules["frequency_over_min_basis_rate"])
        for key,power in [("R",4),("tau_basis",-1)]:
            close("scale/"+key,relative(scaled_r[key],original_r[key]*scale**power),tol)
        scale_record={"factor":scale,"R":scaled_r["R"],"tau_basis":scaled_r["tau_basis"]}
    else:scale_record=None;flag("nonempty_banks",False)
    paths=[path,ROOT/p["card"],REGISTRY,Path(__file__).resolve(),ROOT/p["galerkin_contract"],ROOT/p["galerkin_verifier"],ROOT/p["galerkin_artifact"]]
    paths += [ROOT/f for f in old["input_hashes"]]
    hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
    passed=all(q["pass"] for q in checks.values());converged=bool(gates) and all(q["pass"] for q in gates)
    failures=[{"T":q["T"],"target":k} for q in gates for k,v in q["targets"].items() if not v["pass"]]
    return {"schema_version":"t010-core-o2-vector-refinement-audit-v1","date":p["date"],
      "status":"PASS_STABLE_VECTOR_DIAGNOSTIC_ONLY" if passed else "STABLE_VECTOR_DIAGNOSTIC_FAIL",
      "check_count":len(checks),"passing_check_count":sum(q["pass"] for q in checks.values()),"checks":checks,
      "input_hashes":hashes,"locked_verification":rules,"basis_banks":banks,"state_results":rows,"scale_control":scale_record,
      "refinement_gate":{"status":"PASS_CURRENT_FINITE_TARGETS_ONLY" if converged else "MEASURED_REFINEMENT_TARGETS_OPEN",
          "target_pass":converged,"state_targets":gates,"failed_targets":failures,"physical_admission":False},
      "candidate_controller":p["candidate_controller"],"physical_controller":p["physical_controller"],
      "controlling_measured_blocker":"stable_finite_vector_refinement_passed_but_continuum_physical_current_admission_open" if converged else
          "stable_vector_basis_cross_family_or_cutoff_current_response_not_converged",
      "stable_shared_vector_basis_evaluated":bool(rows),"physical_heat_current_matched":False,
      "full_interacting_collision_completed":False,"continuum_spectral_gap_established":False,"thermalization_derived":False,
      "physical_frequency_window_established":False,"collective_sound_damping_assigned":False,
      "physical_UET_operator_admitted":False,"physical_HeII_state_assigned":False,
      "physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,
      "whole_Core_runtime_executed":False,"live_Phi_executed":False,"claim_promotion":False,"dependency_unlock":False,
      "thresholds_relaxed":False,"parameters_fitted":False,
      "notes":["EVEN same-span checks isolate numerical conditioning from changes in trial space.",
               "SOFT enrichment is Hilbert-admissible, not a fitted distribution or a discontinuity in matter phase.",
               "Original failed Galerkin package remains unchanged; scalar block is reused, not newly rerun.",
               "Finite variational response/time does not establish a continuum gap or physical thermalization."]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT);args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"],a["refinement_gate"]["status"])
    for row in a["state_results"]:print("T",row["T"],"targets",row["measured_targets"])
    failed=[(k,v) for k,v in a["checks"].items() if not v["pass"]]
    if failed:print("FAIL",failed)
    return 0 if not failed else 1


if __name__=="__main__":raise SystemExit(main())
