"""Charged/neutral mixed one-loop kernel in the canonical normal O(2) lane.

Physical frequency Omega = grand-canonical omega + q*mu. Real pole evaluation
is restricted to the gap between Landau and pair cuts; no width is inserted.
This is not a full current vertex, collision resummation or material match.
"""
from __future__ import annotations
from dataclasses import asdict
from math import pi,sqrt
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
from docs.scripts.audit import audit_topic13_response_one_loop_match as response

thermal=response.thermal
CFG=response.CFG
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_charged_one_loop_match_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_charged_one_loop_addendum.json"
EQUATION_ID="uet.o2.thermal.charged_mixed_one_loop_match"
TEMPERATURES=(.1,.25,.5,1.)


def occupation(energy,T):
    e=np.asarray(energy,dtype=float)
    if not np.isfinite(T) or T<0 or np.any(~np.isfinite(e)) or np.any(e<=0):
        raise ValueError("positive finite excitation energy and T>=0 required")
    if T==0:
        return np.zeros_like(e)
    return np.exp(-e/T)/(-np.expm1(-e/T))


def divided_occupation(a,b,T):
    """Exact Bose divided difference with the analytic coincident limit."""
    a,b=np.broadcast_arrays(np.asarray(a,float),np.asarray(b,float))
    na=occupation(a,T); occupation(b,T)
    if not T:
        return np.zeros_like(a)
    d=abs(a-b)
    result=np.empty_like(a)
    same=d==0
    result[same]=-na[same]*(1+na[same])/T
    different=~same
    result[different]=(np.exp(-np.minimum(a,b)[different]/T)*np.expm1(-d[different]/T)
        /(d[different]*(-np.expm1(-a[different]/T))*(-np.expm1(-b[different]/T))))
    return result


def mixed_bubble(E,W,z,T,mu,*,thermal_only=True):
    """Fixed-momentum bubble at complex physical frequency z."""
    E,W=np.broadcast_arrays(np.asarray(E,float),np.asarray(W,float))
    if not np.isfinite(mu) or np.any(E<=abs(mu)):
        raise ValueError("strict charged Bose gap required")
    np_=occupation(E-mu,T); nm=occupation(E+mu,T); n0=occupation(W,T)
    if not np.isfinite(z):
        raise ValueError("finite complex physical frequency required")
    S=E+W; D=E-W
    vacuum=0. if thermal_only else 1.
    if z==mu:
        # Static Matsubara limit: apparent Landau denominators are removable.
        value=((vacuum+np_+n0)/(S-mu)+(vacuum+nm+n0)/(S+mu)
            -divided_occupation(E-mu,W,T)-divided_occupation(E+mu,W,T))
    else:
        if np.any(S-z==0) or np.any(S+z==0) or np.any(D-z==0) or np.any(D+z==0):
            raise ValueError("cut pole requires spectral or principal-value treatment")
        value=((vacuum+np_+n0)/(S-z)+(vacuum+nm+n0)/(S+z)
            -(np_-n0)/(D-z)+(n0-nm)/(D+z))
    return value/(4*E*W)


def vacuum_kernel(s,cfg=CFG,order=160):
    if not np.isfinite(s) or s>=(cfg.mass+sqrt(cfg.response_mass_sq))**2:
        raise ValueError("real kernel below pair threshold required")
    if isinstance(order,bool) or not isinstance(order,(int,np.integer)) or order<32:
        raise ValueError("integer quadrature order >=32 required")
    u,w=thermal.nodes(order); u=(u+1)/2; w=w/2
    denominator=u*cfg.mass**2+(1-u)*cfg.response_mass_sq
    c=u*(1-u)/denominator; arg=c*s
    factor=-cfg.cubic**2/(16*pi*pi)
    value=factor*float(w@np.array([response._log_subtracted(float(x)) for x in arg]))
    ds=factor*float(w@(c*arg/(1-arg)))
    return value,ds


