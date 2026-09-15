"""Fixed four-case comparison of transition coordinates and direction rules."""
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


def main():
    config=natural_bridge_config()
    controls=dict(radial_order=8,collision_integration_order=24,angular_order=24,
        cutoff_factor=48.,transition_quadrature_order=24,transition_channel_count=64,
        transition_interpolation_order=40)
    cases=[dict(_direction_rule=d,_transition_map=m) for d in ("axis6","axis_cube14")
           for m in ("legacy_z_interpolation","weighted_psi_pullback")]
    r=dict(major_result_id="T13_TRANSITION_PULLBACK_IMPLEMENTATION",topic="0.13",closure_level="PARTIAL",
        status="RUNNING",completed=False,what_is_closed="Pending fixed four-case evaluation",
        equation_or_mapping="U=V sqrt(W_exact) S.T inv_sqrt(W_basis); remaining projector and rates unchanged",
        units="natural",derivation_class="Coordinate identity with numerical interpolation approximation",
        observable="Rate-weighted collision and heat response",data_role="INTERNAL_NO_FIT",
        config=asdict(config),controls=controls,cases=cases,rows=[],
        open_blockers=["interpolation_and_angular_convergence","rate_weighted_stability","material_mapping"],
        dependency_unlocked=[],full_core_unlock=False,
        claim_boundary="Opt-in revised coordinate map; legacy default preserved as comparator, not endorsed as scalar interpolation. No physical validation.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            "docs/scripts/audit/audit_topic13_transition_pullback_pilot.py",
            "docs/core/test/test_topic13_transition_pullback.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_action_derived_transition_kernel.py",
            "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/07_artifacts/topic13/t13_transition_coordinate_map_audit.json")])
    out=ROOT/"docs/core/07_artifacts/topic13/t13_transition_pullback_pilot.json"
    def save():
        out.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    save()
    for case in cases:
        row=dict(case=case)
        try:
            op=continuum_collision_operator_state(.22,.35,.15,config,**controls,**case)
            row.update(operator_evaluated=True,map=op.transition_coordinate_map,
                conservation_residual=op.collision_conservation_residual,
                minimum_eigenvalue=op.positive_semidefinite_min_eigenvalue,
                null_mode_count=op.null_mode_count,
                vertex_trace_ratio=op.transition_vertex_trace_ratio,
                projection_correction=op.projection_correction_relative_norm)
            eigen=np.asarray(op.collision_operator_eigenvalues)
            largest=float(np.max(np.abs(eigen)))
            row.update(maximum_absolute_eigenvalue=largest,
                maximum_collision_width=max(op.collision_widths),
                eigen_to_width_ratio=largest/max(op.collision_widths),
                relative_pinv_retained_modes=int(np.sum(np.abs(eigen)>1e-12*largest)),
                basis_weight_span=max(op.susceptibility_weights)/min(op.susceptibility_weights))
            heat=covariant_entropy_heat_flux_balance_state(.22,.35,.15,config,operator_state=op)
            row.update(status="EVALUATED",kappa=heat.kappa_natural,
                entropy_residual=heat.entropy_balance_residual,boost_residual=heat.lorentz_covariance_residual,
                isotropy_residual=heat.heat_response_isotropy_residual,
                original_gates=dict(entropy=heat.entropy_balance_residual<=1e-7,
                    boost=heat.lorentz_covariance_residual<=1e-10,isotropy=heat.heat_response_isotropy_residual<=1e-8))
        except Exception as exc:
            row.update(status="ERROR",error_type=type(exc).__name__,error=str(exc))
        r["rows"].append(row);save();print(json.dumps(row),flush=True)
    failed=any(row["status"]=="ERROR" for row in r["rows"])
    r.update(completed=True,status="BLOCKED_PULLBACK_NUMERICAL_FAILURE" if failed else "PULLBACK_PILOT_MEASURED_NOT_CERTIFIED",
        verification_status="ALL_PREREGISTERED_CASES_ATTEMPTED",
        what_is_closed="Weighted coordinate path installed and measured separately from legacy interpolation")
    save()
    return 0 if all(row["status"]=="EVALUATED" for row in r["rows"]) else 1


if __name__=="__main__":
    raise SystemExit(main())
