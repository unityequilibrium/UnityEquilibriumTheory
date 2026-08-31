"""Response-axis one-loop subtraction and collisionless k=0 retarded kernel.

This matches the response sector at an explicitly declared loop order. It
does not supply charged-sector self-energies, full vertex matching, transport
resummation or material/SI calibration. No existing result is overwritten.
"""
from __future__ import annotations
from dataclasses import asdict
from math import pi,sqrt,log1p
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
from docs.scripts.audit import audit_topic13_normal_thermal_background as thermal

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_response_one_loop_match_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_response_one_loop_addendum.json"
EQUATION_ID="uet.o2.thermal.response_axis_one_loop_match"
CFG=thermal.MixtureInputs()
TEMPERATURES=(.1,.25,.5,1.)


def vacuum_remainder(r,degree):
    """Taylor remainder of (1+r)^2 log(1+r), including two derivatives."""
    if not np.isfinite(r) or r<=-1 or degree not in (2,4):
        raise ValueError("positive mass and degree 2 or 4 required")
    if abs(r)<.125:
        # Stable analytic remainder; no subtraction of nearly equal CW values.
        terms=[0.,0.,0.]
        for n in range(degree+1,90):
            c=2*(-1)**(n+1)/(n*(n-1)*(n-2))
            terms[0]+=c*r**n
            terms[1]+=n*c*r**(n-1)
            terms[2]+=n*(n-1)*c*r**(n-2)
        return tuple(terms)
    l=log1p(r)
    result=[(1+r)**2*l-r-1.5*r*r,2*(1+r)*l-2*r,2*l]
    if degree==4:
        result[0]+=-r**3/3+r**4/12
        result[1]+=-r*r+r**3/3
        result[2]+=-2*r+r*r
    return tuple(result)


def vacuum_axis(phi_c,cfg=CFG):
    """Remove the response-axis Taylor polynomial through field degree four."""
    x=float(phi_c)
    if not np.isfinite(x):
        raise ValueError("finite response displacement required")
    rows=[]
    for name,base2,degeneracy,r,dr,ddr,degree in (
        ("charged",cfg.mass**2,2,-cfg.cubic*x/cfg.mass**2,-cfg.cubic/cfg.mass**2,0.,4),
        ("response",cfg.response_mass_sq,1,3*cfg.neutral_quartic*x*x/cfg.response_mass_sq,
         6*cfg.neutral_quartic*x/cfg.response_mass_sq,6*cfg.neutral_quartic/cfg.response_mass_sq,2)):
        f,df,ddf=vacuum_remainder(r,degree)
        factor=degeneracy*base2*base2/(64*pi*pi)
        rows.append({"species":name,"potential":factor*f,"force":factor*df*dr,
                     "curvature":factor*(ddf*dr*dr+df*ddr)})
    return {key:sum(row[key] for row in rows) for key in ("potential","force","curvature")}


def renormalized_axis_state(x,T=.25,mu=.2,cfg=CFG,*,order=160,cutoff_factor=64.):
    result=thermal.effective_state(x,T,mu,cfg,order=order,cutoff_factor=cutoff_factor)
    vac=vacuum_axis(x,cfg)
    result["omega"]+=vac["potential"]
    result["pressure"]-=vac["potential"]
    result["energy_density"]+=vac["potential"]
    result["force"]+=vac["force"]
    result["static_response_curvature"]+=vac["curvature"]
    result["vacuum_axis"]=vac
    return result


def stationary_axis(T=.25,mu=.2,cfg=CFG,*,order=160,cutoff_factor=64.):
    options=dict(order=order,cutoff_factor=cutoff_factor)
    initial=renormalized_axis_state(0.,T,mu,cfg,**options)
    if not T or not cfg.cubic:
        x=0.
    else:
        upper=(cfg.mass**2-mu*mu)/cfg.cubic*(1-1e-8)
        force=lambda y:renormalized_axis_state(y,T,mu,cfg,**options)["force"]
        if force(upper)<=0:
            raise ValueError("no response-axis stationary bracket in normal domain")
        x=brentq(force,0.,upper,xtol=1e-13*max(cfg.mass,T),rtol=1e-12)
    result=renormalized_axis_state(x,T,mu,cfg,**options)
    if result["static_response_curvature"]<=0:
        raise ValueError("response stationary point is not a local minimum")
    strict=-initial["force"]/cfg.response_mass_sq
    result.update({"strict_one_loop_mean_shift":strict,
                   "stationary_vs_strict_relative_change":abs(x/strict-1) if strict else 0.,
                   "stationary_charge_susceptibility":result["fixed_phi_charge_susceptibility"]
                       +result["omega_phi_mu"]**2/result["static_response_curvature"],
                   "boundary":"Stationary one-loop functional reuses selected higher-order terms; strict mean shift is reported separately."})
    return result


