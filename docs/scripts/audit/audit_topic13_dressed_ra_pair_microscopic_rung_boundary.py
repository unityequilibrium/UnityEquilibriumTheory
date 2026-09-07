"""Dressed RA-pair normalization and microscopic rung compatibility audit."""
from __future__ import annotations
from dataclasses import asdict,replace
from math import pi,sqrt
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.integrate import quad

from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import ActionInputs,amplitude
from docs.scripts.audit import audit_topic13_charged_one_loop_current_vertex as current

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_dressed_ra_pair_microscopic_rung_boundary_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_ra_pair_rung_boundary_addendum.json"
EQUATION_ID="uet.o2.thermal.dressed_ra_pair_microscopic_rung_boundary"
CFG=current.CFG


def ra_pair_energy_integral(energy,width):
    if not np.isfinite(energy) or not np.isfinite(width) or energy<=0 or width<=0:
        raise ValueError("positive finite energy and width required")
    integrand=lambda x:1/(4*energy*energy*(x*x+(width/2)**2))/(2*pi)
    numeric,error=quad(integrand,-np.inf,np.inf,epsabs=1e-12,epsrel=1e-12)
    analytic=1/(4*energy*energy*width)
    return {"energy":energy,"width":width,"numeric":numeric,"analytic":analytic,
        "quadrature_error":error,"relative_error":abs(numeric/analytic-1)}


def dressed_current_source_match(momentum_x,momentum_squared,temperature,mu,q,width,mass=1.):
    if momentum_squared<momentum_x*momentum_x or temperature<=0 or q not in (-1,1):
        raise ValueError("physical momentum, positive T and signed charge required")
    energy=sqrt(momentum_squared+mass*mass)
    excitation=energy-q*mu
    if excitation<=0: raise ValueError("strict positive excitation required")
    n=np.exp(-excitation/temperature)/(-np.expm1(-excitation/temperature))
    thermal_weight=n*(1+n)/temperature
    pair=ra_pair_energy_integral(energy,width)
    qft=(2*q*momentum_x)**2*pair["analytic"]*thermal_weight
    kinetic=(q*momentum_x/energy)**2*thermal_weight/width
    return {"energy":energy,"thermal_weight":thermal_weight,"qft":qft,"kinetic":kinetic,
        "relative_error":abs(qft/kinetic-1) if kinetic else abs(qft-kinetic)}


def rung_comparison(s=5.,cosine=.2,cfg=CFG):
    action_cfg=ActionInputs(z=cfg.z,mass_squared=cfg.mass_squared,quartic=cfg.quartic,
        epsilon=cfg.epsilon,response_kinetic=cfg.response_kinetic,
        response_mass_squared=cfg.response_mass_squared,response_coupling=cfg.response_coupling)
    contact_cfg=replace(action_cfg,response_coupling=0.)
    legacy_sigma=cfg.coupling**2/(16*pi*s)
    rows=[]
    for name,charges in (("unlike",(1,-1,1,-1)),("like",(1,1,1,1))):
        identical=charges[2]==charges[3]
        divisor=2 if identical else 1
        m_contact=float(amplitude(s,cosine,charges,contact_cfg))
        m_full=float(amplitude(s,cosine,charges,action_cfg))
        sigma_contact=m_contact*m_contact/(16*pi*s*divisor)
        sigma_full=m_full*m_full/(16*pi*s*divisor)
        rows.append({"channel":name,"charges":charges,"legacy_amplitude":cfg.coupling,
            "action_contact_amplitude":m_contact,"action_full_amplitude":m_full,
            "legacy_cross_section":legacy_sigma,"action_contact_cross_section":sigma_contact,
            "action_full_cross_section":sigma_full,"contact_to_legacy_ratio":sigma_contact/legacy_sigma,
            "full_to_legacy_ratio":sigma_full/legacy_sigma})
    return rows


