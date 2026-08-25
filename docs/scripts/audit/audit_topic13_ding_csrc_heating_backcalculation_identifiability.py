"""Audit the identifiability boundary for back-calculating Ding C_src."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_experimental_heating_input_source_package.json"
)
SOURCE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_pmc_full_text.txt"
)
HEATING_AUDIT = ROOT / "docs/core/artifacts/t13_ding_experimental_heating_input_boundary_audit.json"
NORMALIZED_AUDIT = ROOT / "docs/core/artifacts/t13_ding_fig1d_normalized_source_lane_audit.json"
OUT = ROOT / "docs/core/artifacts/t13_ding_csrc_heating_backcalculation_identifiability_no_go.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rows_by_id(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["row_id"]: row
        for row in package.get("source_rows", [])
        if isinstance(row, dict) and isinstance(row.get("row_id"), str)
    }


def main() -> int:
    package = load(PACKAGE)
    source_text = SOURCE.read_text(encoding="utf-8")
    heating = load(HEATING_AUDIT)
    normalized = load(NORMALIZED_AUDIT)
    rows = rows_by_id(package)
    source = package.get("source", {})
    energy_contract = package.get("energy_density_contract", {})
    absorbed = energy_contract.get("absorbed_energy_density", {})
    bound_row = rows.get("ding_surface_temperature_rise_upper_bound", {})
    incident = package.get("derived_records", [{}])[0]

    checks = {
        "source_package_present": PACKAGE.is_file(),
        "source_text_present": SOURCE.is_file(),
        "source_hash_matches_package": digest(SOURCE) == source.get("local_sha256"),
        "heating_boundary_audit_passes": heating.get("status")
        == "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY",
        "reported_pump_energy_is_present": rows.get("ding_pump_pulse_energy", {}).get(
            "value_si"
        )
        == 70.0e-9,
        "incident_fluence_is_derived_not_absorbed": incident.get("unit_si")
        == "J m^-2"
        and incident.get("data_role") == "EXTERNAL_SETUP_DERIVED_NOT_CALIBRATION",
        "surface_temperature_is_upper_bound_only": bound_row.get("value_si") is None
        and bound_row.get("upper_bound_si") == 3.0
        and bound_row.get("uncertainty_status")
        == "BOUND_ONLY_NOT_A_POINT_ESTIMATE",
        "absorbed_energy_density_is_open": absorbed.get("status")
        == "OPEN_NOT_IDENTIFIED"
        and absorbed.get("numeric_value") is None,
        "normalized_ttg_audit_passes": normalized.get("status")
        == "PASS_DING_FIGURE_DERIVED_NORMALIZED_SOURCE_LANE",
        "normalized_ttg_is_dimensionless": normalized.get("major_result", {})
        .get("units", {})
        .get("normalized_signal")
        == "dimensionless",
        "normalized_lane_has_no_raw_author_numeric_source": "raw_author_PBTE_inputs_and_numeric_C_src(T)_not_captured"
        in normalized.get("major_result", {}).get("open_blockers", []),
        "normalized_lane_has_no_numeric_fit": normalized.get("verification", {})
        .get("checks", {})
        .get("numeric_fitting_disabled")
        is True,
        "holdout_is_not_accessed": package.get("holdout_policy", {}).get(
            "xie_2026_accessed"
        )
        is False
        and package.get("holdout_policy", {}).get("xie_2026_source_data_consumed")
        is False
        and normalized.get("verification", {}).get("checks", {}).get(
            "holdout_not_accessed"
        )
        is True,
        "no_landauer_inference": package.get("holdout_policy", {}).get(
            "landauer_used_for_derivation"
        )
        is False,
        "source_reports_no_absolute_delta_t_pair": "surface temperature rise due to the pulses is estimated to be <3"
        in source_text
        and bound_row.get("value_si") is None
        and absorbed.get("numeric_value") is None,
    }

    passed = all(checks.values())
    status = (
        "PASS_SCOPED_NO_GO_DING_C_SRC_HEATING_BACKCALCULATION"
        if passed
        else "FAIL_DING_C_SRC_HEATING_BACKCALCULATION_AUDIT"
    )
    report = {
        "schema_version": "t13-ding-csrc-heating-backcalculation-identifiability-v1",
        "artifact": "t13_ding_csrc_heating_backcalculation_identifiability_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_C_SRC_HEATING_BACKCALCULATION_IDENTIFIABILITY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if passed else "OPEN",
            "what_is_closed": [
                "The incident-pump setup does not identify absorbed energy density because absorption fraction, thermalized depth, and thermalized volume are not source-locked.",
                "The captured Ding temperature statement is an upper bound (<3 K), not an uncertainty-bounded absolute Delta_Tq point record.",
                "The published figure-derived TTG lane is normalized and therefore cannot identify an absolute C_src or alpha_Phi_K scale.",
                "The back-calculation route is separated from the authorized numeric C_src or accepted same-regime PBTE reproduction route.",
            ],
            "equation_or_mapping": {
                "incident_fluence": "F_incident = E_pump / A_1e2",
                "absorbed_energy_density": "Delta_u_abs = eta_abs * F_incident / l_th",
                "source_temperature": "Delta_Tq = Delta_u_abs / C_src = eta_abs * F_incident / (l_th * C_src)",
                "normalized_observable": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
                "identifiability_witness": "(C_src, eta_abs/l_th) -> (s*C_src, s*eta_abs/l_th) leaves Delta_Tq unchanged; normalized y_TTG also removes the overall amplitude",
            },
            "units": {
                "E_pump": "J",
                "F_incident": "J m^-2",
                "Delta_u_abs": "J m^-3",
                "C_src": "J m^-3 K^-1",
                "Delta_Tq": "K",
                "y_TTG": "dimensionless",
            },
            "derivation_class": "source-backed dimensional identifiability no-go; no UET calibration",
            "observable": "Ding incident-heating setup, bounded surface response, and normalized TTG trace",
            "data_role": "EXTERNAL_SOURCE_BOUNDARY_NO_GO_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": relative(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": relative(SOURCE), "sha256": digest(SOURCE)},
                {"path": relative(HEATING_AUDIT), "sha256": digest(HEATING_AUDIT)},
                {"path": relative(NORMALIZED_AUDIT), "sha256": digest(NORMALIZED_AUDIT)},
            ],
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "absorbed_energy_density_and_thermalized_volume_not_source_locked",
                "independent_alpha_Phi_K_calibration_missing",
            ],
            "dependency_unlocked": "Back-calculation route is closed as a no-go only; no Ding C_src, alpha, dimensional Phi, transport, Core, Gravity, or Galaxy dependency is unlocked.",
            "claim_boundary": "This no-go is scoped to the captured incident-heating and normalized-TTG routes. It does not prove that an authorized raw Ding package or accepted same-regime PBTE reproduction cannot supply C_src.",
        },
        "numeric_witness": {
            "incident_fluence_J_m2": incident.get("value_si"),
            "surface_temperature_upper_bound_K": bound_row.get("upper_bound_si"),
            "absolute_delta_Tq_point_available": False,
            "absorbed_energy_density_available": False,
            "numeric_C_src_emitted": False,
            "numeric_alpha_Phi_K_emitted": False,
        },
        "checks": checks,
        "what_changed": "Closed the incident-heating/normalized-TTG back-calculation route as a scoped identifiability no-go without fabricating C_src or alpha_Phi_K.",
        "verification": "Source/package hashes, incident-fluence role, <3 K bound semantics, normalized-source role, no-fit policy, no-Landauer policy, and holdout exclusion are checked.",
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_action": "Obtain an authorized Ding mode-resolved C_src payload or an accepted same-regime PBTE reproduction with material mapping, convergence, uncertainty, and permission; do not infer C_src from incident fluence, the <3 K bound, or normalized TTG rows.",
        "claim_boundary": "Scoped route no-go only; not numeric C_src, alpha calibration, TTG prediction, external validation, Core closure, or global UET closure.",
        "claim_promotion": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": relative(OUT),
                "checks_passed": sum(checks.values()),
                "checks_total": len(checks),
                "numeric_C_src_emitted": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
