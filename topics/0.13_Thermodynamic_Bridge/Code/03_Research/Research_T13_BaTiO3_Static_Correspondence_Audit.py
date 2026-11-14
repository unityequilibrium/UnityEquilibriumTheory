"""Offline source-bound BaTiO3 static correspondence diagnostic, not validation."""
from __future__ import annotations
import argparse
from copy import deepcopy
from functools import lru_cache
import importlib
import json
from pathlib import Path
import sys
import sympy as s

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json

# Reuse only restricted source-AST utilities, not old calculate/algebra/main.
old=importlib.import_module("Research_T13_Retained_Response_Regime_Classification")
T="docs/topics/0.13_Thermodynamic_Bridge"
STEM="batio3_static_correspondence_audit"
CONTRACT=f"{T}/calculation_contracts/{STEM}.json"
INPUT=f"{T}/Data/03_Research/{STEM}_sources.json"
OUTPUT=f"{T}/Result/artifacts/t13_{STEM}.json"
BASELINE="3d42f606ea27af1ae0d2215b183c537073d09bd1"
SPECIMEN="W2006_BTO001_Pt_135C_10kHz"
C,Phi,P=s.symbols("C Phi P",real=True)
a=s.Symbol("a_C",real=True)
b=s.Symbol("b_C",positive=True)
alpha,beta=s.symbols("a_Phi b_Phi",positive=True)
g=s.Symbol("g",nonnegative=True)
An,Bn,Gn,Dn=s.symbols("alpha_N beta_N gamma_N delta_N",real=True)
UNITS={"length":"mm","width":"mm","thickness":"mm","temperature":"degC","frequency":"kHz",
       "minus_beta8":"V m5 C-3","gamma8":"V m9 C-5","delta8":"V m13 C-7",
       "li_alpha11":"N m6 C-4","li_alpha111":"N m10 C-6","li_alpha1111":"N m14 C-8"}
POLICY=("physical_acceptance","fit_core_parameters","independent_validation","holdout",
        "source_fit_has_hard_uncertainty","native_G_is_bare_joint_F","DFT_calibrates_specimen",
        "LCR_is_DC_by_default","biased_branch_is_retained_memory","physical_work_is_old_injection_work",
        "selected_realization")


def exact(x):
    if type(x) not in (str,int):raise ValueError("exact decimal string required, not float/bool")
    v=s.Rational(x)
    if not v.is_finite:raise ValueError("nonfinite input")
    return v


def equal(x,y):
    return s.simplify(s.cancel(x-y))==0


def same_context(*facts):
    if not facts or len({x["context"] for x in facts})!=1:
        raise ValueError("cross-source/specimen/ensemble tuple not admitted")
    return True


def validate_subset(data):
    if data["schema_version"]!="uet-batio3-source-subset-v1" or data["baseline_commit"]!=BASELINE:
        raise ValueError("source subset scope changed")
    if tuple(x["id"] for x in data["sources"])!=("w2006","li2005","w2007","j2016"):
        raise ValueError("fixed four-source corpus only")
    src={x["id"]:x for x in data["sources"]}
    for x in src.values():
        if not all(x.get(k) for k in ("doi","url","version","read_scope","access","terms","role","copy_availability")):
            raise ValueError("source identity/access/role incomplete")
        if "METADATA" in x["access"]:raise ValueError("abstract is not parameter evidence")
    facts={x["id"]:x for x in data["facts"]}
    if len(facts)!=len(data["facts"]) or set(facts)!=set(UNITS):raise ValueError("fact set changed")
    for name,x in facts.items():
        if x["source"] not in src or not x.get("locator") or x["unit"]!=UNITS[name]:
            raise ValueError("fact source/locator/unit mismatch")
        exact(x["value"])
        if x["uncertainty"]!={"kind":"UNKNOWN","value":None}:
            raise ValueError("this source subset supplies no hard uncertainty; unknown is not zero")
        primary=not name.startswith("li_")
        if primary and (x["source"]!="w2006" or x["context"]!=SPECIMEN):
            raise ValueError("main specimen tuple cannot include follow-up/DFT parameters")
        if not primary and (x["source"]!="li2005" or x["context"]!="LI2005_STRESS_FREE_POTENTIAL_NOT_W2006"):
            raise ValueError("Li potential is context, not specimen calibration")
    if data["specimen"]["id"]!=SPECIMEN:raise ValueError("specimen changed")
    if set(data["policy"])!=set(POLICY) or any(data["policy"][k] is not False for k in POLICY):
        raise ValueError("diagnostic policy cannot promote a physical or retained-memory claim")
    return src,facts


