"""Locked support study plus pre-projection on-shell interpolation defects."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_constrained_tensor import (
    tensor_response,natural_bridge_config,finite_temperature_o2_state,
    action_derived_transition_kernel_state,energy_momentum_conserving_bs_state,_interpolation_matrix,
)


def shell_defects(s,basis_p,basis_e,exact_p,exact_e,mass):
    s=np.asarray(s); p=s.T@np.asarray(basis_p); energy=s.T@np.asarray(basis_e)
    on_shell=np.sqrt(np.sum(p*p,axis=1)+mass*mass)
    target=np.asarray(exact_e)
    return dict(constant_max=float(np.max(np.abs(s.sum(axis=0)-1))),
        max_energy_relative_error=float(np.max(np.abs(energy-target)/target)),
        rms_energy_relative_error=float(np.sqrt(np.mean(((energy-target)/target)**2))),
        max_momentum_over_energy_error=float(np.max(np.linalg.norm(p-np.asarray(exact_p),axis=1)/target)),
        minimum_jensen_gap=float(np.min(energy-on_shell)),
        maximum_jensen_gap=float(np.max(energy-on_shell)),
        effective_support_min=int(np.min(np.sum(s>0,axis=0))),
        effective_support_max=int(np.max(np.sum(s>0,axis=0))))


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_interpolation_support_plan.json"
    plan=json.loads((ROOT/plan_path).read_text())
    state=plan["state"]; config=natural_bridge_config()
    eos=finite_temperature_o2_state(*state,config)
    h=(eos.energy_density+eos.pressure)/eos.charge_density
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=plan["transition_quadrature_order"],
        channel_count=plan["transition_channel_count"],cutoff_factor=plan["cutoff_factor"])
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    r=dict(major_result_id="T13_INTERPOLATION_SUPPORT_AND_MASS_SHELL_BOUNDARY",topic="0.13",
        closure_level="PARTIAL",status="RUNNING",completed=False,what_is_closed="Pending all-case support comparison",
        equation_or_mapping="Positive S: E(mean p)<=mean E(p), strictly unless support momenta coincide for mass>0",
        units="natural; normalized energy/momentum defects",derivation_class="Convex massive mass-shell identity plus numerical study",
        observable="Internal tensor sensitivity and unweighted channel-leg interpolation defects",
        data_role="INTERNAL_NO_FIT",plan=plan,rows=[],dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["interpolation_consistency_under_refinement","input_sensitivity","material_mapping"],
        claim_boundary=plan["policy"],
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            plan_path,"docs/scripts/audit/audit_topic13_interpolation_support.py",
            "docs/core/test/test_topic13_interpolation_support.py",
            "docs/scripts/audit/audit_topic13_constrained_tensor.py",
            "docs/scripts/audit/audit_topic13_constrained_precision.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_action_derived_transition_kernel.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_interpolation_support_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for rule in plan["direction_rules"]:
        controls={key:plan[key] for key in ("radial_order","collision_integration_order","angular_order","cutoff_factor")}
        b=energy_momentum_conserving_bs_state(*state,config,**controls,_direction_rule=rule)
        p=np.asarray(b.state_momenta); e=np.asarray(b.state_energies); q=np.asarray(b.charge_by_state)
        f=np.column_stack((q,e,p)); g=(e-h*q)[:,None]*p/e[:,None]
        for support in plan["support_orders"]:
            print(json.dumps(dict(starting_rule=rule,support=support)),flush=True)
            row=dict(rule=rule,support_order=support)
            try:
                s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
                    b.state_species_signs,b.state_momenta,b.state_energies,cutoff=b.momentum_cutoff,support_order=support)
                row["preprojection"]=shell_defects(s,p,e,exact.state_momenta,exact.state_energies,b.effective_mass)
                row.update(tensor_response(b.susceptibility_weights,b.collision_widths,incidence@s.T,exact.channel_rates,
                    f,g,plan["dps"]),status="EVALUATED")
            except Exception as exc: row.update(status="ERROR",error=str(exc))
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="SUPPORT_SENSITIVITY_MEASURED_NOT_CONVERGENCE",
        verification_status="ALL_SIX_CASES_ATTEMPTED",what_is_closed="Support sensitivity and pre-projection shell defects measured")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in r["rows"]) else 1


if __name__=="__main__": raise SystemExit(main())