def _log_subtracted(a):
    if abs(a)<.01:
        return sum(a**n/n for n in range(2,32))
    return -log1p(-a)-a


def vacuum_retarded(s,cfg=CFG,order=160):
    """Pi_vac(s)-Pi_vac(0)-s Pi_vac'(0), from a Feynman parameter."""
    if not np.isfinite(s) or s>=4*cfg.mass**2:
        raise ValueError("real subthreshold kernel required; no invented width")
    if isinstance(order,bool) or not isinstance(order,(int,np.integer)) or order<32:
        raise ValueError("integer quadrature order >=32 required")
    u,w=thermal.nodes(order); u=.5*(u+1); w=.5*w
    c=u*(1-u)/cfg.mass**2; a=c*s
    factor=-cfg.cubic**2/(16*pi*pi)
    value=factor*float(w@np.array([_log_subtracted(float(z)) for z in a]))
    derivative=factor*float(w@(c*a/(1-a)))
    return value,derivative


def response_self_energy(s,T=.25,mu=.2,cfg=CFG,*,order=160,cutoff_factor=64.):
    """Strict one-loop k=0 kernel at the renormalized zero-field background."""
    # Validation and quartic tadpole use the same one-loop thermal determinant.
    thermal.thermal_terms(cfg.mass**2,T,mu,(-1,1),order=order,cutoff_factor=cutoff_factor)
    neutral=thermal.thermal_terms(cfg.response_mass_sq,T,0.,(0,),order=order,cutoff_factor=cutoff_factor)
    vac,dvac=vacuum_retarded(s,cfg,order)
    tadpole=6*cfg.neutral_quartic*neutral["tadpole"]
    bubble=dbubble=population=0.
    if T:
        u,w=thermal.nodes(order)
        cutoff=cutoff_factor*max(T,cfg.mass)
        p=.5*cutoff*(u+1); measure=.5*cutoff*w*p*p/(2*pi*pi)
        E=np.sqrt(p*p+cfg.mass**2); fsum=np.zeros_like(p); fluct=np.zeros_like(p)
        for q in (-1,1):
            exponent=(E-q*mu)/T
            f=np.exp(-exponent)/(-np.expm1(-exponent))
            fsum+=f; fluct+=f*(1+f)
        denominator=4*E*E-s
        bubble=-cfg.cubic**2*float(measure@(fsum/(E*denominator)))
        dbubble=-cfg.cubic**2*float(measure@(fsum/(E*denominator**2)))
        population=cfg.cubic**2*float(measure@(fluct/(4*T*E*E)))
    return {"s":s,"vacuum_subtracted":vac,"quartic_thermal_tadpole":tadpole,
            "charged_thermal_pair":bubble,"self_energy":vac+tadpole+bubble,
            "self_energy_s_derivative":dvac+dbubble,"static_population_term":population}


