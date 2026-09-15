"""Audit a source-locked anisotropic TPG thermal-expansion comparator.

The IHEP report supplies separate in-plane and out-of-plane TPG slopes.  The
audit derives a family-level hexagonal alpha_V comparator while retaining the
fact that the two rows are not a same-specimen, same-point pair.  This lane
does not provide K_T, a Ding material match, or a UET calibration.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ihep_2001_32_tpg_anisotropic_alpha_v_source_package.json"
)
RAW_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ihep_2001_32_tpg_thermal_expansion.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"
EXPECTED_RAW_SHA256 = "e9527b8dba9d3944a1a9298e9d516e501279b500586cf0179ec076b94fdd6f2e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    source = package["source"]
    row = package["source_row"]
    derived = package["derived_comparator"]
    boundary = source["material_regime_boundary"]
    alpha_v = 2.0 * float(row["alpha_a_per_K"]) + float(row["alpha_c_per_K"])
    alpha_v_uncertainty = math.sqrt(
        (2.0 * float(row["alpha_a_uncertainty_per_K"])) ** 2
        + float(row["alpha_c_uncertainty_per_K"]) ** 2
    )
    actual_hash = digest(RAW_PATH) if RAW_PATH.is_file() else None
    checks = {
        "source_pdf_present": RAW_PATH.is_file(),
        "source_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "package_source_identity_present": bool(
            source.get("report") and source.get("record_url") and source.get("source_locators")
        ),
        "measurement_method_declared": "Pt100" in source.get("measurement_method", "")
        and "copper" in source.get("measurement_method", ""),
        "temperature_range_declared": row["temperature_range_C"] == [25.0, 60.0]
        and row["temperature_range_K"] == [298.15, 333.15],
        "linear_rows_have_units": all(
            isinstance(row[key], (int, float)) and math.isfinite(float(row[key]))
            for key in (
                "alpha_a_per_K",
                "alpha_a_uncertainty_per_K",
                "alpha_c_per_K",
                "alpha_c_uncertainty_per_K",
            )
        ),
        "source_rows_have_expected_signs": row["alpha_a_per_K"] < 0.0
        and row["alpha_c_per_K"] > 0.0,
        "anisotropic_alpha_volume_relation_explicit": "2*alpha_a + alpha_c"
        in package["major_result"]["equation_or_mapping"]["anisotropic_volumetric_expansion"],
        "alpha_v_reconstruction_matches_package": math.isclose(
            alpha_v, float(derived["alpha_V_per_K"]), rel_tol=0.0, abs_tol=1.0e-15
        ),
        "uncertainty_reconstruction_matches_package": math.isclose(
            alpha_v_uncertainty,
            float(derived["alpha_V_uncertainty_per_K"]),
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ),
        "mixed_row_boundary_is_explicit": boundary["same_specimen_for_both_axes"] is False
        and derived["same_specimen_alpha_V"] is False,
        "uncertainty_covariance_boundary_is_explicit": "zero-covariance" in package[
            "major_result"
        ]["equation_or_mapping"]["uncertainty_boundary"],
        "K_T_not_emitted": derived["K_T_emitted"] is False,
        "density_uncertainty_not_claimed": boundary["density_uncertainty_available"] is False,
        "same_state_Cp_Cv_not_claimed": boundary["same_state_Cp_Cv_available"] is False,
        "Ding_material_mapping_not_claimed": boundary[
            "ding_ttg_material_regime_mapping_closed"
        ] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_fit_not_performed": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_Phi_K_fit_not_performed": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-tpg-anisotropic-alpha-v-source-audit-v1",
        "artifact": "t13_tpg_anisotropic_alpha_v_source_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR"
        if passed
        else "FAIL_TPG_ANISOTROPIC_ALPHA_V_AUDIT",
        "major_result": {
            "major_result_id": "T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the IHEP 2001-32 primary report is archived with a reproducible local hash",
                "the ATOMGRAPH TPG in-plane and averaged TPG out-of-plane rows are source-locked with ranges and uncertainty",
                "the hexagonal alpha_V relation and zero-covariance comparator propagation are deterministic",
                "the mixed-row and non-Ding material boundary is retained instead of being promoted",
            ],
            "equation_or_mapping": {
                "anisotropic_volumetric_expansion": "alpha_V = 2*alpha_a + alpha_c",
                "uncertainty_propagation": "u(alpha_V) = sqrt((2*u(alpha_a))^2 + u(alpha_c)^2), zero covariance assumed only for comparator output",
                "temperature_scope": "source slopes over 25-60 deg C; not an exact 300 K point",
            },
            "units": {
                "temperature": "deg C source range and K mirror",
                "alpha_a": "K^-1",
                "alpha_c": "K^-1",
                "alpha_V": "K^-1",
            },
            "derivation_class": "source transcription plus anisotropic thermodynamic geometry conversion; no UET derivation",
            "observable": "TPG alpha_a, alpha_c, and family-level alpha_V comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_THERMODYNAMIC_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": PACKAGE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PACKAGE_PATH)},
                {"path": RAW_PATH.relative_to(ROOT).as_posix(), "sha256": actual_hash},
            ],
            "verification_status": "PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR"
            if passed
            else "FAIL_TPG_ANISOTROPIC_ALPHA_V_AUDIT",
            "open_blockers": [
                "in_plane_and_out_of_plane_rows_are_not_a_same_specimen_pair",
                "same_state_density_uncertainty_and_Cp_Cv_are_not_source_locked",
                "TPG_to_Ding_TTG_material_regime_mapping_is_not_closed",
                "base_Phi_to_thermal_observable_map_and_independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["IHEP TPG alpha_V source checks failed"],
            "dependency_unlocked": "declared TPG anisotropic alpha_V comparator lane only; no same-grade K_T, Ding C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This closes only a source-traceable TPG family-level alpha_V comparator. It is not a same-specimen volumetric measurement, not a Ding TTG match, not a complete Cp-to-Cv correction, and not an alpha_Phi_K calibration.",
        },
        "source": {
            **source,
            "local_hash_observed": actual_hash,
            "package_path": PACKAGE_PATH.relative_to(ROOT).as_posix(),
            "package_sha256": digest(PACKAGE_PATH),
        },
        "source_row": row,
        "derived_comparator": {
            **derived,
            "alpha_V_reconstructed_per_K": alpha_v,
            "alpha_V_uncertainty_reconstructed_per_K": alpha_v_uncertainty,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "same_specimen_alpha_V_K_T_and_Ding_material_regime_mapping_missing",
        "next_controller": "Obtain a same-state, same-specimen alpha_V/K_T pair or a permitted direct volumetric heat-capacity route; keep this TPG family comparator separate from Ding C_src and base-Phi calibration.",
        "claim_boundary": "This closes only a source-traceable TPG anisotropic alpha_V comparator lane. It does not close same-grade K_T, Ding C_src, e0, base Phi, alpha_Phi_K, transport, SK/KMS, entropy, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "raw_sha256": actual_hash,
                "alpha_V_per_K": alpha_v,
                "alpha_V_uncertainty_per_K": alpha_v_uncertainty,
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