def main():
    pair_rows=[ra_pair_energy_integral(E,w) for E in (.7,1.,2.) for w in (.01,.05,.2)]
    source_rows=[dressed_current_source_match(px,p2,.25,.2,q,w) for px,p2 in ((.1,.2),(.3,.5)) for q in (-1,1) for w in (.02,.1)]
    rung_rows=rung_comparison()
    checks={"RA_pair_integral":bool(max(r["relative_error"] for r in pair_rows)<1e-10),
        "dressed_pair_matches_kinetic_source":bool(max(r["relative_error"] for r in source_rows)<1e-13),
        "production_contact_differs_from_legacy_rung":bool(all(r["contact_to_legacy_ratio"]!=1 for r in rung_rows)),
        "known_charge_counting_ratios":bool(sorted(r["contact_to_legacy_ratio"] for r in rung_rows)==[8.,16.]),
        "Phi_exchange_changes_rung":bool(all(abs(r["full_to_legacy_ratio"]-r["contact_to_legacy_ratio"])>1e-6 for r in rung_rows))}
    paths=["docs/scripts/audit/audit_topic13_dressed_ra_pair_microscopic_rung_boundary.py",
        "docs/core/test/test_topic13_dressed_ra_pair_microscopic_rung_boundary.py",
        "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
        "docs/core/uet_o2_action_derived_transition_kernel.py","docs/core/uet_o2_contact_sk_transition_vertex_match.py"]
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    priors=["docs/core/artifacts/t13_retarded_ra_mixed_current_vertex_audit.json",
        "docs/core/artifacts/t13_microscopic_current_ladder_matching_boundary_audit.json"]
    artifact={"schema_version":"t13-dressed-ra-pair-rung-boundary-v1","major_result_id":"T13_DRESSED_RA_PAIR_MICROSCOPIC_RUNG_BOUNDARY",
        "topic":"0.13_Thermodynamic_Bridge","closure_level":"CLOSED_FOR_LANE","closure_disposition":"CLOSED_AS_LEGACY_RUNG_NO_GO",
        "verification_status":"PASS_RA_PAIR_MATCH_LEGACY_RUNG_BLOCKED" if all(checks.values()) else "WARN_RA_PAIR_RUNG_BOUNDARY",
        "what_is_closed":["The narrow-width dressed scalar RA pole-pair energy integral reproduces the kinetic 1/Gamma source normalization.",
            "Combining the canonical tree current with the RA pair and thermal derivative exactly reproduces the weighted kinetic current source squared.",
            "The legacy M=lambda transition/SK rung is not the charge-resolved production-action rung: contact-only cross sections differ by factors 8 and 16, and Phi exchange adds kinematic dependence."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{"RA_pair":"integral dp0/(2pi) G_R G_A=1/(4E^2 Gamma) in the pole approximation",
            "source_match":"(2q p_i)^2*[1/(4E^2 Gamma)]*[-dn/dE]=(q p_i/E)^2*n(1+n)/(T Gamma)",
            "legacy_rung":"sigma_legacy=lambda^2/(16*pi*s)",
            "required_rung":"sigma_channel=|M_contact+M_Phi(s,t,u)|^2/[16*pi*s*S_final] with charge-resolved channels"},
        "ontology":{"C":"not q or collision density","Phi":"effective response; exchange is lane-specific, not particle ontology","R_gen":"excluded","R_obs":"excluded"},
        "unit_lane":"natural_units","units":{"E":1,"Gamma_width":1,"RA_pair_integral":-3,"cross_section":-2},
        "derivation_class":"pole_approximation_match_and_structural_rung_no_go","observable":"Microscopic-to-kinetic normalization and rung compatibility boundary",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC","config":asdict(CFG),"RA_pair_rows":pair_rows,"source_match_rows":source_rows,
        "rung_comparison_rows":rung_rows,"checks":checks,"open_blockers":["charge_resolved_contact_plus_Phi_SK_rung",
            "self_consistent_width_from_same_rung","number_changing_response_channels","continuum_ladder_and_heat_current_match"],
        "controlling_blocker":"charge_resolved_contact_plus_Phi_SK_rung_and_self_consistent_width_missing",
        "source_hashes":{p:sha(p) for p in paths},"evidence_artifacts":[{"path":p,"sha256":sha(p)} for p in priors],
        "dependency_unlocked":["dressed_RA_pair_to_kinetic_source_normalization"],"full_core_unlock":False,"claim_promotion":False,
        "xie_2026_accessed":False,"parameter_fitting_performed":False,
        "claim_boundary":"Dressed pole-pair normalization and legacy-rung incompatibility only; not a completed microscopic rung, self-consistent width, ladder, physical Kubo/SI coefficient or Full Topic 13 closure."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"CLOSED_FOR_LANE/CLOSED_AS_NO_GO","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":artifact["dependency_unlocked"],"STATUS":artifact["verification_status"],
        "WHAT_CHANGED":"Closed the dressed RA-pair normalization and blocked reuse of the legacy constant-amplitude rung as a microscopic action match.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,"CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Replace the legacy rung by charge-resolved contact plus Phi-exchange SK cuts and derive Gamma from the same kernel before solving the ladder.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","unit_lane","units","derivation_class","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"version":"1","classification":"structural_interface_no_go","relation_or_code_path":artifact["equation_or_mapping"],
        "standard_physics_counterpart":"Pinch-pole kinetic reduction and cut four-point ladder rung","variables":{"Gamma_width":"dressed pole width","M":"charge-resolved scattering amplitude"},
        "mathematical_role":"RA pair and rung matching boundary","observable_mapping":artifact["observable"],"parameter_dimensions":artifact["units"],
        "source_or_origin":"Canonical current/pole approximation and production action scattering amplitude","assumptions":{"pole":"narrow positive-energy quasiparticle","rung_comparison":"same synthetic action coefficients"},
        "symmetry_and_conservation":"charge-resolved channels required","limiting_cases":["Gamma>0","G=0 contact","G nonzero Phi exchange"],
        "implementation_paths":[paths[0]],"verifier_paths":[paths[1]],"evidence_class":"INTERNAL_STRUCTURAL_DIAGNOSTIC",
        "proof_status":"RA_PAIR_MATCHED_LEGACY_RUNG_REJECTED","evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT)}],
        "downstream_dependencies":[],"dependency_role":"microscopic_ladder_controller","physical_dependency_unlock":False,
        "failure_mode":artifact["open_blockers"],"next_hardening_step":artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"rung_rows":rung_rows},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__": raise SystemExit(main())
