"""Resolve the projected moment heat current in a linear charged-fluid frame."""
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
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state


def linear_frame_entropy(temperature, mu, n, s, h, charge_current):
    if temperature <= 0 or abs(n) < 1.e-14:
        raise ValueError("Positive temperature and nonzero charge density required")
    v = np.asarray(charge_current, dtype=float)
    if v.shape != (3,) or not np.all(np.isfinite(v)):
        raise ValueError("finite spatial charge current required")
    drift = v/n
    heat = -h*v
    landau_entropy = -mu*v/temperature
    eckart_entropy_in_landau_coordinates = s*drift+heat/temperature
    return {"frame_drift": drift.tolist(), "heat_current": heat.tolist(),
            "landau_entropy_spatial": landau_entropy.tolist(),
            "eckart_entropy_spatial_transformed": eckart_entropy_in_landau_coordinates.tolist(),
            "relative_entropy_frame_residual": float(np.linalg.norm(landau_entropy-eckart_entropy_in_landau_coordinates)/max(np.linalg.norm(landau_entropy),1.e-30)),
            "raw_heat_over_T_is_not_landau_entropy": (heat/temperature).tolist()}


def main():
    t, mu, phi = .22, .35, .15
    config = natural_bridge_config()
    eos = finite_temperature_o2_state(t, mu, phi, config)
    op = continuum_collision_operator_state(t, mu, phi, config,
        radial_order=8, collision_integration_order=24, angular_order=24,
        cutoff_factor=48., transition_quadrature_order=24,
        transition_channel_count=64, transition_interpolation_order=40)
    weights = np.asarray(op.susceptibility_weights)
    energies = np.asarray(op.state_energies)
    momenta = np.asarray(op.state_momenta)
    charges = np.asarray(op.state_species_signs)
    invariants = np.column_stack((charges, energies, momenta))*np.sqrt(weights)[:,None]
    basis, _ = np.linalg.qr(invariants, mode="reduced")
    projector = np.eye(len(weights))-basis@basis.T
    energy_source = momenta*np.sqrt(weights)[:,None]
    charge_source = charges[:,None]*(momenta/energies[:,None])*np.sqrt(weights)[:,None]
    h = (eos.energy_density+eos.pressure)/eos.charge_density
    heat_source = energy_source-h*charge_source
    projected_heat = projector@heat_source
    projected_charge = projector@charge_source
    raw = np.asarray(op.continuum_operator)
    collision = (raw+raw.T)/2
    inverse = np.linalg.pinv(collision, rcond=1.e-12)
    k_heat = projected_heat.T@inverse@projected_heat
    k_charge = projected_charge.T@inverse@projected_charge
    witnesses = []
    for amplitude in (1.e-9, 5.e-10, 2.5e-10):
        force = np.array([amplitude,0.,0.])
        z = inverse@projected_heat@force
        energy_current = energy_source.T@z
        charge_current = charge_source.T@z
        heat_current = heat_source.T@z
        entropy_kinetic = float(z@collision@z/t)
        grad_mu_over_T = h*force/t
        entropy_charge = float(-charge_current@grad_mu_over_T)
        witness = linear_frame_entropy(t,mu,eos.charge_density,eos.entropy_density,h,charge_current)
        witness.update(force_amplitude=amplitude, energy_current=energy_current.tolist(),
            charge_current=charge_current.tolist(), direct_heat_current=heat_current.tolist(),
            energy_over_heat_norm=float(np.linalg.norm(energy_current)/np.linalg.norm(heat_current)),
            heat_plus_h_charge_relative=float(np.linalg.norm(heat_current+h*charge_current)/np.linalg.norm(heat_current)),
            entropy_kinetic=entropy_kinetic, entropy_charge_diffusion=entropy_charge,
            relative_entropy_production_residual=abs(entropy_kinetic/entropy_charge-1))
        witnesses.append(witness)
    coefficient_residual=float(np.linalg.norm(k_heat-h*h*k_charge)/np.linalg.norm(k_heat))
    checks = {
        "projected_energy_moment_null": float(np.linalg.norm(projector@energy_source)/np.linalg.norm(energy_source)) < 1.e-10,
        "heat_charge_response_relation": coefficient_residual < 1.e-10,
        "frame_current_identity": all(w["relative_entropy_frame_residual"]<1.e-10 for w in witnesses),
        "kinetic_charge_entropy_agree": all(w["relative_entropy_production_residual"]<1.e-8 for w in witnesses),
        "energy_frame_and_heat_identity": all(w["energy_over_heat_norm"]<1.e-10 and w["heat_plus_h_charge_relative"]<1.e-10 for w in witnesses),
        "small_frame_drift": all(np.linalg.norm(w["frame_drift"])<.001 for w in witnesses),
    }
    result = {
        "major_result_id":"T13_LINEAR_HEAT_CHARGE_FRAME_MAP", "topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "status":"LINEAR_FRAME_MAP_RESOLVED" if all(checks.values()) else "FRAME_MAP_FAILED",
        "what_is_closed":"Projected heat moment is Q-h*V; with projected energy flux Q=0 it is -h*V, not Landau energy flux",
        "equation_or_mapping":"u_E=u_L+V/n+O(V^2); S_L=s*u_L-mu*V/T; S_E=s*u_E+q_E/T; q_E=-h*V; K_heat=h^2*K_charge",
        "units":"natural units; V is signed O(2) charge current, not mass flow",
        "derivation_class":"Linear frame transformation and explicit finite-grid moment calculation",
        "observable":"Formal charge diffusion and frame-invariant heat combination",
        "data_role":"INTERNAL_FIXED_ACTION_LINEAR_PROBES_NO_FIT",
        "config":asdict(config), "witnesses":witnesses, "checks":checks,
        "heat_charge_matrix_relative_residual":coefficient_residual,
        "charge_entropy_force_response":"V=(T*K_charge)*[-grad(mu/T)]; fixed-pressure, fixed-Phi local relation grad(mu/T)=h*X/T",
        "verification_status":"FINITE_GRID_LINEAR_IDENTITIES" if all(checks.values()) else "FAILED",
        "open_blockers":["propagate_frame_labels_to_core_contract_and_composition", "finite_cutoff_convergence", "physical_material_charge_and_protocol_map", "full_two_fluid_tensor"],
        "dependency_unlocked":[], "claim_promotion":False,
        "claim_boundary":"Not nonlinear frame equivalence, He4 mass-flow identification, SI heat conductivity, microscopic SK match or full Core readiness. No historical artifact replaced.",
        "evidence_artifacts":[{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            "docs/scripts/audit/audit_topic13_heat_charge_frame_map.py",
            "docs/core/test/test_topic13_heat_charge_frame_map.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_finite_temperature_quasiparticle_eos.py")],
    }
    (ROOT/"docs/core/07_artifacts/topic13/t13_heat_charge_frame_map_audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"checks":checks,"coefficient_residual":coefficient_residual,"witnesses":witnesses},indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
