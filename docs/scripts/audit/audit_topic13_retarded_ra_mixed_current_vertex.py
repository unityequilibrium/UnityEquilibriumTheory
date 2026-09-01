"""Retarded/advanced continuation of the mixed one-loop current triangle.

Thermal residue weights are fixed before analytic continuation.  The current
leg is the latest-time leg: its energy has positive imaginary part while the
two charged legs have negative imaginary parts whose sum is conserved.  The
strict zero-width transport limit is reported as a pinch boundary, not used
as a Kubo coefficient.
"""
from __future__ import annotations
from dataclasses import asdict
from math import sqrt
from pathlib import Path
import hashlib
import json
import numpy as np

from docs.scripts.audit import audit_topic13_charged_one_loop_current_vertex as euclidean

CFG = euclidean.CFG
charged = euclidean.charged
thermal = euclidean.thermal
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_retarded_ra_mixed_current_vertex_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_retarded_ra_vertex_addendum.json"
EQUATION_ID = "uet.o2.thermal.retarded_ra_mixed_current_vertex"


def weighted_residue_sum(roots, weights, numerator):
    result = 0j
    for i, (root, weight) in enumerate(zip(roots, weights)):
        denominator = np.prod([root - other for j, other in enumerate(roots) if j != i])
        if abs(denominator) < 1e-15:
            raise ValueError("coincident real-time poles require a finite width or confluent branch")
        result += weight * numerator(root) / denominator
    return result


def mixed_ra_integrand(k, costheta, T, q, P0, Q0, pz, Qz, mu, cfg=CFG):
    W = sqrt(k*k + cfg.response_mass_sq)
    E1 = sqrt(k*k + pz*pz - 2*k*pz*costheta + cfg.mass**2)
    p2 = pz + Qz
    E2 = sqrt(k*k + p2*p2 - 2*k*p2*costheta + cfg.mass**2)
    roots = (W, -W, -q*mu + 1j*P0 + E1, -q*mu + 1j*P0 - E1,
             -q*mu + 1j*(P0+Q0) + E2, -q*mu + 1j*(P0+Q0) - E2)
    weights = (float(charged.occupation(W,T)), -float(charged.occupation(W,T)),
               float(charged.occupation(E1-q*mu,T)), -float(charged.occupation(E1+q*mu,T)),
               float(charged.occupation(E2-q*mu,T)), -float(charged.occupation(E2+q*mu,T)))
    temporal = lambda x: q*(2*P0+Q0+2j*x+2j*q*mu)
    spatial = lambda x: q*(2*(pz-k*costheta)+Qz)
    return np.array([weighted_residue_sum(roots,weights,temporal),
                     weighted_residue_sum(roots,weights,spatial)],complex)


def ra_vertex(T=.25, mu=.2, q=1, pz=.3, Qz=.2, omega=.15, eta=.02,
              cfg=CFG, *, order_radial=96, order_angle=48):
    if T <= 0 or q not in (-1,1) or eta <= 0 or abs(mu) >= cfg.mass:
        raise ValueError("positive T/eta, signed charge and strict normal gap required")
    if not all(np.isfinite(x) for x in (mu,pz,Qz,omega,eta)):
        raise ValueError("finite kinematics required")
    Omega = sqrt(pz*pz + cfg.mass**2)
    z_in = Omega - 1j*eta
    z_current = omega + 2j*eta
    P0 = 1j*(z_in-q*mu)
    Q0 = 1j*z_current
    mixed = cfg.cubic**2*euclidean.integrate_vertex_integrand(
        mixed_ra_integrand,T,q,P0,Q0,pz,Qz,mu,cfg=cfg,
        order_radial=order_radial,order_angle=order_angle)
    vacuum = euclidean.vacuum_vertex(P0,Q0,pz,Qz,q,mu,cfg)
    bare = q*np.array([2*(P0+1j*q*mu)+Q0,2*pz+Qz],complex)
    total = bare+mixed+vacuum
    before = euclidean.mixed_thermal_self_energy(P0,pz,T,q,mu,cfg,order_radial,order_angle)+euclidean.vacuum_self_energy(P0,pz,q,mu,cfg)
    after = euclidean.mixed_thermal_self_energy(P0+Q0,pz+Qz,T,q,mu,cfg,order_radial,order_angle)+euclidean.vacuum_self_energy(P0+Q0,pz+Qz,q,mu,cfg)
    Q = np.array([Q0,Qz],complex)
    bare_difference = ((P0+Q0+1j*q*mu)**2+(pz+Qz)**2-(P0+1j*q*mu)**2-pz*pz)
    target = q*(bare_difference+after-before)
    transverse_basis = np.array([Qz,-Q0],complex)
    transverse_coefficient = complex((transverse_basis@total)/(transverse_basis@transverse_basis))
    return {"T":T,"mu":mu,"q":q,"pz":pz,"Qz":Qz,"omega":omega,"eta":eta,
            "Omega_in":Omega,"P0":P0,"Q0":Q0,"bare":bare,"mixed_thermal":mixed,
            "vacuum":vacuum,"total":total,"Ward_lhs":complex(Q@total),"Ward_target":complex(target),
            "Ward_relative_error":float(abs(Q@total-target)/max(abs(target),1e-300)),
            "transverse_coefficient":transverse_coefficient,
            "prescription":"current latest-time: Im z_current=+2 eta; incoming/outgoing charged legs=-eta",
            "boundary":"Proper bare+mixed+vacuum RA vertex; response-relaxed bath and collision ladder excluded."}


