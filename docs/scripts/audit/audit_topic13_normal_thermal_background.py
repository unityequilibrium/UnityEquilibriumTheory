"""Thermal-only one-loop stationary response background in the normal lane.

The input zero-temperature polynomial is held fixed; the field-dependent
vacuum determinant, counterterms and interacting self-energies are NOT added.
This is not a complete renormalized finite-temperature effective action.
"""
from __future__ import annotations
from dataclasses import asdict
from functools import lru_cache
from math import pi, sqrt
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from docs.scripts.audit.audit_topic13_coupled_gain_loss_operator import MixtureInputs, polarization, tensors
from docs.core.uet_covariant_matter import CovariantMatterConfig, joint_potential_energy
from docs.core.uet_covariant_response import CovariantResponseConfig

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_normal_thermal_background_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_thermal_background_addendum.json"
EQUATION_ID="uet.o2.thermal.normal_response_stationarity"
TEMPERATURES=(.1,.25,.5,1.)
GRIDS=((96,48.),(160,64.),(256,80.))
AMPLITUDE_S_GRID=(4.,8.,16.)
AMPLITUDE_COSINES=(-.8,0.,.8)


@lru_cache(maxsize=16)
def nodes(order):
    x,w=np.polynomial.legendre.leggauss(order)
    x.setflags(write=False); w.setflags(write=False)
    return x,w


def canonical_background(phi_c,cfg):
    x=float(phi_c)
    if not np.isfinite(x):
        raise ValueError("finite canonical response displacement required")
    return {
        "tree_potential":.5*cfg.response_mass_sq*x*x+.25*cfg.neutral_quartic*x**4,
        "tree_force":cfg.response_mass_sq*x+cfg.neutral_quartic*x**3,
        "matter_mass_squared":cfg.mass**2-cfg.cubic*x,
        "response_tree_mass_squared":cfg.response_mass_sq+3*cfg.neutral_quartic*x*x,
        "matter_mass_derivative":-cfg.cubic,
        "response_mass_derivative":6*cfg.neutral_quartic*x,
        "response_mass_second_derivative":6*cfg.neutral_quartic,
        "response_tree_cubic":6*cfg.neutral_quartic*x,
    }


def production_potential(phi_c,matter_c,cfg):
    rc=CovariantResponseConfig(epsilon_nc=cfg.epsilon,response_kinetic=cfg.response_kinetic,
        response_mass_sq=cfg.response_mass_squared,response_quartic=cfg.response_quartic)
    mc=CovariantMatterConfig(matter_kinetic=cfg.z,matter_mass_sq=cfg.mass_squared,
        matter_quartic=cfg.quartic,response_coupling=cfg.response_coupling)
    return joint_potential_energy(phi_c/sqrt(cfg.epsilon*cfg.response_kinetic),
                                  np.asarray(matter_c)/sqrt(cfg.z),rc,mc)


def thermal_terms(mass_squared,T,mu,charges,*,order=160,cutoff_factor=64.):
    if not np.isfinite(T) or T<0 or not np.isfinite(mu):
        raise ValueError("finite T>=0 and chemical potential required")
    if not np.isfinite(mass_squared) or mass_squared<=0 or max(abs(q*mu) for q in charges)>=sqrt(mass_squared):
        raise ValueError("strict positive normal-mode gap required")
    if isinstance(order,bool) or not isinstance(order,(int,np.integer)) or order<32:
        raise ValueError("integer quadrature order >=32 required")
    if not np.isfinite(cutoff_factor) or cutoff_factor<16:
        raise ValueError("finite cutoff factor >=16 required")
    if any(q not in (-1,0,1) for q in charges) or not charges:
        raise ValueError("valid nonempty species list required")
    keys=("omega","tadpole","mass_second","charge","entropy","energy","charge_susceptibility_fixed_mass","tadpole_mu")
    if T==0:
        return dict.fromkeys(keys,0.)
    u,w=nodes(order)
    cutoff=cutoff_factor*max(T,sqrt(mass_squared))
    p=.5*cutoff*(u+1); measure=.5*cutoff*w*p*p/(2*pi*pi)
    E=np.sqrt(p*p+mass_squared)
    result=dict.fromkeys(keys,0.)
    for q in charges:
        exponent=(E-q*mu)/T
        expminus=np.exp(-exponent)
        f=expminus/(-np.expm1(-exponent))
        logone=np.log(-np.expm1(-exponent))
        values=(
            T*logone,
            f/(2*E),
            -f*(1+f)/(4*T*E*E)-f/(4*E**3),
            q*f,
            -logone+exponent*f,
            E*f,
            q*q*f*(1+f)/T,
            q*f*(1+f)/(2*T*E),
        )
        for name,value in zip(keys,values):
            result[name]+=float(measure@value)
    return result


