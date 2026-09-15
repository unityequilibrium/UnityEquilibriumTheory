"""Locked coarse-grid angular comparison; no angular convergence claim."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_continuum_collision_operator import continuum_collision_operator_state
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state


def main():
    controls = dict(radial_order=8, collision_integration_order=24, angular_order=24,
                    cutoff_factor=48., transition_quadrature_order=24,
                    transition_channel_count=64, transition_interpolation_order=40)
    config = natural_bridge_config()
    record = dict(major_result_id="T13_WEIGHTED_DIRECTION_TRANSPORT_PILOT", topic="0.13",
        closure_level="PARTIAL", status="RUNNING", completed=False,
        what_is_closed="Pending full-path angular comparison",
        equation_or_mapping="w_state=w_radial*w_direction; same conserved projection and full heat tensor",
        units="natural response; dimensionless angular weights",
        derivation_class="Analytic degree-four quadrature, finite collocation experiment",
        observable="Internal heat response, not SI conductivity", data_role="INTERNAL_NO_FIT",
        state=[.22, .35, .15], config=asdict(config), controls=controls,
        rules=["axis6", "axis_cube14"], rows=[], dependency_unlocked=[], full_core_unlock=False,
        open_blockers=["angular_and_transition_convergence", "weighted_transition_interpolation_correspondence",
                       "physical_material_mapping"],
        claim_boundary="Coarse pilot only; degree-six moments incomplete. No material or full Topic13 closure.",
        evidence_artifacts=[dict(path=p, sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            "docs/scripts/audit/audit_topic13_weighted_direction_pilot.py",
            "docs/core/test/test_topic13_weighted_directions.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py")])
    out = ROOT / "docs/core/07_artifacts/topic13/t13_weighted_direction_pilot.json"
    def save():
        out.write_text(json.dumps(record, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    save()
    for rule in record["rules"]:
        op = continuum_collision_operator_state(*record["state"], config, **controls, _direction_rule=rule)
        heat = covariant_entropy_heat_flux_balance_state(*record["state"], config, operator_state=op)
        p = np.asarray(op.state_momenta)
        w = np.asarray(op.susceptibility_weights)
        row = dict(rule=op.moment_direction_rule, state_count=op.state_count,
            kappa=heat.kappa_natural, entropy_residual=heat.entropy_balance_residual,
            boost_residual=heat.lorentz_covariance_residual, isotropy_residual=heat.heat_response_isotropy_residual,
            conservation_residual=op.collision_conservation_residual,
            shear_xy_source_norm=float(np.linalg.norm(p[:,0]*p[:,1]*np.sqrt(w))),
            projection_correction=op.projection_correction_relative_norm,
            basis_coverage_count=op.basis_coverage_count)
        row["original_gates"] = dict(entropy=heat.entropy_balance_residual <= 1e-7,
            boost=heat.lorentz_covariance_residual <= 1e-10,
            isotropy=heat.heat_response_isotropy_residual <= 1e-8)
        record["rows"].append(row)
        save()
        print(json.dumps(row), flush=True)
    record.update(status="WARN_COARSE_ANGULAR_COMPARISON_NOT_CONVERGED", completed=True,
        verification_status="TWO_DECLARED_RULES_EVALUATED_NOT_CONVERGENCE",
        what_is_closed="Weighted rule propagated through susceptibility, conserved projector, collision and heat response",
        kappa_relative_change=record["rows"][1]["kappa"]/record["rows"][0]["kappa"]-1)
    save()


if __name__ == "__main__":
    main()
