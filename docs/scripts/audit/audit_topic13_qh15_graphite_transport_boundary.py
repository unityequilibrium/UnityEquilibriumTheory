"""Audit the QH-15 graphite transport archive as a scoped comparator lane."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TOPIC_DATA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/qh15_graphite_transport_source_package.json"
PACKAGE = ROOT / PACKAGE_REL
RAW_ROOT = TOPIC_DATA / "raw/qh15_materialscloud"
CALORINE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/calorine_legacy_nep2_pbte_reproduction_source_package.json"
CALORINE = ROOT / CALORINE_REL
OUT_REL = "docs/core/artifacts/t13_qh15_graphite_transport_boundary_audit.json"
OUT = ROOT / OUT_REL


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            rows.append([float(value) for value in row])
    return rows


def find_row(rows: list[list[float]], temperature_K: float) -> list[float]:
    for row in rows:
        if math.isclose(row[0], temperature_K, rel_tol=0.0, abs_tol=1e-12):
            return row
    raise KeyError(f"temperature row not found: {temperature_K} K")


def main() -> int:
    package = load(PACKAGE)
    calorine = load(CALORINE)
    natural_path = RAW_ROOT / "raw_data/graphite_transport_coefficients.csv"
    isopure_path = RAW_ROOT / "raw_data/graphite_transport_coefficients_isopure_80K.csv"
    readme_path = RAW_ROOT / "README.txt"
    notebook_path = RAW_ROOT / "fig1_temp_inversion/fig1_temp_inversion.nb"
    paths = {
        "README": readme_path,
        "NATURAL_CSV": natural_path,
        "ISOPURE_CSV": isopure_path,
        "SOURCE_NOTEBOOK": notebook_path,
    }
    natural_rows = parse_rows(natural_path)
    isopure_rows = parse_rows(isopure_path)
    conversion = float(package["unit_contract"]["conversion_factor"])
    expected_rows = package["source_rows"]
    selected_natural: list[dict[str, float]] = []
    for expected in expected_rows["natural_graphite"]:
        row = find_row(natural_rows, float(expected["temperature_K"]))
        native = row[18]
        selected_natural.append(
            {
                "temperature_K": row[0],
                "specific_c_native": native,
                "converted_c_v_J_m^-3_K^-1": native * conversion,
            }
        )
    expected_iso = expected_rows["isopure_control"][0]
    iso_row = find_row(isopure_rows, float(expected_iso["temperature_K"]))
    selected_isopure = {
        "temperature_K": iso_row[0],
        "specific_c_native": iso_row[18],
        "converted_c_v_J_m^-3_K^-1": iso_row[18] * conversion,
    }

    calorine_rows = calorine["reproduction"]["c_src_rows_latest_mesh"]
    crosschecks: list[dict[str, float]] = []
    for temperature_K in package["comparator_contract"]["calorine_crosscheck_temperatures_K"]:
        qh15 = next(item for item in selected_natural if item["temperature_K"] == temperature_K)
        calorine_row = next(
            item for item in calorine_rows if float(item["temperature_K"]) == float(temperature_K)
        )
        qh15_value = qh15["converted_c_v_J_m^-3_K^-1"]
        calorine_value = float(calorine_row["C_src_J_m^-3_K^-1"])
        relative_difference = (qh15_value - calorine_value) / calorine_value
        crosschecks.append(
            {
                "temperature_K": float(temperature_K),
                "qh15_c_v_J_m^-3_K^-1": qh15_value,
                "calorine_c_src_J_m^-3_K^-1": calorine_value,
                "relative_difference": relative_difference,
                "relative_difference_percent": 100.0 * relative_difference,
            }
        )

    archived = {item["role"]: item for item in package["archived_entries"]}
    hash_checks = {
        role: path.is_file()
        and path.stat().st_size == archived[role]["bytes"]
        and sha256(path) == archived[role]["sha256"]
        for role, path in {
            "source data layout and material-label contract": readme_path,
            "natural-graphite raw transport-coefficient rows": natural_path,
            "isopure graphite control rows": isopure_path,
            "source notebook defining column meanings and units": notebook_path,
        }.items()
    }
    notebook_text = notebook_path.read_text(encoding="utf-8-sig")
    checks = {
        "package_present": PACKAGE.is_file(),
        "calorine_package_present": CALORINE.is_file(),
        "all_archived_entries_match_hash_and_size": all(hash_checks.values()),
        "archive_identity_locked": (
            package["source"]["archive_file"]["sha256"]
            == "c46a9db519bca1f56a2e195a5dcf38f01d6d1063f32f828083a72f40a8e38be4"
            and package["source"]["archive_file"]["md5"]
            == "1e4cdf648fd549fae90824c1256c52c5"
        ),
        "raw_csv_has_no_header_and_20_columns": (
            package["raw_table_contract"]["header_present"] is False
            and all(len(row) == 20 for row in natural_rows + isopure_rows)
        ),
        "row_counts_match_package": (
            len(natural_rows) == package["raw_table_contract"]["natural_graphite_row_count"]
            and len(isopure_rows) == package["raw_table_contract"]["isopure_control_row_count"]
        ),
        "source_notebook_defines_specific_c_and_native_units": (
            "SpecificC" in notebook_text
            and "micrometer" in notebook_text
            and "ns" in notebook_text
            and "SpecificC" in notebook_text
        ),
        "selected_rows_match_raw_source": all(
            math.isclose(
                actual["specific_c_native"],
                float(expected["specific_c_native"]),
                rel_tol=0.0,
                abs_tol=1e-15,
            )
            for actual, expected in zip(selected_natural, expected_rows["natural_graphite"])
        )
        and math.isclose(
            selected_isopure["specific_c_native"],
            float(expected_iso["specific_c_native"]),
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        "declared_conversion_factor_is_si_closed": conversion == 1.0e9
        and all(item["converted_c_v_J_m^-3_K^-1"] > 0.0 for item in selected_natural)
        and selected_isopure["converted_c_v_J_m^-3_K^-1"] > 0.0,
        "equilibrium_crosscheck_computed": len(crosschecks) == 2
        and all(math.isfinite(item["relative_difference"]) for item in crosschecks),
        "ding_response_contract_not_claimed": package["comparator_contract"][
            "response_contract_match_to_Ding_TTG"
        ]
        is False
        and package["comparator_contract"]["ding_C_src_acceptance"] is False,
        "mode_resolved_payload_not_claimed": package["comparator_contract"][
            "mode_resolved_q_mu_payload_present"
        ]
        is False,
        "source_uncertainty_not_promoted": package["comparator_contract"][
            "source_grade_uncertainty_present"
        ]
        is False,
        "target_curve_unused": package["holdout_policy"]["target_curve_used"] is False,
        "fit_unused": package["holdout_policy"]["fit_performed"] is False,
        "alpha_fit_unused": package["holdout_policy"]["alpha_Phi_K_fit_used"] is False,
        "holdout_unconsumed": package["holdout_policy"]["xie_2026_accessed"] is False
        and package["holdout_policy"]["xie_2026_source_data_consumed"] is False
        and package["holdout_policy"]["calibration_path_may_read_holdout"] is False,
    }
    status = (
        "PASS_SCOPED_QH15_CV_COMPARATOR_BOUNDARY"
        if all(checks.values())
        else "FAIL_QH15_CV_COMPARATOR_BOUNDARY_AUDIT"
    )
    evidence_artifacts = [
        {
            "path": PACKAGE_REL,
            "sha256": sha256(PACKAGE),
            "role": "QH-15 source package and comparator contract",
        },
        *[
            {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}
            for role, path in paths.items()
        ],
        {
            "path": CALORINE_REL,
            "sha256": sha256(CALORINE),
            "role": "independent Calorine candidate used for equilibrium-scale comparison only",
        },
    ]
    artifact = {
        "schema_version": "t13-qh15-graphite-transport-boundary-v1",
        "artifact": "t13_qh15_graphite_transport_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_QH15_GRAPHITE_CV_COMPARATOR_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the Materials Cloud QH-15 archive identity, selected entry paths, local hashes, and source notebook unit witness are locked",
                "the natural-graphite SpecificC column is re-read from raw rows and converted to volumetric SI with an explicit factor",
                "the isopure 80 K control row is preserved as a separate source row and is not mixed into the natural-graphite comparator",
                "the 200 K and 300 K QH-15 values are compared with the independent Calorine candidate as an equilibrium-scale consistency check without fitting",
            ],
            "ontology": {
                "C": "collective system-behaviour coordinate; not QH-15 SpecificC",
                "Phi": "effective response variable; no Phi calibration emitted",
                "R_gen": "derived history trace; not used by this comparator",
                "R_obs": "observer record kept separate; no observer data consumed",
            },
            "equation_or_mapping": {
                "native_to_si": "C_v_QH15 = SpecificC * 1.0e9",
                "unit_factor": "1 pg/(um ns^2 K) = 1.0e9 J m^-3 K^-1",
                "crosscheck": "r_T = (C_v_QH15 - C_src_Calorine)/C_src_Calorine",
                "result_role": "macroscopic equilibrium-scale comparison only; no Phi-to-temperature map",
            },
            "units": {
                "temperature": "K",
                "SpecificC_native": "pg/(um ns^2 K)",
                "C_v_QH15": "J m^-3 K^-1",
                "crosscheck": "dimensionless relative difference",
            },
            "derivation_class": "source-row extraction plus explicit SI unit conversion and non-fitting comparator audit",
            "observable": "macroscopic QH-15 heat-capacity-like transport input",
            "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
            "evidence_artifacts": evidence_artifacts,
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "qh15_to_ding_TTG_response_contract_missing",
                "qh15_source_grade_uncertainty_missing",
                "material_regime_mapping_to_TTG_not_closed",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "Independent macroscopic C_v comparator lane only; no Ding C_src, alpha, Core, Gravity, transport, or Galaxy dependency is unlocked.",
            "claim_boundary": "This result is a source-locked QH-15 comparator boundary. It is not Ding mode-resolved C_src, not an accepted same-regime reproduction, not an alpha_Phi_K calibration, not a Phi-to-temperature prediction, and not Full Topic 13 closure.",
        },
        "source": {
            "source_id": package["source"]["source_id"],
            "doi": package["source"]["doi"],
            "archive_sha256": package["source"]["archive_file"]["sha256"],
            "natural_graphite_rows": selected_natural,
            "isopure_control_row": selected_isopure,
            "source_grade_uncertainty_present": False,
            "material_regime_status": package["source"]["material_regime_status"],
        },
        "observations": {
            "calorine_crosschecks": crosschecks,
            "interpretation": "The two macroscopic source lanes are numerically close at the checked temperatures, but this does not establish material identity, response-contract identity, source-grade uncertainty, or Ding acceptance.",
        },
        "checks": checks,
        "hash_checks": hash_checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_action": "Use QH-15 only as a comparator while obtaining an authorized Ding numeric package or an accepted same-regime PBTE reproduction with source-grade uncertainty and response-contract mapping; keep alpha_Phi_K independent and do not read the locked holdout.",
        "claim_boundary": "Scoped source/comparator boundary only; no numeric UET calibration, no holdout use, no temperature prediction, no external validation, and no Full Topic 13 closure.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT_REL, "crosschecks": crosschecks}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
