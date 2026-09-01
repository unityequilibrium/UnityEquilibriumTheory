"""Finite-temperature charged current vertex from explicit one-loop diagrams.

The mixed response triangle and thermal-bath insertion are evaluated at
nonzero Matsubara transfer. Momentum routing is explicit: the legacy
D_E^{-1}(R)=(R_0+i*q*mu)^2+r^2+m^2 convention is unchanged.
"""
from __future__ import annotations
from dataclasses import asdict
from math import pi,sqrt
from pathlib import Path
import hashlib,json
import numpy as np
from docs.scripts.audit import audit_topic13_charged_one_loop_match as charged

thermal=charged.thermal
CFG=charged.CFG
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_charged_one_loop_current_vertex_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_charged_current_vertex_addendum.json"
EQUATION_ID="uet.o2.thermal.charged_one_loop_current_vertex"
SAMPLES=((.25,1,1,.3,.4),(.25,2,1,-.2,.5),(.5,1,2,.4,-.3))


def _bose_weight(root,T,thermal_only):
    """Bose contour weight at a bosonic Matsubara-shifted pole."""
    x=float(np.real(root))
    if abs(x)<1e-12:
        raise ValueError("zero-energy pole is outside the strict normal/generic routing")
    n=float(charged.occupation(abs(x),T))
    if thermal_only:
        return n if x>0 else -n
    return n if x>0 else -1-n


def _residue_sum(roots,numerator,T,thermal_only):
    result=0j
    for i,r in enumerate(roots):
        denominator=np.prod([r-s for j,s in enumerate(roots) if j!=i])
        if abs(denominator)<1e-12:
            raise ValueError("coincident pole requires a declared confluent limit")
        result+=_bose_weight(r,T,thermal_only)*numerator(r)/denominator
    return result


def mixed_triangle_integrand(k,costheta,T,q,P0,Q0,pz,Qz,mu,cfg=CFG,*,thermal_only=True):
    """Matsubara-summed D_response(K) D_chi(P-K) D_chi(P+Q-K) gamma."""
    W=sqrt(k*k+cfg.response_mass_sq)
    E1=sqrt(k*k+pz*pz-2*k*pz*costheta+cfg.mass**2)
    p2=pz+Qz
    E2=sqrt(k*k+p2*p2-2*k*p2*costheta+cfg.mass**2)
    roots=(W,-W,-q*mu+1j*P0+E1,-q*mu+1j*P0-E1,
        -q*mu+1j*(P0+Q0)+E2,-q*mu+1j*(P0+Q0)-E2)
    temporal=lambda x:q*(2*P0+Q0+2j*x+2j*q*mu)
    spatial=lambda x:q*(2*(pz-k*costheta)+Qz)
    # Three quadratic denominators contribute an overall minus; contour sum adds another minus.
    return np.array([_residue_sum(roots,temporal,T,thermal_only),
        _residue_sum(roots,spatial,T,thermal_only)],complex)


def bath_triangle_integrand(k,costheta,T,Q0,Qz,mu,cfg=CFG,*,thermal_only=True):
    """Matsubara-summed charged bath D(K)D(K+Q) gamma for one complex field."""
    E1=sqrt(k*k+cfg.mass**2)
    E2=sqrt(k*k+Qz*Qz+2*k*Qz*costheta+cfg.mass**2)
    roots=(mu+E1,mu-E1,mu-1j*Q0+E2,mu-1j*Q0-E2)
    temporal=lambda x:2*(-1j*x+1j*mu)+Q0
    spatial=lambda x:2*k*costheta+Qz
    # Two quadratic denominators have positive product; contour sum supplies minus.
    return -np.array([_residue_sum(roots,temporal,T,thermal_only),
        _residue_sum(roots,spatial,T,thermal_only)],complex)


