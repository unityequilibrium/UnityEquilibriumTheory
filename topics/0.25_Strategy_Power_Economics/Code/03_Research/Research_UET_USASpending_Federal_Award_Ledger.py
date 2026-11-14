"""Archive a bounded public federal-award transaction ledger.

USAspending records federal award obligations and recipient/award metadata.  It is
useful for a public-payer lane, but it is not a bank settlement ledger and it does
not identify whether the federal funds came from taxes, borrowing, or money creation.
The query is deliberately fixed to the Department of Energy, FY2024, contract award
codes, and the first five API pages so that the artifact is a bounded diagnostic sample.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_usaspending_federal_project_ledger.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_doe_fy2024_transactions.csv"
API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_transaction/"
OFFICIAL_DOCS = "https://api.usaspending.gov/docs/endpoints"
START_DATE = "2023-10-01"
END_DATE = "2024-09-30"
AGENCY = "Department of Energy"
PAGE_LIMIT = 100
PAGES = 5
AWARD_TYPE_CODES = ["A", "B", "C", "D"]
FIELDS = [
    "Award ID",
    "Recipient Name",
    "Recipient UEI",
    "Action Date",
    "Transaction Amount",
    "Award Type",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Funding Agency",
    "Funding Sub Agency",
    "naics_code",
    "naics_description",
    "product_or_service_code",
    "product_or_service_description",
    "Transaction Description",
    "Primary Place of Performance",
    "generated_internal_id",
    "internal_id",
]
CSV_FIELDS = [
    "transaction_id",
    "award_id",
    "recipient_name",
    "recipient_uei",
    "action_date",
    "transaction_amount_usd",
    "award_type",
    "awarding_agency",
    "awarding_sub_agency",
    "funding_agency",
    "funding_sub_agency",
    "naics_code",
    "naics_description",
    "psc_code",
    "psc_description",
    "transaction_description",
    "primary_place_of_performance",
]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _request_payload(page: int) -> dict:
    return {
        "filters": {
            "time_period": [{"start_date": START_DATE, "end_date": END_DATE}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": AGENCY}],
            "award_type_codes": AWARD_TYPE_CODES,
        },
        "fields": FIELDS,
        "page": page,
        "limit": PAGE_LIMIT,
        "sort": "Action Date",
        "order": "desc",
    }


def _fetch_page(page: int, refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"usaspending_doe_fy2024_page_{page:02d}.json"
    request_payload = _request_payload(page)
    if raw_path.is_file() and not refresh:
        try:
            cached = json.loads(raw_path.read_text(encoding="utf-8"))
            if cached.get("request") == request_payload:
                return {"path": raw_path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(request_payload, separators=(",", ":")).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "UET-Economics-Research/1.0 (public research)",
        },
    )
    error: str | None = None
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        response_payload = {"results": [], "error": str(exc)}
        error = str(exc)
    wrapped = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "source_url": API_URL,
        "documentation_url": OFFICIAL_DOCS,
        "retrieval_timestamp_utc": utc_now(),
        "request": request_payload,
        "response": response_payload,
        "error": error,
    }
    write_json(raw_path, wrapped)
    return {"path": raw_path, "payload": wrapped, "cached": False}


def _transaction_id(row: dict) -> str:
    value = row.get("internal_id") or row.get("generated_internal_id")
    if value not in (None, ""):
        return str(value)
    encoded = json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "row-" + hashlib.sha256(encoded).hexdigest()[:24]


def _normalize(row: dict) -> dict:
    amount = row.get("Transaction Amount")
    try:
        amount_value = float(amount) if amount not in (None, "") else None
    except (TypeError, ValueError):
        amount_value = None
    return {
        "transaction_id": _transaction_id(row),
        "award_id": row.get("Award ID"),
        "recipient_name": row.get("Recipient Name"),
        "recipient_uei": row.get("Recipient UEI"),
        "action_date": row.get("Action Date"),
        "transaction_amount_usd": amount_value,
        "award_type": row.get("Award Type"),
        "awarding_agency": row.get("Awarding Agency"),
        "awarding_sub_agency": row.get("Awarding Sub Agency"),
        "funding_agency": row.get("Funding Agency"),
        "funding_sub_agency": row.get("Funding Sub Agency"),
        "naics_code": row.get("naics_code"),
        "naics_description": row.get("naics_description"),
        "psc_code": row.get("product_or_service_code"),
        "psc_description": row.get("product_or_service_description"),
        "transaction_description": row.get("Transaction Description"),
        "primary_place_of_performance": row.get("Primary Place of Performance"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new provider vintage")
    args = parser.parse_args()
    pages: list[dict] = []
    rows: list[dict] = []
    failures: list[dict] = []
    for page in range(1, PAGES + 1):
        item = _fetch_page(page, args.refresh)
        pages.append(item)
        response = item["payload"].get("response", {})
        if item["payload"].get("error") or response.get("error"):
            failures.append({"page": page, "path": _relative(item["path"]), "error": item["payload"].get("error") or response.get("error")})
        for row in response.get("results", []) if isinstance(response.get("results", []), list) else []:
            rows.append(_normalize(row))
        if not item.get("cached"):
            time.sleep(0.2)

    rows.sort(key=lambda item: (str(item.get("action_date") or ""), str(item.get("transaction_id"))))
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    missing_required = {
        field: sum(row.get(field) in (None, "") for row in rows)
        for field in ["transaction_id", "award_id", "recipient_name", "action_date", "transaction_amount_usd", "funding_agency"]
    }
    manifest_sources = []
    for page in pages:
        path = page["path"]
        manifest_sources.append({
            "source_id": path.stem,
            "source_url": API_URL,
            "documentation_url": OFFICIAL_DOCS,
            "original_filename": path.name,
            "local_path": _relative(path),
            "retrieval_timestamp_utc": page["payload"].get("retrieval_timestamp_utc"),
            "request": page["payload"].get("request"),
            "sha256": sha256(path),
            "units": "transaction amount in current U.S. dollars as reported by USAspending",
            "coverage": f"Department of Energy; FY2024 ({START_DATE} to {END_DATE}); page {path.stem[-2:]}",
            "benchmark_role": "bounded public federal-award payer/recipient ledger; not a bank settlement ledger",
        })
    request_success = len(failures) == 0 and all(page["payload"].get("response", {}).get("results") is not None for page in pages)
    status = "PASS_WITH_BOUNDARY" if rows and request_success and not any(missing_required.values()) else ("WARN" if rows else "BLOCKED")
    manifest = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "official_page": "https://www.usaspending.gov/",
        "api_url": API_URL,
        "documentation_url": OFFICIAL_DOCS,
        "retrieval_vintage": "2026-08-01",
        "terms": "Public USAspending API; DATA Act federal-award data; retain provider attribution and API terms.",
        "coverage": f"{AGENCY}, FY2024, contract award codes {','.join(AWARD_TYPE_CODES)}, {PAGES} pages of {PAGE_LIMIT}",
        "no_imputation": True,
        "sources": manifest_sources,
        "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(rows)},
        "status": status,
    }
    manifest_path = RAW_DIR / "source_manifest.json"
    write_json(manifest_path, manifest)
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "USASPENDING_PUBLIC_AWARD_LEDGER_SOURCE_LOCKED" if status == "PASS_WITH_BOUNDARY" else "USASPENDING_PUBLIC_AWARD_LEDGER_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(manifest_path), "sha256": sha256(manifest_path), "status": status},
        "coverage": {
            "agency": AGENCY,
            "fiscal_year": 2024,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "pages_requested": PAGES,
            "page_limit": PAGE_LIMIT,
            "rows": len(rows),
            "unique_transaction_ids": len({row["transaction_id"] for row in rows}),
            "missing_required_fields": missing_required,
            "no_imputation": True,
        },
        "funding_source_identification": {
            "status": "NOT_IDENTIFIED",
            "boundary": "USAspending identifies federal awarding/funding agencies and obligations, not whether each obligation was financed by taxes, borrowing, or money creation."
        },
        "request_failures": failures,
        "normalized_panel": {"path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED)},
        "claim_boundary": "This is a bounded public federal-award transaction ledger. It can identify an agency-to-recipient award obligation with NAICS/PSC metadata, but it is not private-sector invoice provenance, a bank settlement ledger, or proof of physical resource transformation.",
        "limitations": [
            "The sample is limited to the Department of Energy, FY2024, contract award codes, and five API pages.",
            "Award obligation is not the same as cash settlement or final supplier payment.",
            "Subawards, subcontractor invoices, payroll, and private-sector transactions are not fully represented.",
            "The federal financing source (tax, debt, or money creation) is not identified at transaction level.",
        ],
    }
    write_json(ARTIFACT, artifact)
    print("USAspending federal award ledger:", status, "rows", len(rows), "failures", len(failures))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
