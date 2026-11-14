"""Audit federal-account budgetary resources for accounts observed in fixed awards.

This lane adds budget-account context to the award/account provenance chain.  It
records account identity, FY2024 budget authority, appropriations, obligations,
outlays, and unobligated balances from USAspending's account endpoints.  Those
are federal budget-accounting quantities; they are not a bank settlement ledger
and do not identify whether a dollar came from taxes, borrowing, cash balances,
or money creation.
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

from economic_hardening_common import (
    ARTIFACT_DIR,
    AWARD_FUNDING_ACCOUNT_ARTIFACT,
    RAW_ROOT,
    ROOT,
    sha256,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_usaspending_federal_account_budget_resource_audit.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_federal_account_budget_resource_2024.csv"
BASE = "https://api.usaspending.gov"
DOCS = "https://api.usaspending.gov/docs/endpoints"
FISCAL_YEAR = 2024
AGENCY_CODE = "089"


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_account_codes() -> list[str]:
    payload = json.loads(AWARD_FUNDING_ACCOUNT_ARTIFACT.read_text(encoding="utf-8"))
    accounts = payload.get("funding_linkage", {}).get("unique_federal_accounts", [])
    return sorted({str(value) for value in accounts if value})


def _fetch(url: str, filename: str, refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("request", {}).get("url") == url:
                return {"path": path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "UET-Economics-Research/1.0 (public research)",
            },
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        body = {"error": str(exc)}
        error = str(exc)
    wrapped = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "source_url": url,
        "documentation_url": DOCS,
        "retrieval_timestamp_utc": utc_now(),
        "retrieval_vintage": "2026-08-01",
        "request": {"url": url},
        "response": body,
        "error": error,
    }
    write_json(path, wrapped)
    return {"path": path, "payload": wrapped, "cached": False}


def _page_urls(account_code: str, endpoint: str) -> list[str]:
    first = f"{BASE}/api/v2/federal_accounts/{account_code}/{endpoint}/"
    return [first]


def _fetch_paged(account_code: str, endpoint: str, prefix: str, refresh: bool) -> list[dict]:
    first = _fetch(_page_urls(account_code, endpoint)[0], f"{prefix}_{account_code}_page_1.json", refresh)
    items = [first]
    first_response = first["payload"].get("response", {})
    metadata = first_response.get("page_metadata", {}) if isinstance(first_response, dict) else {}
    page = metadata.get("next")
    while page:
        url = f"{BASE}/api/v2/federal_accounts/{account_code}/{endpoint}/?page={int(page)}"
        item = _fetch(url, f"{prefix}_{account_code}_page_{int(page)}.json", refresh)
        items.append(item)
        metadata = item["payload"].get("response", {}).get("page_metadata", {})
        page = metadata.get("next")
    return items


def _number(value):
    if value in (None, "", "null"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _record_source(item: dict, role: str) -> dict:
    payload = item["payload"]
    return {
        "source_url": payload.get("source_url"),
        "documentation_url": payload.get("documentation_url"),
        "terms": "U.S. government public API; no separate dataset license notice observed at retrieval",
        "original_filename": item["path"].name,
        "local_path": _relative(item["path"]),
        "retrieval_timestamp_utc": payload.get("retrieval_timestamp_utc"),
        "retrieval_vintage": payload.get("retrieval_vintage"),
        "preprocessing": "Cached JSON response; account profile and FY2024 snapshot fields selected; no imputation",
        "units": "current U.S. dollars for budgetary-resource fields; account codes and IDs are categorical identifiers",
        "coverage": "fixed federal accounts observed in the prior ten-award FY2024 funding-account sample",
        "sha256": sha256(item["path"]),
        "benchmark_role": role,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new provider vintage")
    args = parser.parse_args()

    if not AWARD_FUNDING_ACCOUNT_ARTIFACT.exists():
        print("Federal-account budget-resource audit: BLOCKED (award funding-account artifact missing)")
        return 1
    account_codes = _load_account_codes()
    if not account_codes:
        print("Federal-account budget-resource audit: BLOCKED (no observed federal accounts)")
        return 1

    items: list[dict] = []
    failures: list[dict] = []
    account_records: list[dict] = []
    for account_code in account_codes:
        profile = _fetch(
            f"{BASE}/api/v2/federal_accounts/{account_code}/",
            f"federal_account_profile_{account_code}.json",
            args.refresh,
        )
        items.append(profile)
        profile_body = profile["payload"].get("response", {})
        internal_id = profile_body.get("id") if isinstance(profile_body, dict) else None
        if not internal_id:
            failures.append({"account_code": account_code, "stage": "profile", "error": "missing internal account id"})
            continue

        snapshot_url = f"{BASE}/api/v2/federal_accounts/{int(internal_id)}/fiscal_year_snapshot/{FISCAL_YEAR}/"
        snapshot = _fetch(snapshot_url, f"federal_account_snapshot_{account_code}_{FISCAL_YEAR}.json", args.refresh)
        items.append(snapshot)
        tas_url = f"{BASE}/api/v2/references/filter_tree/tas/{AGENCY_CODE}/{urllib.parse.quote(account_code, safe='')}/"
        tas = _fetch(tas_url, f"federal_account_tas_{account_code}.json", args.refresh)
        items.append(tas)
        programs = _fetch_paged(account_code, "program_activities", "federal_account_program_activities", args.refresh)
        items.extend(programs)

        snapshot_body = snapshot["payload"].get("response", {})
        snapshot_results = snapshot_body.get("results", {}) if isinstance(snapshot_body, dict) else {}
        if snapshot.get("payload", {}).get("error") or not isinstance(snapshot_results, dict):
            failures.append({"account_code": account_code, "stage": "fiscal_year_snapshot", "error": snapshot.get("payload", {}).get("error") or "missing results"})
            continue
        program_rows = []
        for program_item in programs:
            program_body = program_item["payload"].get("response", {})
            if isinstance(program_body, dict):
                program_rows.extend(program_body.get("results", []) or [])
        tas_body = tas["payload"].get("response", {})
        tas_rows = tas_body.get("results", []) if isinstance(tas_body, dict) else []
        budget_authority = _number(snapshot_results.get("budget_authority"))
        obligated = _number(snapshot_results.get("obligated"))
        unobligated = _number(snapshot_results.get("unobligated"))
        resource_identity_residual = None
        if budget_authority is not None and obligated is not None and unobligated is not None:
            resource_identity_residual = round(budget_authority - obligated - unobligated, 2)
        account_records.append(
            {
                "federal_account": account_code,
                "internal_account_id": int(internal_id),
                "account_title": profile_body.get("account_title"),
                "agency_identifier": profile_body.get("agency_identifier"),
                "agency_name": profile_body.get("parent_agency_name"),
                "bureau_name": profile_body.get("bureau_name"),
                "snapshot_fiscal_year": FISCAL_YEAR,
                "budget_authority_usd": budget_authority,
                "appropriations_usd": _number(snapshot_results.get("appropriations")),
                "other_budgetary_resources_usd": _number(snapshot_results.get("other_budgetary_resources")),
                "balance_brought_forward_usd": _number(snapshot_results.get("balance_brought_forward")),
                "obligated_usd": obligated,
                "outlay_usd": _number(snapshot_results.get("outlay")),
                "unobligated_usd": unobligated,
                "budget_authority_minus_obligation_minus_unobligated_usd": resource_identity_residual,
                "program_activity_rows": len(program_rows),
                "tas_rows": len(tas_rows),
            }
        )
        if not profile.get("cached") or not snapshot.get("cached") or not tas.get("cached"):
            time.sleep(0.15)

    fieldnames = list(account_records[0]) if account_records else [
        "federal_account",
        "internal_account_id",
        "account_title",
        "agency_identifier",
        "agency_name",
        "bureau_name",
        "snapshot_fiscal_year",
        "budget_authority_usd",
        "appropriations_usd",
        "other_budgetary_resources_usd",
        "balance_brought_forward_usd",
        "obligated_usd",
        "outlay_usd",
        "unobligated_usd",
        "budget_authority_minus_obligation_minus_unobligated_usd",
        "program_activity_rows",
        "tas_rows",
    ]
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(account_records)

    source_records = [_record_source(item, "federal-account budgetary-resource input") for item in items]
    max_identity_residual = max(
        (abs(row["budget_authority_minus_obligation_minus_unobligated_usd"] or 0.0) for row in account_records),
        default=None,
    )
    identity_status = "PASS" if max_identity_residual is not None and max_identity_residual <= 0.01 else "WARN"
    status = (
        "PASS_WITH_BOUNDARY"
        if account_records and not failures and len(account_records) == len(account_codes) and identity_status == "PASS"
        else ("WARN" if account_records else "BLOCKED")
    )
    manifest = {
        "schema_version": "1.0",
        "provider": "USAspending.gov / U.S. Treasury",
        "official_page": "https://api.usaspending.gov/",
        "documentation_url": DOCS,
        "retrieval_vintage": "2026-08-01",
        "coverage": "all unique federal accounts returned by the fixed ten-award funding-account sample; FY2024 snapshot",
        "selection_policy": "derive account set from the prior frozen award funding-account artifact; do not add accounts after inspecting budget results",
        "no_imputation": True,
        "account_codes": account_codes,
        "sources": source_records,
        "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(account_records)},
        "status": status,
    }
    manifest_path = RAW_DIR / "federal_account_budget_resource_manifest.json"
    write_json(manifest_path, manifest)
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "FEDERAL_ACCOUNT_BUDGET_RESOURCE_BOUNDARY" if status == "PASS_WITH_BOUNDARY" else "FEDERAL_ACCOUNT_BUDGET_RESOURCE_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(manifest_path), "sha256": sha256(manifest_path), "status": status},
        "coverage": {
            "fiscal_year": FISCAL_YEAR,
            "requested_accounts": len(account_codes),
            "accounts_with_profile_and_snapshot": len(account_records),
            "no_imputation": True,
        },
        "accounting_identity_check": {
            "formula": "budget_authority = obligated + unobligated",
            "tolerance_usd": 0.01,
            "max_abs_residual_usd": max_identity_residual,
            "status": identity_status,
            "interpretation": "rounded account-reporting identity check; not a financing-source or settlement test",
        },
        "normalized_panel": {"path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(account_records)},
        "account_records": account_records,
        "request_failures": failures,
        "interpretation": "USAspending account snapshots report budget authority, appropriations, other budgetary resources, obligations, outlays, and unobligated balances for federal reporting accounts. These are budget-accounting quantities, not bank settlement observations or ultimate financing-source allocations.",
        "claim_boundary": "This artifact supports bounded federal-account budget-resource provenance only. It does not establish tax-versus-debt-versus-money-creation funding, supplier payment, profit funding, or physical-resource transformation.",
        "limitations": [
            "The account set is inherited from a fixed ten-award sample and is not representative of all federal spending.",
            "The API profile can expose a current/latest fiscal-year view; the primary values here are explicitly the FY2024 internal-ID snapshot.",
            "Budget authority and appropriations are budgetary constructs and cannot be treated as cash settlement or a dollar-by-dollar financing trace.",
            "The identity budget_authority = obligated + unobligated is an account reporting check, not proof of where funding originated.",
        ],
    }
    write_json(ARTIFACT, artifact)
    print("USAspending federal-account budget-resource audit:", status, "accounts", len(account_records), "failures", len(failures))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
