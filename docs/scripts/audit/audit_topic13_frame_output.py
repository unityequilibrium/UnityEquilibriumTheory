"""Record production frame outputs without refreshing historical gates."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state


def main():
    states=[asdict(covariant_entropy_heat_flux_balance_state(.22,.35,.15,natural_bridge_config(),
        thermal_force_covariant=np.array([0.,a,0.,0.]))) for a in (1.,1.e-9)]
    checks={
        "canonical_frame_identity": all(s["frame_current_decomposition"]["entropy_frame_identity_residual"]<1.e-10 for s in states),
        "heat_response_identity": all(s["frame_current_decomposition"]["heat_moment_response_residual"]<1.e-7 for s in states),
        "finite_velocity_not_asserted": all(not s["frame_current_decomposition"]["finite_velocity_state_validated"] for s in states),
        "unit_force_large_formal_shift_disclosed": states[0]["frame_current_decomposition"]["frame_shift_spatial_norm"]>1,
        "small_probe_shift": states[1]["frame_current_decomposition"]["frame_shift_spatial_norm"]<.001,
    }
    result={
        "major_result_id":"T13_FRAME_CURRENT_OUTPUT_INTEGRATED", "topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "status":"FRAME_OUTPUT_INTEGRATED" if all(checks.values()) else "FRAME_OUTPUT_FAILED",
        "what_is_closed":"Explicit energy, charge, invariant heat and canonical entropy outputs in production state",
        "equation_or_mapping":"q_heat=Q-hV; S_L=s*u+(Q-muV)/T; linear Eckart transformation",
        "units":"natural, signed O(2) charge", "derivation_class":"Previously verified linear frame map propagated into state output",
        "observable":"Formal current decomposition", "data_role":"INTERNAL_COEFFICIENT_AND_SMALL_PROBE",
        "checks":checks, "states":states,
        "verification_status":"CURRENT_PRODUCTION_OUTPUT_CHECKED" if all(checks.values()) else "FAILED",
        "open_blockers":["material_charge_and_protocol_map", "finite_cutoff_convergence", "historical_composition_review", "nonlinear_two_fluid_transport"],
        "dependency_unlocked":[], "claim_promotion":False,
        "claim_boundary":"Backward-compatible fields retained with explicit legacy roles. No finite-flow certification, SI coefficient or old gate replacement.",
        "evidence_artifacts":[{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            "docs/scripts/audit/audit_topic13_frame_output.py",
            "docs/core/test/test_topic13_frame_output.py",
            "docs/core/02_equations/o2/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py")],
    }
    (ROOT/"docs/core/07_artifacts/topic13/t13_frame_output_audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"checks":checks,"frame_shifts":[s["frame_current_decomposition"]["frame_shift_spatial_norm"] for s in states]}))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
