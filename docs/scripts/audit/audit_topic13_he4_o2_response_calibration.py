"""Audit the independent He-4 local alpha and field-normalization record."""

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

from docs.core.he4_o2_response_calibration import calibration_record  # noqa: E402


PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_o2_local_response_calibration_source_package.json"
)
SOURCE_ROWS = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_o2_physical_anchor_source_package.json"
)
MODULE = ROOT / "docs/core/he4_o2_response_calibration.py"
NATURAL_BRIDGE = ROOT / "docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json"
OUT = ROOT / "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = load(PACKAGE)
    source_rows = load(SOURCE_ROWS)
    natural_bridge = load(NATURAL_BRIDGE)
    record = calibration_record()
    holdout = package["holdout_policy"]
    checks = {
        "source_package_is_calibration": package["data_role"] == "CALIBRATION",
        "source_rows_are_non_holdout": source_rows["holdout_policy"]["xie_2026_accessed"] is False,
        "source_hash_is_locked": len(package["source_identity"]["interactive_snapshot_sha256"]) == 64,
        "superfluid_uncertainty_bound_is_source_locked": math.isclose(package["uncertainty_source"]["superfluid_density_relative_uncertainty_bound"], 0.005),
        "density_fit_deviation_is_source_locked": math.isclose(package["uncertainty_source"]["total_density_fit_relative_deviation"], 0.5e-6),
        "temperature_grid_condition_is_explicit": "conditional" in package["uncertainty_source"]["excluded_uncertainty"].lower(),
        "alpha_is_finite_nonzero": math.isfinite(float(record["alpha_Phi_K"])) and float(record["alpha_Phi_K"]) != 0.0,
        "alpha_uncertainty_bound_is_positive": float(record["alpha_uncertainty_K_per_normalized_base_Phi"]) > 0.0,
        "alpha_sign_matches_source_slope": float(record["alpha_Phi_K"]) < 0.0 and float(record["d_superfluid_fraction_dT_per_K"]) < 0.0,
        "field_normalization_is_finite_nonzero": math.isfinite(float(record["Z_Phi_normalized_per_natural_Phi"])) and float(record["Z_Phi_normalized_per_natural_Phi"]) != 0.0,
        "field_normalization_uncertainty_is_positive": float(record["Z_Phi_uncertainty_bound"]) > 0.0,
        "natural_bridge_is_action_derived": natural_bridge["status"] == "PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE",
        "natural_bridge_did_not_use_landauer": natural_bridge["state"]["landauer_identity_used"] is False,
        "no_target_data": holdout["target_curve_used"] is False,
        "no_fit_or_tuning": holdout["fit_or_tuning_used"] is False,
        "xie_holdout_unread": holdout["xie_2026_accessed"] is False,
        "no_threshold_adjustment": holdout["threshold_adjustment_used"] is False,
    }
    passed = all(checks.values())
    status = "PASS_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION" if passed else "FAIL_HE4_RESPONSE_CALIBRATION"
    report = {
        "schema_version": "t13-he4-o2-response-calibration-audit-v1",
        "artifact": "t13_he4_o2_response_calibration_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": "A local He-4 normalized response coordinate, independent alpha_Phi_K calibration, conservative property-uncertainty bound, natural-to-kelvin temperature scale, and signed action-field normalization Z_Phi.",
            "equation_or_mapping": {
                "observable_coordinate": record["phi_mapping"],
                "measurement": "Delta_Tq = alpha_Phi_K Delta_Phi_norm",
                "action_field_map": record["action_mapping"],
                "temperature_map": record["temperature_mapping"],
            },
            "units": {
                "alpha_Phi_K": record["alpha_units"],
                "Phi_norm": record["phi_units"],
                "Z_Phi": "normalized base Phi per natural action Phi",
            },
            "derivation_class": "INDEPENDENT_EQUILIBRIUM_SOURCE_CALIBRATION_PLUS_ACTION_DERIVED_NATURAL_BRIDGE",
            "observable": "local He-4 superfluid-fraction response around 1.7 K at SVP",
            "data_role": "CALIBRATION_NOT_HOLDOUT",
            "evidence_artifacts": [
                {"path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PACKAGE)},
                {"path": str(SOURCE_ROWS.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(SOURCE_ROWS)},
                {"path": str(MODULE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MODULE)},
                {"path": str(NATURAL_BRIDGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(NATURAL_BRIDGE)},
            ],
            "verification_status": status,
            "open_blockers": [
                "absolute_temperature_scale_uncertainty_not_included",
                "SI_energy_density_scale_not_closed",
                "normalized_beta_SI_map_not_closed",
                "physical_transport_coefficient_not_closed",
            ],
            "dependency_unlocked": "Independent local alpha_Phi_K and action-field normalization lanes; no SI energy-density, beta, transport, TTG, or Full Topic 13 unlock.",
            "claim_boundary": package["claim_boundary"],
        },
        "record": record,
        "source_identity": package["source_identity"],
        "uncertainty_source": package["uncertainty_source"],
        "checks": checks,
        "controlling_blocker": "SI_energy_density_scale_and_normalized_beta_map_missing",
        "next_controller": "Fix one state-matched SI free-energy or pressure scale with uncertainty, then propagate Z_Phi into normalized beta without identifying the SVP heat capacity with the fixed-mu action susceptibility.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "alpha_Phi_K": record["alpha_Phi_K"], "alpha_uncertainty_bound": record["alpha_uncertainty_K_per_normalized_base_Phi"], "Z_Phi": record["Z_Phi_normalized_per_natural_Phi"], "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
