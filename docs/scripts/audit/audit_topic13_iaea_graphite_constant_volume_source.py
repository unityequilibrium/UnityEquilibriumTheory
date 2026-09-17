"""Audit the IAEA manufactured-graphite table-derived c_v comparator lane."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_graphite_handbook_constant_volume_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "iaea_graphite_handbook_2017.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_graphite_constant_volume_source_audit.json"
EXPECTED_RAW_SHA256 = "91e9d84e5d1828ab1028bf0e5fec0743fe1fb49e416b9e6305edf2f71a30a28a"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    row = package["source_row"]
    derived = package["derived_comparator"]
    cp = float(row["cp_cal_per_g_K"])
    delta_cp = float(row["delta_cp_cal_per_g_K"])
    cw = float(row["cw_cal_per_g_K"])
    ce = float(row["ce_cal_per_g_K"])
    cv = cp - cw - ce
    conversion = float(derived["calorie_to_joule_J_per_cal"])
    cv_mass = cv * conversion * 1000.0
    cp_mass = cp * conversion * 1000.0
    correction_mass = (cw + ce) * conversion * 1000.0
    actual_hash = digest(RAW) if RAW.is_file() else None
    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "raw_size_matches_package": RAW.is_file()
        and RAW.stat().st_size == source["local_raw_size_bytes"],
        "source_identity_and_locators_present": bool(
            source.get("publisher")
            and source.get("official_url")
            and len(source.get("source_locators", [])) == 3
        ),
        "table_row_is_at_300K": row["temperature_K"] == 300.0,
        "formula_is_explicit": row["cv_formula"] == "c_v = c_p - c_w - c_e",
        "cv_reconstruction_matches_package": math.isclose(
            cv, float(row["cv_cal_per_g_K"]), rel_tol=0.0, abs_tol=1.0e-12
        ),
        "cp_to_cv_correction_matches_package": math.isclose(
            cp - cv, cw + ce, rel_tol=0.0, abs_tol=1.0e-12
        ),
        "cv_mass_conversion_matches_package": math.isclose(
            cv_mass, float(derived["cv_mass_J_per_kg_K"]), rel_tol=0.0, abs_tol=1.0e-9
        ),
        "cp_mass_conversion_matches_package": math.isclose(
            cp_mass, float(derived["cp_mass_J_per_kg_K"]), rel_tol=0.0, abs_tol=1.0e-9
        ),
        "correction_conversion_matches_package": math.isclose(
            correction_mass,
            float(derived["cp_minus_cv_mass_J_per_kg_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        ),
        "probable_error_not_promoted_to_standard_uncertainty": row[
            "source_uncertainty_boundary"
        ]["cv_standard_uncertainty"] is None,
        "cv_volumetric_not_emitted": derived["cv_volumetric_emitted"] is False,
        "density_not_emitted": derived["density_emitted"] is False,
        "material_match_not_claimed": derived["material_match_to_Ding_TTG"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "no_fit_or_alpha_calibration": package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_IAEA_TABLE_CV_COMPARATOR_UNCERTAINTY_OPEN"
        if passed
        else "FAIL_IAEA_GRAPHITE_CV_AUDIT"
    )
    equation = "c_p = c_v + c_w + c_e; c_v = c_p - c_w - c_e"
    result = {
        "schema_version": "t13-iaea-graphite-cv-source-audit-v1",
        "artifact": "t13_iaea_graphite_constant_volume_source_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "IAEA-hosted Graphite Engineering Handbook identity and archived raw PDF hash",
                "Table 4.11 manufactured-graphite 300 K cp, delta-cp, cw, and ce row",
                "the table-derived mass-specific lattice cv relation",
                "the boundary between probable error in cp and standard uncertainty for cv",
                "the non-equivalence of this manufactured-graphite average curve to Ding TTG material",
            ],
            "equation_or_mapping": equation,
            "units": {
                "cp": "cal g^-1 K^-1 in source; J kg^-1 K^-1 after declared 4.184 conversion",
                "cw": "cal g^-1 K^-1",
                "ce": "cal g^-1 K^-1",
                "cv": "cal g^-1 K^-1 in source; J kg^-1 K^-1 after declared 4.184 conversion",
            },
            "derivation_class": "source table transcription plus declared algebraic separation of lattice, thermoelastic, and electronic terms; no UET derivation",
            "observable": "manufactured-graphite mass-specific lattice c_v comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(RAW), "sha256": actual_hash},
            ],
            "verification_status": status,
            "open_blockers": [
                "c_v_standard_uncertainty_not_reported",
                "same-grade density and volumetric conversion not source_locked",
                "material_regime_mapping_to_Ding_TTG_not_closed",
                "independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["IAEA source audit checks failed"],
            "dependency_unlocked": "Table-derived manufactured-graphite mass-specific c_v comparator only; no volumetric c_v, Ding C_src, alpha calibration, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes a source-traceable table-derived mass-specific lattice c_v comparator lane. It does not provide a source-grade c_v uncertainty, volumetric c_v, Ding TTG material match, alpha_Phi_K, or Full Topic 13 closure.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": rel(PACKAGE),
            "package_sha256": digest(PACKAGE),
        },
        "source_row": row,
        "derived_comparator": {
            **derived,
            "cv_reconstructed_cal_per_g_K": cv,
            "cv_mass_reconstructed_J_per_kg_K": cv_mass,
            "cp_mass_reconstructed_J_per_kg_K": cp_mass,
            "cp_minus_cv_mass_reconstructed_J_per_kg_K": correction_mass,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "cv_uncertainty_density_volumetric_conversion_and_Ding_material_regime_mapping_missing",
        "next_controller": "Acquire a source-grade cv uncertainty and same-grade density or direct volumetric cv record; keep the table-derived comparator out of calibration and holdout paths.",
        "claim_boundary": "Source-locked IAEA table-derived manufactured-graphite mass-specific lattice c_v comparator only; it does not close volumetric c_v, Ding C_src, base-Phi SI mapping, alpha_Phi_K, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": rel(OUT), "raw_sha256": actual_hash, "cv_cal_per_g_K": cv, "cv_mass_J_per_kg_K": cv_mass}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
