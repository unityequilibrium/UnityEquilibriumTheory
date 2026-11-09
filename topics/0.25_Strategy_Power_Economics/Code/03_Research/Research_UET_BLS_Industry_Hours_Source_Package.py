"""Retrieve and validate BLS industry hours through the official public API.

The BLS download directory currently blocks automated retrieval, so this lane
uses the documented public API instead of bypassing the download control.  The
API requests are archived with their response bodies and hashes.  Coverage is
limited to four-digit NAICS industry hours and is never silently expanded to a
payment-level labor ledger.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from economic_hardening_common import ARTIFACT_DIR, BLS_INDUSTRY_HOURS_RAW_DIR, BLS_INDUSTRY_HOURS_VINTAGE, RAW_ROOT, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_bls_industry_hours_source_package.json"
RAW_DIR = BLS_INDUSTRY_HOURS_RAW_DIR
CONCORDANCE = RAW_ROOT / "bea_io" / "2026-07-16" / "BEA-Industry-and-Commodity-Codes-and-NAICS-Concordance.xlsx"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "bls_industry_hours_1987_2024.csv"
MANIFEST = RAW_DIR / "source_manifest.json"
API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
START_YEAR = 1987
END_YEAR = 2024
MAX_SERIES_PER_REQUEST = 50
REQUEST_YEAR_WINDOW = 10


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _chunks(values: list[str], size: int):
    for start in range(0, len(values), size):
        yield values[start:start + size]


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(text.text or "" for text in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")) for item in root.findall("m:si", ns)]


def _cell_value(cell: ET.Element, strings: list[str]) -> str:
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    node = cell.find(f"{{{ns}}}v")
    value = node.text if node is not None else ""
    if cell.attrib.get("t") == "s" and value:
        return strings[int(value)]
    return value


def concordance_naics4() -> list[str]:
    """Extract unique four-digit NAICS prefixes from the archived BEA workbook."""
    if not CONCORDANCE.is_file():
        raise FileNotFoundError(f"BEA concordance is missing: {CONCORDANCE}")
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    codes: set[str] = set()
    with zipfile.ZipFile(CONCORDANCE) as archive:
        strings = _shared_strings(archive)
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = sheet.findall(".//m:sheetData/m:row", namespace)
        for row in rows[5:]:
            cells = [_cell_value(cell, strings).strip() for cell in row.findall("m:c", namespace)]
            if len(cells) < 12:
                continue
            for code in re.findall(r"\d+", cells[11]):
                if len(code) >= 4:
                    codes.add(code[:4])
    return sorted(codes)


def _request_payload(series_ids: list[str], start_year: int, end_year: int) -> dict:
    return {"seriesid": series_ids, "startyear": str(start_year), "endyear": str(end_year)}


def fetch_batch(series_ids: list[str], start_year: int, end_year: int, batch_index: int, refresh: bool) -> dict:
    request_payload = _request_payload(series_ids, start_year, end_year)
    raw_path = RAW_DIR / f"bls_api_batch_{batch_index:03d}_{start_year}_{end_year}.json"
    # The public API has a daily quota. A normal verifier run must be deterministic and
    # must never replace a successful archived response with a quota failure. Use --refresh
    # only when deliberately acquiring a new provider vintage.
    if raw_path.is_file() and not refresh:
        try:
            cached = json.loads(raw_path.read_text(encoding="utf-8"))
            if cached.get("request") == request_payload:
                return {"path": raw_path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    request_body = json.dumps(request_payload, separators=(",", ":")).encode("utf-8")
    url = urllib.request.Request(API_URL, data=request_body, method="POST", headers={"Content-Type": "application/json", "Accept": "application/json"})
    response_payload: dict
    error: str | None = None
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        response_payload = {"status": "REQUEST_FAILED", "message": [str(exc)], "Results": {"series": []}}
        error = str(exc)
    raw_payload = {
        "schema_version": "1.0",
        "provider": "U.S. Bureau of Labor Statistics",
        "source_url": API_URL,
        "retrieval_timestamp_utc": utc_now(),
        "request": request_payload,
        "response": response_payload,
        "error": error,
    }
    write_json(raw_path, raw_payload)
    return {"path": raw_path, "payload": raw_payload, "cached": False}


def main() -> int:
    refresh = "--refresh" in sys.argv[1:]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    codes = concordance_naics4()
    series_ids = [f"IPUAN{code}__L200000000" for code in codes]
    batches: list[dict] = []
    observations: list[dict[str, object]] = []
    requested_years = list(range(START_YEAR, END_YEAR + 1))
    for series_batch in _chunks(series_ids, MAX_SERIES_PER_REQUEST):
        for start in range(START_YEAR, END_YEAR + 1, REQUEST_YEAR_WINDOW):
            end = min(END_YEAR, start + REQUEST_YEAR_WINDOW - 1)
            batch = fetch_batch(series_batch, start, end, len(batches) + 1, refresh)
            batches.append(batch)
            response = batch["payload"].get("response", {})
            for series in response.get("Results", {}).get("series", []):
                series_id = series.get("seriesID")
                if not series_id:
                    continue
                for item in series.get("data", []):
                    if item.get("period") != "A01":
                        continue
                    try:
                        year = int(item["year"])
                        value = float(item["value"])
                    except (KeyError, TypeError, ValueError):
                        continue
                    observations.append({"series_id": series_id, "naics4": series_id[5:9], "year": year, "hours_million": value})
            if not batch.get("cached"):
                time.sleep(0.15)

    observations.sort(key=lambda row: (str(row["naics4"]), int(row["year"])))
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["series_id", "naics4", "year", "hours_million"])
        writer.writeheader()
        writer.writerows(observations)

    by_series: dict[str, set[int]] = {}
    for row in observations:
        by_series.setdefault(str(row["series_id"]), set()).add(int(row["year"]))
    returned_codes = sorted({str(row["naics4"]) for row in observations})
    missing_codes = sorted(set(codes) - set(returned_codes))
    incomplete = {series_id: sorted(set(requested_years) - years) for series_id, years in by_series.items() if set(requested_years) - years}
    request_failures = [
        {"path": _relative(batch["path"]), "status": batch["payload"].get("response", {}).get("status"), "error": batch["payload"].get("error"), "message": batch["payload"].get("response", {}).get("message", [])}
        for batch in batches
        if batch["payload"].get("error") or batch["payload"].get("response", {}).get("status") != "REQUEST_SUCCEEDED"
    ]
    manifest_records = []
    for batch in batches:
        path = batch["path"]
        manifest_records.append({
            "source_id": path.stem,
            "source_url": API_URL,
            "original_filename": path.name,
            "local_path": _relative(path),
            "retrieval_timestamp_utc": batch["payload"].get("retrieval_timestamp_utc"),
            "request": batch["payload"].get("request"),
            "sha256": sha256(path),
            "units": "annual hours worked; millions of hours",
            "coverage": f"NAICS four-digit series; {START_YEAR}-{END_YEAR}; A01 annual observations",
            "benchmark_role": "industry labor-input join candidate; not payment-level provenance",
        })
    manifest = {
        "schema_version": "1.0",
        "provider": "U.S. Bureau of Labor Statistics",
        "official_page": "https://www.bls.gov/productivity/technical-notes/industry-hours-and-employment.htm",
        "api_url": API_URL,
        "retrieval_vintage": BLS_INDUSTRY_HOURS_VINTAGE,
        "retrieval_mode": "refresh" if refresh else "frozen-archive-reuse",
        "terms": "BLS public API; retain provider attribution and follow current API usage policy.",
        "coverage": f"{len(returned_codes)} returned four-digit NAICS series from a {len(codes)}-code BEA concordance candidate set; {START_YEAR}-{END_YEAR}",
        "no_imputation": True,
        "sources": manifest_records,
        "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(observations)},
        "status": "PASS_WITH_BOUNDARY" if observations and not request_failures and not incomplete else ("WARN" if observations else "BLOCKED"),
    }
    write_json(MANIFEST, manifest)
    status = manifest["status"]
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "BLS_INDUSTRY_HOURS_SOURCE_LOCKED" if status == "PASS_WITH_BOUNDARY" else "BLS_INDUSTRY_HOURS_SOURCE_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(MANIFEST), "sha256": sha256(MANIFEST), "status": status},
        "coverage": {
            "requested_bea_naics4": len(codes),
            "returned_naics4": len(returned_codes),
            "missing_naics4": missing_codes,
            "series_count": len(by_series),
            "complete_series_count": len(by_series) - len(incomplete),
            "rows": len(observations),
            "years": [START_YEAR, END_YEAR],
            "no_imputation": True,
        },
        "request_failures": request_failures,
        "incomplete_series": incomplete,
        "normalized_panel": {"path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED)},
        "claim_boundary": "BLS industry-hours observations provide an annual labor-input measure for returned NAICS series. They do not identify who paid, whether funding was profit or debt, worker occupation within a payment, or causal resource use.",
        "limitations": [
            "The four-digit NAICS set is a concordance candidate, not a one-to-one equivalence to every BEA 1997 I-O industry code.",
            "The public API has a ten-year request window; each response is archived and hashed.",
            "Missing or incomplete series are reported rather than imputed.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("BLS industry-hours source package:", status, "returned", len(returned_codes), "of", len(codes), "NAICS4 codes", "rows", len(observations))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