def response_pole(T=.25,mu=.2,cfg=CFG,*,order=160,cutoff_factor=64.):
    opts=dict(order=order,cutoff_factor=cutoff_factor)
    evaluate=lambda s:response_self_energy(s,T,mu,cfg,**opts)
    at_tree=evaluate(cfg.response_mass_sq)
    strict=cfg.response_mass_sq+at_tree["self_energy"]
    if not 0<strict<4*cfg.mass**2:
        raise ValueError("strict pole outside declared positive subthreshold domain")
    fn=lambda s:s-cfg.response_mass_sq-evaluate(s)["self_energy"]
    upper=4*cfg.mass**2*(1-1e-8)
    if fn(0.)>=0 or fn(upper)<=0:
        raise ValueError("no positive subthreshold Dyson root")
    root=brentq(fn,0.,upper,xtol=1e-13*cfg.mass**2,rtol=1e-12)
    at_pole=evaluate(root); at_zero=evaluate(0.)
    static=thermal.effective_state(0.,T,mu,cfg,**opts)["static_response_curvature"]
    dynamic=cfg.response_mass_sq+at_zero["self_energy"]
    return {"T":T,"mu":mu,"strict_one_loop_pole_squared":strict,
            "partial_Dyson_pole_squared":root,"Dyson_vs_strict_relative_change":abs(root/strict-1),
            "pole_residue":1/(1-at_pole["self_energy_s_derivative"]),
            "static_curvature_at_zero_field":static,"collisionless_dynamic_zero_frequency_mass_squared":dynamic,
            "static_dynamic_gap":dynamic-static,"population_term":at_zero["static_population_term"],
            "kernel_at_tree_pole":at_tree,"kernel_at_Dyson_pole":at_pole,
            "one_loop_on_shell_width":0.,"width_boundary":"Kinematically below pair threshold at k=0; not zero full collision damping.",
            "partial_Dyson_boundary":"Solves a one-loop kernel repeatedly, not a complete higher-loop result."}


def pair_cut(omega,T=.25,mu=.2,cfg=CFG):
    thermal.thermal_terms(cfg.mass**2,T,mu,(-1,1))
    if not np.isfinite(omega) or omega<=0:
        raise ValueError("positive finite frequency required")
    if omega<=2*cfg.mass or cfg.cubic==0:
        return {"omega":omega,"spectral":0.,"greater":0.,"lesser":0.,"noise":0.,
                "log_kms_error":None,"fdt_relative_error":None,"support":False}
    E=omega/2
    plus=minus=0.
    log_lesser=None
    if T:
        xp=(E-mu)/T; xm=(E+mu)/T
        plus=np.exp(-xp)/(-np.expm1(-xp))
        minus=np.exp(-xm)/(-np.expm1(-xm))
    phase=cfg.cubic**2*sqrt(1-4*cfg.mass**2/omega**2)/(8*pi)
    greater=phase*(1+plus)*(1+minus); lesser=phase*plus*minus
    spectral=phase*(1+plus+minus); noise=greater+lesser
    if T:
        # Retain the finite logarithm when the positive lesser weight underflows.
        log_lesser=np.log(phase)-xp-np.log(-np.expm1(-xp))-xm-np.log(-np.expm1(-xm))
        log_greater=np.log(phase)+np.log1p(plus)+np.log1p(minus)
    return {"omega":omega,"spectral":spectral,"greater":greater,"lesser":lesser,"noise":noise,
            "imag_retarded_self_energy":-.5*spectral,
            "log_lesser":float(log_lesser) if T else None,
            "lesser_underflow":bool(T and lesser==0),
            "log_kms_error":float(abs(log_greater-log_lesser-omega/T)) if T else None,
            "fdt_relative_error":float(abs(noise/(spectral/np.tanh(omega/(2*T)))-1)) if T else None,
            "support":True}


def matsubara_witness(E=1.3,T=.25,mu=.2,cutoff=4096):
    if not all(np.isfinite(v) for v in (E,T,mu)) or T<=0 or E<=abs(mu):
        raise ValueError("positive finite T and E>|mu| required")
    if isinstance(cutoff,bool) or not isinstance(cutoff,(int,np.integer)) or cutoff<1:
        raise ValueError("positive integer summation cutoff required")
    l=np.arange(-cutoff,cutoff+1)
    xp=(E-mu)/T; xm=(E+mu)/T
    fplus=np.exp(-xp)/(-np.expm1(-xp)); fminus=np.exp(-xm)/(-np.expm1(-xm))
    rows=[]
    for n in (0,1,2,4):
        D=(2*pi*T*l-1j*mu)**2+E*E
        Dn=(2*pi*T*(l+n)-1j*mu)**2+E*E
        numeric=T*np.sum(1/(D*Dn))
        if n:
            analytic=(1+fplus+fminus)/(E*((2*pi*T*n)**2+4*E*E))
        else:
            analytic=((1+fplus+fminus)/(4*E**3)
                      +(fplus*(1+fplus)+fminus*(1+fminus))/(4*T*E*E))
        rows.append({"external_index":n,"numeric_real":float(numeric.real),"numeric_imag":float(numeric.imag),
                     "analytic":analytic,"relative_error":float(abs(numeric-analytic)/abs(analytic))})
    return {"mode_energy":E,"T":T,"mu":mu,"summation_cutoff":cutoff,"rows":rows}