def effective_state(phi_c,T=.25,mu=.2,cfg=MixtureInputs(),*,order=160,cutoff_factor=64.):
    b=canonical_background(phi_c,cfg)
    matter=thermal_terms(b["matter_mass_squared"],T,mu,(-1,1),order=order,cutoff_factor=cutoff_factor)
    response=thermal_terms(b["response_tree_mass_squared"],T,0.,(0,),order=order,cutoff_factor=cutoff_factor)
    da,db=b["matter_mass_derivative"],b["response_mass_derivative"]
    omega=b["tree_potential"]+matter["omega"]+response["omega"]
    force=b["tree_force"]+da*matter["tadpole"]+db*response["tadpole"]
    curvature=(b["response_tree_mass_squared"]+da*da*matter["mass_second"]
               +db*db*response["mass_second"]+b["response_mass_second_derivative"]*response["tadpole"])
    omega_phi_mu=da*matter["tadpole_mu"]
    return {
        "phi_c":float(phi_c),"Phi_natural_displacement":float(phi_c/sqrt(cfg.epsilon*cfg.response_kinetic)),
        "T":T,"mu":mu,"omega":omega,"pressure":-omega,"force":force,"static_response_curvature":curvature,
        "matter_thermal_force":da*matter["tadpole"],"response_thermal_force":db*response["tadpole"],
        "omega_phi_mu":omega_phi_mu,
        "charge_density":matter["charge"],"entropy_density":matter["entropy"]+response["entropy"],
        "energy_density":b["tree_potential"]+matter["energy"]+response["energy"],
        "fixed_phi_charge_susceptibility":matter["charge_susceptibility_fixed_mass"],
        "matter":matter,"response":response,"background":b,
    }


def stationary_state(T=.25,mu=.2,cfg=MixtureInputs(),*,order=160,cutoff_factor=64.):
    controls=dict(order=order,cutoff_factor=cutoff_factor)
    initial=effective_state(0.,T,mu,cfg,**controls)
    scale=max(cfg.mass,sqrt(cfg.response_mass_sq),T)
    if T==0 or cfg.cubic==0:
        root=0.; bracket=[0.,0.]
    else:
        limit=(cfg.mass**2-mu*mu)/cfg.cubic
        # Stay inside the declared normal domain. This is not a clipped solution.
        upper=limit*(1-1e-8)
        fun=lambda x:effective_state(x,T,mu,cfg,**controls)["force"]
        if fun(upper)<=0:
            raise ValueError("no bracketed stationary point inside the declared normal domain")
        root=brentq(fun,0.,upper,xtol=1e-13*scale,rtol=1e-12)
        bracket=[0.,upper]
    result=effective_state(root,T,mu,cfg,**controls)
    if result["static_response_curvature"]<=0:
        raise ValueError("stationary response point is not a local minimum")
    hessian=result["static_response_curvature"]
    backreaction=result["omega_phi_mu"]**2/hessian
    result.update({
        "config":asdict(cfg),"grid":controls,"root_bracket":bracket,
        "unshifted_force":initial["force"],"unshifted_pressure":initial["pressure"],
        "pressure_shift":result["pressure"]-initial["pressure"],
        "normal_gap":sqrt(result["background"]["matter_mass_squared"])-abs(mu),
        "dphi_dmu":-result["omega_phi_mu"]/hessian,
        "stationary_charge_susceptibility":result["fixed_phi_charge_susceptibility"]+backreaction,
        "susceptibility_backreaction":backreaction,
        "relative_matter_tree_mass_squared_change":result["background"]["matter_mass_squared"]/cfg.mass**2-1,
        "relative_response_tree_mass_squared_change":result["background"]["response_tree_mass_squared"]/cfg.response_mass_sq-1,
        "linearized_background_estimate":-initial["force"]/initial["static_response_curvature"] if initial["static_response_curvature"]>0 else None,
        "status":"LOCAL_THERMAL_ONLY_NORMAL_STATIONARY_POINT",
    })
    return result


