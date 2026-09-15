"""Audit the NIST-archived DeSorbo 1955 Ceylon graphite Cp comparator."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
PACKAGE = BASE / "desorbo_1955_ceylon_graphite_cp_source_package.json"
RAW = BASE / "raw/nist_srd69_graphite_desorbo_1955.html"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_desorbo_ceylon_graphite_cp_audit.json"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    package = load_json(PACKAGE)
    raw_text = RAW.read_text(encoding="utf-8", errors="replace") if RAW.is_file() else ""
    row = package["source_row"]
    uncertainty = package["uncertainty_boundary"]
    checks: dict[str, bool] = {
        "package_status_is_numeric_comparator": package["status"]
        == "SOURCE_LOCKED_NUMERIC_CP_COMPARATOR_CV_UNCERTAINTY_OPEN",
        "raw_source_present": RAW.is_file(),
        "raw_hash_matches_package": RAW.is_file()
        and sha256(RAW) == package["source"]["local_raw_sha256"],
        "nist_cp_table_locator_present": "Constant pressure heat capacity of solid"
        in raw_text,
        "nist_numeric_row_present": '<td class="right-nowrap">7.841</td><td class="right-nowrap">298.15</td>'
        in raw_text,
        "nist_primary_reference_present": "Low temperature heat capacity of Ceylon graphite"
        in raw_text,
        "row_units_are_molar_cp": row["reported_units"] == "J mol^-1 K^-1"
        and row["quantity"] == "Cp,solid",
        "row_temperature_is_declared": row["temperature_K"] == 298.15,
        "accuracy_not_relabelled_as_standard_uncertainty": uncertainty[
            "standard_uncertainty_value"
        ]
        is None
        and uncertainty["do_not_relabel_as_standard_uncertainty"] is True
        and uncertainty["consumed_in_uncertainty_propagation"] is False,
        "volumetric_cv_not_emitted": package["required_quantity_contract"][
            "conversion_status"
        ]
        == "OPEN_DENSITY_CP_TO_CV_AND_MATERIAL_MAPPING",
        "no_fit_or_target_used": package["source"]["preprocessing"].find("fitting") >= 0
        and package["holdout_policy"]["target_curve_used"] is False
        and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
        "xie_holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"]
        is False
        and package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "alpha_not_emitted": "alpha_Phi_K" not in package["claim_boundary"].split("emit")[0],
    }
    status = (
        "PASS_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_LOCKED_COMPARATOR"
        if all(checks.values())
        else "FAIL_DESORBO_CEYLON_GRAPHITE_CP_AUDIT"
    )
    artifact = {
        "schema_version": "t13-desorbo-ceylon-graphite-cp-audit-v1",
        "artifact": "t13_desorbo_ceylon_graphite_cp_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "official NIST table row attributed to DeSorbo 1955 is archived with a local hash",
                "Ceylon natural graphite material identity and primary-paper citation are recorded",
                "7.841 J mol^-1 K^-1 at 298.15 K is source-locked as Cp,solid",
                "the reported accuracy boundary is preserved without promotion to standard uncertainty",
                "the row is isolated from fitting, target access, Phi calibration, and holdout access",
            ],
            "equation_or_mapping": "Cp,solid^m(298.15 K) = 7.841 J mol^-1 K^-1; conversion to c_v^V is not consumed",
            "units": {
                "source_row": "J mol^-1 K^-1",
                "required_downstream_quantity": "J m^-3 K^-1",
            },
            "derivation_class": "official secondary numeric table with primary-source attribution; no UET derivation",
            "observable": "Ceylon natural graphite molar constant-pressure heat capacity",
            "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {
                    "path": PACKAGE.relative_to(ROOT).as_posix(),
                    "sha256": sha256(PACKAGE),
                },
                {"path": RAW.relative_to(ROOT).as_posix(), "sha256": sha256(RAW)},
                {"path": OUT.relative_to(ROOT).as_posix()},
            ],
            "verification_status": status,
            "open_blockers": [
                "standard_uncertainty_not_reported_in_archived_numeric_row",
                "density_and_cp_to_cv_conversion_not_source_locked",
                "Ceylon_natural_graphite_to_Ding_TTG_material_mapping_not_closed",
                "Ding_specific_PBTE_C_src_remains_missing",
                "base_Phi_SI_anchor_and_independent_alpha_Phi_K_remain_missing",
            ],
            "dependency_unlocked": "Ceylon natural-graphite numeric Cp comparator lane only; no c_v, C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": package["claim_boundary"],
        },
        "source": package["source"],
        "source_row": row,
        "uncertainty_boundary": uncertainty,
        "checks": checks,
        "numeric_cp_emitted": True,
        "volumetric_cv_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "standard_uncertainty_density_and_Ding_material_mapping_missing",
        "next_action": "Acquire a source-grade standard uncertainty and density/material-regime mapping, or retain this row as comparison-only evidence.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": [key for key, value in checks.items() if not value],
                "numeric_cp_J_per_mol_K": row["value_J_per_mol_K"],
                "controlling_blocker": artifact["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