def charged_self_energy(Omega,T=.25,mu=.2,q=1,cfg=CFG,*,order=160,cutoff_factor=64.,static=False):
    if q not in (-1,1):
        raise ValueError("signed charged species required")
    matter=thermal.thermal_terms(cfg.mass**2,T,mu,(-1,1),order=order,cutoff_factor=cutoff_factor)
    m=cfg.mass; M=sqrt(cfg.response_mass_sq); qm=q*mu
    if static:
        if Omega!=qm:
            raise ValueError("static response has physical frequency q*mu")
    elif not np.isfinite(Omega) or not abs(m-M)<Omega<m+M:
        raise ValueError("real dynamic kernel requires gap between Landau and pair cuts")
    u,w=thermal.nodes(order); cutoff=cutoff_factor*max(T,m,M)
    p=(u+1)*cutoff/2; measure=w*cutoff/2*p*p/(2*pi*pi)
    E=np.sqrt(p*p+m*m); W=np.sqrt(p*p+M*M)
    bubble=-cfg.cubic**2*float(measure@mixed_bubble(E,W,Omega,T,qm))
    mean_shift=cfg.cubic*matter["tadpole"]/cfg.response_mass_sq
    mean_mass=-cfg.cubic*mean_shift
    quartic=4*cfg.coupling*matter["tadpole"]
    vac,dvac=vacuum_kernel(Omega*Omega,cfg,order)
    derivative=None
    if not static:
        np_=occupation(E-qm,T); nm=occupation(E+qm,T); n0=occupation(W,T)
        S=E+W; D=E-W
        db=((np_+n0)/(S-Omega)**2-(nm+n0)/(S+Omega)**2
            -(np_-n0)/(D-Omega)**2-(n0-nm)/(D+Omega)**2)/(4*E*W)
        derivative=2*Omega*dvac-cfg.cubic**2*float(measure@db)
    return {"physical_frequency":Omega,"grand_frequency":Omega-qm,"charge":q,
        "strict_response_mean_shift":mean_shift,"mean_mass_shift":mean_mass,
        "quartic_tadpole":quartic,"mixed_thermal_bubble":bubble,"vacuum_subtracted":vac,
        "self_energy":mean_mass+quartic+bubble+vac,"Omega_derivative":derivative}


def charged_pole(T=.25,mu=.2,q=1,cfg=CFG,*,order=160,cutoff_factor=64.):
    opts=dict(order=order,cutoff_factor=cutoff_factor)
    m=cfg.mass; M=sqrt(cfg.response_mass_sq)
    evaluate=lambda z:charged_self_energy(z,T,mu,q,cfg,**opts)
    on_tree=evaluate(m)
    strict_energy=m+on_tree["self_energy"]/(2*m)
    if not abs(m-M)<strict_energy<m+M or strict_energy-q*mu<=0:
        raise ValueError("strict pole leaves normal positive-excitation cut gap")
    lower=abs(m-M)+1e-7*m; upper=m+M-1e-7*m
    fun=lambda z:z*z-m*m-evaluate(z)["self_energy"]
    root=brentq(fun,lower,upper,xtol=1e-12*m)
    at_root=evaluate(root)
    if root-q*mu<=0:
        raise ValueError("partial Dyson root has nonpositive grand excitation")
    derivative=at_root["Omega_derivative"]
    residue=1/(1-derivative/(2*root))
    static=charged_self_energy(q*mu,T,mu,q,cfg,static=True,**opts)
    return {"T":T,"mu":mu,"q":q,"strict_energy":strict_energy,
        "strict_grand_energy":strict_energy-q*mu,"partial_Dyson_energy":root,
        "partial_Dyson_grand_energy":root-q*mu,"partial_reuse_relative_change":abs(root/strict_energy-1),
        "residue":residue,"temporal_Ward_required_vertex":q*(2*root-derivative),
        "static_grand_curvature":m*m-mu*mu+static["self_energy"],
        "kernel_at_tree":on_tree,"kernel_at_partial_pole":at_root,
        "one_loop_on_shell_width":0.,
        "boundary":"Strict O(loop) energy, partial Dyson reuse, and temporal Ward requirement are distinct; no transverse/heat-current vertex or collision width is derived."}


