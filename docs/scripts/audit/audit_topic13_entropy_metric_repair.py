"""Generate a separate repaired reference without overwriting old entropy gates."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    covariant_entropy_heat_flux_balance_state, covariant_entropy_heat_flux_balance_contract,
)
from docs.scripts.audit.audit_topic13_entropy_force_convention import witness


def main():
    state = asdict(covariant_entropy_heat_flux_balance_state(.22, .35, .15))
    old_path = "docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
    old = json.loads((ROOT/old_path).read_text())["state"]
    controls = [witness(t) for t in (.22, .5, 1., 2.)]
    checks = {
        "independent_current_divergence": all(abs(c["reported_over_divergence"]-1)<1.e-10 for c in controls),
        "kinetic_entropy_balance_original_threshold": state["entropy_balance_residual"] <= 1.e-7,
        "entropy_positive": state["entropy_production"] >= 0,
        "charge_balance_original_threshold": state["charge_balance_residual"] <= 1.e-10,
        "energy_balance_original_threshold": state["energy_balance_residual"] <= 1.e-10,
        "momentum_balance_original_threshold": state["momentum_balance_residual"] <= 1.e-10,
        "covariance_original_threshold": state["lorentz_covariance_residual"] <= 1.e-10,
    }
    record = {
        "major_result_id": "T13_ENTROPY_METRIC_NORMALIZATION_REPAIRED",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "status": "INTERNAL_NORMALIZATION_REPAIRED" if all(checks.values()) else "REPAIR_VERIFICATION_FAILED",
        "what_is_closed": "Susceptibility-coordinate entropy metric and heat-only current-divergence normalization; not material transport",
        "equation_or_mapping": "w=m*f*(1+f)/T; z=sqrt(w)*psi; delta f=f*(1+f)*psi/T; sigma=z.L.z/T=X.q/T",
        "units": "Natural k_B=1; z.L.z is temperature times entropy-production density",
        "derivation_class": "Bose entropy Hessian and fixed-pressure local streaming; collocation normalization repair",
        "observable": "Formal heat-only entropy production", "data_role": "INTERNAL_NO_CALIBRATION",
        "state": state, "contract": covariant_entropy_heat_flux_balance_contract(),
        "checks": checks, "independent_controls": controls,
        "historical_reference": {"path": old_path, "old_entropy": old["entropy_production"],
            "old_entropy_divided_by_T": old["entropy_production"]/.22,
            "kappa_relative_change": abs(state["kappa_natural"]/old["kappa_natural"]-1)},
        "verification_status": "CURRENT_REFERENCE_AND_INDEPENDENT_CONTROLS" if all(checks.values()) else "FAILED",
        "open_blockers": ["hydrodynamic_frame_and_charge_diffusion_map", "action_configuration_correspondence", "physical_Kubo_SK_and_material_map"],
        "dependency_unlocked": [], "claim_promotion": False,
        "claim_boundary": "No full He4 revalidation, SI coefficient, two-fluid tensor, or historical artifact replacement.",
        "evidence_artifacts": [{"path":p, "sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            old_path, "docs/scripts/audit/audit_topic13_entropy_metric_repair.py",
            "docs/core/test/test_topic13_entropy_metric_repair.py",
            "docs/core/test/test_topic13_entropy_force_convention.py",
            "docs/core/02_equations/o2/uet_o2_covariant_entropy_heat_flux_balance.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/02_equations/o2/uet_o2_continuum_collision_operator.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py")],
    }
    (ROOT/"docs/core/07_artifacts/topic13/t13_entropy_metric_repair_audit.json").write_text(json.dumps(record, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"status":record["status"], "checks": checks,
        "entropy":state["entropy_production"], "balance_residual":state["entropy_balance_residual"]}))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
