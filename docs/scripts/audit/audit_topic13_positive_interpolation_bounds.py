"""Positive local-radius bounds and existing-rate-weighted channel error."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_interpolation_refinement import (
    grid,natural_bridge_config,energy_momentum_conserving_bs_state,
    action_derived_transition_kernel_state,_interpolation_matrix,
)


def positive_bounds(s,p,e,target_p,target_e,mass,incidence,rates):
    s=np.asarray(s); p=np.asarray(p); target_p=np.asarray(target_p)
    e=np.asarray(e); target_e=np.asarray(target_e); rates=np.asarray(rates)
    if not np.all(np.isfinite(s)) or np.any(s<0) or not np.allclose(s.sum(axis=0),1,rtol=0,atol=1e-12):
        raise ValueError("positive normalized interpolation required")
    if mass<=0 or np.any(rates<0) or not np.any(rates>0):
        raise ValueError("positive mass and nonnegative nonzero rates required")
    distance=np.linalg.norm(p[:,None,:]-target_p[None,:,:],axis=2)
    radius=np.sum(s*distance,axis=0)
    basis=np.column_stack((p[:,0]*p[:,1]/e**2,mass/e))
    target=np.column_stack((target_p[:,0]*target_p[:,1]/target_e**2,mass/target_e))
    error=s.T@basis-target
    lipschitz=np.array([1/mass,2/(3*np.sqrt(3)*mass)])
    normalization_defect=np.abs(s.sum(axis=0)-1)
    bound=radius[:,None]*lipschitz[None,:]+normalization_defect[:,None]*np.abs(target)
    channel_error=np.asarray(incidence)@error
    channel_bound=np.abs(incidence)@bound
    scaled_rates=rates/rates.max()
    normalized=scaled_rates/scaled_rates.sum()
    return dict(radius_mean=float(radius.mean()),radius_max=float(radius.max()),
        normalization_defect_max=float(normalization_defect.max()),
        lipschitz=lipschitz.tolist(),leg_error_rms=np.sqrt(np.mean(error**2,axis=0)).tolist(),
        leg_bound_rms=np.sqrt(np.mean(bound**2,axis=0)).tolist(),
        max_leg_bound_violation=float(np.max(np.maximum(np.abs(error)-bound,0))),
        rate_weighted_channel_error_rms=np.sqrt(normalized@(channel_error**2)).tolist(),
        rate_weighted_channel_bound_rms=np.sqrt(normalized@(channel_bound**2)).tolist(),
        raw_rate_weighted_error_norm=(np.sqrt(rates.max())*np.sqrt(scaled_rates@(channel_error**2))).tolist(),
        max_channel_bound_violation=float(np.max(np.maximum(np.abs(channel_error)-channel_bound,0))))


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_interpolation_refinement_plan.json"
    plan=json.loads((ROOT/plan_path).read_text()); config=natural_bridge_config(); state=plan["state"]
    base=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
        angular_order=24,cutoff_factor=plan["cutoff_factor"])
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=plan["transition_order"],
        channel_count=plan["channel_count"],cutoff_factor=plan["cutoff_factor"])
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    ep=np.asarray(exact.state_momenta); ee=np.asarray(exact.state_energies)
    r=dict(major_result_id="T13_POSITIVE_INTERPOLATION_ERROR_BOUND",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending local and channel bound measurements",
        equation_or_mapping="|error_leg|<=L sum_i a_i |p_i-p_target|+|sum a-1| |probe_target|; |error_channel|<=|incidence| bound_leg",
        units="Natural momentum radius, inverse-momentum Lipschitz constants; dimensionless probes",
        derivation_class="Lipschitz/triangle inequalities and positive-rate norm monotonicity",
        observable="Two probe approximation errors; not whole collision-operator error",
        data_role="INTERNAL_NO_FIT",plan=plan,rows=[],
        rates_policy="Original sampled rates unchanged; normalization is only for descriptive RMS, not a physical probability law",
        dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["full_operator_consistency","boundary_and_projection_control","material_mapping"],
        claim_boundary="Bounds cover specified probe amplitudes, not arbitrary distributions, transport coefficient error or continuum convergence. No output clipping: positive-part expressions report violation only.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            plan_path,"docs/scripts/audit/audit_topic13_positive_interpolation_bounds.py",
            "docs/core/test/test_topic13_positive_interpolation_bounds.py",
            "docs/scripts/audit/audit_topic13_interpolation_refinement.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_action_derived_transition_kernel.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_positive_interpolation_bounds_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for radial in plan["radial_orders"]:
        for angular in plan["angular_rules"]:
            signs,p,e=grid(radial,angular,base.momentum_cutoff,base.effective_mass)
            s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
                tuple(signs),tuple(map(tuple,p)),tuple(e),cutoff=base.momentum_cutoff,support_order=plan["support_order"])
            row=dict(radial_order=radial,angular_rule=angular,
                **positive_bounds(s,p,e,ep,ee,base.effective_mass,incidence,exact.channel_rates))
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="PROBE_BOUNDS_MEASURED_NOT_OPERATOR_CLOSURE",
        verification_status="NINE_POSITIVE_GRIDS_EVALUATED",what_is_closed="Local Lipschitz and channel error bounds measured on the nine fixed grids")
    save()


if __name__=="__main__": main()