def mixed_cut(Omega,T=.25,mu=.2,q=1,cfg=CFG):
    """Positive physical-frequency pair and m>M Landau cuts, with charged KMS."""
    if q not in (-1,1) or not np.isfinite(Omega) or Omega<=0:
        raise ValueError("positive physical frequency and signed charge required")
    m=cfg.mass; M=sqrt(cfg.response_mass_sq); qm=q*mu
    occupation(m-abs(mu),T)
    if m<M:
        raise ValueError("reversed mass ordering requires separately declared Landau routing")
    if Omega>m+M:
        E=(Omega*Omega+m*m-M*M)/(2*Omega); W=Omega-E
        kind="PAIR"
    elif Omega<m-M:
        E=(m*m-M*M+Omega*Omega)/(2*Omega); W=E-Omega
        kind="LANDAU"
    else:
        return {"kind":"NO_CUT_SUPPORT","spectral":0.,"greater":0.,"lesser":0.,
            "kms_log_error":None,"fdt_cross_relative_error":None}
    momentum=sqrt((Omega*Omega-(m+M)**2)*(Omega*Omega-(m-M)**2))/(2*Omega)
    phase=cfg.cubic**2*momentum/(4*pi*Omega)
    if phase==0:
        return {"kind":"DECOUPLED","spectral":0.,"greater":0.,"lesser":0.,
            "kms_log_error":None,"fdt_cross_relative_error":None}
    nc=float(occupation(E-qm,T)); n0=float(occupation(W,T))
    if kind=="PAIR":
        greater=phase*(1+nc)*(1+n0); lesser=phase*nc*n0
        spectral=phase*(1+nc+n0)
    else:
        greater=phase*n0*(1+nc); lesser=phase*nc*(1+n0)
        spectral=phase*(n0-nc)
    noise=greater+lesser
    log_error=fdt=None
    if T:
        lc=-(E-qm)/T-np.log(-np.expm1(-(E-qm)/T))
        l0=-W/T-np.log(-np.expm1(-W/T))
        lg=np.log(phase)+(np.log1p(nc)+np.log1p(n0) if kind=="PAIR" else l0+np.log1p(nc))
        ll=np.log(phase)+(lc+l0 if kind=="PAIR" else lc+np.log1p(n0))
        log_error=float(abs(lg-ll-(Omega-qm)/T))
        # Cross-multiplied FDT stays finite at grand frequency zero.
        fdt=float(abs(spectral-noise*np.tanh((Omega-qm)/(2*T)))/noise) if noise else None
    return {"kind":kind,"physical_frequency":Omega,"grand_frequency":Omega-qm,
        "charged_energy":E,"neutral_energy":W,"momentum":momentum,
        "spectral":spectral,"greater":greater,"lesser":lesser,"noise":noise,
        "imag_retarded":-.5*spectral,"kms_log_error":log_error,
        "fdt_cross_relative_error":fdt,"underflow":bool(T and lesser==0)}


def matsubara_witness(E=1.2,W=.8,T=.25,mu=.2,cutoff=8192):
    occupation(E-abs(mu),T); occupation(W,T)
    if T<=0 or isinstance(cutoff,bool) or not isinstance(cutoff,int) or cutoff<1:
        raise ValueError("positive T and integer cutoff required")
    ell=np.arange(-cutoff,cutoff+1); frequencies=2*pi*T*ell
    rows=[]
    for n in (0,1,2,4):
        nu=2*pi*T*n
        # Legacy convention is D_q(R)=[(R0+i*mu)^2+E^2]^-1.  With
        # response loop K, the charged line carries P-K.
        numeric=T*np.sum(1/((frequencies**2+W*W)*((nu-frequencies+1j*mu)**2+E*E)))
        analytic=complex(mixed_bubble(E,W,mu-1j*nu,T,mu,thermal_only=False))
        rows.append({"n":n,"numeric":[float(numeric.real),float(numeric.imag)],
            "analytic":[analytic.real,analytic.imag],"relative_error":float(abs(numeric-analytic)/abs(analytic))})
    return {"E":E,"W":W,"T":T,"mu":mu,"cutoff":cutoff,
        "routing":"response K, charged P-K; D_q^-1(R)=(R0+i*mu)^2+E^2", "rows":rows}


