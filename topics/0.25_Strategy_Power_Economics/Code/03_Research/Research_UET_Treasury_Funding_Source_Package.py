"""Archive a fixed Treasury Fiscal Data funding-source snapshot.

This package separates an aggregate federal funding bridge from transaction-level
payment provenance. It records FY2024 receipts, outlays, deficit financing, and
public debt at the official Treasury reporting date 2024-09-30. It cannot assign
a tax, debt, or cash-balance source to an individual USAspending award.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json

ARTIFACT = ARTIFACT_DIR / "0_25_treasury_funding_source_audit.json"
RAW_DIR = RAW_ROOT / "treasury_fiscal_data" / "2026-08-01"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "treasury_fy2024_funding_source_snapshot.csv"
BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
DOCS = "https://fiscaldata.treasury.gov/api-documentation/"
AS_OF = "2024-09-30"
ENDPOINTS = {
    "mts_table_1": "/v1/accounting/mts/mts_table_1",
    "mts_table_2": "/v1/accounting/mts/mts_table_2",
    "mts_table_4": "/v1/accounting/mts/mts_table_4",
    "mts_table_5": "/v1/accounting/mts/mts_table_5",
    "mts_table_6": "/v1/accounting/mts/mts_table_6",
    "debt_to_penny": "/v2/accounting/od/debt_to_penny",
}
CSV_FIELDS = ["endpoint", "record_date", "classification_desc", "amount_field", "amount_usd", "fiscal_year"]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _url(endpoint: str) -> str:
    query = {"filter": f"record_date:eq:{AS_OF}", "page[size]": "10000", "format": "json"}
    return BASE + ENDPOINTS[endpoint] + "?" + urllib.parse.urlencode(query)


def _fetch(endpoint: str, refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{endpoint}_{AS_OF}.json"
    request_url = _url(endpoint)
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("request_url") == request_url:
                return {"path": path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        req = urllib.request.Request(request_url, headers={"Accept": "application/json", "User-Agent": "UET-Economics-Research/1.0 (public research)"})
        with urllib.request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        body = {"data": [], "error": str(exc)}
        error = str(exc)
    wrapped = {
        "schema_version": "1.0",
        "provider": "U.S. Department of the Treasury, Fiscal Service",
        "source_url": request_url,
        "documentation_url": DOCS,
        "retrieval_timestamp_utc": utc_now(),
        "retrieval_vintage": "2026-08-01",
        "request_url": request_url,
        "endpoint": endpoint,
        "record_date": AS_OF,
        "response": body,
        "error": error,
    }
    write_json(path, wrapped)
    return {"path": path, "payload": wrapped, "cached": False}


def _amount(row: dict, fields: list[str]) -> tuple[str | None, float | None]:
    for field in fields:
        value = row.get(field)
        if value not in (None, "", "null"):
            try:
                return field, float(value)
            except (TypeError, ValueError):
                return field, None
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new official provider vintage")
    args = parser.parse_args()
    fetched: dict[str, dict] = {}
    failures: list[dict] = []
    all_rows: list[dict] = []
    for endpoint in ENDPOINTS:
        item = _fetch(endpoint, args.refresh)
        fetched[endpoint] = item
        payload = item["payload"]
        response = payload.get("response", {})
        if payload.get("error") or response.get("error"):
            failures.append({"endpoint": endpoint, "path": _relative(item["path"]), "error": payload.get("error") or response.get("error")})
        for row in response.get("data", []) if isinstance(response.get("data", []), list) else []:
            if endpoint == "mts_table_2": candidates = ["current_fytd_budget_amt"]
            elif endpoint == "mts_table_4": candidates = ["current_fytd_net_rcpt_amt", "current_fytd_gross_rcpt_amt"]
            elif endpoint == "mts_table_5": candidates = ["current_fytd_net_outly_amt", "current_fytd_gross_outly_amt"]
            elif endpoint == "mts_table_6": candidates = ["fytd_net_txn_amt"]
            elif endpoint == "debt_to_penny": candidates = ["tot_pub_debt_out_amt", "debt_held_public_amt"]
            else: candidates = ["current_month_dfct_sur_amt"]
            field, amount = _amount(row, candidates)
            all_rows.append({"endpoint": endpoint, "record_date": row.get("record_date"), "classification_desc": row.get("classification_desc", "Total public debt" if endpoint == "debt_to_penny" else None), "amount_field": field, "amount_usd": amount, "fiscal_year": row.get("record_fiscal_year", "2024")})
        if not item.get("cached"): time.sleep(0.15)
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    all_rows.sort(key=lambda row: (row["endpoint"], str(row["classification_desc"] or ""), str(row["amount_field"] or "")))
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS); writer.writeheader(); writer.writerows(all_rows)
    sources = []
    for endpoint, item in fetched.items():
        sources.append({"source_id": endpoint, "source_url": item["payload"].get("source_url"), "documentation_url": DOCS, "original_filename": item["path"].name, "local_path": _relative(item["path"]), "retrieval_timestamp_utc": item["payload"].get("retrieval_timestamp_utc"), "sha256": sha256(item["path"]), "units": "current U.S. dollars as reported by Treasury Fiscal Data", "coverage": f"record date {AS_OF}; endpoint {endpoint}", "benchmark_role": "aggregate federal receipts/outlays/financing/debt; not individual award settlement"})
    manifest_path = RAW_DIR / "source_manifest.json"
    manifest = {"schema_version": "1.0", "provider": "U.S. Department of the Treasury, Fiscal Service", "official_page": "https://fiscaldata.treasury.gov/", "documentation_url": DOCS, "retrieval_vintage": "2026-08-01", "record_date": AS_OF, "terms": "Public Treasury Fiscal Data API; retain provider attribution and API terms.", "coverage": "FY2024 final monthly Treasury Statement record date with MTS tables 1, 2, 4, 5, 6 and debt-to-the-penny snapshot", "no_imputation": True, "sources": sources, "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(all_rows)}, "status": "PASS_WITH_BOUNDARY" if all_rows and not failures else ("WARN" if all_rows else "BLOCKED")}
    write_json(manifest_path, manifest)
    def find(endpoint: str, needle: str, field: str) -> float | None:
        for row in all_rows:
            if row["endpoint"] == endpoint and needle.lower() in str(row.get("classification_desc") or "").lower() and row["amount_field"] == field:
                return row["amount_usd"]
        return None
    summary = {"total_receipts_fytd_usd": find("mts_table_2", "Total Receipts", "current_fytd_budget_amt"), "total_outlays_fytd_usd": find("mts_table_2", "Total Outlays", "current_fytd_budget_amt"), "deficit_fytd_usd": find("mts_table_2", "Total Surplus", "current_fytd_budget_amt"), "total_financing_fytd_usd": find("mts_table_2", "Total On-Budget and Off-Budget Financing", "current_fytd_budget_amt"), "total_public_debt_outstanding_usd": find("debt_to_penny", "Total public debt", "tot_pub_debt_out_amt")}
    status = manifest["status"]
    artifact = {"schema_version": "1.0", "topic": "0.25_Strategy_Power_Economics", "status": status, "controller_status": "TREASURY_AGGREGATE_FUNDING_SOURCE_LOCKED" if status == "PASS_WITH_BOUNDARY" else "TREASURY_FUNDING_SOURCE_GATE", "generated_at_utc": utc_now(), "source_manifest": {"path": _relative(manifest_path), "sha256": sha256(manifest_path), "status": status}, "coverage": {"record_date": AS_OF, "fiscal_year": 2024, "endpoints": list(ENDPOINTS), "rows": len(all_rows), "request_failures": failures, "no_imputation": True}, "aggregate_summary": summary, "funding_source_identification": {"status": "AGGREGATE_ONLY", "observed_categories": ["tax and social-insurance receipts", "federal outlays", "public debt financing", "operating-cash and other financing adjustments"], "boundary": "Treasury reports aggregate federal receipts, outlays, and financing. It cannot assign the source of a tax dollar, borrowed dollar, or cash-balance adjustment to an individual USAspending award, invoice, bank settlement, or physical transformation."}, "claim_boundary": "This artifact is an aggregate federal funding-source diagnostic. It does not establish profit-versus-debt funding for a specific purchase and does not identify money creation at award level.", "limitations": ["The snapshot is fixed to FY2024 record date 2024-09-30 and is not a real-time settlement ledger.", "MTS and debt data are government-wide aggregate accounting reports; individual award timing and settlement are not joined.", "USAspending award obligations can precede or differ from Treasury cash outlays.", "Aggregate financing categories do not identify which instrument financed a particular project or recipient."]}
    write_json(ARTIFACT, artifact)
    print("Treasury funding source package:", status, "rows", len(all_rows), "failures", len(failures))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1

if __name__ == "__main__": raise SystemExit(main())
