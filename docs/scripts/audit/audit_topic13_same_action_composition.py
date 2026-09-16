"""Evaluate alpha, beta and heat entropy using one explicit existing action."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import (
    natural_bridge_config, action_natural_phi_thermal_bridge_state,
)
from docs.core.uet_o2_action_thermal_stiffness_beta import action_thermal_stiffness_beta_state
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import covariant_entropy_heat_flux_balance_state
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import FiniteTemperatureO2QuasiparticleConfig


def config_identity(config):
    return sha256(json.dumps(asdict(config), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_same_config(configurations):
    if not configurations or len({config_identity(c) for c in configurations}) != 1:
        raise ValueError("All components must use the same explicit action and numerical configuration")


def main():
    config = natural_bridge_config()
    require_same_config([config, config, config])
    alpha = asdict(action_natural_phi_thermal_bridge_state(config=config))
    beta = asdict(action_thermal_stiffness_beta_state(config=config))
    entropy = asdict(covariant_entropy_heat_flux_balance_state(.22, .35, .15, config))
    default = asdict(covariant_entropy_heat_flux_balance_state(.22, .35, .15))
    checks = {
        "same_branch": alpha["branch"] == beta["branch"] == entropy["eos_branch"] == "normal",
        "same_pressure": alpha["pressure"] == beta["pressure"] == entropy["pressure"],
        "same_entropy": alpha["entropy_density"] == beta["entropy_density"] == entropy["entropy_density"],
        "same_energy": alpha["energy_density"] == entropy["energy_density"],
        "same_charge": alpha["charge_density"] == entropy["charge_density"],
        "same_coupling": beta["response_coupling"] == config.eos.matter.response_coupling,
        "entropy_original_threshold": entropy["entropy_balance_residual"] <= 1.e-7,
        "energy_original_threshold": entropy["energy_balance_residual"] <= 1.e-10,
        "charge_original_threshold": entropy["charge_balance_residual"] <= 1.e-10,
        "momentum_original_threshold": entropy["momentum_balance_residual"] <= 1.e-10,
        "covariance_original_threshold": entropy["lorentz_covariance_residual"] <= 1.e-10,
        "isotropy_original_threshold": entropy["heat_response_isotropy_residual"] <= 1.e-8,
        "positive_heat_response": entropy["kappa_natural"] > 0,
    }
    result = {
        "major_result_id": "T13_SAME_ACTION_LOCAL_THERMODYNAMIC_COMPOSITION",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "status": "SAME_ACTION_REFERENCE_CONSISTENT" if all(checks.values()) else "SAME_ACTION_REFERENCE_FAILED",
        "what_is_closed": "One explicitly shared existing action for local alpha, beta, EOS and corrected entropy response",
        "equation_or_mapping": "Existing alpha and beta derivatives plus sigma=X.q/T; identical config passed to all three builders",
        "units": "Natural units only", "derivation_class": "Same-configuration internal composition, not microscopic matching",
        "observable": "Local natural response and entropy balance", "data_role": "INTERNAL_NO_CALIBRATION",
        "config": asdict(config), "config_sha256": config_identity(config),
        "component_config_hashes": {name: config_identity(config) for name in ("alpha", "beta", "entropy")},
        "default_entropy_config": asdict(FiniteTemperatureO2QuasiparticleConfig()),
        "default_entropy_config_sha256": config_identity(FiniteTemperatureO2QuasiparticleConfig()),
        "alpha": alpha, "beta": beta, "entropy": entropy, "checks": checks,
        "default_comparison": {"kappa_default": default["kappa_natural"], "kappa_shared_action": entropy["kappa_natural"],
            "relative_change": entropy["kappa_natural"]/default["kappa_natural"]-1,
            "scope": "Full configuration difference including numerical controls; not isolated causal attribution to coupling alone"},
        "verification_status": "CURRENT_COMMON_ACTION_REFERENCE" if all(checks.values()) else "FAILED",
        "open_blockers": ["hydrodynamic_frame_charge_diffusion_map", "finite_cutoff_transport_convergence", "physical_state_and_protocol_correspondence", "historical_composition_integration_review"],
        "dependency_unlocked": [], "claim_promotion": False,
        "claim_boundary": "No SI coefficient or He4 external validation. No replacement of default branch or historical artifacts. No parameter search or holdout read.",
        "evidence_artifacts": [{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            "docs/scripts/audit/audit_topic13_same_action_composition.py",
            "docs/core/test/test_topic13_same_action_composition.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
            "docs/core/02_equations/o2/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py")],
    }
    (ROOT/"docs/core/07_artifacts/topic13/t13_same_action_composition_audit.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": checks, "default_comparison":result["default_comparison"]}))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
