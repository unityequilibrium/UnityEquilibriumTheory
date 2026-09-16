"""Attribute the fixed finest-grid two-probe Gram error to all sampled channels."""
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


def attribute(exact,mapped,rates):
    a=np.asarray(exact); b=np.asarray(mapped); rates=np.asarray(rates)
    if np.any(rates<0) or not np.any(rates>0): raise ValueError("nonnegative nonzero rates required")
    w=rates/rates.max(); w=w/w.sum()
    reference=w[:,None,None]*np.einsum('ci,cj->cij',a,a)
    delta=w[:,None,None]*(np.einsum('ci,cj->cij',b,b)-np.einsum('ci,cj->cij',a,a))
    total=delta.sum(axis=0); eigen,vectors=np.linalg.eigh(total)
    index=int(np.argmax(np.abs(eigen))); witness=vectors[:,index]
    contributions=np.einsum('i,cij,j->c',witness,delta,witness)
    trace=np.trace(reference,axis1=1,axis2=2)
    fraction=trace/trace.sum()
    return dict(rate_weights=w,reference=reference,delta=delta,witness=witness,
        contributions=contributions,reference_fraction=fraction,
        relative_error=float(np.linalg.norm(total,2)/np.linalg.norm(reference.sum(axis=0),2)),
        rate_concentration_inverse_sum_squares=float(1/np.sum(w*w)),
        reference_concentration_inverse_sum_squares=float(1/np.sum(fraction*fraction)),
        witness_eigenvalue=float(eigen[index]),reconstruction_residual=float(abs(contributions.sum()-eigen[index])))


def main():
    config=natural_bridge_config(); state=(.22,.35,.15)
    base=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
        angular_order=24,cutoff_factor=48.)
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=24,channel_count=64,cutoff_factor=48.)
    signs,p,e=grid(32,"product8x16",base.momentum_cutoff,base.effective_mass)
    ep=np.asarray(exact.state_momenta); ee=np.asarray(exact.state_energies)
    s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
        tuple(signs),tuple(map(tuple,p)),tuple(e),cutoff=base.momentum_cutoff,support_order=40)
    m=base.effective_mass
    target=np.column_stack((ep[:,0]*ep[:,1]/ee**2,m/ee))
    basis=np.column_stack((p[:,0]*p[:,1]/e**2,m/e)); leg_error=s.T@basis-target
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    a=incidence@target; b=incidence@(s.T@basis)
    result=attribute(a,b,exact.channel_rates)
    rows=[]
    for c in range(64):
        indices=np.flatnonzero(incidence[c])
        outside=np.linalg.norm(ep[indices],axis=1)>base.momentum_cutoff
        rows.append(dict(channel_index=c,leg_indices=indices.tolist(),
            rate=float(exact.channel_rates[c]),rate_fraction=float(result["rate_weights"][c]),
            reference_trace_fraction=float(result["reference_fraction"][c]),
            exact_amplitude=a[c].tolist(),mapped_amplitude=b[c].tolist(),
            delta_gram=result["delta"][c].tolist(),
            signed_witness_contribution=float(result["contributions"][c]),
            momenta_over_temperature=(np.linalg.norm(ep[indices],axis=1)/state[0]).tolist(),
            leg_probe_errors=leg_error[indices].tolist(),has_outside_leg=bool(np.any(outside))))
    order=np.argsort(-np.abs(result["contributions"]))
    absolute_total=float(np.sum(np.abs(result["contributions"])))
    r=dict(major_result_id="T13_TWO_PROBE_CHANNEL_ERROR_ATTRIBUTION",topic="0.13",closure_level="PARTIAL",
        status="CHANNEL_ATTRIBUTION_MEASURED",completed=True,
        what_is_closed="All64 signed contributions reconstruct the finest-grid Gram error witness",
        equation_or_mapping="Delta G=sum_c r_c(b_c b_c.T-a_c a_c.T); v.T Delta G v=sum_c witness_contribution_c",
        units="Rate-normalized two-probe Gram",derivation_class="Exact finite-sample matrix decomposition",
        observable="Channel contributions to the previously observed two-probe form error",
        data_role="INTERNAL_FIXED_SAMPLE_NO_FIT",rows=rows,
        worst_coefficient_direction=result["witness"].tolist(),relative_gram_error=result["relative_error"],
        witness_eigenvalue=result["witness_eigenvalue"],reconstruction_residual=result["reconstruction_residual"],
        rate_concentration_inverse_sum_squares=result["rate_concentration_inverse_sum_squares"],
        reference_concentration_inverse_sum_squares=result["reference_concentration_inverse_sum_squares"],
        sorted_channel_indices=order.tolist(),
        top_five_absolute_witness_fraction=float(np.sum(np.abs(result["contributions"][order[:5]]))/absolute_total),
        outside_absolute_witness_fraction=sum(abs(row["signed_witness_contribution"]) for row in rows if row["has_outside_leg"])/absolute_total,
        verification_status="ALL_CHANNELS_INCLUDED_SIGNED_SUM_CHECKED",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["local_interpolation_accuracy_on_dominant_channels","sample_quadrature_representativeness","material_mapping"],
        claim_boundary="Diagnostic ranking is not permission to delete/reweight channels or fit probes. Concentration indices are descriptive, not IID effective sample sizes or statistical error bars. Excludes width and projection.",
        evidence_artifacts=[dict(path=q,sha256=sha256((ROOT/q).read_bytes()).hexdigest()) for q in (
            "docs/scripts/audit/audit_topic13_channel_error_attribution.py",
            "docs/core/test/test_topic13_channel_error_attribution.py",
            "docs/scripts/audit/audit_topic13_positive_interpolation_bounds.py",
            "docs/scripts/audit/audit_topic13_interpolation_refinement.py",
            "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/07_artifacts/topic13/t13_local_quadratic_bounds_audit.json")])
    (ROOT/"docs/core/07_artifacts/topic13/t13_channel_error_attribution_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({key:r[key] for key in ("relative_gram_error","witness_eigenvalue","reconstruction_residual",
        "rate_concentration_inverse_sum_squares","reference_concentration_inverse_sum_squares",
        "top_five_absolute_witness_fraction","outside_absolute_witness_fraction")}))
    for index in order[:5]: print(json.dumps(rows[index]))


if __name__=="__main__": main()
