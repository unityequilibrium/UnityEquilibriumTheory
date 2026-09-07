"""Audit the source and unit boundary for Ding's reported TTG heating setup.

This audit derives incident fluence from reported pulse energy and beam size.
It deliberately does not infer absorbed energy density, C_src, e0, or alpha.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
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
OUT = ROOT / "docs/core/artifacts/t13_ding_experimental_heating_input_boundary_audit.json"

EXPECTED_STATUS = "PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"
EXPECTED_SOURCE_SHA256 = "b1b029f2812586647077a7b8506c2f52aeb7261714395907f8f8d20868fe2874"
EXPECTED_SOURCE_BYTES = 41581


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_source(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u03bc", "u").replace("\u00b5", "u")
    normalized = normalized.replace("\u2212", "-").replace("\u2013", "-")
    return " ".join(normalized.lower().split())


def row_index(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = package.get("source_rows")
    if not isinstance(rows, list):
        return {}
    return {
        row["row_id"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("row_id"), str)
    }


def main() -> int:
    package = load(PACKAGE)
    source_text = SOURCE.read_text(encoding="utf-8")
    normalized = normalize_source(source_text)
    rows = row_index(package)
    derived = {
        item["record_id"]: item
        for item in package.get("derived_records", [])
        if isinstance(item, dict) and isinstance(item.get("record_id"), str)
    }

    pump_energy = 70.0e-9
    pump_diameter = 120.0e-6
    pump_radius = pump_diameter / 2.0
    pump_area = math.pi * pump_radius**2
    pump_fluence = pump_energy / pump_area

    probe_energy = 52.0e-9
    probe_diameter = 105.0e-6
    probe_radius = probe_diameter / 2.0
    probe_area = math.pi * probe_radius**2
    probe_fluence = probe_energy / probe_area

    markers = {
        "natural_graphite_sample": "natural graphite sample" in normalized,
        "grain_area": "average area of grain is estimated as 382" in normalized
        and "270" in normalized,
        "grain_size": "grain size larger than 20" in normalized,
        "pulse_duration": (
            "duration about 290 fs" in normalized
            or "duration about290 fs" in normalized
        ),
        "wavelengths": "515 nm and 532 nm wavelengths" in normalized,
        "repetition_rate": "repetition rate of the laser pulses is 25 khz" in normalized,
        "spot_sizes": "spot sizes (1/e2 diameters) of 120 um and 105 um" in normalized,
        "pulse_energies": "pulse energies are set at 70 nj and 52 nj" in normalized,
        "temperature_bound": "surface temperature rise due to the pulses is estimated to be <3 k"
        in normalized,
    }

    checks = {
        "package_is_ascii": all(byte < 128 for byte in PACKAGE.read_bytes()),
        "source_exists": SOURCE.is_file(),
        "source_bytes_match": SOURCE.stat().st_size == EXPECTED_SOURCE_BYTES,
        "source_hash_matches_expected": sha256(SOURCE) == EXPECTED_SOURCE_SHA256,
        "source_hash_matches_package": package.get("source", {}).get("local_sha256")
        == sha256(SOURCE),
        "source_bytes_match_package": package.get("source", {}).get("local_bytes")
        == SOURCE.stat().st_size,
        "source_identity_locked": package.get("source", {}).get("doi")
        == "10.1038/s41467-021-27907-z"
        and package.get("source", {}).get("pmcid") == "PMC8755757",
        "all_source_markers_present": all(markers.values()),
        "required_rows_present": set(rows)
        >= {
            "ding_pump_pulse_energy",
            "ding_probe_pulse_energy",
            "ding_pump_spot_diameter_1e2",
            "ding_probe_reference_spot_diameter_1e2",
            "ding_pulse_duration",
            "ding_pump_wavelength",
            "ding_probe_wavelength",
            "ding_laser_repetition_rate",
            "ding_pump_chopper_rate",
            "ding_surface_temperature_rise_upper_bound",
            "ding_average_grain_area",
            "ding_typical_grain_size_lower_bound",
        },
        "source_row_units_are_explicit": all(
            isinstance(row.get("unit_si"), str) for row in rows.values()
        ),
        "pulse_input_uncertainty_boundary_is_explicit": all(
            rows[row_id].get("uncertainty") is None
            and isinstance(rows[row_id].get("uncertainty_status"), str)
            for row_id in (
                "ding_pump_pulse_energy",
                "ding_probe_pulse_energy",
                "ding_pump_spot_diameter_1e2",
                "ding_probe_reference_spot_diameter_1e2",
            )
        ),
        "temperature_is_bound_not_point": rows.get(
            "ding_surface_temperature_rise_upper_bound", {}
        ).get("bound_operator")
        == "<"
        and rows.get("ding_surface_temperature_rise_upper_bound", {}).get("value_si")
        is None
        and rows.get("ding_surface_temperature_rise_upper_bound", {}).get(
            "upper_bound_si"
        )
        == 3.0,
        "pump_fluence_formula_is_declared": derived.get(
            "ding_pump_1e2_incident_fluence", {}
        ).get("equation")
        == "w = d_1e2 / 2; A_1e2 = pi*w^2; F_incident = E_pump / A_1e2",
        "pump_fluence_units_close": derived.get(
            "ding_pump_1e2_incident_fluence", {}
        ).get("unit_si")
        == "J m^-2",
        "pump_fluence_matches_geometry": math.isclose(
            derived.get("ding_pump_1e2_incident_fluence", {}).get("value_si", math.nan),
            pump_fluence,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
        and math.isclose(
            derived.get("ding_pump_1e2_incident_fluence", {}).get("area_si", math.nan),
            pump_area,
            rel_tol=0.0,
            abs_tol=1.0e-20,
        ),
        "probe_fluence_matches_geometry": math.isclose(
            derived.get("ding_probe_1e2_incident_fluence", {}).get("value_si", math.nan),
            probe_fluence,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
        and math.isclose(
            derived.get("ding_probe_1e2_incident_fluence", {}).get("area_si", math.nan),
            probe_area,
            rel_tol=0.0,
            abs_tol=1.0e-20,
        ),
        "absorbed_energy_density_remains_open": package.get(
            "energy_density_contract", {}
        ).get("absorbed_energy_density", {}).get("status")
        == "OPEN_NOT_IDENTIFIED"
        and package.get("energy_density_contract", {})
        .get("absorbed_energy_density", {})
        .get("numeric_value")
        is None,
        "base_phi_and_alpha_remain_open": package.get("energy_density_contract", {})
        .get("base_phi_map", {})
        .get("numeric_e0")
        is None
        and package.get("energy_density_contract", {})
        .get("base_phi_map", {})
        .get("numeric_alpha_Phi_K")
        is None,
        "no_holdout_or_fit": package.get("holdout_policy", {}).get(
            "xie_2026_accessed"
        )
        is False
        and package.get("holdout_policy", {}).get("xie_2026_source_data_consumed")
        is False
        and package.get("holdout_policy", {}).get("target_curve_used") is False
        and package.get("holdout_policy", {}).get("fit_performed") is False
        and package.get("holdout_policy", {}).get("threshold_adjusted") is False,
        "landauer_not_used": package.get("holdout_policy", {}).get(
            "landauer_used_for_derivation"
        )
        is False,
        "major_result_contract_present": all(
            key in package.get("major_result", {})
            for key in (
                "major_result_id",
                "topic",
                "closure_level",
                "what_is_closed",
                "equation_or_mapping",
                "units",
                "derivation_class",
                "observable",
                "data_role",
                "evidence_artifacts",
                "open_blockers",
                "dependency_unlocked",
                "claim_boundary",
            )
        ),
    }

    status = EXPECTED_STATUS if all(checks.values()) else "FAIL_DING_EXPERIMENTAL_HEATING_INPUT_AUDIT"
    major_result = package["major_result"]
    report = {
        "schema_version": "t13-ding-experimental-heating-input-boundary-audit-v1",
        "artifact": "t13_ding_experimental_heating_input_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": major_result["major_result_id"],
            "topic": major_result["topic"],
            "closure_level": major_result["closure_level"],
            "what_is_closed": major_result["what_is_closed"],
            "equation_or_mapping": major_result["equation_or_mapping"],
            "units": major_result["units"],
            "derivation_class": major_result["derivation_class"],
            "observable": major_result["observable"],
            "data_role": major_result["data_role"],
            "evidence_artifacts": [
                {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
                {
                    "path": rel(SOURCE),
                    "sha256": sha256(SOURCE),
                    "bytes": SOURCE.stat().st_size,
                },
            ],
            "verification_status": status,
            "open_blockers": major_result["open_blockers"],
            "dependency_unlocked": major_result["dependency_unlocked"],
            "claim_boundary": major_result["claim_boundary"],
        },
        "source": {
            "path": rel(SOURCE),
            "sha256": sha256(SOURCE),
            "bytes": SOURCE.stat().st_size,
            "doi": package.get("source", {}).get("doi"),
            "pmcid": package.get("source", {}).get("pmcid"),
            "locators": package.get("source", {}).get("source_locators", []),
        },
        "source_rows": package.get("source_rows", []),
        "derived_records": package.get("derived_records", []),
        "energy_density_contract": package.get("energy_density_contract", {}),
        "marker_checks": markers,
        "checks": checks,
        "what_changed": "The Ding methods text is now source-hash locked with typed incident setup rows and independently recomputed 1/e2 incident fluence. Absorption, thermalized volume, C_src, e0, base Phi, and alpha remain explicit open boundaries.",
        "verification": "Source identity, byte/hash parity, phrase locators, SI units, bound semantics, geometric fluence, non-circularity, and holdout non-access are checked.",
        "controlling_blocker": "absorbed_energy_density_and_ding_C_src_not_source_locked",
        "next_action": "Obtain an authorized absorption/thermalized-volume record and a Ding-compatible numeric C_src package, or keep this as a setup-only boundary; do not infer alpha_Phi_K from incident fluence or the <3 K bound.",
        "claim_boundary": "This is a scoped source/setup boundary. It does not provide absorbed energy density, temperature prediction, e0, alpha_Phi_K, external validation, or Full Topic 13 closure.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "checks_passed": sum(checks.values()),
                "checks_total": len(checks),
                "pump_fluence_J_m2": pump_fluence,
                "controlling_blocker": report["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status == EXPECTED_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
