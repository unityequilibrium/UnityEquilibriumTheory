"""Segment-local derivative bounds and a two-probe collision-form certificate."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_positive_interpolation_bounds import (
    grid,natural_bridge_config,energy_momentum_conserving_bs_state,
    action_derived_transition_kernel_state,_interpolation_matrix,
)


def segment_constants(p,target,mass):
    """Maximize radial gradient envelopes on each complete straight segment."""
    if mass<=0: raise ValueError("positive mass required")
    p=np.asarray(p,dtype=float); target=np.asarray(target,dtype=float)
    delta=p-target; square=np.sum(delta*delta,axis=1)
    fraction=np.divide(-delta@target,square,out=np.zeros_like(square),where=square>0)
    # Geometric segment minimizer, not clipping data or physical outputs.
    fraction=np.minimum(1.,np.maximum(0.,fraction))
    lower=np.linalg.norm(target+fraction[:,None]*delta,axis=1)
    upper=np.maximum(np.linalg.norm(p,axis=1),np.linalg.norm(target))
    peak_one=mass*np.sqrt((3+np.sqrt(17))/4)
    peak_two=mass/np.sqrt(2)
    r1=np.maximum(lower,np.minimum(peak_one,upper))
    r2=np.maximum(lower,np.minimum(peak_two,upper))
    d=mass*mass+r1*r1
    return np.column_stack((r1/d+r1**3/d**2,mass*r2/(mass*mass+r2*r2)**1.5))


def quadratic_certificate(exact,mapped,bounds,rates):
    rates=np.asarray(rates)
    if np.any(rates<0) or not np.any(rates>0): raise ValueError("nonnegative nonzero rates required")
    scaled=rates/rates.max(); normalized=scaled/scaled.sum()
    a=np.sqrt(normalized)[:,None]*exact; b=np.sqrt(normalized)[:,None]*mapped
    epsilon=np.linalg.norm(np.sqrt(normalized)[:,None]*bounds)
    limit=2*np.linalg.norm(a,2)*epsilon+epsilon**2
    difference=np.linalg.norm(b.T@b-a.T@a,2)
    return dict(exact_gram=(a.T@a).tolist(),mapped_gram=(b.T@b).tolist(),
        error_norm=float(difference),error_bound=float(limit),amplitude_error_bound=float(epsilon),
        actual_amplitude_error=float(np.linalg.norm(b-a,2)),
        raw_rate_sum=float(rates.max()*scaled.sum()),
        raw_quadratic_error_bound=float(limit*rates.max()*scaled.sum()))


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_interpolation_refinement_plan.json"
    plan=json.loads((ROOT/plan_path).read_text()); state=plan["state"]; config=natural_bridge_config()
    base=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
        angular_order=24,cutoff_factor=plan["cutoff_factor"])
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=plan["transition_order"],
        channel_count=plan["channel_count"],cutoff_factor=plan["cutoff_factor"])
    m=base.effective_mass; ep=np.asarray(exact.state_momenta); ee=np.asarray(exact.state_energies)
    target=np.column_stack((ep[:,0]*ep[:,1]/ee**2,m/ee))
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    r=dict(major_result_id="T13_LOCAL_TWO_PROBE_QUADRATIC_ERROR_BOUND",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending segment and quadratic bounds",
        equation_or_mapping="||B.T B-A.T A||_2 <= 2||A||_2 epsilon+epsilon^2; epsilon bounds ||B-A||_2 via local leg bounds",
        units="Rate-normalized probe Gram, plus raw rate-scaled bound",
        derivation_class="Analytic segment derivative envelope and matrix norm inequality",
        observable="Collision quadratic form restricted to two fixed probes, not full operator norm",
        data_role="INTERNAL_NO_FIT",rows=[],dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["larger_function_space_certificate","projection_and_boundary_control","transport_uncertainty","material_mapping"],
        claim_boundary="No closure of the full collision operator or inverse transport; exact sampled channels are the reference, not continuum data",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            plan_path,"docs/scripts/audit/audit_topic13_local_quadratic_bounds.py",
            "docs/core/test/test_topic13_local_quadratic_bounds.py",
            "docs/scripts/audit/audit_topic13_positive_interpolation_bounds.py",
            "docs/scripts/audit/audit_topic13_interpolation_refinement.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_local_quadratic_bounds_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for radial in plan["radial_orders"]:
        for angular in plan["angular_rules"]:
            signs,p,e=grid(radial,angular,base.momentum_cutoff,m)
            s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
                tuple(signs),tuple(map(tuple,p)),tuple(e),cutoff=base.momentum_cutoff,support_order=plan["support_order"])
            basis=np.column_stack((p[:,0]*p[:,1]/e**2,m/e))
            mapped=s.T@basis; bounds=[]; globals_=[]
            for col in range(len(ee)):
                support=np.flatnonzero(s[:,col]>0); weight=s[support,col]
                distance=np.linalg.norm(p[support]-ep[col],axis=1)
                defect=abs(weight.sum()-1)*np.abs(target[col])
                bounds.append((weight*distance)@segment_constants(p[support],ep[col],m)+defect)
                globals_.append((weight@distance)*np.array([1/m,2/(3*np.sqrt(3)*m)])+defect)
            bounds=np.asarray(bounds); globals_=np.asarray(globals_)
            channel_bound=np.abs(incidence)@bounds
            cert=quadratic_certificate(incidence@target,incidence@mapped,channel_bound,exact.channel_rates)
            row=dict(radial_order=radial,angular_rule=angular,
                local_leg_bound_rms=np.sqrt(np.mean(bounds**2,axis=0)).tolist(),
                global_leg_bound_rms=np.sqrt(np.mean(globals_**2,axis=0)).tolist(),
                actual_leg_error_rms=np.sqrt(np.mean((mapped-target)**2,axis=0)).tolist(),
                max_leg_violation=float(np.max(np.maximum(np.abs(mapped-target)-bounds,0))),
                max_local_exceeds_global=float(np.max(np.maximum(bounds-globals_,0))),
                certificate=cert)
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="LOCAL_PROBE_FORM_CERTIFICATE_NOT_FULL_OPERATOR_CLOSURE",
        verification_status="ALL_NINE_FIXED_GRIDS_EVALUATED",what_is_closed="Segment-local bounds and two-probe quadratic certificate evaluated")
    save()


if __name__=="__main__": main()
