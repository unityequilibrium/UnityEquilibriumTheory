"""Audit the source-locked NPL IG-11 graphite c_p comparator lane."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "npl_rsa40_graphite_specific_heat_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "npl_rsa40_graphite_specific_heat.pdf"
)
OUT = ROOT / "docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json"
EXPECTED_RAW_SHA256 = "aabe560c3e4e012e606b2d87facb67600653a781c4b46c8fde986f3fd9fa28f1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    rows = {row["source_row_id"]: row for row in package["source_rows"]}
    cp_row = rows["npl_rsa40_ig11_cp_295_15K"]
    density_row = rows["npl_rsa40_ig11_density_nominal"]
    uncertainty_row = rows["npl_rsa40_combined_relative_uncertainty"]
    actual_hash = digest(RAW) if RAW.is_file() else None
    cp = float(cp_row["value_J_per_kg_K"])
    sigma_cp = float(cp_row["standard_uncertainty_J_per_kg_K"])
    nominal_density = float(density_row["value_kg_per_m3"])
    nominal_volumetric_cp = cp * nominal_density
    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_signature_present": RAW.is_file() and RAW.read_bytes()[:5] == b"%PDF-",
        "raw_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "raw_size_matches_package": RAW.is_file()
        and RAW.stat().st_size == source["local_raw_size_bytes"],
        "report_identity_and_locators_present": bool(
            source.get("report")
            and source.get("official_url")
            and len(source.get("source_locators", [])) >= 4
        ),
        "material_identity_is_explicit": source["material_identity"]["grade"] == "IG 11"
        and source["material_identity"]["supplier"] == "Southern Graphite"
        and source["material_identity"]["ding_ttg_match"] is False,
        "cp_row_units_and_uncertainty_present": cp > 0.0 and sigma_cp > 0.0,
        "cp_row_is_at_reference_temperature": cp_row["temperature_K"] == 295.15
        and cp_row["temperature_C"] == 22.0,
        "source_equation_is_preserved": "710.6+3.0" in cp_row["source_equation"],
        "uncertainty_budget_is_preserved": uncertainty_row["value"] == 0.00096
        and uncertainty_row["reported_units"] == "relative",
        "nominal_mass_to_volume_crosscheck_is_reproducible": math.isclose(
            cp * nominal_density,
            float(package["derived_comparator"]["nominal_volumetric_cp_J_per_m3_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        ),
        "volumetric_cp_not_emitted_without_density_uncertainty": package[
            "derived_comparator"
        ]["volumetric_cp_emitted"] is False,
        "cv_and_alpha_not_emitted": package["derived_comparator"]["cv_emitted"] is False
        and package["derived_comparator"]["alpha_Phi_K_emitted"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False
        and package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "no_fit_or_target_used": package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_NPL_CP_UNCERTAINTY_COMPARATOR_CV_OPEN"
        if passed
        else "FAIL_NPL_RSA40_GRAPHITE_SPECIFIC_HEAT_AUDIT"
    )
    result = {
        "schema_version": "t13-npl-rsa40-graphite-specific-heat-audit-v1",
        "artifact": "t13_npl_rsa40_graphite_specific_heat_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_NPL_GRAPHITE_CP_UNCERTAINTY_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "official NPL RSA(EXT)40 report identity and local PDF hash",
                "Southern Graphite IG-11 sample identity and nominal density metadata",
                "source-reported mass-specific c_p at 295.15 K with standard uncertainty",
                "source-reported 19-25 deg C scope and combined relative uncertainty budget",
                "explicit boundary that nominal c_p times density is not emitted as an uncertainty-grade volumetric c_p",
            ],
            "equation_or_mapping": "c_p,g(T,H)=710.6+3.0*(T-22 deg C) J kg^-1 K^-1; c_p^V=rho*c_p only as a nominal cross-check; c_v^V=c_p^V-T*alpha_V^2*K_T remains open",
            "units": {
                "c_p": "J kg^-1 K^-1",
                "rho": "kg m^-3",
                "nominal_c_p_volumetric_crosscheck": "J m^-3 K^-1",
                "alpha_V": "K^-1",
                "K_T": "Pa = J m^-3",
            },
            "derivation_class": "source transcription plus nominal unit conversion cross-check; no UET derivation",
            "observable": "IG-11 graphite mass-specific heat-capacity comparator with source-reported uncertainty",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(RAW), "sha256": actual_hash},
            ],
            "verification_status": status,
            "open_blockers": [
                "c_v_source_uncertainty_not_closed",
                "same_grade_alpha_V_and_K_T_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ]
            if passed
            else ["NPL source audit checks failed"],
            "dependency_unlocked": "NPL IG-11 mass-specific c_p comparator with source uncertainty only; no volumetric c_v, Ding C_src, alpha calibration, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes a source-traceable NPL IG-11 c_p comparator lane. It is not c_v, not Ding/HOPG TTG validation, not an independent alpha_Phi_K calibration, and not Full Topic 13 closure.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": rel(PACKAGE),
            "package_sha256": digest(PACKAGE),
        },
        "source_rows": package["source_rows"],
        "derived_comparator": {
            **package["derived_comparator"],
            "nominal_volumetric_cp_reconstructed_J_per_m3_K": nominal_volumetric_cp,
        },
        "checks": checks,
        "numeric_cp_emitted": True,
        "nominal_volumetric_cp_emitted": True,
        "uncertainty_grade_volumetric_cp_emitted": False,
        "cv_emitted": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "c_v_conversion_density_uncertainty_and_Ding_material_mapping_missing",
        "next_controller": "Acquire same-regime alpha_V and K_T or a direct volumetric c_v source with uncertainty; keep this c_p comparator out of calibration and holdout paths.",
        "claim_boundary": "Source-locked NPL IG-11 mass-specific c_p comparator only; it does not close c_v, Ding C_src, base-Phi SI mapping, alpha_Phi_K, or Full Topic 13.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "raw_sha256": actual_hash,
                "cp_J_per_kg_K": cp,
                "cp_standard_uncertainty_J_per_kg_K": sigma_cp,
                "nominal_volumetric_cp_J_per_m3_K": nominal_volumetric_cp,
                "failed_checks": [key for key, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