def derivative_witness(state):
    cfg=MixtureInputs(**state["config"]); T,mu,x=state["T"],state["mu"],state["phi_c"]
    controls=state["grid"]
    h=1e-4*max(T,cfg.mass)
    fixed=lambda y:effective_state(y,T,mu,cfg,**controls)
    omega_derivative=(fixed(x+h)["omega"]-fixed(x-h)["omega"])/(2*h)
    hessian=(fixed(x+h)["force"]-fixed(x-h)["force"])/(2*h)
    plus_mu=stationary_state(T,mu+h,cfg,**controls)
    minus_mu=stationary_state(T,mu-h,cfg,**controls)
    plus_T=stationary_state(T+h,mu,cfg,**controls)
    minus_T=stationary_state(T-h,mu,cfg,**controls)
    independent=minimize_scalar(lambda y:fixed(y)["omega"],bounds=(0.,min(state["root_bracket"][1],max(5*x,1e-3))),
                                 method="bounded",options={"xatol":1e-12})
    return {
        "step":h,"force_finite_difference":omega_derivative,"analytic_force":state["force"],
        "hessian_relative_error":abs(hessian/state["static_response_curvature"]-1),
        "charge_envelope_relative_error":abs((plus_mu["pressure"]-minus_mu["pressure"])/(2*h)/state["charge_density"]-1),
        "entropy_envelope_relative_error":abs((plus_T["pressure"]-minus_T["pressure"])/(2*h)/state["entropy_density"]-1),
        "susceptibility_relative_error":abs((plus_mu["charge_density"]-minus_mu["charge_density"])/(2*h)/state["stationary_charge_susceptibility"]-1),
        "dphi_dmu_relative_error":abs((plus_mu["phi_c"]-minus_mu["phi_c"])/(2*h)/state["dphi_dmu"]-1),
        "independent_minimum_success":bool(independent.success),
        "independent_minimum_relative_error":abs(independent.x/x-1),
        "energy_identity_residual":state["energy_density"]+state["pressure"]-T*state["entropy_density"]-mu*state["charge_density"],
    }


def shifted_tree_amplitude(s,t,u,charges,state,*,include_induced_cubic=True):
    """Tree vertices at x_star, not a dressed finite-temperature amplitude."""
    cfg=MixtureInputs(**state["config"])
    b=state["background"]
    if len(charges)!=4 or any(q not in (-1,0,1) for q in charges):
        raise ValueError("four valid species labels required")
    if any(np.any(~np.isfinite(v)) for v in (s,t,u)):
        raise ValueError("finite Mandelstam invariants required")
    shape=np.broadcast(np.asarray(s),np.asarray(t),np.asarray(u)).shape
    if sum(charges[:2])!=sum(charges[2:]):
        return np.zeros(shape,complex)
    cubic,quartic=tensors(cfg)
    if include_induced_cubic:
        cubic[2,2,2]=b["response_tree_cubic"]
    legs=[polarization(q) for q in (*charges[:2],-charges[2],-charges[3])]
    result=np.full(shape,np.einsum("abcd,a,b,c,d",quartic,*legs),complex)
    for invariant,(aa,bb,cc,dd) in zip((s,t,u),((0,1,2,3),(0,2,1,3),(0,3,1,2))):
        left=np.einsum("abi,a,b->i",cubic,legs[aa],legs[bb])
        right=np.einsum("cdi,c,d->i",cubic,legs[cc],legs[dd])
        for i in range(3):
            factor=left[i]*right[i]
            if factor==0:
                continue
            m2=b["matter_mass_squared"] if i<2 else b["response_tree_mass_squared"]
            denominator=np.asarray(invariant)-m2
            if np.any(abs(denominator)<1e-12):
                raise ValueError("pole requires separate resummation; no width inserted")
            result+=factor/denominator
    return result


