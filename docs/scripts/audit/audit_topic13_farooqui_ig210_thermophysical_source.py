"""Audit the published NPL/Springer IG-210 thermophysical source table."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "farooqui_2022_ig210_thermophysical_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "farooqui_2022_ig210_thermophysical_table.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_farooqui_ig210_thermophysical_source_audit.json"

EXPECTED_SIZE = 4116498
EXPECTED_MD5 = "95237ebba081f28e48d5ee7ec88babe8"
EXPECTED_SHA256 = "777eebdc380f0707c3b63e612cce8977fcb6cab4ee5ed086e45f09aa81e2bd45"
EXPECTED_ROWS = [
    ("farooqui_2022_table1_ig210_500C", 500.0, 773.15, 1781.0, 1549.0, 24.6e-6, 5.0e-6, 68.3),
    ("farooqui_2022_table1_ig210_700C", 700.0, 973.15, 1775.0, 1807.0, 19.5e-6, 5.2e-6, 59.2),
    ("farooqui_2022_table1_ig210_1000C", 1000.0, 1273.15, 1765.0, 1892.0, 15.2e-6, 5.5e-6, 51.5),
]


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def close(value: object, expected: float) -> bool:
    return isinstance(value, (int, float)) and math.isclose(float(value), expected, rel_tol=0.0, abs_tol=1.0e-12)


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    rows = package["source_rows"]
    comparator = package["derived_comparator"]
    raw_md5 = digest(RAW, "md5") if RAW.is_file() else None
    raw_sha256 = digest(RAW) if RAW.is_file() else None

    row_checks = []
    for row, expected in zip(rows, EXPECTED_ROWS):
        row_checks.append(
            row.get("source_row_id") == expected[0]
            and close(row.get("temperature_C"), expected[1])
            and close(row.get("temperature_K"), expected[2])
            and close(row.get("density_kg_per_m3"), expected[3])
            and close(row.get("specific_heat_Cp_J_per_kg_K"), expected[4])
            and close(row.get("thermal_diffusivity_m2_per_s"), expected[5])
            and close(row.get("alpha_l_from_23C_K^-1"), expected[6])
            and close(row.get("thermal_conductivity_W_per_m_K"), expected[7])
            and row.get("table_locator")
        )

    uncertainty_checks = []
    for row in rows:
        uncertainty = row.get("uncertainty", {})
        uncertainty_checks.append(
            uncertainty.get("coverage_factor") == 2
            and close(uncertainty.get("density_relative_expanded"), 0.003)
            and close(uncertainty.get("specific_heat_relative_expanded"), 0.06)
            and close(uncertainty.get("thermal_diffusivity_relative_expanded"), 0.04)
            and close(uncertainty.get("alpha_l_relative_expanded"), 0.10)
            and uncertainty.get("thermal_conductivity_relative_expanded_range") == [0.08, 0.10]
        )

    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_size_matches": RAW.is_file() and RAW.stat().st_size == EXPECTED_SIZE,
        "raw_pdf_md5_matches": raw_md5 == EXPECTED_MD5,
        "raw_pdf_sha256_matches": raw_sha256 == EXPECTED_SHA256,
        "source_identity_locator_and_license_present": bool(
            source.get("doi")
            and source.get("official_url")
            and source.get("repository_url")
            and source.get("download_url")
            and source.get("license") == "CC BY 4.0"
            and len(source.get("source_locators", [])) >= 5
            and source.get("local_raw_path") == rel(RAW)
        ),
        "material_batch_and_temperature_scope_declared": source.get("material") == "IG-210 grade isotropic graphite from Toyo Tanso"
        and "intercomparison" in source.get("batch_statement", "")
        and source.get("temperature_scope") == "500 C, 700 C, and 1000 C Table 1 thermophysical values",
        "numeric_rows_have_identity_units_and_expected_values": len(rows) == 3 and all(row_checks),
        "source_uncertainty_rows_are_preserved": len(rows) == 3 and all(uncertainty_checks),
        "density_correction_footnote_is_declared": "thermal-expansion corrections" in package["preprocessing"]["density_policy"],
        "alpha_volume_conversion_is_conditional": package["preprocessing"]["alpha_volume_policy"] == "alpha_V = 3*alpha_l is a conditional isotropic geometry comparator and is not source-reported",
        "cp_is_not_relabelled_as_cv": package["preprocessing"]["cp_cv_policy"].startswith("retain C_p; do not relabel as C_v"),
        "kt_and_cv_are_explicitly_open": comparator.get("same_state_K_T_present") is False and comparator.get("c_v_present") is False,
        "ding_equivalence_is_not_claimed": comparator.get("Ding_TTG_material_match_closed") is False,
        "alpha_phi_k_is_not_emitted": comparator.get("alpha_Phi_K_calibration_emitted") is False,
        "no_fit_or_holdout_access": package["preprocessing"]["fit_or_tuning"] == "none"
        and package["holdout_policy"]["xie_2026_accessed"] is False
        and package["holdout_policy"]["calibration_path_may_read_holdout"] is False,
    }
    passed = all(checks.values())
    major_result = {
        "major_result_id": "T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "published Table 1 IG-210 density, C_p, thermal diffusivity, alpha_l, and thermal-conductivity rows at 500, 700, and 1000 C",
            "same-grade IG-210 batch statement and source locators",
            "source expanded uncertainty bounds at coverage factor k=2",
            "explicit separation of C_p from the unresolved C_p-to-C_v correction",
        ],
        "equation_or_mapping": {
            "conditional_volume_expansion": "alpha_V = 3*alpha_l under isotropic geometry",
            "cp_to_cv": "c_v^V = rho*(C_p - T*alpha_V^2*K_T)",
            "thermal_diffusivity_conductivity_context": "kappa = rho*C_p*D is source context only; it is not a UET transport derivation",
        },
        "units": {
            "temperature": "C and K",
            "density": "kg m^-3",
            "specific_heat": "J kg^-1 K^-1",
            "thermal_diffusivity": "m^2 s^-1",
            "alpha_l": "K^-1",
            "thermal_conductivity": "W m^-1 K^-1",
            "uncertainty": "expanded relative source bounds, k=2",
        },
        "derivation_class": "source transcription with unit normalization; conditional geometry mapping only; no UET derivation",
        "observable": "IG-210 high-temperature thermophysical property comparator",
        "data_role": "EXTERNAL_SOURCE_COMPARATOR_NOT_CALIBRATION",
        "evidence_artifacts": [
            {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
            {"path": rel(RAW), "sha256": raw_sha256},
        ],
        "verification_status": "PASS_SCOPED_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE" if passed else "FAIL_SOURCE_PACKAGE_INTEGRITY",
        "open_blockers": [
            "same_state_IG210_isothermal_K_T_missing",
            "C_p_to_C_v_correction_not_closed",
            "Ding_TTG_material_regime_mapping_not_closed",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "IG-210 density/C_p/alpha_l source lane only; no C_v, Ding C_src, alpha_Phi_K, transport, Core, or Gravity unlock",
        "claim_boundary": package["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-farooqui-ig210-thermophysical-source-audit-v1",
        "artifact": "t13_farooqui_ig210_thermophysical_source_audit",
        "generated_at": date.today().isoformat(),
        "status": major_result["verification_status"],
        "claim_promotion": False,
        "full_core_unlock": False,
        "major_result": major_result,
        "source": {
            "doi": source.get("doi"),
            "official_url": source.get("official_url"),
            "repository_url": source.get("repository_url"),
            "local_raw_path": source.get("local_raw_path"),
            "size_bytes": RAW.stat().st_size if RAW.is_file() else None,
            "md5": raw_md5,
            "sha256": raw_sha256,
        },
        "row_summary": {
            "count": len(rows),
            "temperatures_C": [row.get("temperature_C") for row in rows],
            "same_grade_ig210": True,
            "density_uncertainty_locked": True,
            "specific_heat_uncertainty_locked": True,
            "K_T_present": False,
            "C_v_emitted": False,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "same_state_IG210_isothermal_K_T_and_independent_alpha_Phi_K_missing",
        "next_controller": "source-lock a permitted same-state IG-210 K_T record or retain the C_p-to-C_v blocker; pursue independent Phi SI anchor separately",
        "claim_boundary": major_result["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "passed_checks": sum(checks.values()), "total_checks": len(checks), "artifact": rel(OUT)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
