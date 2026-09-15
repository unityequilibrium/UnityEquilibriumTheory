"""Audit the archived Georgia Tech graphite heat-capacity workbook.

The workbook is used only to establish an independent, source-traceable
specific-heat candidate. The audit deliberately stops before treating c_p as
the TTG volumetric c_v quantity.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shared_strings(root: ElementTree.Element) -> list[str]:
    values: list[str] = []
    for item in root.findall("m:si", NS):
        values.append("".join(item.itertext()))
    return values


def workbook_rows(path: Path) -> list[list[object]]:
    with ZipFile(path) as archive:
        strings = shared_strings(
            ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        )
        sheet = ElementTree.fromstring(
            archive.read("xl/worksheets/sheet1.xml")
        )
    rows: list[list[object]] = []
    for row in sheet.findall("m:sheetData/m:row", NS):
        cells: dict[int, object] = {}
        for cell in row.findall("m:c", NS):
            ref = cell.attrib["r"]
            column = 0
            for character in ref:
                if character.isalpha():
                    column = (
                        column * 26
                        + ord(character.upper())
                        - ord("A")
                        + 1
                    )
                else:
                    break
            value = cell.find("m:v", NS)
            if value is None:
                parsed: object = None
            elif cell.attrib.get("t") == "s":
                parsed = strings[int(value.text or "0")]
            else:
                parsed = float(value.text or "nan")
            cells[column] = parsed
        rows.append([cells.get(index) for index in range(1, 8)])
    return rows


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1.0e-12, abs_tol=1.0e-12)


def main() -> int:
    package = load(PACKAGE)
    rows = workbook_rows(RAW)
    header = [str(value).strip() if value is not None else "" for value in rows[0]]
    target_candidates = [
        (index + 1, row)
        for index, row in enumerate(rows[1:], start=1)
        if row
        and row[0] is not None
        and close(float(row[0]), package["row_identity"]["temperature_C"])
    ]
    target_excel_row, target = (
        target_candidates[0]
        if len(target_candidates) == 1
        else (None, None)
    )
    expected = package["reported_values"]
    raw_digest = sha256(RAW)
    checks = {
        "raw_workbook_present": RAW.is_file(),
        "raw_hash_matches": raw_digest == package["source"]["local_raw_sha256"],
        "raw_bytes_match": RAW.stat().st_size
        == package["source"]["local_raw_bytes"],
        "worksheet_header_present": header
        == [
            "Temperature (C)",
            "Average Thermal Conductivity (W/m-K)",
            "Uncertainty at 95% confidence level (W/m-K)",
            "Average Specific Heat (J/g-K)",
            "Uncertainty at 95% confidence level (J/g-K)",
            "Average Thermal Diffusivity (mm^2/s)",
            "Uncertainty at 95% confidence level (mm^2/s)",
        ],
        "target_row_unique": target is not None,
        "target_excel_row_matches_manifest": target_excel_row == 3,
        "temperature_C_matches": target is not None
        and close(float(target[0]), 300.0),
        "temperature_K_conversion_explicit": package["row_identity"][
            "temperature_K"
        ]
        == 573.15,
        "specific_heat_matches": target is not None
        and close(
            float(target[3]), expected["average_specific_heat_J_per_g_K"]
        ),
        "specific_heat_uncertainty_matches": target is not None
        and close(
            float(target[4]), expected["uncertainty_95pct_J_per_g_K"]
        ),
        "uncertainty_is_95pct": package["reported_values"][
            "uncertainty_confidence"
        ]
        == "95%",
        "density_uncertainty_gap_is_explicit": package["density_contract"][
            "status"
        ]
        == "ASSUMED_CONSTANT_NO_SOURCE_UNCERTAINTY",
        "cv_conversion_gap_is_explicit": package["required_quantity_contract"][
            "conversion_status"
        ]
        == "OPEN_CP_TO_CV_AND_DENSITY_UNCERTAINTY",
        "no_additional_local_interpolation_or_fit": "no additional interpolation"
        in package["source"]["preprocessing"],
        "publisher_cp_interpolation_disclosed": package["source"][
            "publisher_preprocessing"
        ]["specific_heat_temperature_alignment"]
        == "SOURCE_PROVIDER_1D_LINEAR_INTERPOLATION_TO_DIFFUSIVITY_TEMPERATURES",
        "conductivity_is_declared_derived": package[
            "property_origin_contract"
        ]["thermal_conductivity"]
        == "DERIVED_FROM_DIFFUSIVITY_CP_AND_ASSUMED_DENSITY_NOT_AN_INDEPENDENT_MEASUREMENT",
        "density_is_declared_assumed": package["property_origin_contract"][
            "density"
        ]
        == "ASSUMED_CONSTANT_NOT_MEASURED_IN_THIS_PACKAGE",
        "candidate_not_consumed": package["source"]["source_data_role"]
        == "independent calibration candidate; not consumed by target fitting",
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"]
        is False,
        "holdout_not_consumed": package["holdout_policy"][
            "xie_2026_source_data_consumed"
        ]
        is False,
    }
    status = (
        "PASS_SOURCE_CP_95CI_CV_OPEN"
        if all(checks.values())
        else "FAIL_SOURCE_AUDIT"
    )
    report = {
        "schema_version": "t13-gatech-source-audit-v1",
        "artifact": "t13_gatech_graphite_source_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_SOURCE_CP_95CI_ANCHOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "One independent graphite specific-heat row, workbook identity, raw hash, Celsius-to-kelvin locator, 95% confidence interval, publisher interpolation, and derived-conductivity dependency are source-locked without target fitting.",
            "equation_or_mapping": "c_p,mass(T=573.15 K) = 1.25981694473522 +/- 0.0698470681678102 J g^-1 K^-1 at 95% confidence",
            "units": {
                "source_temperature": "degC and K after exact +273.15 conversion",
                "specific_heat": "J g^-1 K^-1",
                "uncertainty": "J g^-1 K^-1 at 95% confidence",
                "required_TTG_quantity": "J m^-3 K^-1 c_v; not supplied by this row",
            },
            "derivation_class": "source extraction and provenance audit; no UET derivation",
            "observable": "independent material heat-capacity candidate",
            "data_role": "CALIBRATION_CANDIDATE_NOT_CONSUMED",
            "evidence_artifacts": [
                {"path": "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"},
                {
                    "path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": sha256(PACKAGE),
                },
                {
                    "path": str(RAW.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": raw_digest,
                    "bytes": RAW.stat().st_size,
                },
            ],
            "verification_status": status,
            "open_blockers": [
                "source_quantity_is_c_p_not_volumetric_c_v",
                "density_uncertainty_missing_for_volumetric_conversion",
                "source_k_is_derived_not_independent_density_evidence",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "dependency_unlocked": "independent c_p source anchor only; no numeric alpha or TTG holdout comparison",
            "claim_boundary": "The source package is a traceable independent c_p candidate at 573.15 K. It is not c_v, not an alpha_Phi_K calibration, and not external validation of UET.",
        },
        "row_identity": package["row_identity"],
        "reported_values": package["reported_values"],
        "source_identity": {
            "package_path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"),
            "package_sha256": sha256(PACKAGE),
            "raw_path": str(RAW.relative_to(ROOT)).replace("\\", "/"),
            "raw_sha256": raw_digest,
            "raw_bytes": RAW.stat().st_size,
            "worksheet": "Sheet1",
            "excel_row": target_excel_row,
        },
        "reported_row": target,
        "checks": checks,
        "controlling_blocker": "gatech_source_is_c_p_and_volumetric_c_v_conversion_remains_open",
        "next_controller": "source-lock a direct volumetric c_v or an independently measured same-grade density with uncertainty plus Cp-to-cv inputs; do not invert the source-derived conductivity into density and do not use the 573.15 K row as TTG target data",
        "claim_boundary": "Source closure only: this artifact source-locks c_p and discloses the source dependency graph. The reported k is not independent density or volumetric-heat-capacity evidence and this does not close alpha_Phi_K or Full Topic 13.",
    }
    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "raw_sha256": raw_digest,
            },
            indent=2,
        )
    )
    return 0 if status == "PASS_SOURCE_CP_95CI_CV_OPEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