def reduction_scope(a_phi=1,mechanical_source=0,reference_phi=0,ensemble="matched_conditional_static"):
    if not s.sympify(a_phi).is_positive or mechanical_source!=0 or reference_phi!=0 or ensemble!="matched_conditional_static":
        raise ValueError("analytic origin/static/positive-curvature premises not supplied")


@lru_cache(maxsize=1)
def algebra():
    V=a*C**2/2+b*C**4/4+alpha*Phi**2/2+beta*Phi**4/4-g*C**2*Phi/2
    q1=g/(2*alpha)
    q3=-beta*q1**3/alpha
    q5=-3*beta*q1**2*q3/alpha
    ph=q1*C**2+q3*C**6+q5*C**10
    reduced=s.series(V.subs(Phi,ph),C,0,12).removeO().expand()
    native=An*P**2/2+Bn*P**4/4+Gn*P**6/6+Dn*P**8/8
    force=s.diff(native,P);curvature=s.diff(force,P)
    f0=V.subs({C:old.C,Phi:old.Phi,a:old.a,b:old.b,alpha:old.alpha,beta:old.beta,g:old.g},simultaneous=True)
    phi0,yy=s.symbols("Phi_0 y",real=True)
    shifted=s.expand(V.subs(Phi,phi0+yy))
    return {"V":V,"phi_series":ph,"reduced":reduced,"native":native,"force":force,
            "curvature":curvature,"source_equivalent_V":f0,"shifted":shifted,
            "shifted_cubic":shifted.coeff(yy,3)}


def dimensions():
    # Integer exponents in (mass,length,time,electric charge), no unit guesses.
    V=(1,2,-2,-1);N=(1,1,-2,0);pol=(0,-2,0,1);density=(1,-1,-2,0)
    add=lambda *xs:tuple(sum(x[i] for x in xs) for i in range(4))
    mul=lambda n,x:tuple(n*v for v in x)
    coeff=lambda m,q:add(V,(0,m,0,q))
    return {
        "beta_V_and_Li_N_units_equal":coeff(5,-3)==add(N,(0,6,0,-4)),
        "gamma_V_and_Li_N_units_equal":coeff(9,-5)==add(N,(0,10,0,-6)),
        "delta_V_and_Li_N_units_equal":coeff(13,-7)==add(N,(0,14,0,-8)),
        "all_native_terms_are_energy_density":all(add(coeff(m,q),mul(n,pol))==density
            for m,q,n in [(1,-1,2),(5,-3,4),(9,-5,6),(13,-7,8)]),
        "E_times_P_is_energy_density":add(V,(0,-1,0,0),pol)==density,
        "Q_is_not_energy_coupling":(0,4,0,-2)!=coeff(1,-1),
        "energy_density_times_volume_is_energy":add(density,(0,3,0,0))==(1,2,-2,0),
    }


def checks():
    d=algebra();red=d["reduced"]
    residual=s.diff(d["V"],Phi).subs(Phi,d["phi_series"])
    kk,lam,Q=s.symbols("k_e Lambda Q",positive=True)
    eps,eps0,epsb,area,thickness,cap=s.symbols("epsilon epsilon_0 epsilon_b A_s d_s C_cap",positive=True)
    mc,mu,J,cdot=s.symbols("M_C mu_C J_C C_dot",real=True)
    density=s.Symbol("V_s",positive=True)
    out={
        "canonical_potential_matches_current_source":equal(old.source_law()[0],d["source_equivalent_V"]),
        "stationary_phi_series_residual_through_order10":s.series(residual,C,0,12).removeO()==0,
        "reduced_expansion":equal(red,a*C**2/2+(b/4-g**2/(8*alpha))*C**4+beta*g**4*C**8/(64*alpha**4)),
        "no_C6_in_conditional_reduced_potential":red.coeff(C,6)==0,
        "no_C5_in_conditional_force":s.diff(red,C).expand().coeff(C,5)==0,
        "no_C4_in_conditional_curvature":s.diff(red,C,2).expand().coeff(C,4)==0,
        "native_force_and_curvature_conventions":equal(d["force"],An*P+Bn*P**3+Gn*P**5+Dn*P**7) and equal(d["curvature"],An+3*Bn*P**2+5*Gn*P**4+7*Dn*P**6),
        "linear_rescaling_cannot_erase_nonzero_sextic":s.diff(d["native"],P,6).subs(P,0)==120*Gn,
        "strain_shift_generates_cubic":equal(d["shifted_cubic"],beta*s.Symbol("Phi_0",real=True)),
        "Q_vs_energy_coupling_factor2":equal(s.diff(kk*eps**2/2-lam*P**2*eps/2,eps).subs(eps,lam*P**2/(2*kk)),0),
        "relaxed_quartic_not_bare":equal(b-2*kk*Q**2,b-(2*kk*Q)**2/(2*kk)),
        "permittivity_background_relation":equal((area*(eps0*epsb+eps)/thickness)*thickness/area-eps0*epsb,eps),
        "relative_vs_absolute_permittivity":not equal(eps0*eps,eps),
        "native_dielectric_map_even":equal(d["curvature"].subs(P,-P),d["curvature"]),
        "strain_P_squared_map_even":equal((Q*P**2).subs(P,-P),Q*P**2),
        "force_port_vs_injection_work_difference":equal((J/mc*cdot-mu*J).subs(cdot,-mc*mu+J),J**2/mc-2*mu*J),
        "total_electrical_conjugate_force_has_volume":s.diff(-density*s.Symbol("E_int")*P,P)==-density*s.Symbol("E_int"),
    }
    out.update(dimensions())
    return out


