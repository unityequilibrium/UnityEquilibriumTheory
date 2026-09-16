"""Constrained high-precision response of fixed binary64 finite-grid inputs."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_action_derived_transition_kernel import action_derived_transition_kernel_state
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import energy_momentum_conserving_bs_state
from docs.core.uet_o2_continuum_collision_operator import _interpolation_matrix
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state


def constrained_response(weights,widths,jacobian,rates,invariants,force,dps):
    """Retain diagonal and channel factors; impose all five moments directly."""
    with mp.workdps(dps):
        w=mp.matrix(np.asarray(weights).tolist()); d=mp.matrix(np.asarray(widths).tolist())
        j=mp.matrix(np.asarray(jacobian).tolist()); rates=mp.matrix(np.asarray(rates).tolist())
        f=mp.matrix(np.asarray(invariants).tolist()); g=mp.matrix(np.asarray(force).tolist())
        n,k=f.rows,f.cols
        if any(w[i]<=0 or d[i]<=0 for i in range(n)) or any(x<0 for x in rates):
            raise ValueError("positive weights/widths and nonnegative rates required")
        h=mp.diag([w[i]*d[i] for i in range(n)])+j.T*mp.diag(list(rates))*j
        c=mp.matrix(n,k)
        for a in range(k):
            scale=max(abs(w[i]*f[i,a]) for i in range(n))
            for i in range(n): c[i,a]=w[i]*f[i,a]/scale
        system=mp.matrix(n+k,n+k); rhs=mp.matrix(n+k,1)
        for i in range(n):
            rhs[i]=w[i]*g[i]
            for q in range(n): system[i,q]=h[i,q]
            for a in range(k): system[i,n+a]=system[n+a,i]=c[i,a]
        solution=mp.lu_solve(system,rhs)
        psi=solution[:n,:]
        amplitude=mp.fdot([w[i]*g[i] for i in range(n)],psi)
        channel=j*psi
        dissipation=mp.fsum(w[i]*d[i]*psi[i]**2 for i in range(n))+mp.fsum(rates[i]*channel[i]**2 for i in range(j.rows))
        return dict(dps=dps,response=mp.nstr(amplitude,50),dissipation=mp.nstr(dissipation,50),
            balance_relative=mp.nstr(abs(amplitude-dissipation)/max(abs(amplitude),mp.mpf(1)),12),
            constraint_max=mp.nstr(max(abs(x) for x in c.T*psi),12),
            equation_max=mp.nstr(max(abs(x) for x in system*solution-rhs),12))


def main():
    config=natural_bridge_config(); state=(.22,.35,.15)
    eos=finite_temperature_o2_state(*state,config)
    enthalpy=(eos.energy_density+eos.pressure)/eos.charge_density
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=24,channel_count=64,cutoff_factor=48.)
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    r=dict(major_result_id="T13_CONSTRAINED_PRECISION_RESPONSE",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending precision comparison",
        equation_or_mapping="H=diag(w*gamma)+J.T R J; C=w*F; H psi+C lambda=w*g, C.T psi=0",
        units="natural response; x-directed force",derivation_class="Constrained quadratic minimization equivalent to exact projected solve",
        observable="K_xx only, not isotropic kappa or material conductivity",data_role="INTERNAL_NO_FIT",
        precision_plan=[120,180],direction_rules=["axis6","axis_cube14"],rows=[],
        input_precision="Binary64 inputs treated as fixed; higher precision solves do not upgrade input accuracy",
        controls=dict(state=list(state),radial=8,collision=24,angular=24,cutoff=48,channels=64,transition=24,interpolation=40),
        dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["interpolation_consistency","full_tensor_convergence","material_mapping"],
        claim_boundary="Fixed-grid x-response only. No rcond change, clipping, fitting or production-default change.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            "docs/scripts/audit/audit_topic13_constrained_precision.py",
            "docs/core/test/test_topic13_constrained_precision.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/07_artifacts/topic13/t13_transition_pullback_pilot.json")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_constrained_precision_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for rule in r["direction_rules"]:
        b=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
            angular_order=24,cutoff_factor=48.,_direction_rule=rule)
        s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
            b.state_species_signs,b.state_momenta,b.state_energies,cutoff=b.momentum_cutoff,support_order=40)
        j=incidence@s.T
        p=np.asarray(b.state_momenta); e=np.asarray(b.state_energies); q=np.asarray(b.charge_by_state)
        w=np.asarray(b.susceptibility_weights)
        factors=np.sqrt(exact.channel_rates)[:,None]*j/np.sqrt(w)[None,:]
        diagonal=np.sum(factors*factors,axis=0)
        index=int(np.argmax(diagonal))
        tail=dict(largest_vertex_diagonal=float(diagonal[index]),basis_index=index,
            momentum_over_temperature=float(np.linalg.norm(p[index])/.22),weight=float(w[index]),
            diagonal_fraction=float(diagonal[index]/diagonal.sum()))
        f=np.column_stack((q,e,p)); g=(e-enthalpy*q)*p[:,0]/e
        for dps in r["precision_plan"]:
            print(json.dumps(dict(starting_rule=rule,dps=dps)),flush=True)
            row=dict(rule=rule,tail=tail)
            try:
                row.update(constrained_response(w,b.collision_widths,j,exact.channel_rates,f,g,dps),status="EVALUATED")
            except Exception as exc:
                row.update(dps=dps,status="ERROR",error=str(exc))
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="PRECISION_STUDY_MEASURED_NOT_PHYSICAL_CLOSURE",
        verification_status="ALL_FIXED_CASES_ATTEMPTED",what_is_closed="Constrained response evaluated at two locked precisions")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in r["rows"]) else 1


if __name__=="__main__":
    raise SystemExit(main())
