"""Audit the official Nelson-Riley natural/crystalline graphite alpha_V route."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "argonne_anl_5524_nelson_riley_alpha_v_source_package.json"
)
RAW_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "argonne_anl_5524_graphite_thermal_expansion_table.pdf"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"
EXPECTED_RAW_SHA256 = "7e334a4c380c130773f6c34a6238f25a9c28e15c3a9c0e1f9aa3769647e98561"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    source = package["source"]
    row = package["source_row"]
    derived = package["derived_comparator"]
    alpha_c = 27.00e-6 + 3.05e-9 * float(row["temperature_C"])
    alpha_v = 2.0 * float(row["alpha_a_per_K"]) + alpha_c
    actual_hash = digest(RAW_PATH) if RAW_PATH.is_file() else None
    checks = {
        "source_pdf_present": RAW_PATH.is_file(),
        "source_pdf_hash_matches": actual_hash == EXPECTED_RAW_SHA256,
        "package_source_identity_present": bool(
            source.get("report") and source.get("record_url") and source.get("source_locators")
        ),
        "table_locator_declared": "Table XIX" in " ".join(source.get("source_locators", [])),
        "temperature_inside_alpha_a_scope": 0.0 <= float(row["temperature_C"]) <= 150.0,
        "alpha_c_formula_explicit": row["alpha_c_formula"] == "27.00e-6 + 3.05e-9*T_C",
        "alpha_c_reconstruction_matches_package": math.isclose(
            alpha_c, float(row["alpha_c_per_K"]), rel_tol=0.0, abs_tol=1.0e-15
        ),
        "anisotropic_alpha_volume_relation_explicit": package["major_result"][
            "equation_or_mapping"
        ]["anisotropic_volumetric_expansion"] == "alpha_V = 2*alpha_a + alpha_c",
        "alpha_v_reconstruction_matches_package": math.isclose(
            alpha_v, float(derived["alpha_V_per_K"]), rel_tol=0.0, abs_tol=1.0e-15
        ),
        "row_uncertainty_absence_is_explicit": row["row_level_uncertainty_available"] is False
        and derived["alpha_V_uncertainty_per_K"] is None,
        "same_specimen_not_claimed": derived["same_specimen_alpha_V"] is False,
        "K_T_not_emitted": derived["K_T_emitted"] is False,
        "Ding_material_mapping_not_claimed": "Ding" in package["major_result"][
            "claim_boundary"
        ],
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_fit_not_performed": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_Phi_K_fit_not_performed": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-natural-graphite-nelson-riley-alpha-v-source-audit-v1",
        "artifact": "t13_natural_graphite_nelson_riley_alpha_v_source_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_NATURAL_GRAPHITE_ALPHA_V_COMPARATOR"
        if passed
        else "FAIL_NATURAL_GRAPHITE_ALPHA_V_AUDIT",
        "major_result": {
            "major_result_id": "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the official OSTI/Argonne ANL-5524 report is archived with a reproducible local hash",
                "Table XIX alpha_a interval and alpha_c relation are source-locked with a page/table locator",
                "the alpha_V relation is deterministic at the declared approximate room-temperature comparison point",
                "the source's lack of row-level uncertainty and same-specimen identity is retained",
            ],
            "equation_or_mapping": {
                "alpha_a": "-1.5e-6 K^-1 for 0-150 deg C",
                "alpha_c": "27.00e-6 + 3.05e-9*T_C K^-1",
                "anisotropic_volumetric_expansion": "alpha_V = 2*alpha_a + alpha_c",
            },
            "units": {
                "temperature": "deg C source relation; comparison point also reported in K",
                "alpha_a": "K^-1",
                "alpha_c": "K^-1",
                "alpha_V": "K^-1",
            },
            "derivation_class": "official table transcription plus anisotropic thermodynamic geometry conversion; no UET derivation",
            "observable": "natural/crystalline graphite alpha_V comparator",
            "data_role": "EXTERNAL_INPUT_STANDARD_THERMODYNAMIC_COMPARATOR_NOT_DING_TTG_GRADE",
            "evidence_artifacts": [
                {"path": PACKAGE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PACKAGE_PATH)},
                {"path": RAW_PATH.relative_to(ROOT).as_posix(), "sha256": actual_hash},
            ],
            "verification_status": "PASS_SCOPED_NATURAL_GRAPHITE_ALPHA_V_COMPARATOR"
            if passed
            else "FAIL_NATURAL_GRAPHITE_ALPHA_V_AUDIT",
            "open_blockers": [
                "source table has no row-level statistical uncertainty",
                "crystalline graphite and Hanfland natural graphite powder are not a same-specimen matched-state pair",
                "Ding TTG material regime mapping is not closed",
                "base_Phi_to_thermal_observable_map_and_independent_alpha_Phi_K_missing",
            ]
            if passed
            else ["Argonne Nelson-Riley alpha_V source checks failed"],
            "dependency_unlocked": "official natural/crystalline graphite alpha_V comparator lane only; no same-specimen K_T, Ding C_src, alpha_Phi_K, transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This is a source-traceable natural/crystalline graphite family comparator based on official Table XIX. It is not a same-specimen alpha_V measurement, not a matched Hanfland state, not a Ding TTG material match, and not an alpha_Phi_K calibration.",
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
            "alpha_c_reconstructed_per_K": alpha_c,
            "alpha_V_reconstructed_per_K": alpha_v,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "same_specimen_alpha_V_K_T_uncertainty_and_Ding_material_regime_mapping_missing",
        "next_controller": "Obtain a same-state, same-specimen alpha_V/K_T pair with uncertainty or a permitted direct volumetric heat-capacity route; keep the official family comparator separate from Ding C_src and base-Phi calibration.",
        "claim_boundary": "This closes only an official natural/crystalline graphite family-level alpha_V comparator. It does not close same-grade K_T, Ding C_src, e0, base Phi, alpha_Phi_K, transport, SK/KMS, entropy, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "raw_sha256": actual_hash,
                "temperature_K": row["temperature_K"],
                "alpha_V_per_K": alpha_v,
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