def matsubara_reduction_witness(T=.25,q=1,mu=.2,k=.7,c=.23,pz=.3,Qz=.4,nP=1,nQ=1):
    from math import pi
    P0=2*pi*T*nP; Q0=2*pi*T*nQ
    old=euclidean.mixed_triangle_integrand(k,c,T,q,P0,Q0,pz,Qz,mu)
    new=mixed_ra_integrand(k,c,T,q,P0,Q0,pz,Qz,mu)
    return float(np.linalg.norm(old-new)/max(np.linalg.norm(old),1e-300))


def zero_transfer_1pi_scan(T=.25,mu=.2,q=1,pz=.3,c=.2,k=.3):
    Omega=sqrt(pz*pz+CFG.mass**2)
    rows=[]
    for eta in (.08,.04,.02,.01,.005):
        P0=1j*(Omega-1j*eta-q*mu); Q0=1j*(2j*eta)
        value=mixed_ra_integrand(k,c,T,q,P0,Q0,pz,0.,mu)
        rows.append({"eta":eta,"norm":float(np.linalg.norm(value)),"eta_times_norm":float(eta*np.linalg.norm(value))})
    return rows


def _serial(value):
    if isinstance(value,complex): return [value.real,value.imag]
    if isinstance(value,np.ndarray): return [_serial(x) for x in value]
    if isinstance(value,np.generic): return value.item()
    if isinstance(value,dict): return {k:_serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [_serial(v) for v in value]
    return value


def main():
    rows=[ra_vertex(q=q,eta=eta) for q in (-1,1) for eta in (.04,.02,.01)]
    reductions=[matsubara_reduction_witness(q=q) for q in (-1,1)]
    finite=[ra_vertex(eta=eta) for eta in (.04,.02,.01)]
    finite_changes=[float(np.linalg.norm(b["total"]-a["total"])/np.linalg.norm(b["total"]))
                    for a,b in zip(finite,finite[1:])]
    zero_scan=zero_transfer_1pi_scan()
    zero_last_change=abs(zero_scan[-1]["norm"]/zero_scan[-2]["norm"]-1)
    checks={"frozen_weights_reduce_to_Matsubara":max(reductions)<1e-13,
        "continued_Ward_identity":max(r["Ward_relative_error"] for r in rows)<2e-8,
        "finite_transfer_eta_convergence":finite_changes[-1]<.02,
        "finite_nonzero_transverse_component":all(np.isfinite(r["transverse_coefficient"]) and abs(r["transverse_coefficient"])>0 for r in rows),
        "proper_1PI_zero_transfer_no_inverse_eta_growth":zero_scan[-1]["norm"]<2*zero_scan[0]["norm"],
        "proper_1PI_zero_transfer_eta_convergence":zero_last_change<1e-3}
    paths=["docs/scripts/audit/audit_topic13_retarded_ra_mixed_current_vertex.py",
        "docs/core/test/test_topic13_retarded_ra_mixed_current_vertex.py",
        "docs/scripts/audit/audit_topic13_charged_one_loop_current_vertex.py",
        "docs/scripts/audit/audit_topic13_microscopic_current_ladder_matching_boundary.py"]
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    priors=["docs/core/artifacts/t13_charged_one_loop_current_vertex_audit.json",
        "docs/core/artifacts/t13_microscopic_current_ladder_matching_boundary_audit.json"]
    artifact={"schema_version":"t13-retarded-ra-mixed-current-vertex-v1",
        "major_result_id":"T13_RETARDED_RA_MIXED_CURRENT_VERTEX","topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"PARTIAL","verification_status":"PASS_SCOPED_RETARDED_RA_MIXED_VERTEX" if all(checks.values()) else "WARN_RETARDED_RA_MIXED_VERTEX",
        "what_is_closed":["Thermal residue weights are fixed before analytic continuation and reduce exactly to the Matsubara mixed triangle.",
            "The declared latest-time current RA continuation of the proper bare+mixed+vacuum vertex satisfies the continued Ward identity at finite transfer.",
            "The strict proper 1PI zero-transfer scan is finite rather than inverse-eta divergent; transport pinch resummation belongs to the subsequent current-current correlator."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{"RA_prescription":"Im z_current=+2 eta; Im z_in=Im z_out=-eta; energy sum conserved",
            "mixed_triangle":"G^2 sum_residues D_response(K)D_q(P-K)D_q(P+Q-K)gamma_q with thermal weights frozen before continuation",
            "Ward":"Q_mu Gamma_RA^mu=q*[D_RA^-1(P+Q)-D_RA^-1(P)]",
            "transport_boundary":"proper Gamma_RA remains finite; pinch pair arises only after RA external propagators in the current-current/ladder equation"},
        "ontology":{"C":"collective coordinate, not charge","Phi":"effective response, not a particle identity","R_gen":"excluded derived trace","R_obs":"excluded"},
        "unit_lane":"natural_units","units":{"energy":1,"momentum":1,"eta":1,"Gamma":1},
        "derivation_class":"analytic_continuation_with_numerical_quadrature",
        "observable":"Proper RA charged three-point vertex diagnostic, not a Kubo coefficient",
        "data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC","config":asdict(CFG),"samples":_serial(rows),
        "matsubara_reduction_residuals":reductions,"finite_transfer_eta_relative_changes":finite_changes,
        "zero_transfer_proper_1pi_probe":zero_scan,"failed_hypothesis":"The first probe expected inverse-eta growth in the proper triangle; the computed norm converged, locating the pinch requirement in the current-current RA pair instead.",
        "checks":checks,"open_blockers":["response_relaxed_bath_RA_continuation","same_action_on_shell_residue_LSZ_match",
            "current_current_RA_pinch_pair_with_finite_width","microscopic_retarded_four_point_ladder_kernel","continuum_heat_current_and_SI_mapping"],
        "controlling_blocker":"same_action_current_current_RA_pinch_and_four_point_ladder_kernel_missing",
        "source_hashes":{p:sha(p) for p in paths},"evidence_artifacts":[{"path":p,"sha256":sha(p)} for p in priors],
        "literature_context":[{"url":"https://doi.org/10.1103/PhysRevD.49.4107","role":"Primary all-orders imaginary-to-retarded N-point continuation context; no numeric input"},
            {"url":"https://doi.org/10.1103/PhysRevD.52.3591","role":"Primary scalar transport ladder/pinch and kinetic-equation equivalence context; no numeric input"}],
        "dependency_unlocked":["proper_mixed_RA_vertex_handoff_to_current_current_kernel"],"full_core_unlock":False,
        "claim_promotion":False,"xie_2026_accessed":False,"parameter_fitting_performed":False,
        "claim_boundary":"Proper bare+mixed+vacuum RA one-loop vertex in a declared finite-transfer branch only; response-relaxed bath, dressed RA pair, microscopic ladder, Kubo/heat transport, SI, external validation and Full Topic 13 remain open."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":artifact["dependency_unlocked"],
        "STATUS":artifact["verification_status"],"WHAT_CHANGED":"Added a declared latest-time RA continuation with frozen thermal weights and relocated the failed 1/eta hypothesis from the proper vertex to the current-current RA pair.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Construct the same-action dressed RA propagator pair and microscopic four-point rung, then test the ladder/kinetic equivalence with an explicit width ledger.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","unit_lane","units","derivation_class","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"version":"1","classification":"numerical_analytic_continuation",
        "relation_or_code_path":artifact["equation_or_mapping"],"standard_physics_counterpart":"Latest-time retarded thermal three-point analytic continuation",
        "variables":{"Gamma_RA":"proper RA current vertex","eta":"declared continuation regulator, not fitted width","q":"O(2) charge, not C"},
        "mathematical_role":"Proper retarded/advanced three-point kernel","observable_mapping":artifact["observable"],
        "parameter_dimensions":artifact["units"],"source_or_origin":"Canonical one-loop diagrams with thermal weights fixed before continuation",
        "assumptions":{"current_leg":"latest time","external_imaginary_parts":"(+2,-1,-1)*eta","scope":"proper mixed plus vacuum and bare"},
        "symmetry_and_conservation":"Continued O(2) Ward identity","limiting_cases":["Matsubara reduction","finite eta","proper zero transfer"],
        "implementation_paths":[paths[0]],"verifier_paths":[paths[1]],"evidence_class":"INTERNAL_SYNTHETIC_DIAGNOSTIC",
        "proof_status":"CHECKED_DECLARED_RA_PROPER_VERTEX_ONLY","evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT)}],
        "downstream_dependencies":[],"dependency_role":"proper_RA_vertex_handoff_only","physical_dependency_unlock":False,
        "failure_mode":artifact["open_blockers"],"next_hardening_step":artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"Ward_errors":[r["Ward_relative_error"] for r in rows],
        "finite_transfer_changes":finite_changes,"zero_transfer_probe":zero_scan},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