def shifted_vertex_witness(state):
    b=state["background"]; cfg=MixtureInputs(**state["config"])
    m2,M2=b["matter_mass_squared"],b["response_tree_mass_squared"]
    G,H=cfg.cubic,b["response_tree_cubic"]
    rows=[]
    for s in AMPLITUDE_S_GRID:
        if s<=(sqrt(m2)+sqrt(M2))**2:
            continue
        p2=((s-(sqrt(m2)+sqrt(M2))**2)*(s-(sqrt(m2)-sqrt(M2))**2))/(4*s)
        for cosine in AMPLITUDE_COSINES:
            t=-2*p2*(1-cosine); u=2*(m2+M2)-s-t
            full=complex(shifted_tree_amplitude(s,t,u,(1,0,1,0),state)).real
            mass_only=complex(shifted_tree_amplitude(s,t,u,(1,0,1,0),state,include_induced_cubic=False)).real
            missing=-G*H/(t-M2)
            expected=G*G*(1/(s-m2)+1/(u-m2))+missing
            rows.append({"s":s,"cosine":cosine,"t":t,"u":u,"full_shifted_tree_amplitude":full,
                         "mass_only_amplitude":mass_only,"missing_exchange_term":missing,
                         "analytic_relative_error":abs(full-expected)/max(abs(expected),1e-30),
                         "squared_amplitude_ratio":(full/mass_only)**2 if mass_only else None})
    return {"T":state["T"],"phi_c":state["phi_c"],"induced_cubic":H,"rows":rows,
            "relation":"M(chi Phi -> chi Phi)=G^2[(s-m_chi^2)^-1+(u-m_chi^2)^-1]-G*H/(t-M_response^2)",
            "role":"SHIFTED_TREE_SENSITIVITY_NOT_COMPLETE_THERMAL_PERTURBATION_THEORY"}


