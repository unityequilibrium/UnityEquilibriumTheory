"""Signed local moment reproduction, separate from physical probability weights."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_interpolation_support import (
    tensor_response,natural_bridge_config,finite_temperature_o2_state,
    action_derived_transition_kernel_state,energy_momentum_conserving_bs_state,_interpolation_matrix,
)


def moment_correct(s,basis_features,target_features,rank_floor=1e-12):
    s=np.asarray(s,dtype=float); b=np.asarray(basis_features,dtype=float); target=np.asarray(target_features,dtype=float)
    if s.shape!=(len(b),len(target)) or b.shape[1]!=target.shape[1] or any(not np.all(np.isfinite(x)) for x in (s,b,target)) or np.any(s<0):
        raise ValueError("finite compatible features and nonnegative seed required")
    corrected=s.copy(); conditions=[]
    for col in range(s.shape[1]):
        support=np.flatnonzero(s[:,col]>0)
        a=b[support].T
        singular=np.linalg.svd(a,compute_uv=False)
        if len(singular)!=b.shape[1] or singular[-1]<=rank_floor*singular[0]:
            raise ValueError("rank-deficient fixed interpolation support")
        q,r=np.linalg.qr(a.T,mode="reduced")
        delta=q@np.linalg.solve(r.T,target[col]-a@s[support,col])
        corrected[support,col]+=delta
        conditions.append(float(singular[0]/singular[-1]))
    return corrected,dict(max_feature_residual=float(np.max(np.abs(corrected.T@b-target))),
        max_condition=max(conditions),minimum_coefficient=float(corrected.min()),
        negative_coefficient_count=int(np.sum(corrected<0)),
        max_column_l1=float(np.max(np.sum(np.abs(corrected),axis=0))),
        correction_frobenius=float(np.linalg.norm(corrected-s)))


def probe_errors(s,p,e,target_p,target_e,mass):
    b=np.column_stack((p[:,0]*p[:,1]/e**2,mass/e))
    target=np.column_stack((target_p[:,0]*target_p[:,1]/target_e**2,mass/target_e))
    error=s.T@b-target
    return dict(rms_absolute=np.sqrt(np.mean(error**2,axis=0)).tolist(),maximum_absolute=np.max(np.abs(error),axis=0).tolist())


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_moment_interpolation_plan.json"
    plan=json.loads((ROOT/plan_path).read_text()); state=plan["state"]; config=natural_bridge_config()
    eos=finite_temperature_o2_state(*state,config); h=(eos.energy_density+eos.pressure)/eos.charge_density
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=plan["transition_quadrature_order"],
        channel_count=plan["transition_channel_count"],cutoff_factor=plan["controls"]["cutoff_factor"])
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    ep=np.asarray(exact.state_momenta); ee=np.asarray(exact.state_energies)
    record=dict(major_result_id="T13_SIGNED_MOMENT_INTERPOLATION_CANDIDATE",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending fixed-support candidate evaluation",
        equation_or_mapping="A s=t; delta_s=Q solve(R.T,t-A s0), with A.T=Q R; minimize ||s-s0||_2",
        units="Dimensionless scaled moment features and coefficients; natural thermal response",
        derivation_class="Constrained numerical interpolation ansatz, not microscopic physics",
        observable="Per-leg moment reproduction and internal tensor",data_role="INTERNAL_NO_FIT",
        plan=plan,rows=[],dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["nonlinear_interpolation_accuracy","refinement_and_input_sensitivity","material_mapping"],
        claim_boundary=plan["policy"],
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            plan_path,"docs/scripts/audit/audit_topic13_moment_interpolation.py",
            "docs/core/test/test_topic13_moment_interpolation.py",
            "docs/scripts/audit/audit_topic13_interpolation_support.py",
            "docs/scripts/audit/audit_topic13_constrained_tensor.py",
            "docs/scripts/audit/audit_topic13_constrained_precision.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_action_derived_transition_kernel.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_moment_interpolation_audit.json"
    def save(): out.write_text(json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for rule in plan["direction_rules"]:
        row=dict(rule=rule)
        try:
            b=energy_momentum_conserving_bs_state(*state,config,**plan["controls"],_direction_rule=rule)
            p=np.asarray(b.state_momenta); e=np.asarray(b.state_energies); q=np.asarray(b.charge_by_state)
            s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
                b.state_species_signs,b.state_momenta,b.state_energies,cutoff=b.momentum_cutoff,support_order=plan["support_order"])
            scale=b.momentum_cutoff
            bf=np.column_stack((np.ones(len(e)),e/scale,p/scale))
            tf=np.column_stack((np.ones(len(ee)),ee/scale,ep/scale))
            corrected,diagnostic=moment_correct(s,bf,tf,plan["rank_relative_floor"])
            row.update(mapping=diagnostic,legacy_feature_residual=float(np.max(np.abs(s.T@bf-tf))),
                legacy_probes=probe_errors(s,p,e,ep,ee,b.effective_mass),
                corrected_probes=probe_errors(corrected,p,e,ep,ee,b.effective_mass),
                raw_channel_feature_residual=float(np.max(np.abs(incidence@corrected.T@bf))))
            print(json.dumps(dict(rule=rule,mapping=diagnostic)),flush=True)
            forces=(e-h*q)[:,None]*p/e[:,None]
            row.update(tensor_response(b.susceptibility_weights,b.collision_widths,incidence@corrected.T,
                exact.channel_rates,np.column_stack((q,e,p)),forces,plan["dps"]),status="EVALUATED")
        except Exception as exc: row.update(status="ERROR",error=str(exc))
        record["rows"].append(row);save();print(json.dumps(row),flush=True)
    record.update(completed=True,status="SIGNED_MOMENT_CANDIDATE_MEASURED_NOT_CONVERGED",
        verification_status="BOTH_LOCKED_RULES_ATTEMPTED",what_is_closed="Fixed-support moment correction evaluated with nonlinear probes and tensor")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in record["rows"]) else 1


if __name__=="__main__": raise SystemExit(main())
