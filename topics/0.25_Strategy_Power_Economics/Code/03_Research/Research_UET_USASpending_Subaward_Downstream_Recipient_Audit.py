"""Audit reported downstream recipients under the frozen USAspending award sample.

USAspending defines a subaward as an agreement made by a prime recipient with
another entity.  This lane therefore adds downstream-recipient and described-
work visibility, but it remains an award-reporting diagnostic: a subaward amount
is not a bank settlement, invoice, payroll record, or proof of the ultimate
financing source.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from economic_hardening_common import (
    ARTIFACT_DIR,
    RAW_ROOT,
    ROOT,
    sha256,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_usaspending_subaward_downstream_recipient_audit.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
AWARD_MANIFEST = RAW_DIR / "award_funding_account_manifest.json"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_subaward_downstream_recipients_2024.csv"
BASE = "https://api.usaspending.gov"
DOCS = "https://api.usaspending.gov/docs/endpoints"
GUIDE = "https://www.usaspending.gov/federal-spending-guide"
PRIMARY_FISCAL_YEAR = 2024
PAGE_LIMIT = 100


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_award_ids() -> list[str]:
    payload = json.loads(AWARD_MANIFEST.read_text(encoding="utf-8"))
    ids = payload.get("sample_policy", {}).get("award_ids", [])
    return [str(value) for value in ids if value]


def _load_internal_ids(award_ids: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for award_id in award_ids:
        path = RAW_DIR / f"award_detail_{award_id.replace('/', '_')}.json"
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        response = payload.get("response", payload)
        if isinstance(response, dict) and response.get("id") is not None:
            mapping[award_id] = int(response["id"])
    return mapping


def _fetch_get(url: str, filename: str, refresh: bool) -> dict:
    return _fetch(url, filename, refresh, method="GET", body=None)


def _fetch_post(url: str, filename: str, payload: dict, refresh: bool) -> dict:
    return _fetch(url, filename, refresh, method="POST", body=payload)


def _fetch(url: str, filename: str, refresh: bool, *, method: str, body: dict | None) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("request", {}).get("url") == url and cached.get("request", {}).get("body") == body:
                return {"path": path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        encoded = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            url,
            data=encoded,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "UET-Economics-Research/1.0 (public research)",
            },
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        response_body = {"error": str(exc)}
        error = str(exc)
    wrapped = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "source_url": url,
        "documentation_url": DOCS,
        "retrieval_timestamp_utc": utc_now(),
        "retrieval_vintage": "2026-08-01",
        "request": {"url": url, "method": method, "body": body},
        "response": response_body,
        "error": error,
    }
    write_json(path, wrapped)
    return {"path": path, "payload": wrapped, "cached": False}


def _fy(action_date: str | None) -> int | None:
    if not action_date:
        return None
    try:
        parsed = date.fromisoformat(action_date[:10])
    except ValueError:
        return None
    return parsed.year + 1 if parsed.month >= 10 else parsed.year


def _source_record(item: dict, role: str) -> dict:
    payload = item["payload"]
    return {
        "source_url": payload.get("source_url"),
        "documentation_url": payload.get("documentation_url"),
        "terms": "U.S. government public API; subaward data are award-reporting records; no separate dataset license notice observed at retrieval",
        "original_filename": item["path"].name,
        "local_path": _relative(item["path"]),
        "retrieval_timestamp_utc": payload.get("retrieval_timestamp_utc"),
        "retrieval_vintage": payload.get("retrieval_vintage"),
        "preprocessing": "Cached JSON response; preserve page/count metadata; normalize recipient, action date, amount, and description; derive fiscal year from action_date; no imputation",
        "units": "current U.S. dollars for reported subaward amount; dates and identifiers are categorical/time fields",
        "coverage": "fixed ten-award sample; count endpoint for all awards; paginated subaward rows for awards reporting positive counts",
        "sha256": sha256(item["path"]),
        "benchmark_role": role,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new provider vintage")
    args = parser.parse_args()

    if not AWARD_MANIFEST.exists():
        print("USAspending subaward downstream audit: BLOCKED (award manifest missing)")
        return 1
    award_ids = _load_award_ids()
    internal_ids = _load_internal_ids(award_ids)
    if not award_ids or len(internal_ids) != len(award_ids):
        print("USAspending subaward downstream audit: BLOCKED (fixed award internal IDs incomplete)")
        return 1

    items: list[dict] = []
    failures: list[dict] = []
    count_by_award: dict[str, int] = {}
    rows: list[dict] = []
    pages_by_award: dict[str, int] = {}
    for award_id in award_ids:
        encoded_award = urllib.parse.quote(award_id, safe="")
        count_url = f"{BASE}/api/v2/awards/count/subaward/{encoded_award}/"
        count_item = _fetch_get(count_url, f"subaward_count_{award_id}.json", args.refresh)
        items.append(count_item)
        count_body = count_item["payload"].get("response", {})
        expected = count_body.get("subawards") if isinstance(count_body, dict) else None
        try:
            expected_count = int(expected)
        except (TypeError, ValueError):
            expected_count = None
        if expected_count is None:
            failures.append({"award_id": award_id, "stage": "count", "error": "missing subaward count"})
            continue
        count_by_award[award_id] = expected_count
        page = 1
        retrieved = 0
        while True:
            page_payload = {"award_id": internal_ids[award_id], "page": page, "limit": PAGE_LIMIT}
            page_item = _fetch_post(
                f"{BASE}/api/v2/subawards/",
                f"subaward_{award_id}_page_{page}.json",
                page_payload,
                args.refresh,
            )
            items.append(page_item)
            body = page_item["payload"].get("response", {})
            result_rows = body.get("results", []) if isinstance(body, dict) else []
            if page_item["payload"].get("error") or not isinstance(result_rows, list):
                failures.append({"award_id": award_id, "stage": "subaward_page", "page": page, "error": page_item["payload"].get("error") or "missing results"})
                break
            for raw in result_rows:
                rows.append(
                    {
                        "prime_award_id": award_id,
                        "prime_award_internal_id": internal_ids[award_id],
                        "subaward_id": raw.get("id"),
                        "subaward_number": raw.get("subaward_number"),
                        "action_date": raw.get("action_date"),
                        "action_fiscal_year_derived": _fy(raw.get("action_date")),
                        "amount_usd": raw.get("amount"),
                        "recipient_name": raw.get("recipient_name"),
                        "description": raw.get("description"),
                    }
                )
            retrieved += len(result_rows)
            metadata = body.get("page_metadata", {}) if isinstance(body, dict) else {}
            next_page = metadata.get("next")
            if not next_page:
                break
            page = int(next_page)
        pages_by_award[award_id] = page
        if retrieved != expected_count:
            failures.append({"award_id": award_id, "stage": "coverage", "expected_count": expected_count, "retrieved_count": retrieved, "error": "reported count does not equal retrieved page rows"})
        if not count_item.get("cached"):
            time.sleep(0.1)

    rows.sort(key=lambda row: (row["prime_award_id"], str(row["action_date"]), str(row["subaward_id"])))
    fieldnames = [
        "prime_award_id",
        "prime_award_internal_id",
        "subaward_id",
        "subaward_number",
        "action_date",
        "action_fiscal_year_derived",
        "amount_usd",
        "recipient_name",
        "description",
    ]
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    complete_awards = [award_id for award_id in award_ids if award_id in count_by_award and not any(f.get("award_id") == award_id for f in failures)]
    status = "PASS_WITH_BOUNDARY" if len(complete_awards) == len(award_ids) and rows else ("WARN" if count_by_award else "BLOCKED")
    primary_rows = [row for row in rows if row.get("action_fiscal_year_derived") == PRIMARY_FISCAL_YEAR]
    manifest_path = RAW_DIR / "subaward_downstream_recipient_manifest.json"
    manifest = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "official_page": "https://api.usaspending.gov/",
        "documentation_url": DOCS,
        "guide_url": GUIDE,
        "retrieval_vintage": "2026-08-01",
        "coverage": "fixed ten-award sample; all reported subaward pages retrieved at limit 100; primary descriptive slice is action_fiscal_year_derived=2024",
        "selection_policy": "inherit the first-ten fixed generated award IDs from award_level_outlay_manifest.json; query all ten counts and all pages for every award with a positive reported count",
        "page_limit": PAGE_LIMIT,
        "no_imputation": True,
        "award_ids": award_ids,
        "reported_subaward_counts": count_by_award,
        "pages_by_award": pages_by_award,
        "sources": [_source_record(item, "USAspending subaward count or downstream-recipient response") for item in items],
        "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(rows), "primary_fiscal_year_rows": len(primary_rows)},
        "status": status,
    }
    write_json(manifest_path, manifest)
    total_amount = sum(float(row["amount_usd"]) for row in rows if row.get("amount_usd") not in (None, ""))
    primary_amount = sum(float(row["amount_usd"]) for row in primary_rows if row.get("amount_usd") not in (None, ""))
    recipients = sorted({row["recipient_name"] for row in rows if row.get("recipient_name")})
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "SUBAWARD_DOWNSTREAM_RECIPIENT_BOUNDARY" if status == "PASS_WITH_BOUNDARY" else "SUBAWARD_DOWNSTREAM_RECIPIENT_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(manifest_path), "sha256": sha256(manifest_path), "status": status},
        "coverage": {
            "requested_awards": len(award_ids),
            "complete_awards": len(complete_awards),
            "reported_subaward_rows": len(rows),
            "primary_fiscal_year": PRIMARY_FISCAL_YEAR,
            "primary_fiscal_year_rows": len(primary_rows),
            "unique_downstream_recipients": len(recipients),
            "no_imputation": True,
        },
        "reported_subaward_counts": count_by_award,
        "summary": {
            "all_year_reported_amount_usd": total_amount,
            "primary_fiscal_year_reported_amount_usd": primary_amount,
            "unique_recipients": recipients,
        },
        "request_failures": failures,
        "interpretation": "USAspending subaward records identify agreements reported by a prime recipient with downstream entities and reported amounts/descriptions. They add downstream-recipient visibility but are not bank settlement, invoice, payroll, or ultimate financing-source observations.",
        "claim_boundary": "This artifact supports bounded downstream-award and described-work provenance only. It does not establish that a reported amount was paid, that a particular resource was purchased, or that funds came from taxes, debt, cash balances, money creation, or profit.",
        "limitations": [
            "Subaward reporting is incomplete when primes do not report; the fixed sample is not representative.",
            "Reported subaward amount and action date are award-reporting fields, not settlement dates or bank transfers.",
            "Descriptions are text metadata and do not prove the physical resource, labor, or innovation actually delivered.",
        ],
    }
    write_json(ARTIFACT, artifact)
    print("USAspending subaward downstream audit:", status, "rows", len(rows), "complete_awards", len(complete_awards), "failures", len(failures))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