def negative_controls(data):
    def rejected(call):
        try:call()
        except ValueError:return True
        return False
    bad=deepcopy(data);bad["facts"][0]["uncertainty"]["value"]="0"
    mixed=deepcopy(data);mixed["facts"][0]["context"]="DFT_FIXED_D_ZERO_T"
    wrongunit=deepcopy(data);wrongunit["facts"][4]["unit"]="Hz"
    metadata=deepcopy(data);metadata["sources"][0]["access"]="METADATA_ONLY"
    out={
        "unknown_uncertainty_zero_rejected":rejected(lambda:validate_subset(bad)),
        "mixed_specimen_tuple_rejected":rejected(lambda:validate_subset(mixed)),
        "frequency_unit_relabel_rejected":rejected(lambda:validate_subset(wrongunit)),
        "metadata_parameter_evidence_rejected":rejected(lambda:validate_subset(metadata)),
        "degenerate_reduction_rejected":rejected(lambda:reduction_scope(a_phi=0)),
        "prestressed_reference_rejected":rejected(lambda:reduction_scope(reference_phi=1)),
        "mechanical_source_rejected":rejected(lambda:reduction_scope(mechanical_source=1)),
        "unmatched_ensemble_rejected":rejected(lambda:reduction_scope(ensemble="fixed_D")),
        "source_beta_column_minus_retained":exact(next(x["value"] for x in data["facts"] if x["id"]=="minus_beta8"))>0,
        "negative_relaxed_quartic_can_have_positive_bare":(
            (s.Symbol("k",positive=True)*s.Symbol("Q",positive=True)**2).is_positive
            and (-s.Symbol("k",positive=True)*s.Symbol("Q",positive=True)**2).is_negative),
    }
    for key in POLICY:
        changed=deepcopy(data);changed["policy"][key]=True
        out[key+"_promotion_rejected"]=rejected(lambda changed=changed:validate_subset(changed))
    return out


