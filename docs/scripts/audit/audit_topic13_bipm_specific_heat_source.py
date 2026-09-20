"""Audit the source-locked BIPM graphite c_p comparator lane."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "bipm_2006_01_graphite_specific_heat_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "bipm_2006_01_graphite_specific_heat.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_bipm_specific_heat_source_audit.json"
EXPECTED_RAW_SHA256 = "2c491c94adb3f70f4b1ba915259f0a1d2f4788e072e99c8d34a87f964f69ce42"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    rows = {row["source_row_id"]: row for row in package["source_rows"]}
    cp_row = rows["bipm_2006_01_sample_h_cp_22C"]
    rho_row = rows["bipm_2006_01_graphite_density_mean"]
    cp = float(cp_row["value_J_per_kg_K"])
    sigma_cp = float(cp_row["standard_uncertainty_J_per_kg_K"])
    rho = float(rho_row["value_kg_per_m3"])
    sigma_rho = float(rho_row["standard_uncertainty_kg_per_m3"])
    cp_volume = rho * cp
    sigma_cp_volume = cp_volume * math.sqrt(
        (sigma_cp / cp) ** 2 + (sigma_rho / rho) ** 2
    )
    derived = package["derived_comparator"]
    actual_hash = digest(RAW) if RAW.is_file() else None
    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "raw_size_matches_package": RAW.is_file()
        and RAW.stat().st_size == source["local_raw_size_bytes"],
        "report_identity_and_locators_present": bool(
            source.get("report")
            and source.get("official_url")
            and source.get("archived_mirror_url")
            and len(source.get("source_locators", [])) >= 3
        ),
        "cp_row_units_and_uncertainty_present": cp_row["value_J_per_kg_K"] > 0
        and cp_row["standard_uncertainty_J_per_kg_K"] > 0,
        "density_row_units_and_uncertainty_present": rho_row["value_kg_per_m3"] > 0
        and rho_row["standard_uncertainty_kg_per_m3"] > 0,
        "reported_temperature_is_inside_fit_scope": 19.0
        <= cp_row["temperature_C"]
        <= 25.0,
        "volumetric_cp_reconstruction_matches_package": math.isclose(
            cp_volume,
            float(derived["volumetric_cp_J_per_m3_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        ),
        "volumetric_cp_uncertainty_reconstruction_matches_package": math.isclose(
            sigma_cp_volume,
            float(derived["volumetric_cp_standard_uncertainty_J_per_m3_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-3,
        ),
        "cv_not_emitted": derived["cv_emitted"] is False,
        "alpha_and_KT_not_emitted": derived["alpha_V_emitted"] is False
        and derived["K_T_emitted"] is False,
        "material_match_not_claimed": derived["material_match_to_Ding_TTG"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "no_fit_or_alpha_calibration": package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
    }
    passed = all(checks.values())
    status = "PASS_SCOPED_BIPM_CP_COMPARATOR_CV_OPEN" if passed else "FAIL_BIPM_SPECIFIC_HEAT_AUDIT"
    equation = "c_p^V = rho*c_p; c_v^V = c_p^V - T*alpha_V^2*K_T"
    result = {
        "schema_version": "t13-bipm-specific-heat-source-audit-v1",
        "artifact": "t13_bipm_specific_heat_source_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "BIPM-2006/01 primary report identity and archived raw PDF hash",
                "source-reported sample-H mass-specific cp at 22 deg C with standard uncertainty",
                "same-report density mean and standard uncertainty",
                "volumetric cp comparator and first-order uncertainty propagation",
                "explicit boundary that this source does not provide cv without alpha_V and K_T",
            ],
            "equation_or_mapping": equation,
            "units": {
                "c_p": "J kg^-1 K^-1",
                "rho": "kg m^-3",
                "c_p^V": "J m^-3 K^-1",
                "alpha_V": "K^-1",
                "K_T": "Pa = J m^-3",
            },
            "derivation_class": "source transcription plus standard mass-to-volume conversion and independent first-order uncertainty propagation",
            "observable": "ultra-pure graphite volumetric c_p comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(RAW), "sha256": actual_hash},
            ],
            "verification_status": status,
            "open_blockers": [
                "alpha_V_and_K_T_not_source_locked_for_this_specimen",
                "c_v_source_uncertainty_not_closed",
                "material_regime_mapping_to_Ding_TTG_not_closed",
                "independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["BIPM source audit checks failed"],
            "dependency_unlocked": "BIPM source-locked graphite volumetric c_p comparator only; no c_v, Ding C_src, alpha calibration, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes a source-traceable standard graphite c_p comparator lane. It is not a same-state Ding/HOPG source, not c_v, not an alpha_Phi_K calibration, and not Full Topic 13 closure.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": rel(PACKAGE),
            "package_sha256": digest(PACKAGE),
        },
        "source_rows": package["source_rows"],
        "derived_comparator": {
            **derived,
            "volumetric_cp_reconstructed_J_per_m3_K": cp_volume,
            "volumetric_cp_standard_uncertainty_reconstructed_J_per_m3_K": sigma_cp_volume,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "alpha_V_K_T_c_v_and_Ding_material_regime_mapping_missing",
        "next_controller": "Source-lock same-regime alpha_V and K_T or acquire a direct volumetric c_v source; keep this c_p comparator out of calibration and holdout paths.",
        "claim_boundary": "Source-locked BIPM ultra-pure graphite volumetric c_p comparator only; it does not close c_v, Ding C_src, base-Phi SI mapping, alpha_Phi_K, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": rel(OUT), "raw_sha256": actual_hash, "volumetric_cp_J_per_m3_K": cp_volume, "volumetric_cp_standard_uncertainty_J_per_m3_K": sigma_cp_volume}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
