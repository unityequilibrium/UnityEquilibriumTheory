"""Audit the IAEA GR-280 same-state Cp and density comparator lane."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_gr280_same_state_cp_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "iaea_thermophysical_properties_web.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_gr280_same_state_cp_source_audit.json"
EXPECTED_RAW_SHA256 = "bdb8454de8bdadf83ecdb1794621180651bcf00108f1214f8f3a82193c05976b"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    source = package["source"]
    rows = {row["source_row_id"]: row for row in package["source_rows"]}
    cp_row = rows["iaea_gr280_cp_table_4_4_300C"]
    density_row = rows["iaea_gr280_density_table_4_6_300C"]
    temperature_K = float(cp_row["temperature_K_source"])
    cp = float(cp_row["value_J_per_kg_K"])
    density = float(density_row["value_kg_per_m3"])
    relative_uncertainty = 0.10 + (temperature_K - 500.0) * (0.05 - 0.10) / (800.0 - 500.0)
    cp_uncertainty = cp * relative_uncertainty
    cp_volume = cp * density
    cp_volume_uncertainty = cp_uncertainty * density
    derived = package["derived_comparator"]
    actual_hash = digest(RAW) if RAW.is_file() else None
    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "raw_size_matches_package": RAW.is_file()
        and RAW.stat().st_size == source["local_raw_size_bytes"],
        "source_identity_and_locators_present": bool(
            source.get("publisher")
            and source.get("official_url")
            and len(source.get("source_locators", [])) >= 4
        ),
        "cp_row_is_300C_573K": cp_row["temperature_C"] == 300.0
        and cp_row["temperature_K_source"] == 573.0,
        "density_row_is_300C": density_row["temperature_C"] == 300.0,
        "same_state_rows_are_explicit": package["derived_comparator"][
            "same_state_cp_density_rows"
        ]
        and cp_row["temperature_C"] == density_row["temperature_C"],
        "cp_uncertainty_interpolation_matches_package": math.isclose(
            relative_uncertainty,
            float(cp_row["source_uncertainty"]["relative_fraction"]),
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ),
        "cp_volume_reconstruction_matches_package": math.isclose(
            cp_volume,
            float(derived["cp_volumetric_J_per_m3_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        ),
        "cp_volume_uncertainty_reconstruction_matches_package": math.isclose(
            cp_volume_uncertainty,
            float(derived["cp_volumetric_cp_only_uncertainty_J_per_m3_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-9,
        ),
        "density_standard_uncertainty_not_invented": derived[
            "density_standard_uncertainty_reported"
        ]
        is False
        and derived["cp_volumetric_standard_uncertainty_J_per_m3_K"] is None,
        "cv_not_emitted": derived["c_v_emitted"] is False,
        "alpha_and_KT_not_emitted": derived["alpha_V_and_K_T_emitted"] is False,
        "material_match_not_claimed": derived["material_match_to_Ding_TTG"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"][
            "xie_2026_source_data_consumed"
        ]
        is False,
        "no_fit_or_alpha_calibration": package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_IAEA_GR280_SAME_STATE_CP_COMPARATOR"
        if passed
        else "FAIL_IAEA_GR280_SAME_STATE_CP_AUDIT"
    )
    result = {
        "schema_version": "t13-iaea-gr280-same-state-cp-source-audit-v1",
        "artifact": "t13_iaea_gr280_same_state_cp_source_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "same_state_cp_and_density_rows": bool(
            passed and package["derived_comparator"]["same_state_cp_density_rows"]
        ),
        "major_result": {
            "major_result_id": "T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "IAEA-THPH identity, official locator, and archived raw PDF hash",
                "GR-280 300 C / 573 K Cp row from Table 4.4",
                "GR-280 300 C density row from Table 4.6",
                "same-state Cp-density availability boundary",
                "conditional Cp-only volumetric conversion and uncertainty propagation",
                "the boundary that published density precision is not a standard uncertainty",
                "the non-equivalence of reactor graphite GR-280 to Ding HOPG/TTG",
            ],
            "equation_or_mapping": "C_p^V = rho*C_p; u(C_p^V | rho fixed) = rho*u(C_p); c_v^V = C_p^V - T*alpha_V^2*K_T",
            "units": {
                "C_p": "J kg^-1 K^-1",
                "rho": "kg m^-3",
                "C_p^V": "J m^-3 K^-1",
                "u(C_p^V | rho fixed)": "J m^-3 K^-1",
                "alpha_V": "K^-1",
                "K_T": "Pa = J m^-3",
            },
            "derivation_class": "source transcription plus same-temperature row matching, mass-to-volume conversion, and conditional one-input uncertainty propagation",
            "observable": "reactor-graphite same-state volumetric Cp comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(RAW), "sha256": actual_hash},
            ],
            "verification_status": status,
            "open_blockers": [
                "density_standard_uncertainty_not_reported",
                "c_v_source_uncertainty_not_closed",
                "same_grade_alpha_V_and_K_T_missing",
                "material_regime_mapping_to_Ding_TTG_not_closed",
                "independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["IAEA GR-280 same-state Cp audit checks failed"],
            "dependency_unlocked": "The full gate may close only the availability sub-blocker for a same-state Cp source; no Ding C_src, c_v uncertainty, alpha calibration, transport, Core, Gravity, or Galaxy dependency is unlocked.",
            "claim_boundary": "This closes a source-traceable same-state reactor-graphite Cp and density comparator lane. It is not a direct volumetric measurement, not source-grade density uncertainty, not c_v, not Ding TTG C_src, not alpha_Phi_K calibration, and not Full Topic 13 closure.",
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
            "cp_relative_uncertainty_reconstructed": relative_uncertainty,
            "cp_uncertainty_reconstructed_J_per_kg_K": cp_uncertainty,
            "cp_volumetric_reconstructed_J_per_m3_K": cp_volume,
            "cp_volumetric_cp_only_uncertainty_reconstructed_J_per_m3_K": cp_volume_uncertainty,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "density_standard_uncertainty_c_v_and_Ding_material_regime_mapping_missing",
        "next_controller": "Acquire a source-grade density uncertainty or direct same-state volumetric c_v record, then match alpha_V and K_T to the same specimen and material regime; keep this comparator out of calibration and holdout paths.",
        "claim_boundary": "Source-locked IAEA GR-280 same-state Cp and density comparator only; it does not close c_v, Ding C_src, base-Phi SI mapping, alpha_Phi_K, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": rel(OUT),
                "raw_sha256": actual_hash,
                "same_state_cp_density_rows": result["same_state_cp_and_density_rows"],
                "cp_volumetric_J_per_m3_K": cp_volume,
                "cp_volumetric_cp_only_uncertainty_J_per_m3_K": cp_volume_uncertainty,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