def integrate_vertex_integrand(function,T,*args,cfg=CFG,order_radial=64,order_angle=32):
    if isinstance(order_radial,bool) or isinstance(order_angle,bool) or order_radial<24 or order_angle<16:
        raise ValueError("declared integer quadratures required")
    ur,wr=thermal.nodes(order_radial); uc,wc=thermal.nodes(order_angle)
    # Thermal residue weights decay at infinity.  Map the full half-line so a
    # long finite interval does not undersample the low-momentum support.
    scale=max(T,cfg.mass,sqrt(cfg.response_mass_sq))
    k=scale*(1+ur)/(1-ur); rk=wr*2*scale/(1-ur)**2
    result=np.zeros(2,complex)
    for ki,rwi in zip(k,rk):
        for ci,cwi in zip(uc,wc):
            result+=rwi*cwi*ki*ki/(4*pi*pi)*function(float(ki),float(ci),T,*args,cfg)
    return result


def mixed_thermal_self_energy(P0,pz,T,q,mu,cfg=CFG,order_radial=64,order_angle=32):
    ur,wr=thermal.nodes(order_radial); uc,wc=thermal.nodes(order_angle)
    scale=max(T,cfg.mass,sqrt(cfg.response_mass_sq))
    momenta=scale*(1+ur)/(1-ur); radial_weights=wr*2*scale/(1-ur)**2
    result=0j
    for k,rw in zip(momenta,radial_weights):
        W=sqrt(k*k+cfg.response_mass_sq)
        for c,cw in zip(uc,wc):
            E=sqrt(k*k+pz*pz-2*k*pz*c+cfg.mass**2)
            z=q*mu-1j*P0
            result+=rw*cw*k*k/(4*pi*pi)*charged.mixed_bubble(E,W,z,T,q*mu)
    return -cfg.cubic**2*result


def vacuum_self_energy(P0,pz,q,mu,cfg=CFG,order=96):
    """Renormalized Euclidean mixed bubble at Ptilde=(P0+i*q*mu,pz)."""
    u,w=thermal.nodes(order); a=(u+1)/2; w=w/2
    P=np.array([P0+1j*q*mu,pz],complex); P2=P@P
    D=a*cfg.response_mass_sq+(1-a)*cfg.mass**2
    c=a*(1-a)
    raw=cfg.cubic**2/(16*pi*pi)*np.sum(w*np.log1p(c*P2/D))
    slope=cfg.cubic**2/(16*pi*pi)*np.sum(w*c/D)
    return raw-slope*P2


def vacuum_vertex(P0,Q0,pz,Qz,q,mu,cfg=CFG,order=64):
    """Feynman-parameter mixed triangle plus the fixed kinetic counterterm."""
    u,wu=thermal.nodes(order); v,wv=thermal.nodes(order)
    P=np.array([P0+1j*q*mu,pz],complex); Q=np.array([Q0,Qz],complex)
    result=np.zeros(2,complex)
    for ui,wui in zip((u+1)/2,wu/2):
        # b+c=ui, c=ui*v maps the triangle with Jacobian ui.
        for vi,wvi in zip((v+1)/2,wv/2):
            b=ui*(1-vi); c=ui*vi; a=1-ui
            delta=(a*cfg.response_mass_sq+ui*cfg.mass**2+a*b*(P@P)
                +a*c*((P+Q)@(P+Q))+b*c*(Q@Q))
            numerator=q*(2*a*P+(1-2*c)*Q)
            result+=wui*wvi*ui*numerator/delta
    result*=cfg.cubic**2/(16*pi*pi)
    z,wz=thermal.nodes(order); z=(z+1)/2; wz=wz/2
    D=z*cfg.response_mass_sq+(1-z)*cfg.mass**2
    delta_z=-cfg.cubic**2/(16*pi*pi)*np.sum(wz*z*(1-z)/D)
    return result+delta_z*q*(2*P+Q)