def static_thermal_hessian_witness(T=.25,cfg=CFG):
    """Independent mu=0 three-field Gaussian determinant curvature."""
    def omega(r):
        matrix=np.array([[cfg.mass**2+3*cfg.coupling*r*r,0.,-cfg.cubic*r],
            [0.,cfg.mass**2+cfg.coupling*r*r,0.],[-cfg.cubic*r,0.,cfg.response_mass_sq]])
        return sum(thermal.thermal_terms(m2,T,0.,(0,))["omega"] for m2 in np.linalg.eigvalsh(matrix))
    h=.003*cfg.mass
    fd=(-omega(2*h)+16*omega(h)-30*omega(0)+16*omega(-h)-omega(-2*h))/(12*h*h)
    kernel=charged_self_energy(0.,T,mu=0.,cfg=cfg,static=True)
    analytic=kernel["quartic_tadpole"]+kernel["mixed_thermal_bubble"]
    return {"T":T,"mu":0.,"field_step":h,"determinant_curvature":fd,"diagram_curvature":analytic,
        "relative_error":abs(fd/analytic-1),"scope":"thermal determinant at fixed x=0; strict mean insertion is separate"}


def thermal_dispersion_witness(T=.25,mu=.2,cfg=CFG):
    """Reconstruct the real mixed bubble from both signed thermal cuts."""
    m=cfg.mass; M=sqrt(cfg.response_mass_sq); Omega=m
    if not M<m:
        raise ValueError("this dispersion witness declares m>M")
    def rho(w,chemical,kind):
        E=(w*w+m*m-M*M)/(2*w)
        if kind=="PAIR":
            W=w-E; weight=float(occupation(E-chemical,T)+occupation(W,T))
        else:
            W=E-w; weight=float(occupation(W,T)-occupation(E-chemical,T))
        phase=cfg.cubic**2*sqrt((w*w-(m+M)**2)*(w*w-(m-M)**2))/(8*pi*w*w)
        return phase*weight
    def integrand(w,kind):
        return -(rho(w,mu,kind)/(w-Omega)+rho(w,-mu,kind)/(w+Omega))/(2*pi)
    pair,pe=quad(lambda w:integrand(w,"PAIR"),m+M,np.inf,epsabs=1e-13)
    landau,le=quad(lambda w:integrand(w,"LANDAU"),0,m-M,epsabs=1e-13)
    expected=charged_self_energy(Omega,T,mu,cfg=cfg)["mixed_thermal_bubble"]
    return {"T":T,"mu":mu,"Omega":Omega,"pair_dispersion":pair,"Landau_dispersion":landau,
        "diagram":expected,"absolute_error":abs(pair+landau-expected),"quadrature_errors":[pe,le]}