def dispersion_witness(s=.5,T=.25,mu=.2,cfg=CFG):
    """Independent spectral dispersion integrals, with explicit vacuum subtractions."""
    kernel=response_self_energy(s,T,mu,cfg)
    def vacuum(t):
        rho=cfg.cubic**2/(8*pi)*sqrt(1-4*cfg.mass**2/t)
        return -rho*s*s/(2*pi*t*t*(t-s))
    def thermal_cut(t):
        E=sqrt(t)/2
        occupations=sum(np.exp(-(E-q*mu)/T)/(-np.expm1(-(E-q*mu)/T)) for q in (-1,1)) if T else 0.
        rho_T=cfg.cubic**2/(8*pi)*sqrt(1-4*cfg.mass**2/t)*occupations
        return -rho_T/(2*pi*(t-s))
    vac,ve=quad(vacuum,4*cfg.mass**2,np.inf,epsabs=1e-14,epsrel=1e-10)
    hot,he=quad(thermal_cut,4*cfg.mass**2,np.inf,epsabs=1e-14,epsrel=1e-10)
    return {"s":s,"T":T,"mu":mu,"vacuum_dispersion":vac,"thermal_dispersion":hot,
            "vacuum_absolute_error":abs(vac-kernel["vacuum_subtracted"]),
            "thermal_absolute_error":abs(hot-kernel["charged_thermal_pair"]),
            "quadrature_error_estimates":[ve,he]}