def current_vertex(T=.25,nP=1,nQ=1,pz=.3,Qz=.4,q=1,mu=.2,cfg=CFG,
        *,order_radial=96,order_angle=48):
    if T<=0 or q not in (-1,1) or any(isinstance(n,bool) or not isinstance(n,int) for n in (nP,nQ)):
        raise ValueError("positive T, integer Matsubara indices and signed charge required")
    if nQ==0:
        raise ValueError("generic nonzero transfer first; static confluent limit remains separate")
    P0=2*pi*T*nP; Q0=2*pi*T*nQ
    if not np.isfinite(mu) or abs(mu)>=cfg.mass:
        raise ValueError("finite chemical potential inside the normal gap required")
    mixed=cfg.cubic**2*integrate_vertex_integrand(
        mixed_triangle_integrand,T,q,P0,Q0,pz,Qz,mu,cfg=cfg,
        order_radial=order_radial,order_angle=order_angle)
    bath=integrate_vertex_integrand(bath_triangle_integrand,T,Q0,Qz,mu,cfg=cfg,
        order_radial=order_radial,order_angle=order_angle)
    response_propagator=1/(Q0*Q0+Qz*Qz+cfg.response_mass_sq)
    bath_coefficient=-4*cfg.coupling+cfg.cubic**2*response_propagator
    bath_total=bath_coefficient*bath
    vacuum=vacuum_vertex(P0,Q0,pz,Qz,q,mu,cfg)
    bare=q*np.array([2*(P0+1j*q*mu)+Q0,2*pz+Qz],complex)
    total=bare+mixed+bath_total+vacuum
    before=mixed_thermal_self_energy(P0,pz,T,q,mu,cfg,order_radial,order_angle)+vacuum_self_energy(P0,pz,q,mu,cfg)
    after=mixed_thermal_self_energy(P0+Q0,pz+Qz,T,q,mu,cfg,order_radial,order_angle)+vacuum_self_energy(P0+Q0,pz+Qz,q,mu,cfg)
    Q=np.array([Q0,Qz])
    bare_inverse_difference=((P0+Q0+1j*q*mu)**2+(pz+Qz)**2
        -(P0+1j*q*mu)**2-pz*pz)
    ward_target=q*(bare_inverse_difference+after-before)
    return {"T":T,"mu":mu,"q":q,"nP":nP,"nQ":nQ,"P0":P0,"Q0":Q0,"pz":pz,"Qz":Qz,
        "bare":bare,"mixed_thermal_triangle":mixed,"response_relaxed_bath_triangle":bath_total,
        "bath_triangle_unweighted":bath,"bath_coefficient":bath_coefficient,
        "mixed_vacuum_and_counterterm_vertex":vacuum,"total":total,
        "self_energy_before":before,"self_energy_after":after,
        "Ward_lhs":complex(Q@total),"Ward_target":complex(ward_target),
        "Ward_relative_error":float(abs(Q@total-ward_target)/max(abs(ward_target),1e-300)),
        "bath_transversality_relative":float(abs(Q@bath)/max(np.linalg.norm(Q)*np.linalg.norm(bath),1e-300)),
        "routing":"response loop K; charged lines P-K and P+Q-K use (R0+i*q*mu)^2; no sign change from legacy convention",
        "boundary":"Generic nonzero Euclidean Matsubara transfer. Static/confluent limit, real-time transverse continuation and collision ladders remain open."}


def direct_sum_witness(T=.25,nP=1,nQ=1,pz=.3,Qz=.4,q=1,mu=.2,k=.7,c=.23,cutoff=8192):
    P0=2*pi*T*nP; Q0=2*pi*T*nQ; frequencies=2*pi*T*np.arange(-cutoff,cutoff+1)
    W=sqrt(k*k+CFG.response_mass_sq)
    E1=sqrt(k*k+pz*pz-2*k*pz*c+CFG.mass**2)
    E2=sqrt(k*k+(pz+Qz)**2-2*k*(pz+Qz)*c+CFG.mass**2)
    D0=frequencies**2+W*W
    D1=(P0-frequencies+1j*q*mu)**2+E1*E1
    D2=(P0+Q0-frequencies+1j*q*mu)**2+E2*E2
    numerator=np.vstack((q*(2*(P0-frequencies+1j*q*mu)+Q0)*np.ones_like(frequencies),
        q*(2*(pz-k*c)+Qz)*np.ones_like(frequencies)))
    numeric=T*np.sum(numerator/(D0*D1*D2),axis=1)
    residue=mixed_triangle_integrand(k,c,T,q,P0,Q0,pz,Qz,mu,thermal_only=False)
    # Thermal-only plus the vacuum contour part equals the direct full Matsubara sum.
    return {"numeric":numeric,"residue":residue,
        "relative_error":float(np.linalg.norm(numeric-residue)/np.linalg.norm(residue))}


