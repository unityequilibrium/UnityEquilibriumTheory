"""Propagate the source-reported IG-210 uncertainty into volumetric C_p.

This is a standard-physics comparator lane only. It deliberately stops at
``C_p^V = rho * C_p`` and does not infer ``C_v``, ``K_T``, Ding ``C_src``, or
any UET calibration quantity.
"""

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
OUT = ROOT / "docs/core/artifacts/t13_farooqui_ig210_volumetric_cp_uncertainty_audit.json"


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def close(first: float, second: float) -> bool:
    return math.isclose(first, second, rel_tol=0.0, abs_tol=1.0e-9)


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    source_rows = package["source_rows"]
    derived_rows = []
    row_checks = []

    for row in source_rows:
        rho = float(row["density_kg_per_m3"])
        cp = float(row["specific_heat_Cp_J_per_kg_K"])
        rho_u = float(row["uncertainty"]["density_relative_expanded"])
        cp_u = float(row["uncertainty"]["specific_heat_relative_expanded"])
        cp_volume = rho * cp

        # Use interval endpoints instead of a quadrature combination. This
        # remains conservative when the source does not publish covariance.
        lower = rho * (1.0 - rho_u) * cp * (1.0 - cp_u)
        upper = rho * (1.0 + rho_u) * cp * (1.0 + cp_u)
        lower_relative = (cp_volume - lower) / cp_volume
        upper_relative = (upper - cp_volume) / cp_volume
        derived_rows.append(
            {
                "source_row_id": row["source_row_id"],
                "table_locator": row["table_locator"],
                "temperature_K": float(row["temperature_K"]),
                "density_kg_per_m3": rho,
                "specific_heat_Cp_J_per_kg_K": cp,
                "volumetric_Cp_J_per_m3_K": cp_volume,
                "conservative_expanded_interval_J_per_m3_K": {
                    "lower": lower,
                    "upper": upper,
                },
                "relative_interval_fraction": {
                    "lower": lower_relative,
                    "upper": upper_relative,
                },
                "uncertainty_contract": {
                    "source_coverage_factor": row["uncertainty"]["coverage_factor"],
                    "density_relative_expanded": rho_u,
                    "specific_heat_relative_expanded": cp_u,
                    "combination": "conservative rectangular product bounds; covariance not assumed",
                    "standard_uncertainty_emitted": False,
                },
                "data_role": "EXTERNAL_SOURCE_COMPARATOR_NOT_CALIBRATION",
            }
        )
        row_checks.append(
            rho > 0.0
            and cp > 0.0
            and 0.0 < rho_u < 1.0
            and 0.0 < cp_u < 1.0
            and lower < cp_volume < upper
            and close(lower, rho * (1.0 - rho_u) * cp * (1.0 - cp_u))
            and close(upper, rho * (1.0 + rho_u) * cp * (1.0 + cp_u))
        )

    checks = {
        "source_package_present": PACKAGE.is_file(),
        "raw_source_present": RAW.is_file(),
        "raw_source_hash_matches": RAW.is_file()
        and digest(RAW) == source["local_raw_sha256"],
        "raw_source_size_matches": RAW.is_file()
        and RAW.stat().st_size == source["local_raw_size_bytes"],
        "same_grade_ig210_rows_present": source.get("material")
        == "IG-210 grade isotropic graphite from Toyo Tanso"
        and len(source_rows) == 3,
        "source_row_locators_present": all(
            row.get("table_locator") for row in source_rows
        ),
        "source_expanded_uncertainty_is_preserved": all(
            row.get("uncertainty", {}).get("coverage_factor") == 2
            and row.get("uncertainty", {}).get("density_relative_expanded") == 0.003
            and row.get("uncertainty", {}).get("specific_heat_relative_expanded")
            == 0.06
            for row in source_rows
        ),
        "volumetric_cp_unit_conversion_is_closed": all(row_checks),
        "interval_propagation_is_conservative": all(
            row["conservative_expanded_interval_J_per_m3_K"]["lower"]
            < row["volumetric_Cp_J_per_m3_K"]
            < row["conservative_expanded_interval_J_per_m3_K"]["upper"]
            for row in derived_rows
        ),
        "cp_is_not_relabelled_as_cv": package["derived_comparator"]["c_v_present"]
        is False,
        "kt_remains_open": package["derived_comparator"]["same_state_K_T_present"]
        is False,
        "ding_material_match_remains_open": package["derived_comparator"][
            "Ding_TTG_material_match_closed"
        ]
        is False,
        "alpha_is_not_emitted": package["derived_comparator"][
            "alpha_Phi_K_calibration_emitted"
        ]
        is False,
        "no_fit_or_holdout_access": package["preprocessing"]["fit_or_tuning"] == "none"
        and package["holdout_policy"]["xie_2026_accessed"] is False
        and package["holdout_policy"]["calibration_path_may_read_holdout"] is False,
    }
    passed = all(checks.values())
    major_result = {
        "major_result_id": "T13_FAROOQUI_IG210_VOLUMETRIC_CP_UNCERTAINTY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "source-locked IG-210 density and specific-heat rows are converted to volumetric C_p",
            "conservative expanded intervals are propagated without assuming covariance",
            "C_p is kept distinct from C_v, Ding C_src, Phi, and alpha_Phi_K",
        ],
        "what_remains_open": [
            "same_state_IG210_isothermal_K_T_missing",
            "C_p_to_C_v_correction_not_closed",
            "Ding_TTG_material_regime_mapping_not_closed",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "IG-210 volumetric C_p comparator and uncertainty contract only; no C_v, Ding C_src, alpha_Phi_K, transport, Core, or Gravity unlock",
        "equation_or_mapping": {
            "volumetric_heat_capacity": "C_p^V = rho * C_p",
            "lower_bound": "C_p^V,low = rho*(1-u_rho)*C_p*(1-u_Cp)",
            "upper_bound": "C_p^V,high = rho*(1+u_rho)*C_p*(1+u_Cp)",
            "not_emitted": "C_v^V = C_p^V - T*alpha_V^2*K_T",
        },
        "units": {
            "density": "kg m^-3",
            "specific_heat": "J kg^-1 K^-1",
            "volumetric_specific_heat": "J m^-3 K^-1",
            "temperature": "K",
            "uncertainty": "source-reported expanded interval, k=2",
        },
        "derivation_class": "source-backed standard-physics unit conversion plus conservative interval propagation; no UET derivation",
        "observable": "IG-210 volumetric constant-pressure heat-capacity comparator",
        "data_role": "EXTERNAL_SOURCE_COMPARATOR_NOT_CALIBRATION",
        "evidence_artifacts": [
            {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
            {"path": rel(RAW), "sha256": digest(RAW)},
        ],
        "verification_status": (
            "PASS_SCOPED_FAROOQUI_IG210_VOLUMETRIC_CP_UNCERTAINTY"
            if passed
            else "FAIL_FAROOQUI_IG210_VOLUMETRIC_CP_UNCERTAINTY"
        ),
        "controlling_blocker": "same_state_IG210_isothermal_K_T_missing",
        "claim_boundary": "This closes only a source-traceable IG-210 volumetric C_p comparator with conservative source-expanded bounds. It is not C_v, not Ding C_src, not alpha_Phi_K calibration, not a UET transport coefficient, and not Full Topic 13 closure.",
    }
    artifact = {
        "schema_version": "t13-farooqui-ig210-volumetric-cp-uncertainty-v1",
        "artifact": "t13_farooqui_ig210_volumetric_cp_uncertainty_audit",
        "generated_at": date.today().isoformat(),
        "status": major_result["verification_status"],
        "claim_promotion": False,
        "full_core_unlock": False,
        "major_result": major_result,
        "source": {
            "source_id": source["source_id"],
            "official_url": source["official_url"],
            "local_raw_path": source["local_raw_path"],
            "local_raw_sha256": source["local_raw_sha256"],
            "local_raw_size_bytes": source["local_raw_size_bytes"],
        },
        "derived_rows": derived_rows,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "alpha_Phi_K_fit_used": False,
        },
        "numeric_alpha_Phi_K_emitted": False,
        "numeric_C_v_emitted": False,
        "numeric_Ding_C_src_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "controlling_blocker": "same_state_IG210_isothermal_K_T_missing",
        "next_controller": "Source-lock a same-state IG-210 isothermal K_T record before applying the C_p-to-C_v correction; do not use this comparator to calibrate Phi or alpha_Phi_K.",
        "claim_boundary": major_result["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "passed_checks": sum(checks.values()),
                "total_checks": len(checks),
                "artifact": rel(OUT),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