def main():
    cfg=MixtureInputs()
    states=[stationary_state(T,.2,cfg) for T in TEMPERATURES]
    witnesses=[derivative_witness(s) for s in states]
    shifted_vertices=[shifted_vertex_witness(s) for s in states]
    refined=[stationary_state(.25,.2,cfg,order=n,cutoff_factor=c) for n,c in GRIDS]
    changes=[abs(b["phi_c"]/a["phi_c"]-1) for a,b in zip(refined,refined[1:])]
    production=[]
    for x in (0.,.01,.1):
        h=.01
        v=lambda y:production_potential(y,[0.,0.],cfg)
        production.append({"phi_c":x,"tree_force_error":abs((v(x-2*h)-8*v(x-h)+8*v(x+h)-v(x+2*h))/(12*h)-canonical_background(x,cfg)["tree_force"])})
    checks={
        "nonzero_thermal_force_at_old_background":all(s["unshifted_force"]<0 for s in states),
        "stable_local_stationary_response":all(abs(s["force"])<1e-10 and s["static_response_curvature"]>0 and s["normal_gap"]>0 for s in states),
        "production_tree_force":all(s["tree_force_error"]<1e-10 for s in production),
        "hessian_derivative":all(w["hessian_relative_error"]<1e-6 for w in witnesses),
        "thermodynamic_envelope":all(max(w["charge_envelope_relative_error"],w["entropy_envelope_relative_error"],w["susceptibility_relative_error"],w["dphi_dmu_relative_error"])<1e-4 for w in witnesses),
        "independent_minimum":all(w["independent_minimum_success"] and w["independent_minimum_relative_error"]<1e-3 for w in witnesses),
        "energy_identity":all(abs(w["energy_identity_residual"])<1e-10 for w in witnesses),
        "quadrature_refinement":max(changes)<1e-5,
        "induced_response_cubic_nonzero":all(s["background"]["response_tree_cubic"]>0 for s in states),
        "shifted_vertex_matches_analytic_exchange":all(row["analytic_relative_error"]<1e-10 for v in shifted_vertices for row in v["rows"]),
    }
    source_paths=[
        "docs/scripts/audit/audit_topic13_normal_thermal_background.py",
        "docs/core/test/test_topic13_normal_thermal_background.py",
        "docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py",
        "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
        "docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py",
    ]
    evidence_path="docs/core/artifacts/t13_coupled_gain_loss_operator_audit.json"
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    artifact={
        "schema_version":"t13-normal-thermal-background-v1",
        "major_result_id":"T13_NORMAL_THERMAL_BACKGROUND_STATIONARITY",
        "topic":"0.13_Thermodynamic_Bridge","closure_level":"PARTIAL",
        "verification_status":"PASS_THERMAL_ONLY_STATIONARITY_FULL_MATCH_OPEN" if all(checks.values()) else "WARN_THERMAL_BACKGROUND",
        "what_is_closed":["Thermal-only Gaussian normal-response stationary point, force/Hessian and envelope derivative checks.",
                          "Old zero-displacement collision background has a nonzero thermal force; shifted tree response has an induced cubic vertex.",
                          "Mass-only collision update omits a tree exchange term; its effect is quantified at declared kinematic points, not as a thermal rate."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{
            "canonical":"x=sqrt(epsilon*K)*Delta_Phi_natural; m_chi^2(x)=m_chi0^2-G*x; M_response^2(x)=M0^2+3*lambda_response*x^2",
            "potential":"Omega_T(x)=V_tree(x)+sum_species T integral log(1-exp(-(E_i(x)-q_i*mu)/T))",
            "force":"Omega_x=M0^2*x+lambda_response*x^3-G*I_chi+6*lambda_response*x*I_response",
            "tadpole":"I_i=integral f_i/(2*E_i); J_i=partial I_i/partial m_i^2",
            "curvature":"Omega_xx=M0^2+3*lambda_response*x^2+G^2*J_chi+(6*lambda_response*x)^2*J_response+6*lambda_response*I_response",
            "envelope":"p=-Omega_T(x_star); n=partial_mu p; s=partial_T p; chi_stationary=chi_fixed+Omega_xmu^2/Omega_xx",
            "shifted_tree_vertex":"V_response_cubic=6*lambda_response*x_star, not a dressed thermal vertex",
            "weak_source_response":"x_star approx G*I_chi(0)/[M0^2+6*lambda_response*I_response(0)+G^2*J_chi(0)] when the small-displacement expansion is controlled",
        },
        "ontology":{"C":"not charge or particle count","Phi":"effective response; x is its canonical natural-unit displacement",
                    "R_gen":"derived, not a state or source","R_obs":"excluded"},
        "variable_meanings":{"x":"canonical natural-unit response displacement, not a temperature",
            "I_chi":"sum of the two charged thermal integrals f/(2E)","I_response":"one neutral thermal integral f/(2E)",
            "J_i":"partial I_i / partial mass_squared at fixed T and mu",
            "H_cubic":"third derivative of shifted tree response potential, not the effective static Hessian",
            "static_response_curvature":"Omega_xx at zero external frequency/momentum; not identified with a pole mass"},
        "unit_lane":"natural_units",
        "units":{"x":1,"T":1,"mu":1,"potential_pressure_energy":4,"force_entropy_charge":3,"curvature_susceptibility":2,"cubic_vertex":1,"I_i":2,"J_i":0,"G":1,"quartic":0},
        "derivation_class":"numerical_approximation",
        "derivation_origin":"Tree polynomial plus thermal part of one-loop Bose determinant; independent action Hessian and thermal integral checks.",
        "constant_origin":"Declared synthetic action coefficients, no fit or experimental calibration.",
        "observable":"Stationary natural-unit response and thermodynamic derivatives; not SI temperature or heat conductivity.",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC",
        "vacuum_policy":"Field-dependent vacuum determinant and counterterms omitted; input zero-T polynomial held fixed. Not a complete renormalization prescription.",
        "matter_quartic_boundary":"Matter quartic does not enter the chi=0 one-loop response determinant directly; its interacting Hartree/two-loop effects are not set to zero physically, but are omitted here.",
        "normal_domain_policy":"Reject nonpositive Bose gaps; bracketing stays strictly within normal domain. No clipped solution, phase transition or global-minimum claim.",
        "old_background_disposition":"The old zero-displacement result remains a fixed tree/background control. Holding it stationary under this thermal functional would require a declared external holding-source contract.",
        "states":states,"derivative_witnesses":witnesses,"refinement":refined,"refinement_relative_changes":changes,
        "production_force_witness":production,"checks":checks,
        "shifted_vertex_witnesses":shifted_vertices,
        "collision_handoff":{
            "status":"BLOCKED_BACKGROUND_AND_VERTEX_MATCH",
            "reason":"Do not update only masses in the old kernel: a shifted response cubic adds tree exchange terms; static effective curvature is not a quasiparticle pole mass. The partial higher-order terms induced by a shifted background are not a complete thermal loop expansion.",
            "old_collision_artifact_preserved":True,"coupled_collision_rerun":False,
            "sensitivity_boundary":"Pointwise squared-amplitude ratios can be large near cancellations of the mass-only comparator; they are not integrated rate ratios or reliable high-T predictions.",
        },
        "open_blockers":["vacuum_renormalization_and_interacting_thermal_self_energy","charged_or_condensed_phase_stability_not_complete",
                         "shifted_background_collision_vertices_and_current_matching","full_KMS_entropy_heat_frame_and_material_SI_mapping"],
        "controlling_blocker":"consistent_thermal_background_propagator_vertex_current_matching",
        "source_hashes":{p:sha(p) for p in source_paths},
        "evidence_artifacts":[{"path":evidence_path,"sha256":sha(evidence_path)}],
        "literature_context":[{"url":"https://www.tpi.uni-jena.de/~floerchinger/qft2/lecture22/","role":"Thermal determinant and stationary-pressure method; no numeric input."},
                              {"url":"https://arxiv.org/abs/hep-ph/9901312","role":"Effective potential and finite-temperature approximation context."}],
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,"xie_2026_accessed":False,"parameter_fitting_performed":False,
        "claim_boundary":"Thermal-only local normal stationary-background diagnostic; not full finite-T EOS, renormalized action, physical transport, SI alpha, or Full Topic 13 closure.",
    }
    artifact["report"]={
        "MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],
        "STATUS":artifact["verification_status"],"WHAT_CHANGED":"Solved response thermal force and exposed shifted-vertex handoff instead of reusing a zero-T background.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Build a consistent background/propagator/vertex approximation and audit current matching before inserting thermal masses into the collision form.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","variable_meanings","unit_lane","units","derivation_class","derivation_origin","constant_origin","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"relation_or_code_path":artifact["equation_or_mapping"],
                  "standard_physics_counterpart":"Gaussian thermal effective potential on a normal scalar background",
                  "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT.relative_to(ROOT))}],
                  "dependency_role":"diagnostic_only","physical_dependency_unlock":False})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"refinement_changes":changes,
                      "states":[{k:s[k] for k in ("T","phi_c","unshifted_force","static_response_curvature","normal_gap")} for s in states],
                      "derivative_witnesses":witnesses},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
