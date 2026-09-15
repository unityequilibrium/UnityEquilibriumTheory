"""Audit the source-locked Hi-Trace IG210 expansion comparator."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "zenodo_5799133_ig210_alpha_l_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "zenodo_5799133_hitrace_thermal_diffusivity.xlsx"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_zenodo_ig210_alpha_l_source_audit.json"

EXPECTED_RAW_SIZE = 33113
EXPECTED_RAW_MD5 = "a0a8a2a6e9a9bc607a29c7d17471f89f"
EXPECTED_RAW_SHA256 = "fcd9517fab77025737de2d0da5d92b8b9b90ebd40b9f99c3330c21853c2d79d3"
EXPECTED_TEMPERATURES_C = [
    50.0,
    100.0,
    150.0,
    200.0,
    250.0,
    300.0,
    400.0,
    600.0,
    800.0,
    1000.0,
    1200.0,
    1400.0,
    1600.0,
    1800.0,
    2000.0,
]


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    rows = package["source_rows"]
    uncertainty = package["uncertainty_contract"]
    comparator = package["derived_comparator"]
    raw_md5 = digest(RAW, "md5") if RAW.is_file() else None
    raw_sha256 = digest(RAW) if RAW.is_file() else None

    row_temperatures = [row.get("temperature_C") for row in rows]
    row_ids = [row.get("source_row_id") for row in rows]
    row_checks = []
    for row in rows:
        replicates = row.get("alpha_l_replicates_1e-6_K^-1", [])
        mean_value = row.get("alpha_l_mean_1e-6_K^-1")
        model_value = row.get("alpha_l_model_1e-6_K^-1")
        row_checks.append(
            row.get("sheet") == "Table 1"
            and isinstance(row.get("excel_row"), int)
            and row.get("cell_range")
            and row.get("quantity") == "mean_linear_thermal_expansion_coefficient_alpha_l"
            and row.get("temperature_K") == row.get("temperature_C") + 273.15
            and isinstance(mean_value, (int, float))
            and math.isfinite(float(mean_value))
            and float(mean_value) > 0.0
            and isinstance(model_value, (int, float))
            and math.isfinite(float(model_value))
            and len(replicates) == 4
            and all(math.isfinite(float(value)) and float(value) > 0.0 for value in replicates)
        )

    checks = {
        "raw_workbook_present": RAW.is_file(),
        "raw_workbook_size_matches": RAW.is_file() and RAW.stat().st_size == EXPECTED_RAW_SIZE,
        "raw_workbook_md5_matches": raw_md5 == EXPECTED_RAW_MD5,
        "raw_workbook_sha256_matches": raw_sha256 == EXPECTED_RAW_SHA256,
        "source_identity_and_locator_present": bool(
            source.get("doi")
            and source.get("official_url")
            and source.get("download_url")
            and source.get("local_raw_path") == rel(RAW)
            and len(source.get("source_locators", [])) >= 4
        ),
        "material_and_temperature_scope_declared": source.get("material") == "Isotropic graphite IG210 from Toyo Tanso"
        and "2000 C" in source.get("temperature_scope", ""),
        "all_numeric_rows_have_identity_and_units": len(rows) == 15 and all(row_checks),
        "row_ids_are_unique": len(row_ids) == len(set(row_ids)),
        "source_temperature_grid_matches_table": row_temperatures == EXPECTED_TEMPERATURES_C,
        "source_mean_and_model_are_kept_separate": all(
            row.get("alpha_l_mean_1e-6_K^-1") != row.get("alpha_l_model_1e-6_K^-1")
            or row.get("temperature_C") in {100.0, 1200.0, 1600.0, 2000.0}
            for row in rows
        ),
        "reported_expanded_uncertainty_boundary_present": uncertainty.get("type")
        == "expanded_relative_source_bound"
        and uncertainty.get("coverage_factor") == 2
        and math.isclose(float(uncertainty.get("relative_fraction")), 0.10, rel_tol=0.0, abs_tol=1.0e-12)
        and uncertainty.get("not_a_row_level_independent_standard_uncertainty") is True,
        "isotropic_alpha_v_conversion_is_explicit": comparator.get("alpha_v_relation")
        == "alpha_V = 3 * alpha_l under the declared isotropic geometry assumption"
        and comparator.get("alpha_v_status") == "CONDITIONAL_DERIVED_COMPARATOR_NOT_SOURCE_REPORTED",
        "missing_cp_cv_kt_and_density_are_explicit": comparator.get("same_state_K_T_present") is False
        and comparator.get("density_present") is False
        and comparator.get("c_p_or_c_v_present") is False,
        "ding_material_match_is_not_claimed": comparator.get("Ding_TTG_material_match_closed") is False,
        "no_fit_or_tuning": package.get("preprocessing", {}).get("fit_or_tuning") == "none",
        "holdout_not_consumed": package.get("holdout_policy", {}).get("xie_2026_accessed") is False
        and package.get("holdout_policy", {}).get("calibration_path_may_read_holdout") is False,
        "alpha_phi_k_not_emitted": comparator.get("alpha_Phi_K_calibration_emitted") is False,
    }
    passed = all(checks.values())

    major_result = {
        "major_result_id": "T13_ZENODO_HITRACE_IG210_ALPHA_L_COMPARATOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "source-locked Table 1 mean linear expansion alpha_l rows for isotropic graphite IG210",
            "row identity, temperature units, replicate columns, and source model columns",
            "source-reported expanded uncertainty boundary of 10 percent at coverage factor k=2",
            "conditional isotropic geometry relation alpha_V = 3 alpha_l without relabelling it as a source row",
        ],
        "equation_or_mapping": {
            "source_quantity": "alpha_l^mean(T; T0=23 C) = mean Delta_L/L over (T-T0)",
            "unit_conversion": "alpha_l[K^-1] = alpha_l[10^-6 K^-1] * 10^-6",
            "conditional_volume_mapping": "alpha_V = 3 * alpha_l for an isotropic geometry comparator",
            "cp_cv_contract_not_closed": "c_p^V - c_v^V = T * alpha_V^2 * K_T",
        },
        "units": {
            "temperature": "K and C",
            "alpha_l_source": "10^-6 K^-1",
            "alpha_l_normalized": "K^-1",
            "alpha_V_conditional": "K^-1",
            "uncertainty": "relative expanded bound, k=2",
        },
        "derivation_class": "source transcription plus conditional isotropic geometry conversion; no UET derivation",
        "observable": "IG210 high-temperature mean thermal expansion comparator",
        "data_role": "EXTERNAL_SOURCE_COMPARATOR_NOT_CALIBRATION",
        "evidence_artifacts": [
            {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
            {"path": rel(RAW), "sha256": raw_sha256},
        ],
        "verification_status": "PASS_SCOPED_IG210_ALPHA_L_SOURCE" if passed else "FAIL_SOURCE_PACKAGE_INTEGRITY",
        "open_blockers": [
            "same_state_isothermal_K_T_not_present",
            "density_and_Cp_or_Cv_not_present",
            "IG210_to_Ding_TTG_material_regime_mapping_not_closed",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "IG210 alpha_l source comparator and conditional alpha_V geometry lane only; no Cp-to-Cv, Ding C_src, alpha_Phi_K, transport, Core, or Gravity unlock",
        "claim_boundary": "This lane is a source comparator. It is not a source-reported volumetric alpha_V, not a same-state K_T pair, not Ding C_src, not alpha_Phi_K calibration, and not Full Topic 13 closure.",
    }

    artifact = {
        "schema_version": "t13-zenodo-ig210-alpha-l-source-audit-v1",
        "artifact": "t13_zenodo_ig210_alpha_l_source_audit",
        "generated_at": date.today().isoformat(),
        "status": major_result["verification_status"],
        "claim_promotion": False,
        "full_core_unlock": False,
        "major_result": major_result,
        "source": {
            "doi": source.get("doi"),
            "official_url": source.get("official_url"),
            "local_raw_path": source.get("local_raw_path"),
            "size_bytes": RAW.stat().st_size if RAW.is_file() else None,
            "md5": raw_md5,
            "sha256": raw_sha256,
        },
        "row_summary": {
            "count": len(rows),
            "temperature_min_C": min(row_temperatures) if row_temperatures else None,
            "temperature_max_C": max(row_temperatures) if row_temperatures else None,
            "quantity": "mean_linear_thermal_expansion_coefficient_alpha_l",
            "alpha_v_is_conditional": True,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "same_state_alpha_V_K_T_and_Ding_material_regime_mapping_missing",
        "next_controller": "source-lock a permitted same-specimen/state-matched alpha_V and isothermal K_T pair, or document a material-state map with uncertainty before using this comparator in Cp-to-Cv correction",
        "claim_boundary": major_result["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "passed_checks": sum(checks.values()), "total_checks": len(checks), "artifact": rel(OUT)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
