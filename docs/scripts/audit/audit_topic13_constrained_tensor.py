"""Three-source constrained tensor reference; fixed grid and no physical promotion."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_constrained_precision import (
    natural_bridge_config, finite_temperature_o2_state, action_derived_transition_kernel_state,
    energy_momentum_conserving_bs_state, _interpolation_matrix,
)


def multi_solve(a,b):
    """Reuse one public LU decomposition; P*A=L*U for all source columns."""
    p,l,u=mp.lu(a)
    rhs=p*b; y=mp.matrix(b.rows,b.cols); x=mp.matrix(b.rows,b.cols)
    for col in range(b.cols):
        for i in range(b.rows):
            y[i,col]=(rhs[i,col]-mp.fsum(l[i,j]*y[j,col] for j in range(i)))/l[i,i]
        for i in reversed(range(b.rows)):
            x[i,col]=(y[i,col]-mp.fsum(u[i,j]*x[j,col] for j in range(i+1,b.rows)))/u[i,i]
    return x


def tensor_response(weights,widths,jacobian,rates,invariants,forces,dps):
    with mp.workdps(dps):
        w=mp.matrix(np.asarray(weights).tolist()); d=mp.matrix(np.asarray(widths).tolist())
        j=mp.matrix(np.asarray(jacobian).tolist()); rates=mp.matrix(np.asarray(rates).tolist())
        f=mp.matrix(np.asarray(invariants).tolist()); g=mp.matrix(np.asarray(forces).tolist())
        n,k=f.rows,f.cols
        if g.rows!=n or g.cols!=3 or any(w[i]<=0 or d[i]<=0 for i in range(n)) or any(v<0 for v in rates):
            raise ValueError("three forces, positive weights/widths and nonnegative rates required")
        diagonal=mp.diag([w[i]*d[i] for i in range(n)])
        rate_matrix=mp.diag(list(rates))
        h=diagonal+j.T*rate_matrix*j
        c=mp.matrix(n,k)
        for a in range(k):
            scale=max(abs(w[i]*f[i,a]) for i in range(n))
            for i in range(n): c[i,a]=w[i]*f[i,a]/scale
        system=mp.matrix(n+k,n+k); rhs=mp.matrix(n+k,3)
        for i in range(n):
            for axis in range(3): rhs[i,axis]=w[i]*g[i,axis]
            for q in range(n): system[i,q]=h[i,q]
            for a in range(k): system[i,n+a]=system[n+a,i]=c[i,a]
        solution=multi_solve(system,rhs); psi=solution[:n,:]
        response=rhs[:n,:].T*psi
        channel=j*psi
        dissipation=psi.T*diagonal*psi+channel.T*rate_matrix*channel
        norm=max(max(abs(x) for x in response),mp.mpf(1))
        kappa=mp.fsum(response[a,a] for a in range(3))/3
        eigenvalues=mp.eigsy((response+response.T)/2,eigvals_only=True)
        def matrix_strings(a): return [[mp.nstr(a[i,j],50) for j in range(a.cols)] for i in range(a.rows)]
        return dict(dps=dps,response=matrix_strings(response),dissipation=matrix_strings(dissipation),
            kappa_trace_over_three=mp.nstr(kappa,50),
            reciprocity_relative=mp.nstr(max(abs(x) for x in response-response.T)/norm,12),
            balance_relative=mp.nstr(max(abs(x) for x in response-dissipation)/norm,12),
            isotropy_relative=mp.nstr(max(abs(x) for x in response-kappa*mp.eye(3))/max(abs(kappa),1),12),
            constraint_max=mp.nstr(max(abs(x) for x in c.T*psi),12),
            equation_max=mp.nstr(max(abs(x) for x in system*solution-rhs),12),
            minimum_symmetric_eigenvalue=mp.nstr(min(eigenvalues),50))


def main():
    config=natural_bridge_config(); state=(.22,.35,.15)
    eos=finite_temperature_o2_state(*state,config)
    enthalpy=(eos.energy_density+eos.pressure)/eos.charge_density
    exact=action_derived_transition_kernel_state(*state,config,quadrature_order=24,channel_count=64,cutoff_factor=48.)
    incidence=np.asarray(exact.transition_vectors)*np.sqrt(exact.state_weights)[None,:]
    r=dict(major_result_id="T13_CONSTRAINED_THREE_SOURCE_TENSOR",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending full tensor evaluation",
        equation_or_mapping="H Psi+C Lambda=W G; C.T Psi=0; K=G.T W Psi; D=Psi.T diag(w*gamma) Psi+(J Psi).T R (J Psi)",
        units="natural response",derivation_class="Three-source constrained quadratic response",
        observable="3x3 internal heat-response tensor",data_role="INTERNAL_FIXED_BINARY64_INPUTS",
        precision_plan=[120,180],direction_rules=["axis6","axis_cube14"],rows=[],
        controls=dict(state=list(state),radial=8,collision=24,angular=24,cutoff=48,channels=64,transition=24,interpolation=40),
        dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["input_sensitivity","interpolation_consistency","resolution_convergence","production_integration","material_mapping"],
        claim_boundary="High-precision solve is not high-precision input physics, continuum limit or external validation. Symmetric eigenvalues are diagnostic only; K is not symmetrized for reporting.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            "docs/scripts/audit/audit_topic13_constrained_tensor.py",
            "docs/core/test/test_topic13_constrained_tensor.py",
            "docs/scripts/audit/audit_topic13_constrained_precision.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_action_derived_transition_kernel.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/07_artifacts/topic13/t13_constrained_precision_audit.json")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_constrained_tensor_audit.json"
    def save(): out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for rule in r["direction_rules"]:
        b=energy_momentum_conserving_bs_state(*state,config,radial_order=8,collision_integration_order=24,
            angular_order=24,cutoff_factor=48.,_direction_rule=rule)
        s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
            b.state_species_signs,b.state_momenta,b.state_energies,cutoff=b.momentum_cutoff,support_order=40)
        j=incidence@s.T
        p=np.asarray(b.state_momenta); e=np.asarray(b.state_energies); q=np.asarray(b.charge_by_state)
        f=np.column_stack((q,e,p)); g=(e-enthalpy*q)[:,None]*p/e[:,None]
        for dps in r["precision_plan"]:
            print(json.dumps(dict(starting_rule=rule,dps=dps)),flush=True)
            row=dict(rule=rule,dps=dps)
            try:
                row.update(tensor_response(b.susceptibility_weights,b.collision_widths,j,exact.channel_rates,f,g,dps),status="EVALUATED")
            except Exception as exc: row.update(status="ERROR",error=str(exc))
            r["rows"].append(row);save();print(json.dumps(row),flush=True)
    r.update(completed=True,status="TENSOR_REFERENCE_MEASURED_NOT_PHYSICAL_CLOSURE",
        verification_status="ALL_LOCKED_CASES_ATTEMPTED",what_is_closed="Three-source tensor and factorized balance evaluated")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in r["rows"]) else 1


if __name__=="__main__": raise SystemExit(main())
