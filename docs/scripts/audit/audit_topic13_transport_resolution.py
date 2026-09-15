"""Execute locked one-factor resolution controls without changing physics."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_continuum_collision_operator import continuum_collision_operator_state
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state

PLAN="docs/core/07_artifacts/topic13/t13_transport_resolution_plan.json"
OUT="docs/core/07_artifacts/topic13/t13_transport_resolution_audit.json"


def main():
    plan=json.loads((ROOT/PLAN).read_text())
    config=natural_bridge_config()
    rows=[]
    record={
        "major_result_id":"T13_SHARED_ACTION_TRANSPORT_RESOLUTION_DIAGNOSTIC",
        "topic":"0.13_Thermodynamic_Bridge", "closure_level":"PARTIAL",
        "status":"RUNNING", "completed":False,
        "what_is_closed":"Nothing promoted by this resolution diagnostic",
        "equation_or_mapping":"Existing projected collision response and corrected entropy, with unchanged action",
        "units":"natural only", "derivation_class":"One-factor numerical resolution experiment",
        "observable":"Natural heat moment response, not SI conductivity", "data_role":"INTERNAL_NO_FIT",
        "config":asdict(config), "rows":rows,
        "open_blockers":["finite_cutoff_transport_convergence", "material_protocol_mapping"],
        "dependency_unlocked":[], "claim_promotion":False,
        "claim_boundary":plan["known_scope"]+" No continuum proof or material error bar.",
        "evidence_artifacts":[{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            PLAN, "docs/scripts/audit/audit_topic13_transport_resolution.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py")],
    }
    def save():
        (ROOT/OUT).write_text(json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for case in plan["cases"]:
        controls={**plan["base"],**case["override"]}
        start=perf_counter()
        row={"id":case["id"],"controls":controls}
        try:
            op=continuum_collision_operator_state(*plan["state"],config,**controls)
            s=covariant_entropy_heat_flux_balance_state(*plan["state"],config,operator_state=op)
            row.update(status="EVALUATED",kappa=s.kappa_natural,
                entropy_residual=s.entropy_balance_residual,
                entropy_original_gate=s.entropy_balance_residual<=1.e-7,
                heat_response_xx=s.heat_response_matrix[0][0],
                scalar_lift_entropy_discrepancy=abs(s.heat_response_matrix[0][0]-s.kappa_natural)/s.temperature,
                tensor_entropy_vs_kinetic_residual=abs(s.heat_response_matrix[0][0]/s.temperature-s.kinetic_entropy_production),
                charge_residual=s.charge_balance_residual,energy_residual=s.energy_balance_residual,
                momentum_residual=s.momentum_balance_residual,
                kinetic_residual=s.kinetic_equation_residual,
                lorentz_residual=s.lorentz_covariance_residual,
                heat_flux_response_residual=s.heat_flux_response_residual,
                isotropy_residual=s.heat_response_isotropy_residual,
                state_count=op.state_count,null_modes=op.null_mode_count,
                min_operator_eigenvalue=op.positive_semidefinite_min_eigenvalue,
                vertex_trace_ratio=op.transition_vertex_trace_ratio,
                projection_correction_relative_norm=op.projection_correction_relative_norm)
            if rows and "kappa" in rows[0]:
                row["relative_change_from_base"]=s.kappa_natural/rows[0]["kappa"]-1
        except Exception as exc:
            row.update(status="ERROR",error_type=type(exc).__name__,error=str(exc))
        row["elapsed_seconds"]=perf_counter()-start
        rows.append(row)
        save()
        print(json.dumps(row),flush=True)
    record.update(status="RESOLUTION_MEASURED_CONVERGENCE_NOT_CERTIFIED",completed=True,
                  verification_status="ALL_PLANNED_CASES_ATTEMPTED",
                  diagnostic_extension="After first pass showed entropy failures, record K_xx/T versus kinetic entropy to distinguish scalar isotropic-lift error. Original plan, action and thresholds unchanged; this extra diagnostic was post hoc.")
    save()
    return 1 if any(r["status"]=="ERROR" for r in rows) else 0


if __name__=="__main__":
    raise SystemExit(main())
