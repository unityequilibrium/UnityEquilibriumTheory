"""Joint radial/cutoff controls with a separate spectral inverse diagnostic."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_continuum_collision_operator import continuum_collision_operator_state
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state


def spectral_response(eigenvalues,eigenvectors,source,rcond):
    keep=np.abs(eigenvalues)>rcond*np.max(np.abs(eigenvalues))
    coefficients=eigenvectors[:,keep].T@source
    response=coefficients.T@(coefficients/eigenvalues[keep,None])
    return response,int(np.sum(keep)),int(np.sum(eigenvalues[keep]<0))


def main():
    plan_path="docs/core/07_artifacts/topic13/t13_joint_resolution_plan.json"
    plan=json.loads((ROOT/plan_path).read_text())
    config=natural_bridge_config()
    record={"major_result_id":"T13_JOINT_TRANSPORT_RESOLUTION", "topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"PARTIAL", "status":"RUNNING", "completed":False,
        "equation_or_mapping":"Existing tensor moment response; spectral pseudoinverse diagnostic retains both signs above cutoff",
        "units":"natural", "derivation_class":"numerical resolution experiment", "observable":"formal heat response",
        "data_role":"INTERNAL_NO_FIT", "config":asdict(config), "rows":[],
        "open_blockers":["joint_transport_convergence", "transition_and_directional_basis", "physical_material_mapping"],
        "dependency_unlocked":[], "claim_promotion":False,
        "claim_boundary":plan["policy"],
        "evidence_artifacts":[{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            plan_path,"docs/scripts/audit/audit_topic13_joint_resolution.py","docs/core/test/test_topic13_joint_resolution.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py","docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_continuum_collision_operator.py","docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py","docs/core/uet_o2_covariant_entropy_heat_flux_balance.py")],
    }
    output=ROOT/"docs/core/07_artifacts/topic13/t13_joint_resolution_audit.json"
    def save():
        output.write_text(json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for case in plan["cases"]:
        row={"controls":{**plan["base"],**case}}
        try:
            op=continuum_collision_operator_state(*plan["state"],config,**row["controls"])
            s=covariant_entropy_heat_flux_balance_state(*plan["state"],config,operator_state=op)
            p=np.asarray(op.state_momenta); e=np.asarray(op.state_energies); q=np.asarray(op.state_species_signs); w=np.asarray(op.susceptibility_weights)
            invariant=np.column_stack((q,e,p))*np.sqrt(w)[:,None]
            basis,_=np.linalg.qr(invariant,mode="reduced")
            source=(e-s.enthalpy_per_charge*q)[:,None]*(p/e[:,None])*np.sqrt(w)[:,None]
            source-=basis@(basis.T@source)
            matrix=np.asarray(op.continuum_operator); matrix=(matrix+matrix.T)/2
            eigenvalues,eigenvectors=np.linalg.eigh(matrix)
            inverse_rows=[]
            for cutoff in plan["diagnostic_rcond"]:
                response,rank,negative=spectral_response(eigenvalues,eigenvectors,source,cutoff)
                kappa=float(np.trace(response)/3)
                inverse_rows.append({"rcond":cutoff,"kappa":kappa,"rank":rank,"retained_negative":negative,"relative_to_production":kappa/s.kappa_natural-1})
            row.update(status="EVALUATED",kappa=s.kappa_natural,entropy_residual=s.entropy_balance_residual,
                entropy_original_gate=s.entropy_balance_residual<=1.e-7,lorentz_residual=s.lorentz_covariance_residual,
                isotropy_residual=s.heat_response_isotropy_residual,state_count=op.state_count,
                minimum_momentum=float(np.min(np.linalg.norm(p,axis=1))),inverse_diagnostic=inverse_rows)
        except Exception as exc:
            row.update(status="ERROR",error_type=type(exc).__name__,error=str(exc))
        record["rows"].append(row); save(); print(json.dumps(row),flush=True)
    record.update(status="JOINT_RESOLUTION_MEASURED_NOT_CERTIFIED",completed=True,verification_status="ALL_LOCKED_CASES_ATTEMPTED")
    save()
    return 0 if all(r["status"]=="EVALUATED" for r in record["rows"]) else 1


if __name__=="__main__":
    raise SystemExit(main())
