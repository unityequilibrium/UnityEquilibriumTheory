"""Audit the MP48 boundary for temperature-resolved volumetric c_v uncertainty.

The MP48 package is useful as an independent harmonic comparator, but its
room-temperature volume anchor and non-statistical display envelope cannot be
promoted to a source-grade temperature-resolved uncertainty contract.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "mp48_independent_graphite_cv_source_package.json"
)
BASE_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_temperature_volume_uncertainty_boundary_audit.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = load_json(PACKAGE)
    base_audit = load_json(BASE_AUDIT)
    volume = package["experimental_volume_anchor"]
    uncertainty = package["uncertainty_contract"]
    rows = package["representative_rows"]
    temperatures = [float(row["temperature_K"]) for row in rows]
    row_identity = {float(row["temperature_K"]): row["row_identity"] for row in rows}
    holdout = package["holdout_policy"]

    checks = {
        "package_status_is_independent_comparator": package["status"]
        == "SOURCE_LOCKED_INDEPENDENT_HARMONIC_CV_COMPARATOR",
        "base_mp48_audit_is_passing": base_audit["status"]
        == "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE",
        "base_mp48_audit_is_lane_closed": base_audit["major_result"]["closure_level"]
        == "CLOSED_FOR_LANE",
        "equation_keeps_volumetric_conversion_explicit": package["unit_contract"][
            "conversion"
        ]
        == "C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell",
        "room_temperature_volume_scope_is_explicit": "room-temperature"
        in volume["temperature_scope"].lower(),
        "temperature_resolved_volume_is_open": volume["temperature_resolved_volume_status"]
        == "OPEN",
        "source_statistical_uncertainty_is_not_reported": uncertainty[
            "source_statistical_uncertainty"
        ]
        == "NOT_REPORTED_BY_DEPOSIT",
        "combined_envelope_is_not_statistical": uncertainty[
            "combined_envelope_status"
        ]
        == "NON_STATISTICAL_DISPLAY_ONLY",
        "temperature_volume_uncertainty_is_open": uncertainty[
            "temperature_volume_uncertainty_status"
        ]
        == "OPEN",
        "interpolation_rows_are_declared": row_identity.get(125.0)
        == "linear_interpolation_120_to_130_K"
        and row_identity.get(225.0) == "linear_interpolation_220_to_230_K",
        "representative_temperature_contract_is_present": temperatures
        == [100.0, 125.0, 150.0, 200.0, 225.0, 250.0, 300.0],
        "no_cp_to_cv_correction_is_declared": package["unit_contract"][
            "no_Cp_to_Cv_correction"
        ]
        is True,
        "no_uet_energy_anchor_is_declared": package["unit_contract"][
            "no_UET_energy_anchor"
        ]
        is True,
        "holdout_is_unconsumed": holdout["xie_2026_accessed"] is False
        and holdout["xie_2026_source_data_consumed"] is False
        and holdout["calibration_path_may_read_holdout"] is False
        and holdout["target_curve_used"] is False
        and holdout["alpha_fit_used"] is False,
    }
    status = (
        "PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO"
        if all(checks.values())
        else "FAIL_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_AUDIT"
    )

    package_rel = PACKAGE.relative_to(ROOT).as_posix()
    base_audit_rel = BASE_AUDIT.relative_to(ROOT).as_posix()
    report = {
        "schema_version": "t13-mp48-temperature-volume-uncertainty-boundary-v1",
        "artifact": "t13_mp48_temperature_volume_uncertainty_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": (
                "The current MP48 route is closed as a scoped boundary: its "
                "room-temperature volume anchor and non-statistical display "
                "envelope cannot be promoted to source-grade, "
                "temperature-resolved volumetric c_v uncertainty."
            ),
            "equation_or_mapping": {
                "volumetric_heat_capacity": "C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell(T)",
                "current_comparator_approximation": "V_mol,cell(T) = V_mol,cell(room-temperature anchor)",
                "thermal_response": "Delta_Tq = Delta_u / C_v^vol(T)",
            },
            "units": {
                "source_heat_capacity": "J K^-1 mol^-1 primitive cell",
                "volume": "m^3 mol^-1 primitive cell",
                "volumetric_heat_capacity": "J m^-3 K^-1",
                "required_volume_uncertainty": "temperature-resolved standard uncertainty in m^3 mol^-1 primitive cell",
            },
            "derivation_class": "source-contract boundary audit; no UET derivation and no calibration",
            "observable": "temperature-resolved volumetric graphite c_v uncertainty contract",
            "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION",
            "evidence_artifacts": [package_rel, base_audit_rel],
            "verification_status": status,
            "open_blockers": [
                "temperature_resolved_graphite_volume_missing",
                "source_statistical_c_v_uncertainty_missing",
                "ding_material_regime_mapping_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "MP48 comparator-boundary reporting only; no Ding C_src, alpha_Phi_K, full Topic 13, or Gravity unlock",
            "claim_boundary": (
                "This result closes a route-level no-go boundary, not the thermal "
                "bridge. MP48 remains an independent harmonic comparator and is "
                "not a Ding PBTE C_src source, UET calibration, TTG prediction, "
                "or external validation."
            ),
        },
        "boundary_observations": {
            "source_package_sha256": sha256(PACKAGE),
            "base_mp48_audit_sha256": sha256(BASE_AUDIT),
            "volume_anchor_source_id": volume["source_id"],
            "volume_anchor_temperature_scope": volume["temperature_scope"],
            "volume_anchor_relative_uncertainty": volume["relative_uncertainty"],
            "source_statistical_uncertainty": uncertainty[
                "source_statistical_uncertainty"
            ],
            "combined_display_envelope_relative": uncertainty[
                "combined_display_envelope_relative"
            ],
            "combined_envelope_status": uncertainty["combined_envelope_status"],
            "temperature_interpolation_status": uncertainty[
                "temperature_interpolation_status"
            ],
            "temperature_volume_uncertainty_status": uncertainty[
                "temperature_volume_uncertainty_status"
            ],
            "fixed_volume_is_comparator_approximation": True,
            "ding_c_src_equivalence_claimed": False,
            "alpha_Phi_K_emitted": False,
        },
        "checks": checks,
        "controlling_blocker": "temperature_resolved_graphite_volume_and_source_grade_c_v_uncertainty_missing",
        "next_controller": (
            "Obtain a permitted same-state temperature-resolved graphite volume "
            "source with uncertainty, or record a source-backed equivalent; keep "
            "MP48 as comparator-only until that contract and Ding material mapping "
            "are closed. Independently resolve alpha_Phi_K without Xie 2026."
        ),
        "claim_boundary": (
            "No temperature-resolved source-grade c_v uncertainty, Ding C_src, "
            "alpha_Phi_K calibration, TTG prediction, or Core closure is claimed."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