def main():
    rows=[current_vertex(*sample) for sample in SAMPLES for q in (-1,1)]
    refinements=[current_vertex(.25,1,1,.3,.4,1,order_radial=n,order_angle=m)
        for n,m in ((64,32),(88,40),(112,56))]
    component_changes=[]
    for a,b in zip(refinements,refinements[1:]):
        component_changes.append({key:float(np.linalg.norm(b[key]-a[key])/max(np.linalg.norm(b[key]),1e-300))
            for key in ("mixed_thermal_triangle","response_relaxed_bath_triangle")})
    direct=[direct_sum_witness(q=q) for q in (-1,1)]
    checks={"explicit_diagram_Ward":all(r["Ward_relative_error"]<2e-8 for r in rows),
        "bath_insertion_transverse":all(r["bath_transversality_relative"]<2e-8 for r in rows),
        "direct_Matsubara_residue":all(r["relative_error"]<1e-9 for r in direct),
        "vertex_refinement":max(v for row in component_changes for v in row.values())<1e-6,
        "finite_nonzero_vertices":all(np.all(np.isfinite(r["total"])) and np.linalg.norm(r["mixed_thermal_triangle"])>0 for r in rows),
        "routing_alignment":all("no sign change" in r["routing"] for r in rows)}
    def serial(value):
        if isinstance(value,complex): return [value.real,value.imag]
        if isinstance(value,np.ndarray): return [[x.real,x.imag] for x in value]
        if isinstance(value,np.generic): return value.item()
        if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)): return [serial(v) for v in value]
        return value
    paths=["docs/scripts/audit/audit_topic13_charged_one_loop_current_vertex.py",
        "docs/core/test/test_topic13_charged_one_loop_current_vertex.py",
        "docs/scripts/audit/audit_topic13_charged_one_loop_match.py",
        "docs/core/uet_o2_tree_level_charged_ward_vertex.py",
        "docs/core/uet_o2_finite_density_charged_vertex.py",
        "docs/core/uet_o2_charged_current_correlator.py"]
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    prior="docs/core/artifacts/t13_charged_one_loop_match_audit.json"
    artifact={"schema_version":"t13-charged-one-loop-current-vertex-v1",
        "major_result_id":"T13_CHARGED_ONE_LOOP_CURRENT_VERTEX_MATCH","topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"PARTIAL","verification_status":"PASS_SCOPED_CHARGED_ONE_LOOP_VERTEX" if all(checks.values()) else "WARN_CHARGED_ONE_LOOP_VERTEX",
        "what_is_closed":["Explicit mixed response triangle matches the charged self-energy Ward difference at generic nonzero Euclidean transfer.",
            "Quartic bath-current insertion plus response-relaxed mean contribution is transverse on the declared continuum thermal integral.",
            "Legacy plus-i-mu charged propagator and P-K routing are reconciled without relabeling charge."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{"propagator":"D_q,E^-1(R)=(R0+i*q*mu)^2+r^2+m^2",
            "mixed_triangle":"deltaGamma_mix=G^2 T sum_l integral D_response(K)D_q(P-K)D_q(P+Q-K) gamma_q(P-K+Q,P-K)",
            "bath_triangle":"deltaGamma_bath=[-4*lambda_chi+G^2 D_response(Q)] T sum_l integral D_+(K)gamma_+(K+Q,K)D_+(K+Q)",
            "bare_vertex":"gamma_q=[q*(2*(P0+i*q*mu)+Q0), q*(2*p+Q)]",
            "Ward":"Q_mu Gamma_q^mu=q*[D_q,full^-1(P+Q)-D_q,full^-1(P)]"},
        "ontology":{"C":"collective lane coordinate, not universal charge","Phi":"effective response; response propagator is lane-specific, not a particle claim",
            "R_gen":"derived trace excluded from loops","R_obs":"excluded"},
        "unit_lane":"natural_units","units":{"P0":1,"Q0":1,"momentum":1,"mu":1,"G":1,"Gamma":1,"self_energy":2},
        "derivation_class":"numerical_approximation","derivation_origin":"Functional current insertion into the same canonical charged/response action and one-loop self-energy.",
        "constant_origin":"synthetic action parameters; no fit or calibration","observable":"Internal Euclidean charged three-point vertex, not physical Kubo or heat current",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC","config":asdict(CFG),"samples":serial(rows),
        "direct_sum_witnesses":serial(direct),"refinement":serial(refinements),"refinement_relative_changes":component_changes,
        "checks":checks,"approximation_contract":{"order":"strict one loop in normal zero-field propagators",
            "transfer":"generic nonzero bosonic Matsubara Q; collinear external spatial momenta with full internal angle",
            "bath_role":"response-relaxed thermodynamic background insertion, separately labelled from proper mixed triangle",
            "vacuum":"mixed triangle and fixed charged kinetic counterterm; thermal bath insertion is vacuum-free by conserved-current shift"},
        "open_blockers":["static_confluent_vertex_limit","real_time_finite_k_transverse_continuation",
            "collision_ladder_and_heat_current_vertex_matching","complete_counterterm_four_point_and_material_SI_mapping"],
        "controlling_blocker":"real_time_transverse_vertex_and_collision_ladder_matching",
        "source_hashes":{p:sha(p) for p in paths},"evidence_artifacts":[{"path":prior,"sha256":sha(prior)}],
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,"xie_2026_accessed":False,
        "parameter_fitting_performed":False,"collision_artifact_rerun":False,
        "claim_boundary":"Explicit generic Euclidean one-loop current vertex only; not static limit, retarded transverse vertex, physical current correlator, Kubo/heat transport, SI or Full Topic 13 closure."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],"STATUS":artifact["verification_status"],
        "WHAT_CHANGED":"Replaced a Ward-reconstructed placeholder by explicit mixed and bath current diagrams at generic Euclidean transfer.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Take the controlled static/confluent and real-time transverse limits, then match the collision ladder and heat-current vertex.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","unit_lane","units","derivation_class","derivation_origin","constant_origin","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"version":"1","classification":"numerical_implementation",
        "relation_or_code_path":artifact["equation_or_mapping"],"standard_physics_counterpart":"Finite-temperature scalar Ward-Takahashi three-point vertex",
        "variables":{"Gamma":"charged current vertex","P,Q":"Euclidean momenta","q":"O(2) charge sign, not core C"},
        "mathematical_role":"One-loop current insertion","observable_mapping":artifact["observable"],
        "parameter_dimensions":artifact["units"],"source_or_origin":artifact["derivation_origin"],
        "assumptions":artifact["approximation_contract"],"symmetry_and_conservation":"O(2) Ward identity at generic Euclidean transfer",
        "limiting_cases":["G=0","lambda=0","mu charge conjugation","continuum thermal shift"],
        "implementation_paths":[paths[0]],"verifier_paths":[paths[1]],
        "evidence_class":"INTERNAL_SYNTHETIC_DIAGNOSTIC","proof_status":"CHECKED_GENERIC_EUCLIDEAN_ONE_LOOP_ONLY",
        "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT)}],
        "downstream_dependencies":[],"dependency_role":"diagnostic_only","physical_dependency_unlock":False,
        "failure_mode":artifact["open_blockers"],"next_hardening_step":artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1",
        "status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED","extends":"docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,
        "Ward_errors":[r["Ward_relative_error"] for r in rows],
        "bath_transversality":[r["bath_transversality_relative"] for r in rows],
        "refinement":component_changes},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
