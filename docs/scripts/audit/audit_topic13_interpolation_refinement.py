"""Separate radial/angular mapping refinement, retaining rank failures."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_moment_interpolation import (
    moment_correct,probe_errors,natural_bridge_config,action_derived_transition_kernel_state,
    energy_momentum_conserving_bs_state,_interpolation_matrix,
)
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import _radial_quadrature,_moment_direction_rule


def sphere_rule(name):
    if name=="axis_cube14": return tuple(np.asarray(a) for a in _moment_direction_rule(name))
    options={"product4x8":(4,8),"product8x16":(8,16)}
    nmu,nphi=options[name]
    mu,w=np.polynomial.legendre.leggauss(nmu)
    phi=2*np.pi*np.arange(nphi)/nphi
    directions=np.array([[np.sqrt(1-z*z)*np.cos(a),np.sqrt(1-z*z)*np.sin(a),z] for z in mu for a in phi])
    return directions,np.repeat(w/(2*nphi),nphi)


def grid(radial,angular,cutoff,mass):
    radii,_=_radial_quadrature(radial,cutoff)
    directions,_=sphere_rule(angular)
    momenta=(radii[:,None,None]*directions[None,:,:]).reshape(-1,3)
    signs=np.repeat([-1.,1.],len(momenta))
    momenta=np.tile(momenta,(2,1))
    energies=np.sqrt(mass*mass+np.sum(momenta*momenta,axis=1))
    return signs,momenta,energies


def deficient_columns(s,features,floor):
    bad=[]
    for col in range(s.shape[1]):
        a=features[s[:,col]>0].T
        singular=np.linalg.svd(a,compute_uv=False)
        if len(singular)!=features.shape[1] or singular[-1]<=floor*singular[0]: bad.append(col)
    return bad


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_interpolation_refinement_plan.json"
    plan=json.loads((ROOT/plan_path).read_text()); config=natural_bridge_config(); state=plan["state"]
    base=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
        angular_order=24,cutoff_factor=plan["cutoff_factor"])
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=plan["transition_order"],
        channel_count=plan["channel_count"],cutoff_factor=plan["cutoff_factor"])
    ep=np.asarray(exact.state_momenta); ee=np.asarray(exact.state_energies); cutoff=base.momentum_cutoff
    outside=np.linalg.norm(ep,axis=1)>cutoff
    target=np.column_stack((np.ones(len(ee)),ee/cutoff,ep/cutoff))
    r=dict(major_result_id="T13_INTERPOLATION_REFINEMENT_DIAGNOSTIC",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending nine-grid mapping study",
        equation_or_mapping="Same local signed moment correction; product sphere nodes from Gauss-Legendre mu and uniform azimuth",
        units="natural grid; dimensionless probe error",derivation_class="Numerical refinement experiment",
        observable="Nonlinear interpolation probes, not transport",data_role="INTERNAL_NO_FIT",plan=plan,rows=[],
        outside_cutoff_target_count=int(np.sum(np.linalg.norm(ep,axis=1)>cutoff)),
        outside_cutoff_target_indices=np.flatnonzero(outside).tolist(),
        dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["rank_robust_local_support","nonlinear_interpolation_convergence","physical_material_mapping"],
        claim_boundary=plan["policy"],
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            plan_path,"docs/scripts/audit/audit_topic13_interpolation_refinement.py",
            "docs/core/test/test_topic13_interpolation_refinement.py",
            "docs/scripts/audit/audit_topic13_moment_interpolation.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_interpolation_refinement_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for radial in plan["radial_orders"]:
        for angular in plan["angular_rules"]:
            row=dict(radial_order=radial,angular_rule=angular)
            try:
                signs,p,e=grid(radial,angular,cutoff,base.effective_mass)
                s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
                    tuple(signs),tuple(map(tuple,p)),tuple(e),cutoff=cutoff,support_order=plan["support_order"])
                features=np.column_stack((np.ones(len(e)),e/cutoff,p/cutoff))
                bad=deficient_columns(s,features,plan["rank_relative_floor"])
                row.update(state_count=len(e),rank_deficient_indices=bad,rank_deficient_count=len(bad),
                    positive_probes=probe_errors(s,p,e,ep,ee,base.effective_mass))
                row["rank_deficient_inside_count"]=sum(not outside[i] for i in bad)
                row["rank_deficient_outside_count"]=sum(bool(outside[i]) for i in bad)
                if bad: row["status"]="BLOCKED_RANK"
                else:
                    corrected,report=moment_correct(s,features,target,plan["rank_relative_floor"])
                    row.update(status="EVALUATED",mapping=report,
                        corrected_probes=probe_errors(corrected,p,e,ep,ee,base.effective_mass))
                    row["domain_probes"]={name:dict(count=int(mask.sum()),
                        positive=probe_errors(s[:,mask],p,e,ep[mask],ee[mask],base.effective_mass),
                        corrected=probe_errors(corrected[:,mask],p,e,ep[mask],ee[mask],base.effective_mass))
                        for name,mask in (("inside",~outside),("outside",outside)) if np.any(mask)}
            except Exception as exc: row.update(status="ERROR",error=str(exc))
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="REFINEMENT_MEASURED_WITH_EXPLICIT_RANK_FAILURES" if any(x["status"]!="EVALUATED" for x in r["rows"]) else "REFINEMENT_MEASURED_NOT_CERTIFIED",
        verification_status="ALL_NINE_LOCKED_GRIDS_ATTEMPTED",what_is_closed="Probe trends and fixed-support rank failures evaluated")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in r["rows"]) else 1


if __name__=="__main__": raise SystemExit(main())
