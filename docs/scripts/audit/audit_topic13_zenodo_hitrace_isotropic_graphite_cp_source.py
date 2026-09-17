"""Audit the Zenodo Hi-Trace same-block isotropic-graphite Cp comparator."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "zenodo_hitrace_isotropic_graphite_cp_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "zenodo_6091274_isotropic_graphite_specific_heat.xlsx"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_zenodo_hitrace_isotropic_graphite_cp_source_audit.json"
EXPECTED_RAW_MD5 = "6b9e617fb0266da9a5724d04eccb18b8"
EXPECTED_RAW_SHA256 = "c38e74d22c8b409b347b5d65384f0c172d4a43162ffffe7c2eba231f48d57020"
EXPECTED_RAW_SIZE = 27320


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
    by_lab = {}
    for row in rows:
        by_lab.setdefault(row["laboratory"], []).append(row)

    lne_rows = by_lab.get("LNE", [])
    ptb_rows = by_lab.get("PTB-ADEM", [])
    vinca_rows = by_lab.get("VINCA", [])
    raw_sha256 = digest(RAW) if RAW.is_file() else None
    raw_md5 = digest(RAW, "md5") if RAW.is_file() else None

    lne_uncertainty_checks = [
        math.isclose(
            row["uncertainty"]["value_J_per_kg_K"],
            row["value_J_per_kg_K"] * row["uncertainty"]["derived_relative_fraction"],
            rel_tol=0.0,
            abs_tol=1.0e-9,
        )
        and row["uncertainty"]["coverage_factor"] == 2
        and row["uncertainty"]["reported_relative_percent"] == 3.5
        for row in lne_rows
    ]
    ptb_uncertainty_checks = [
        math.isclose(
            row["uncertainty"]["value_J_per_kg_K"] / row["value_J_per_kg_K"],
            row["uncertainty"]["reported_relative_fraction"],
            rel_tol=0.0,
            abs_tol=1.0e-15,
        )
        and row["uncertainty"]["coverage_factor"] == 2
        for row in ptb_rows
    ]
    checks = {
        "raw_workbook_present": RAW.is_file(),
        "raw_workbook_size_matches": RAW.is_file() and RAW.stat().st_size == EXPECTED_RAW_SIZE,
        "raw_workbook_md5_matches": raw_md5 == EXPECTED_RAW_MD5,
        "raw_workbook_sha256_matches": raw_sha256 == EXPECTED_RAW_SHA256,
        "source_identity_and_locators_present": bool(
            source.get("doi")
            and source.get("official_url")
            and source.get("download_url")
            and len(source.get("source_locators", [])) >= 5
        ),
        "same_block_interlaboratory_scope_present": package["derived_comparator"][
            "same_block_material_claim"
        ]
        and package["derived_comparator"]["laboratory_count"] == 3,
        "all_numeric_rows_have_identity_and_units": len(rows) == 27
        and all(
            row.get("source_row_id")
            and row.get("sheet")
            and row.get("excel_row")
            and row.get("cell_range")
            and row.get("quantity") == "specific_heat_at_constant_pressure_Cp"
            and row.get("value_J_per_kg_K") is not None
            and row.get("temperature_K") is not None
            for row in rows
        ),
        "laboratory_row_counts_match_source_tables": len(lne_rows) == 10
        and len(ptb_rows) == 6
        and len(vinca_rows) == 11,
        "lne_expanded_uncertainty_reconstructed": all(lne_uncertainty_checks),
        "ptb_expanded_uncertainty_reconstructed": all(ptb_uncertainty_checks),
        "vinca_uncertainty_not_imputed": all(
            row.get("uncertainty") is None
            and row.get("uncertainty_status") == "NOT_REPORTED"
            for row in vinca_rows
        ),
        "quantity_boundary_is_cp_not_cv": package["derived_comparator"][
            "quantity_is_Cp_not_Cv"
        ]
        and package["derived_comparator"]["c_v_emitted"] is False,
        "no_unlicensed_density_or_elastic_conversion": package["derived_comparator"][
            "density_rows_present"
        ] is False
        and package["derived_comparator"]["alpha_V_and_K_T_rows_present"] is False,
        "ding_material_match_not_claimed": package["derived_comparator"][
            "material_match_to_Ding_TTG"
        ] is False,
        "not_calibration_or_fit": package["derived_comparator"][
            "calibration_record_emitted"
        ] is False
        and all(row["data_role"] == "COMPARISON_ONLY_NOT_CALIBRATION" for row in rows),
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False
        and package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "no_target_fit_or_alpha_fit": package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR"
        if passed
        else "FAIL_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_AUDIT"
    )
    result = {
        "schema_version": "t13-zenodo-hitrace-isotropic-graphite-cp-source-audit-v1",
        "artifact": "t13_zenodo_hitrace_isotropic_graphite_cp_source_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "Zenodo record identity, DOI, file locator, and local workbook hashes",
                "three-laboratory same-block isotropic-graphite Cp source package",
                "row-level identity for all 27 populated numeric source rows",
                "LNE and PTB expanded uncertainty transcription and reconstruction",
                "VINCA missing-uncertainty boundary without imputation",
                "high-temperature Cp-only comparator boundary from 1000 C to 2800 C",
            ],
            "equation_or_mapping": "C_p(T) is retained as mass-specific source data; c_v^V = rho*(C_p - T*alpha_V^2*K_T) is not evaluated",
            "units": {
                "temperature": "K and C",
                "C_p": "J kg^-1 K^-1",
                "expanded_uncertainty": "J kg^-1 K^-1, coverage factor k=2",
            },
            "derivation_class": "source transcription, row identity preservation, and uncertainty reconstruction from reported absolute Cp uncertainty",
            "observable": "same-block isotropic-graphite mass-specific heat-capacity comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(RAW), "sha256": raw_sha256, "md5": raw_md5},
            ],
            "verification_status": status,
            "open_blockers": [
                "c_v_source_uncertainty_not_closed",
                "density_uncertainty_not_source_locked",
                "same_grade_alpha_V_and_K_T_missing",
                "material_regime_mapping_to_Ding_TTG_not_closed",
                "independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["Zenodo Hi-Trace Cp source audit checks failed"],
            "dependency_unlocked": "This lane supplies a source-locked high-temperature Cp comparator only. It does not unlock c_v, Ding C_src, alpha_Phi_K, EOS, transport, Core, Gravity, or Galaxy dependencies.",
            "claim_boundary": "This is not c_v, not volumetric, not a Ding/HOPG/TTG source, not an alpha_Phi_K calibration, and not Full Topic 13 closure.",
        },
        "source": {
            **source,
            "local_hash_observed": raw_sha256,
            "local_md5_observed": raw_md5,
            "package_path": rel(PACKAGE),
            "package_sha256": digest(PACKAGE),
        },
        "source_rows": rows,
        "derived_comparator": package["derived_comparator"],
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "c_v_source_uncertainty_and_Ding_material_regime_mapping_missing",
        "next_controller": "Acquire source-grade same-state density, alpha_V, and K_T or direct volumetric c_v for the relevant material regime; keep this Cp comparator out of calibration and holdout paths.",
        "claim_boundary": "Source-locked high-temperature same-block isotropic-graphite Cp comparator only; it does not close c_v, Ding C_src, base-Phi SI mapping, alpha_Phi_K, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "raw_sha256": raw_sha256,
                "raw_md5": raw_md5,
                "row_count": len(rows),
                "uncertainty_bearing_row_count": sum(row.get("uncertainty") is not None for row in rows),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