def calculate():
    data=load_json(ROOT/INPUT);src,facts=validate_subset(data)
    old.source_domain();reduction_scope()
    c,n=checks(),negative_controls(data)
    if not all(c.values()) or not all(n.values()):raise ValueError("exact/source diagnostic checks failed")
    val=lambda name:exact(facts[name]["value"])
    same_context(*[facts[k] for k in ("length","width","thickness","temperature","frequency","minus_beta8","gamma8","delta8")])
    length,width,depth=[val(k)/1000 for k in ("length","width","thickness")]
    A_s=length*width;volume=A_s*depth
    native_beta=-val("minus_beta8");native_gamma=val("gamma8");native_delta=val("delta8")
    li={"beta":4*val("li_alpha11"),"gamma":6*val("li_alpha111"),"delta":8*val("li_alpha1111")}
    # These are source point coefficients, not a Core fit or physical interval.
    residual_force=native_gamma*P**5
    residual_curvature=5*native_gamma*P**4
    verdicts=[
        {"interface":"state_C_to_P","outcome":"UNRESOLVED","basis":"C=P/P0 is a candidate coordinate definition, not admitted same-specimen state closure or independent signed-P readout"},
        {"interface":"conditional_reduced_polynomials","outcome":"DIFFERENT","basis":"analytic zero-reference/positive-aPhi/zero-mechanical-source Core has zero sextic; source point polynomial has nonzero gamma; this conditional polynomial mismatch is not certified material rejection"},
        {"interface":"full_joint_potential_and_ensemble","outcome":"UNRESOLVED","basis":"same-specimen mechanical ensemble, bare joint coefficients and error/covariance missing; relaxed source coefficients cannot be recoupled"},
        {"interface":"electrical_port","outcome":"UNRESOLVED","basis":"nominal V/d is not independently calibrated internal field or J_C; physical force work uses Argument18/21, not old injection split"},
        {"interface":"dielectric_channel_as_full_state","outcome":"DIFFERENT","basis":"native curvature and electrostrictive P^2 readouts are noninjective under P sign reversal; this is channel-alone, not all-input observability no-go"},
        {"interface":"LCR_frequency_to_DC","outcome":"UNRESOLVED","basis":"10kHz is finite frequency; no independently bounded band/background/circuit conversion"},
        {"interface":"Phi_Pi_mechanics","outcome":"UNRESOLVED","basis":"no same-specimen calibrated strain/mode readout, inertia, damping or rates"},
        {"interface":"zero_drive_retained_memory","outcome":"UNRESOLVED","basis":"field-induced branches are not a demonstrated write-release-hold-probe preparation"},
    ]
    d=algebra()
    def serial(x):
        if isinstance(x,s.Basic):return str(x)
        if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [serial(v) for v in x]
        return x
    return serial({"source_baseline_commit":BASELINE,"sympy_version":s.__version__,
        "checks":c,"negative_controls":n,"source_ids":list(src),"source_facts":data["facts"],
        "transformations":{"length_m":length,"width_m":width,"thickness_m":depth,"nominal_area_m2":A_s,
            "nominal_volume_m3":volume,"temperature_K":val("temperature")+s.Rational(27315,100),
            "frequency_Hz":1000*val("frequency"),"omega_rad_s":2*s.pi*1000*val("frequency"),
            "converted_values_are_hard_intervals":False},
        "conditional_symbolic_results":{"Phi_series":d["phi_series"],"Omega_reduced_through_C8":d["reduced"],
            "remainder":"O(C^12) local analytic series only, no admitted physical range/error bound",
            "assumptions":"aPhi>0, zero mechanical source/referencePhi, same potential, linear P=P0*C, matched static ensemble",
            "no_C6":True,"native_force":d["force"],"native_curvature":d["curvature"],
            "not_a_dynamic_elimination":True},
        "point_diagnostics":{"W2006_native_beta":native_beta,"W2006_native_gamma":native_gamma,
            "W2006_native_delta":native_delta,"Li_converted_coefficients_different_context":li,
            "Gamma_P5_term_if_other_coefficients_match":residual_force,
            "Gamma_curvature_term_if_other_coefficients_match":residual_curvature,
            "residual_is_full_error_bound":False,"native_alpha":None,"fit_covariance":None,
            "scale_dictionary":None,"Core_predicted_curve":None,"Var_Phi":None},
        "correspondence_verdicts":verdicts,"unknowns":data["unknowns"],
        "old_evidence_reuse":"Argument18/21-29 and regime artifacts by identity; no old calculate/algebra/main or scientific verifier",
        "physical_acceptance":False,"review_scope":"source-bound DIAGNOSTIC; not material validation",
        "fit_core_parameters":False,"old_producers_rerun":False,"numerical_roots":0,
        "trajectories":0,"parameter_sweeps":0,"new_core_terms":0,"new_UET_discriminator":False,
        "next_controller":"physical-parent-preparation remains open. Need a same-specimen joint/bare potential and mechanical-boundary/readout packet before mapping scales or kinetics. Quantum-parent-correspondence stays separate; no automatic new experiment/model/platform."})


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),**calculate()}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group()
    m.add_argument("--check",action="store_true");m.add_argument("--emit-report",action="store_true")
    args=p.parse_args(argv);r=record();text=json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.emit_report:(ROOT/OUTPUT).write_text(text,encoding="utf-8",newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes()!=text.encode("utf-8"):
        raise ValueError("artifact absent/stale; explicit emit only after review")
    print(json.dumps({"checks":len(r["checks"]),"negative_controls":len(r["negative_controls"]),
                      "review":r["contract_review_status"],"physical_acceptance":False}))
    return 0


if __name__=="__main__":raise SystemExit(main())
