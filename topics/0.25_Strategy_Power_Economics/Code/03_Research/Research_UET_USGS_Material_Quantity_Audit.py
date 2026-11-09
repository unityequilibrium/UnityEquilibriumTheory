"""Validate source-locked USGS physical material quantity series.

The workbooks provide national commodity production/consumption quantities.
They are a physical-throughput lane, not a payer ledger and not an industry-
level material-use matrix.  Blank/NA cells remain missing; no zero filling or
industry allocation is performed.
"""

from __future__ import annotations

import csv
import json
import math
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_usgs_material_quantity_audit.json"
RAW_DIR = RAW_ROOT / "usgs_materials" / "2026-07-16"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usgs_material_quantities_1900_2022.csv"
MANIFEST = RAW_DIR / "source_manifest.json"

WORKBOOKS = {
    "cement": {
        "filename": "cement.xlsx",
        "url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-cement-2021.xlsx",
        "unit_basis": "metric tons gross weight",
        "quantity_columns": ["Production", "Apparent consumption"],
    },
    "copper": {
        "filename": "copper.xlsx",
        "url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-copper-2020.xlsx",
        "unit_basis": "metric tons copper content",
        "quantity_columns": ["Primary production", "Secondary production", "Consumption", "Apparent consumption"],
    },
    "gold": {
        "filename": "gold.xlsx",
        "url": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/ds140-gold-2022.xlsx",
        "unit_basis": "metric tons gold content",
        "quantity_columns": ["Primary production", "Secondary production", "Reported consumption"],
    },
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _workbook_rows(path: Path) -> list[list[str]]:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(text.text or "" for text in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")) for item in root.findall("m:si", namespace)]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//m:sheetData/m:row", namespace):
            values: list[str] = []
            for cell in row.findall("m:c", namespace):
                value_node = cell.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                value = value_node.text if value_node is not None else ""
                if cell.attrib.get("t") == "s" and value:
                    value = strings[int(value)]
                if cell.attrib.get("t") == "inlineStr":
                    value = "".join(text.text or "" for text in cell.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                values.append(value.strip())
            rows.append(values)
    return rows


def _number(value: str) -> float | None:
    if value.strip().upper() in {"", "NA", "N/A", "-", "WITHHELD"}:
        return None
    try:
        parsed = float(value.replace(",", ""))
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    normalized_rows: list[dict[str, object]] = []
    file_records: list[dict[str, object]] = []
    parse_failures: list[dict[str, object]] = []
    for commodity, spec in WORKBOOKS.items():
        path = RAW_DIR / spec["filename"]
        record: dict[str, object] = {
            "commodity": commodity,
            "source_url": spec["url"],
            "original_filename": spec["filename"],
            "local_path": _relative(path) if path.is_file() else None,
            "exists": path.is_file(),
            "sha256": sha256(path) if path.is_file() else None,
            "unit_basis": spec["unit_basis"],
            "quantity_columns": spec["quantity_columns"],
        }
        if not path.is_file():
            record["status"] = "MISSING"
            file_records.append(record)
            continue
        try:
            rows = _workbook_rows(path)
        except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            record["status"] = "WARN"
            record["error"] = str(exc)
            file_records.append(record)
            continue
        header_index = next((idx for idx, row in enumerate(rows) if row and row[0].strip().lower() == "year"), None)
        if header_index is None:
            record["status"] = "WARN"
            record["error"] = "Year header not found"
            file_records.append(record)
            continue
        header = rows[header_index]
        columns = {name: header.index(name) for name in spec["quantity_columns"] if name in header}
        years: list[int] = []
        data_rows = 0
        for row_number, row in enumerate(rows[header_index + 1:], start=header_index + 2):
            if not row or not row[0].isdigit():
                continue
            year = int(row[0])
            years.append(year)
            data_rows += 1
            for column_name, column_index in columns.items():
                value = _number(row[column_index] if len(row) > column_index else "")
                if value is None:
                    continue
                normalized_rows.append({
                    "commodity": commodity,
                    "year": year,
                    "quantity_role": column_name.lower().replace(" ", "_"),
                    "quantity_metric_tons": value,
                    "unit_basis": spec["unit_basis"],
                })
        record.update({"status": "PASS_WITH_BOUNDARY", "header_row": header_index + 1, "data_rows": data_rows, "years": [min(years), max(years)] if years else None, "parsed_quantity_rows": sum(1 for row in normalized_rows if row["commodity"] == commodity), "columns_found": sorted(columns)})
        if not columns:
            record["status"] = "WARN"
            parse_failures.append({"commodity": commodity, "reason": "no_declared_quantity_column_found", "header": header})
        file_records.append(record)

    normalized_rows.sort(key=lambda row: (str(row["commodity"]), int(row["year"]), str(row["quantity_role"])))
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["commodity", "year", "quantity_role", "quantity_metric_tons", "unit_basis"])
        writer.writeheader()
        writer.writerows(normalized_rows)

    status = "PASS_WITH_BOUNDARY" if file_records and all(item.get("status") == "PASS_WITH_BOUNDARY" for item in file_records) and normalized_rows else ("WARN" if normalized_rows else "BLOCKED")
    manifest = {
        "schema_version": "1.0",
        "provider": "U.S. Geological Survey, National Minerals Information Center",
        "official_page": "https://www.usgs.gov/centers/national-minerals-information-center/historical-statistics-mineral-commodities-united",
        "retrieval_timestamp_utc": utc_now(),
        "retrieval_vintage": "2026-07-16",
        "terms": "USGS public-domain historical statistics; retain provider attribution.",
        "coverage": "US national mineral commodity production/consumption quantities; commodity-specific historical coverage through the workbook update years",
        "sources": [
            {
                "source_id": f"usgs_{commodity}",
                "source_url": spec["url"],
                "original_filename": spec["filename"],
                "local_path": _relative(RAW_DIR / spec["filename"]),
                "sha256": next((item.get("sha256") for item in file_records if item.get("commodity") == commodity), None),
                "units": spec["unit_basis"],
                "benchmark_role": "physical material throughput; not industry/payment allocation",
            }
            for commodity, spec in WORKBOOKS.items()
        ],
        "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(normalized_rows)},
        "preprocessing": "Read worksheet rows by the Year header and declared quantity columns; retain missing cells as missing; no zero filling, unit conversion, or industry allocation.",
        "status": status,
    }
    write_json(MANIFEST, manifest)
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "USGS_PHYSICAL_QUANTITY_SOURCE_LOCKED" if status == "PASS_WITH_BOUNDARY" else "USGS_MATERIAL_SOURCE_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(MANIFEST), "sha256": sha256(MANIFEST), "status": status},
        "coverage": {"commodities": sorted(WORKBOOKS), "files": file_records, "normalized_rows": len(normalized_rows), "no_imputation": True},
        "parse_failures": parse_failures,
        "mapping_status": "NOT_MAPPED_TO_BEA_INDUSTRY_OR_PROJECT",
        "claim_boundary": "The artifact establishes source-locked national physical quantity series for selected commodities. It does not identify which industry consumed them, which project used them, who paid, or whether funding was profit or debt.",
        "limitations": [
            "Commodity workbooks have different update years and commodity-specific measurement bases.",
            "USGS notes that blank cells may mean unavailable or withheld data and are not zeros.",
            "A material-to-industry concordance and transaction/project ledger are still missing.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("USGS material quantity audit:", status, "commodities", len(WORKBOOKS), "rows", len(normalized_rows))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
