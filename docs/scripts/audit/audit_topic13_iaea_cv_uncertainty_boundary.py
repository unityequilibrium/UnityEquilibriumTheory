"""Audit the IAEA table-derived c_v uncertainty and volumetric boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_graphite_cv_uncertainty_boundary_source_package.json"
)
CV_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "iaea_graphite_handbook_constant_volume_source_package.json"
)
RAW = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "iaea_graphite_handbook_2017.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_iaea_cv_uncertainty_boundary_audit.json"
EXPECTED_RAW_SHA256 = "91e9d84e5d1828ab1028bf0e5fec0743fe1fb49e416b9e6305edf2f71a30a28a"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    cv_package = json.loads(CV_PACKAGE.read_text(encoding="utf-8-sig"))
    observations = package["boundary_observations"]
    mapping = package["mapping_contract"]
    actual_hash = digest(RAW) if RAW.is_file() else None
    checks = {
        "raw_pdf_present": RAW.is_file(),
        "raw_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "raw_size_matches_package": RAW.is_file()
        and RAW.stat().st_size == package["source"]["local_raw_size_bytes"],
        "source_identity_and_locators_present": bool(
            package["source"].get("publisher")
            and package["source"].get("official_url")
            and len(package["source"].get("source_locators", [])) >= 5
        ),
        "table_row_source_locked": observations["table_row_is_source_locked"] is True,
        "probable_error_not_promoted": observations["delta_cp_is_standard_uncertainty"] is False,
        "cw_uncertainty_not_invented": observations["cw_uncertainty_is_source_locked"] is False,
        "rough_compressibility_boundary_recorded": observations[
            "high_temperature_compressibility_is_explicitly_rough"
        ] is True,
        "same_row_density_uncertainty_missing_recorded": observations[
            "same_table_row_density_with_uncertainty"
        ] is False,
        "same_row_cte_uncertainty_missing_recorded": observations[
            "same_table_row_cte_with_uncertainty"
        ] is False,
        "same_row_compressibility_uncertainty_missing_recorded": observations[
            "same_table_row_compressibility_with_uncertainty"
        ] is False,
        "direct_volumetric_cv_uncertainty_missing_recorded": observations[
            "direct_volumetric_cv_with_uncertainty"
        ] is False,
        "cv_standard_uncertainty_missing_recorded": observations[
            "cv_standard_uncertainty_available"
        ] is False,
        "ding_equivalence_not_claimed": observations["material_regime_equivalent_to_Ding_TTG"] is False,
        "ding_substitution_forbidden": observations["substitution_for_Ding_C_src_allowed"] is False,
        "conversion_requires_source_locked_density": mapping["conversion_route"]
        == "c_v^V = rho*c_v requires source-locked same-regime density and uncertainty",
        "uncertainty_propagation_open": mapping["uncertainty_propagation_status"]
        == "OPEN_NOT_SOURCE_LOCKED",
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "no_target_fit": package["holdout_policy"]["target_curve_used"] is False,
        "no_alpha_fit": package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
        "underlying_cv_lane_is_comparator_only": cv_package["derived_comparator"][
            "cv_volumetric_emitted"
        ] is False
        and cv_package["derived_comparator"]["cv_standard_uncertainty_J_per_kg_K"] is None,
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_IAEA_CV_UNCERTAINTY_BOUNDARY_NO_GO"
        if passed
        else "FAIL_IAEA_CV_UNCERTAINTY_BOUNDARY_AUDIT"
    )
    result = {
        "schema_version": "t13-iaea-cv-uncertainty-boundary-audit-v1",
        "artifact": "t13_iaea_cv_uncertainty_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_IAEA_CV_UNCERTAINTY_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the IAEA Table 4.11 comparator remains source-traceable but does not provide a standard uncertainty for derived c_v",
                "the table's probable-error Delta c_p is not promoted to c_v standard uncertainty",
                "the c_w thermoelastic term lacks a source-locked uncertainty contract in this lane",
                "same-row density, CTE, and compressibility uncertainty needed for volumetric propagation is not available in the package",
                "the IAEA manufactured-graphite comparator is not silently substituted for Ding TTG C_src",
            ],
            "equation_or_mapping": mapping["source_relation"],
            "units": {
                "source_row": "cal g^-1 K^-1",
                "mass_specific_conversion": "J kg^-1 K^-1",
                "required_output": "J m^-3 K^-1 with standard uncertainty",
            },
            "derivation_class": "source-provenance boundary and uncertainty no-go; no UET derivation",
            "observable": "source-grade volumetric c_v uncertainty availability",
            "data_role": "EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": rel(OUT)},
                {"path": rel(PACKAGE), "sha256": digest(PACKAGE)},
                {"path": rel(CV_PACKAGE), "sha256": digest(CV_PACKAGE)},
                {"path": rel(RAW), "sha256": actual_hash},
            ],
            "verification_status": status,
            "open_blockers": [
                "c_v_source_uncertainty_not_closed",
                "direct_volumetric_c_v_or_same_state_Cp_source_missing",
                "density_uncertainty_not_source_locked",
                "material_regime_mapping_to_Ding_TTG_not_closed",
            ],
            "dependency_unlocked": "The IAEA uncertainty route is closed as a scoped no-go; a direct uncertainty-grade same-regime volumetric c_v or accepted independent source route is still required.",
            "claim_boundary": package["claim_boundary"],
        },
        "source": {
            **package["source"],
            "local_hash_observed": actual_hash,
            "package_path": rel(PACKAGE),
            "package_sha256": digest(PACKAGE),
        },
        "boundary_observations": observations,
        "mapping_contract": mapping,
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "iaea_table_derived_cv_uncertainty_and_volumetric_conversion_not_source_locked",
        "next_controller": "Acquire direct uncertainty-grade same-regime volumetric c_v or a same-state Cp/density/thermoelastic package; do not infer uncertainty from the table probable error or use it as Ding C_src.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"status": status, "artifact": rel(OUT), "raw_sha256": actual_hash},
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