def main():
    states=[stationary_axis(T) for T in TEMPERATURES]
    poles=[response_pole(T) for T in TEMPERATURES]
    cuts=[{"T":T,**pair_cut(omega,T)} for T in TEMPERATURES for omega in (1.,2.,2.1,3.,4.)]
    mats=matsubara_witness()
    dispersion=[dispersion_witness(T=T) for T in TEMPERATURES]
    refined=[response_pole(.25,order=n,cutoff_factor=c) for n,c in ((96,48.),(160,64.),(256,80.))]
    changes=[abs(b["strict_one_loop_pole_squared"]/a["strict_one_loop_pole_squared"]-1) for a,b in zip(refined,refined[1:])]
    components=("vacuum_subtracted","quartic_thermal_tadpole","charged_thermal_pair","self_energy")
    kernel_changes={key:[abs(b["kernel_at_tree_pole"][key]/a["kernel_at_tree_pole"][key]-1)
        for a,b in zip(refined,refined[1:])] for key in components}
    checks={
        "vacuum_reference_conditions":all(v==0 for v in vacuum_axis(0.).values()) and vacuum_retarded(0.)==(0.,0.),
        "normal_stationarity":all(abs(s["force"])<1e-10 and s["static_response_curvature"]>0 for s in states),
        "positive_subthreshold_response":all(0<p["strict_one_loop_pole_squared"]<4*CFG.mass**2 and p["pole_residue"]>0 for p in poles),
        "static_dynamic_population_match":all(abs(p["static_dynamic_gap"]-p["population_term"])<1e-12 and p["population_term"]>0 for p in poles),
        "independent_matsubara_sum":all(r["relative_error"]<1e-9 for r in mats["rows"]),
        "independent_spectral_dispersion":all(r["vacuum_absolute_error"]<1e-12 and r["thermal_absolute_error"]<1e-12 for r in dispersion),
        "pair_cut_KMS_FDT":all(c["log_kms_error"]<1e-10 and c["fdt_relative_error"]<1e-10 for c in cuts if c["support"]),
        "pair_cut_spectral_positivity":all(c["spectral"]>0 and abs(c["greater"]-c["lesser"]-c["spectral"])<1e-12 for c in cuts if c["support"]),
        "threshold_support":all(c["spectral"]==0 and c["log_kms_error"] is None for c in cuts if not c["support"]),
        "pole_refinement":max(changes)<1e-6,
        "kernel_component_refinement":all(max(v)<1e-6 for v in kernel_changes.values()),
    }
    paths=["docs/scripts/audit/audit_topic13_response_one_loop_match.py",
           "docs/core/test/test_topic13_response_one_loop_match.py",
           "docs/scripts/audit/audit_topic13_normal_thermal_background.py",
           "docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py",
           "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
           "docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py"]
    prior="docs/core/artifacts/t13_normal_thermal_background_audit.json"
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    artifact={
        "schema_version":"t13-response-one-loop-match-v1",
        "major_result_id":"T13_RESPONSE_AXIS_ONE_LOOP_RENORMALIZED_MATCH",
        "topic":"0.13_Thermodynamic_Bridge","closure_level":"PARTIAL",
        "verification_status":"PASS_SCOPED_RESPONSE_ONE_LOOP_MATCH" if all(checks.values()) else "WARN_RESPONSE_ONE_LOOP_MATCH",
        "what_is_closed":["Declared response-axis one-loop vacuum subtraction and kinetic reference conditions.",
                          "Strict-loop mean/pole versus partial resummation are distinguished.",
                          "Collisionless k=0 retarded response, static occupation term and action pair-cut KMS/FDT are linked."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{
            "vacuum_axis":"V_CW_ren(x)=V_CW(x)-Taylor_x=0_through_degree_4[V_CW(x)], charged degeneracy 2 and neutral degeneracy 1",
            "reference_conditions":"d_x^n V_CW_ren(0)=0 for n=0..4; Pi_vac_ren(0)=Pi_vac_ren_s'(0)=0",
            "retarded_convention":"D_R^-1(omega,k=0)=(omega+i0)^2-M0^2-Pi_R; s=omega^2",
            "thermal_kernel":"Pi_T(s)=6*lambda_response*I_response-G^2 integral (n_plus+n_minus)/(E*(4E^2-s))",
            "vacuum_kernel":"Pi_vac_ren(s)=-G^2/(16*pi^2) integral_0^1 [-log(1-z(1-z)*s/m^2)-z(1-z)*s/m^2] dz",
            "static_dynamic":"M_dynamic0^2-M_static^2=G^2 integral [n_plus(1+n_plus)+n_minus(1+n_minus)]/(4*T*E^2)",
            "pole":"M_pole^2(strict 1-loop)=M0^2+Pi_R(M0^2); partial Dyson root separately labelled",
            "pair_cut":"rho_Pi=G^2/(8*pi)*sqrt(1-4*m^2/omega^2)*(1+n_plus+n_minus); Pi_greater/Pi_lesser=exp(omega/T)",
        },
        "loop_order_contract":{"self_energy_loop_order":1,"self_energy_background_x":0.,
            "mean_shift":"x1=-Omega1_prime(0)/M0^2; stationary one-loop functional minimum is separately reported",
            "excluded_at_strict_order":["tree response mass shift proportional to x1^2 (order two)",
                "bubble from induced response cubic squared (order three)",
                "full next-order vertices and collision/ladder widths"],
            "renormalization_scope":"response axis and response two-point kinetic condition, NOT complete charged-sector or full-action matching"},
        "ontology":{"C":"collective system-behaviour coordinate, not universal mass, charge or quasiparticle count","Phi":"effective response, not a particle or metric",
                    "R_gen":"derived trace, not a state or self-energy source","R_obs":"excluded"},
        "unit_lane":"natural_units",
        "config":asdict(CFG),"temperature_grid":TEMPERATURES,"chemical_potential":.2,
        "quadrature":{"order":160,"cutoff_factor":64.},
        "units":{"x":1,"T":1,"mu":1,"s":2,"self_energy":2,"potential":4,"force":3,"curvature":2,"spectral_self_energy":2,"pole_residue":0},
        "unit_convention":"Integer powers of natural energy with hbar=c=k_B=1; not SI or a calibrated material map.",
        "derivation_class":"numerical_approximation",
        "derivation_origin":"Declared one-loop scalar determinant, bubble analytic continuation, and two-particle cut of the same canonical cubic vertex.",
        "constant_origin":"Zero-temperature zero-field subtraction conditions fixed from synthetic action inputs, not fitted to a thermal curve or holdout.",
        "observable":"Internal response-sector stationary displacement, spectral pole and pair-cut kernels; no SI transport coefficient.",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC","checks":checks,"states":states,"poles":poles,"pair_cuts":cuts,
        "matsubara_witness":mats,"dispersion_witness":dispersion,"pole_refinement":refined,"pole_refinement_relative_changes":changes,
        "kernel_component_refinement_relative_changes":kernel_changes,
        "uncertainty_boundary":"Numerical refinement and strict-versus-partially-resummed differences are diagnostic, not a certified omitted-order or physical source uncertainty.",
        "open_blockers":["charged_sector_and_full_vertex_counterterm_matching","finite_k_and_collision_resummed_hydrodynamic_limit",
            "leading_collision_width_current_entropy_transport_matching","material_SI_calibration_and_full_T13_acceptance"],
        "controlling_blocker":"coupled_sector_and_collision_resummed_current_matching",
        "source_hashes":{p:sha(p) for p in paths},"evidence_artifacts":[{"path":prior,"sha256":sha(prior)}],
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,"xie_2026_accessed":False,
        "parameter_fitting_performed":False,"collision_artifact_rerun":False,
        "literature_context":[{"url":"https://arxiv.org/abs/hep-ph/9307335","role":"Order of zero-momentum thermal limits; no numeric input"},
                              {"url":"https://arxiv.org/abs/hep-ph/9901312","role":"One-loop effective-potential and approximation context"}],
        "claim_boundary":"Response-axis and k=0 one-loop scheme only. Not full interacting SK/KMS, finite-width transport, physical Phi particles, SI alpha, or Full Topic 13 closure."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],"STATUS":artifact["verification_status"],
        "WHAT_CHANGED":"Added explicit vacuum/kinetic subtraction, loop-order separation, retarded response and pair-cut KMS/FDT.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Match charged-sector propagators/vertices and collision-resummed response in the declared approximation before a physical transport handoff.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","unit_lane","units","derivation_class","derivation_origin","constant_origin","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"relation_or_code_path":artifact["equation_or_mapping"],
                  "version":"1","classification":"numerical_implementation",
                  "variables":{"x":"canonical response displacement","s":"squared external frequency, k=0",
                      "Pi_R":"retarded self-energy; NOT the core state Pi=d_t Phi",
                      "rho_Pi":"self-energy spectral density, not matter density"},
                  "mathematical_role":"Response-axis one-loop determinant and two-point kernel",
                  "observable_mapping":artifact["observable"],
                  "parameter_dimensions":{"canonical_mass":1,"G":1,"lambda_response":0,"T":1,"mu":1},
                  "source_or_origin":artifact["derivation_origin"],
                  "assumptions":artifact["loop_order_contract"],
                  "symmetry_and_conservation":"Charge conjugation and neutral pair KMS; no full transport ledger claim",
                  "limiting_cases":["zero temperature","G=0","s=0 reference","positive pair threshold"],
                  "implementation_paths":[paths[0]],"verifier_paths":[paths[1]],
                  "evidence_class":"INTERNAL_SYNTHETIC_DIAGNOSTIC","proof_status":"CHECKED_SCOPED_ONE_LOOP_ONLY",
                  "downstream_dependencies":[],"failure_mode":artifact["open_blockers"],
                  "next_hardening_step":artifact["report"]["NEXT_ACTION"],
                  "standard_physics_counterpart":"One-loop scalar-response effective potential and collisionless retarded bubble",
                  "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT.relative_to(ROOT))}],
                  "dependency_role":"diagnostic_only","physical_dependency_unlock":False})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","equation_entries":[entry],
        "full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,
        "pole_refinement":changes,"poles":poles,
        "strict_mean_changes":[s["stationary_vs_strict_relative_change"] for s in states]},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
