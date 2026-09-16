"""Verify the named Topic 13 collective-response EOS/stability contract."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_collective_response_eos import (
    CollectiveResponseEOSInputs,
    chemical_potentials,
    collective_response_eos_contract,
    hessian,
    local_stability,
    normalized_free_energy_density,
)
from docs.core.thermal_response_beta_contract import ThermalResponseBetaInputs


EOS_REL = "docs/core/03_lanes/thermal/thermal_collective_response_eos.py"
BETA_REL = "docs/core/03_lanes/thermal/thermal_response_beta_contract.py"
BETA_AUDIT_REL = "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"
THERMAL_AUDIT_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_closure_derivation_audit.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json"


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def numerical_witness() -> dict[str, Any]:
    """Check declared first and second derivatives without physical inputs."""

    inputs = CollectiveResponseEOSInputs(
        thermal=ThermalResponseBetaInputs(300.0, 1.2, 0.18, 0.4, 0.3),
        a_c=1.1,
        b_c=0.5,
    )
    temperature = 300.0
    c = 0.2
    phi = 0.4
    step = 1.0e-5
    f = normalized_free_energy_density
    mu_c, mu_phi = chemical_potentials(temperature, c, phi, inputs)
    h = hessian(temperature, c, phi, inputs)
    d_c = (f(temperature, c + step, phi, inputs) - f(temperature, c - step, phi, inputs)) / (2.0 * step)
    d_phi = (f(temperature, c, phi + step, inputs) - f(temperature, c, phi - step, inputs)) / (2.0 * step)
    d_cc = (f(temperature, c + step, phi, inputs) - 2.0 * f(temperature, c, phi, inputs) + f(temperature, c - step, phi, inputs)) / step**2
    d_phi_phi = (f(temperature, c, phi + step, inputs) - 2.0 * f(temperature, c, phi, inputs) + f(temperature, c, phi - step, inputs)) / step**2
    d_c_phi = (f(temperature, c + step, phi + step, inputs) - f(temperature, c + step, phi - step, inputs) - f(temperature, c - step, phi + step, inputs) + f(temperature, c - step, phi - step, inputs)) / (4.0 * step**2)
    stability = local_stability(temperature, c, phi, inputs)
    return {
        "role": "synthetic derivative and stability witness only; not an EOS fit or physical data",
        "inputs": {"temperature_K": temperature, "C": c, "Phi": phi, "a_C": inputs.a_c, "b_C": inputs.b_c, "a_Phi_T0": inputs.thermal.a_phi_T0, "b_Phi": inputs.thermal.b_phi, "g": inputs.thermal.coupling_g, "beta_T13": inputs.thermal.beta_t13_dimensionless},
        "analytic": {"mu_C": mu_c, "mu_Phi": mu_phi, "H_CC": h[0][0], "H_CPhi": h[0][1], "H_PhiC": h[1][0], "H_PhiPhi": h[1][1]},
        "finite_difference": {"mu_C": d_c, "mu_Phi": d_phi, "H_CC": d_cc, "H_CPhi": d_c_phi, "H_PhiPhi": d_phi_phi},
        "stability": stability,
        "checks": {
            "mu_C_matches": abs(mu_c - d_c) <= 1.0e-9,
            "mu_Phi_matches": abs(mu_phi - d_phi) <= 1.0e-9,
            "H_CC_matches": abs(h[0][0] - d_cc) <= 1.0e-5,
            "H_PhiPhi_matches": abs(h[1][1] - d_phi_phi) <= 1.0e-5,
            "mixed_hessian_matches": abs(h[0][1] - d_c_phi) <= 1.0e-7,
            "mixed_derivatives_reciprocal": h[0][1] == h[1][0],
            "selected_witness_locally_stable": stability["locally_stable"] is True,
        },
    }


def main() -> int:
    eos_text = text(EOS_REL)
    beta_text = text(BETA_REL)
    beta_audit = load(BETA_AUDIT_REL)
    thermal_audit = load(THERMAL_AUDIT_REL)
    formula = text(FORMULA_REL)
    contract = collective_response_eos_contract()
    witness = numerical_witness()
    checks = {
        "eos_functional_declared": "f_hat=a_C C^2/2" in contract["functional"],
        "collective_ontology_preserved": "collective system-behaviour coordinate" in contract["C"] and "not mass or charge density" in contract["C"],
        "response_ontology_preserved": "effective response coordinate" in contract["Phi"] and "not a particle" in contract["Phi"],
        "mixed_derivative_reciprocity_declared": "partial_Phi(mu_C)=partial_C(mu_Phi)=-g C" == contract["reciprocity"],
        "stability_conditions_declared": contract["stability"] == "H_CC>0, H_PhiPhi>0, det(H)>0",
        "beta_contract_is_precondition": beta_audit.get("status") == "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT",
        "landauer_absent_from_eos_equations": "k_B" not in eos_text and "ln(2)" not in eos_text and "Landauer" not in eos_text,
        "beta_contract_is_not_redefined": "beta_T13" in beta_text and "not a value inferred from Landauer" in beta_text,
        "trace_absent_and_no_backreaction": "derived history trace only" in contract["R_gen"],
        "old_thermal_physical_closure_remains_open": thermal_audit.get("status") == "DIMENSIONAL_THERMAL_CLOSURE_BLOCKED",
        "formula_record_present": "`T13-019`" in formula,
        "derivative_and_stability_witness_passes": all(witness["checks"].values()),
    }
    status = "PASS_NAMED_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT" if all(checks.values()) else "FAIL_T13_COLLECTIVE_RESPONSE_EOS_STABILITY_AUDIT"
    report = {
        "schema_version": "t13-collective-response-eos-stability-v1",
        "artifact": "t13_collective_response_eos_stability_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "a named finite-temperature collective-response EOS functional with explicit normalized derivatives",
                "formal response derivatives mu_C and mu_Phi together with exact mixed-derivative reciprocity",
                "local Hessian stability conditions and a deterministic derivative/stability witness",
                "an EOS lane that keeps C collective and Phi response rather than relabeling them as charge, mass, particle, information, temperature, or heat flux",
                "separation from Landauer, physical coefficient calibration, and nonequilibrium closure",
            ],
            "equation_or_mapping": {"functional": contract["functional"], "mu_C": contract["mu_C"], "mu_Phi": contract["mu_Phi"], "hessian": contract["hessian"], "stability": contract["stability"], "reciprocity": contract["reciprocity"]},
            "units": {"coordinates": "C and Phi dimensionless normalized coordinates", "coefficients": contract["coefficient_units"], "energy": contract["energy_units"], "entropy": contract["entropy_units"]},
            "derivation_class": "declared normalized finite-temperature functional plus exact calculus, Hessian positivity conditions, and synthetic finite-difference verification",
            "observable": "candidate local response-EOS interface only; no physical charge EOS, pressure, heat flux, entropy production, or TTG observable",
            "data_role": "INTERNAL_FORMULA_STABILITY_CONTRACT_NO_CALIBRATION",
            "evidence_artifacts": [{"path": EOS_REL, "sha256": sha256(EOS_REL)}, {"path": BETA_AUDIT_REL, "sha256": sha256(BETA_AUDIT_REL)}, {"path": THERMAL_AUDIT_REL, "sha256": sha256(THERMAL_AUDIT_REL)}, {"path": FORMULA_REL, "sha256": sha256(FORMULA_REL)}, {"path": "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json"}],
            "verification_status": status,
            "open_blockers": ["source_backed_finite_temperature_EOS_coefficient_provenance_missing", "physical_Phi_field_normalization_and_SI_energy_anchor_missing", "physical_charge_density_or_pressure_observable_mapping_not_declared", "covariant_transport_SK_KMS_entropy_production_and_dissipative_balance_missing", "independent_alpha_Phi_K_calibration_or_derivation_missing"],
            "dependency_unlocked": "named response-EOS formula and stability interface only; no physical EOS, Core curved 3+1, Gravity, transport, or external validation unlock",
            "claim_boundary": "The named EOS is a candidate normalized collective-response lane. It does not establish a physical charge-density EOS, material equation of state, covariant transport law, entropy-production positivity, or global UET closure.",
        },
        "named_contract": contract,
        "synthetic_derivative_stability_witness": witness,
        "checks": checks,
        "numeric_coefficients_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "source_backed_finite_temperature_EOS_coefficient_provenance_and_physical_Phi_SI_anchor_missing",
        "next_controller": "Source-lock finite-temperature coefficient provenance and a Phi/e0 observable anchor independently of TTG target fitting; then formulate covariant transport, SK/KMS, entropy production, and dissipative balance without changing C/Phi/R_gen ontology.",
        "claim_boundary": "No physical EOS parameter, charge/mass identification, transport coefficient, entropy-production result, TTG calibration, target comparison, or Xie 2026 result is emitted by this audit.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT.relative_to(ROOT).as_posix(), "failed_checks": [name for name, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