def main():
    poles=[charged_pole(T,q=q) for T in TEMPERATURES for q in (-1,1)]
    cuts=[{"T":T,"q":q,"physical_frequency":z,"grand_frequency":z-q*.2,**mixed_cut(z,T,q=q)} for T in TEMPERATURES
        for q in (-1,1) for z in (.1,.2,.25,1.,2.,3.)]
    mats=[matsubara_witness(mu=mu) for mu in (-.2,0.,.2)]
    hessians=[static_thermal_hessian_witness(T) for T in TEMPERATURES]
    dispersions=[thermal_dispersion_witness(T) for T in TEMPERATURES]
    grids=((96,48.),(160,64.),(256,80.))
    refinement=[charged_pole(order=n,cutoff_factor=c) for n,c in grids]
    keys=("mean_mass_shift","quartic_tadpole","mixed_thermal_bubble","vacuum_subtracted","self_energy")
    changes={key:[abs(b["kernel_at_tree"][key]/a["kernel_at_tree"][key]-1)
        for a,b in zip(refinement,refinement[1:])] for key in keys}
    checks={
        "positive_normal_poles":all(p["strict_grand_energy"]>0 and p["static_grand_curvature"]>0 and p["residue"]>0 for p in poles),
        "independent_mixed_Matsubara":all(r["relative_error"]<1e-9 for m in mats for r in m["rows"]),
        "independent_three_field_thermal_Hessian":all(h["relative_error"]<2e-5 for h in hessians),
        "independent_pair_Landau_dispersion":all(d["absolute_error"]<1e-12 for d in dispersions),
        "charged_KMS":all(c["kms_log_error"]<1e-10 for c in cuts if c["kms_log_error"] is not None),
        "charged_FDT":all(c["fdt_cross_relative_error"]<1e-10 for c in cuts if c["fdt_cross_relative_error"] is not None),
        "positive_transition_weights":all(c["greater"]>=0 and c["lesser"]>=0 for c in cuts),
        "kernel_refinement":all(max(v)<1e-6 for v in changes.values()),
        "vacuum_reference":vacuum_kernel(0.)==(0.,0.),
    }
    source_paths=["docs/scripts/audit/audit_topic13_charged_one_loop_match.py",
        "docs/core/test/test_topic13_charged_one_loop_match.py",
        "docs/scripts/audit/audit_topic13_response_one_loop_match.py",
        "docs/scripts/audit/audit_topic13_normal_thermal_background.py",
        "docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py",
        "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
        "docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py"]
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    prior="docs/core/artifacts/t13_response_one_loop_match_audit.json"
    artifact={"schema_version":"t13-charged-one-loop-match-v1",
        "major_result_id":"T13_CHARGED_MIXED_ONE_LOOP_NORMAL_MATCH","topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"PARTIAL","verification_status":"PASS_SCOPED_CHARGED_ONE_LOOP_MATCH" if all(checks.values()) else "WARN_CHARGED_ONE_LOOP_MATCH",
        "what_is_closed":["Canonical normal charged self-energy including mean shift, O(2) tadpole and mixed bubble at strict one-loop order.",
            "Physical versus grand-canonical frequencies; static Matsubara limit and charged pair/Landau KMS.",
            "Temporal Ward-required longitudinal vertex is identified, not a complete microscopic current vertex."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{"frequency":"Omega=omega+q*mu; D_R^-1=Omega^2-m^2-Sigma_q",
            "self_energy":"Sigma_q=-G*x1+4*lambda_chi*I_chi-G^2 integral B_T(E,W,Omega,q*mu)+Sigma_vac_sub",
            "mean":"x1=G*I_chi/M0^2, with I_chi=integral(n_plus+n_minus)/(2E)",
            "vacuum":"Sigma_vac_sub=-G^2/(16*pi^2) integral[-log(1-a)-a]; a=z(1-z)*Omega^2/[z*m^2+(1-z)*M0^2]",
            "strict_pole":"E_q=m+Sigma_q(Omega=m)/(2m); grand excitation=E_q-q*mu",
            "KMS":"greater/lesser=exp((Omega-q*mu)/T); rho=noise*tanh((Omega-q*mu)/(2T))",
            "Ward_required":"Gamma_q^0(Omega,Omega)=q*(2*Omega-partial_Omega Sigma_q); transverse vertices not fixed"},
        "ontology":{"C":"collective lane coordinate, not universal charge or mass","Phi":"effective response, not particle or metric",
            "R_gen":"derived trace, not state or self-energy source","R_obs":"excluded"},
        "unit_lane":"natural_units","units":{"Omega":1,"mu":1,"T":1,"G":1,"Sigma":2,"curvature":2,"Gamma0":1,"lambda_chi":0},
        "unit_convention":"powers of natural energy; no SI mapping",
        "derivation_class":"numerical_approximation","derivation_origin":"Canonical action tadpoles and mixed charged/neutral bubble with fixed zero-field vacuum subtractions.",
        "constant_origin":"synthetic canonical action inputs, no calibration or fit",
        "observable":"Internal normal charged pole, static curvature and charged spectral kernels, not heat conductivity",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC","config":asdict(CFG),"temperature_grid":TEMPERATURES,
        "chemical_potential":.2,"quadrature":{"order":160,"cutoff_factor":64.},"checks":checks,
        "poles":poles,"cuts":cuts,"matsubara_witnesses":mats,"refinement":refinement,
        "static_thermal_hessian_witnesses":hessians,"thermal_dispersion_witnesses":dispersions,
        "kernel_component_refinement_relative_changes":changes,
        "approximation_contract":{"loop_order":1,"internal_background":"zero-field canonical propagators; mean shift inserted separately once",
            "vacuum_reference":"Sigma_vac(0)=Sigma_vac_s'(0)=0; not full quartic/cubic vertex counterterm closure",
            "real_dynamic_domain":"abs(m-M)<Omega<m+M","cut_routing":"positive physical frequency with m>=M",
            "partial_Dyson":"partial reuse only; not full next-order matching"},
        "uncertainty_boundary":"Numerical refinement and partial-reuse differences do not certify omitted-order or physical uncertainty.",
        "open_blockers":["full_vertex_and_counterterm_matching","finite_k_and_collision_resummed_current_response",
            "number_changing_and_complete_heat_entropy_tensor","material_SI_calibration_and_full_T13_acceptance"],
        "controlling_blocker":"finite_temperature_vertex_and_collision_current_matching",
        "evidence_artifacts":[{"path":prior,"sha256":sha(prior)}],"source_hashes":{p:sha(p) for p in source_paths},
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,"xie_2026_accessed":False,
        "parameter_fitting_performed":False,"collision_artifact_rerun":False,
        "literature_context":[{"url":"https://journals.aps.org/prd/abstract/10.1103/PhysRevD.74.085006",
            "role":"Abstract-level thermal cutting/chemical-potential context, no numeric input"}],
        "claim_boundary":"Internal normal k=0 charged one-loop result only; no physical Phi particles, full microscopic current, collision-resummed transport, SI alpha or Full Topic 13 closure."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],
        "STATUS":artifact["verification_status"],"WHAT_CHANGED":"Added matched charged mean/tadpole/mixed bubble and charged thermal cuts.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Derive finite-temperature vertices/current matching and collision-resummed finite-k response before transport handoff.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    keys=("ontology","unit_lane","units","derivation_class","derivation_origin","constant_origin","observable","data_role","verification_status","controlling_blocker","claim_boundary")
    entry={k:artifact[k] for k in keys}
    entry.update({"equation_id":EQUATION_ID,"version":"1","classification":"numerical_implementation",
        "relation_or_code_path":artifact["equation_or_mapping"],
        "standard_physics_counterpart":"Normal O(2) charged/neutral one-loop thermal bubble and charged KMS",
        "variables":{"Omega":"physical energy","omega":"grand-canonical frequency","Sigma_q":"self-energy, not core Pi","q":"lane charge sign, not universal C"},
        "mathematical_role":"One-loop inverse propagator","observable_mapping":artifact["observable"],
        "parameter_dimensions":artifact["units"],"source_or_origin":artifact["derivation_origin"],
        "assumptions":artifact["approximation_contract"],"symmetry_and_conservation":"Charge conjugation/KMS; full current/energy ledger open",
        "limiting_cases":["T=0","G=0","mu=0","static grand frequency zero"],
        "implementation_paths":[source_paths[0]],"verifier_paths":[source_paths[1]],
        "evidence_class":"INTERNAL_SYNTHETIC_DIAGNOSTIC","proof_status":"CHECKED_SCOPED_ONE_LOOP_ONLY",
        "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT)}],
        "downstream_dependencies":[],"dependency_role":"diagnostic_only","physical_dependency_unlock":False,
        "failure_mode":artifact["open_blockers"],"next_hardening_step":artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1",
        "status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED","extends":"docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"poles":poles},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
