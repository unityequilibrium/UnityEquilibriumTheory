"""Audit the state-matched He-4 SI scale and normalized beta mapping."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.he4_o2_si_beta_mapping import si_beta_record  # noqa: E402


PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_o2_si_beta_mapping_source_package.json"
)
CONSTANTS = ROOT / "docs/data/external/constants/codata/si_2019_exact_constants.json"
DENSITY = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_o2_physical_anchor_source_package.json"
)
CALIBRATION = ROOT / "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json"
ACTION_BETA = ROOT / "docs/core/artifacts/t13_uet_o2_action_thermal_stiffness_beta_audit.json"
MODULE = ROOT / "docs/core/he4_o2_si_beta_mapping.py"
OUT = ROOT / "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = load(PACKAGE)
    constants = load(CONSTANTS)
    calibration = load(CALIBRATION)
    action_beta = load(ACTION_BETA)
    record = si_beta_record()
    checks = {
        "source_package_is_calibration": package["data_role"] == "CALIBRATION",
        "state_is_matched_to_response_calibration": package["state"]["temperature_K"] == calibration["record"]["temperature_K"],
        "its90_uncertainty_is_numeric_positive": package["sources"]["temperature_scale"]["temperature_standard_uncertainty_K"] > 0.0,
        "he4_mass_uncertainty_is_numeric_positive": package["sources"]["he4_relative_atomic_mass"]["standard_uncertainty"] > 0.0,
        "atomic_mass_constant_uncertainty_is_numeric_positive": package["sources"]["atomic_mass_constant"]["standard_uncertainty_kg"] > 0.0,
        "boltzmann_constant_matches_exact_local_record": math.isclose(package["sources"]["boltzmann_constant"]["value_J_K"], constants["constants"]["k_B"]["value"], rel_tol=0.0, abs_tol=0.0),
        "energy_density_scale_is_finite_positive": math.isfinite(float(record["energy_density_scale_J_m3"])) and float(record["energy_density_scale_J_m3"]) > 0.0,
        "energy_density_uncertainty_is_finite_positive": math.isfinite(float(record["energy_density_scale_uncertainty_J_m3"])) and float(record["energy_density_scale_uncertainty_J_m3"]) > 0.0,
        "action_beta_is_source_derived": action_beta["status"] == "PASS_ACTION_DERIVED_THERMAL_STIFFNESS_BETA_LANE",
        "normalized_beta_is_finite_nonzero": math.isfinite(float(record["beta_T13"])) and float(record["beta_T13"]) != 0.0,
        "normalized_beta_uncertainty_is_positive": float(record["beta_T13_uncertainty_bound"]) > 0.0,
        "si_beta_is_finite_nonzero": math.isfinite(float(record["beta_SI_J_m3_per_normalized_Phi2"])) and float(record["beta_SI_J_m3_per_normalized_Phi2"]) != 0.0,
        "si_beta_uncertainty_is_positive": float(record["beta_SI_uncertainty_J_m3_per_normalized_Phi2"]) > 0.0,
        "ensemble_mismatch_is_forbidden": "does not identify" in package["mapping_contract"]["ensemble_boundary"].lower(),
        "landauer_is_not_used": record["holdout_policy"]["landauer_identity_used"] is False,
        "xie_holdout_is_unread": record["holdout_policy"]["xie_2026_accessed"] is False,
        "no_target_curve": record["holdout_policy"]["target_curve_used"] is False,
        "no_fit_or_tuning": record["holdout_policy"]["fit_or_tuning_used"] is False,
    }
    passed = all(checks.values())
    status = "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA" if passed else "FAIL_HE4_SI_BETA_MAPPING"
    evidence_paths = [PACKAGE, CONSTANTS, DENSITY, CALIBRATION, ACTION_BETA, MODULE]
    report = {
        "schema_version": "t13-he4-o2-si-beta-audit-v1",
        "artifact": "t13_he4_o2_si_beta_mapping_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_HE4_O2_SI_SCALE_AND_NORMALIZED_BETA",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": "A state-matched ITS-90 uncertainty contract, external He-4 thermal-cell SI free-energy-density scale, normalized beta_T13, and beta_SI with conservative uncertainty propagation.",
            "equation_or_mapping": {
                "energy_density_scale": record["energy_scale_mapping"],
                "free_energy": record["free_energy_mapping"],
                "field": record["phi_mapping"],
                "beta": record["beta_mapping"],
            },
            "units": {
                "e0": "J m^-3",
                "beta_T13": record["beta_T13_units"],
                "beta_SI": "J m^-3 per normalized Phi squared",
            },
            "derivation_class": package["mapping_contract"]["derivation_class"],
            "observable": "local He-4 O(2) response around 1.7 K on the SVP/ITS-90 state path",
            "data_role": "CALIBRATION_NOT_HOLDOUT",
            "evidence_artifacts": [
                {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
                for path in evidence_paths
            ],
            "verification_status": status,
            "open_blockers": ["physical_transport_coefficient_not_closed"] if passed else ["SI_scale_or_beta_mapping_failed"],
            "dependency_unlocked": "SI dimensional observable and normalized-beta lanes only; physical transport and Full Topic 13 remain locked." if passed else "None",
            "claim_boundary": package["claim_boundary"],
        },
        "record": record,
        "checks": checks,
        "controlling_blocker": "physical_transport_coefficient_not_closed" if passed else "SI_scale_or_beta_mapping_failed",
        "next_controller": "Source-lock one state-matched He-4 physical transport coefficient with uncertainty and connect it to the declared Kubo/SK-KMS/entropy interface.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "e0_J_m3": record["energy_density_scale_J_m3"], "beta_T13": record["beta_T13"], "beta_SI": record["beta_SI_J_m3_per_normalized_Phi2"], "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
