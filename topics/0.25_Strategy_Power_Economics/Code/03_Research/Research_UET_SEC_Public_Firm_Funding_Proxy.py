"""Build a source-locked public-firm funding-to-capital proxy panel.

SEC XBRL company facts can show annual net income, operating cash flow,
capital expenditure, selected debt flows, dividends, and cash balances for
public companies.  They cannot identify the payer of each invoice or the
physical resource behind a project.  This lane therefore reports observed
firm-level accounting channels and keeps funding shares explicitly
``NOT_IDENTIFIED``.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date
import time
import urllib.error
import urllib.request
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_sec_public_firm_funding_proxy.json"
RAW_DIR = RAW_ROOT / "sec_xbrl" / "2026-07-16"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "sec_public_firm_funding_proxy_2010_2024.csv"
MANIFEST = RAW_DIR / "source_manifest.json"
API_ROOT = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
USER_AGENT = "UET-Economics-Audit/1.0 (public research)"
START_YEAR = 2010
END_YEAR = 2024

# Predeclared before reading the results: diversified nonfinancial public firms
# with operations spanning production, logistics, retail, energy, and technology.
FIRMS = {
    "apple": {"cik": "0000320193", "sector": "technology"},
    "microsoft": {"cik": "0000789019", "sector": "technology"},
    "amazon": {"cik": "0001018724", "sector": "retail_logistics"},
    "walmart": {"cik": "0000104169", "sector": "retail_logistics"},
    "exxon_mobil": {"cik": "0000034088", "sector": "energy"},
    "chevron": {"cik": "0000093410", "sector": "energy"},
    "boeing": {"cik": "0000012927", "sector": "manufacturing"},
    "ford": {"cik": "0000037996", "sector": "manufacturing"},
    "caterpillar": {"cik": "0000018230", "sector": "manufacturing"},
    "home_depot": {"cik": "0000354950", "sector": "retail_logistics"},
}

TAGS = {
    "net_income_usd": "NetIncomeLoss",
    "operating_cash_flow_usd": "NetCashProvidedByUsedInOperatingActivities",
    "capex_raw_usd": "PaymentsToAcquirePropertyPlantAndEquipment",
    "debt_proceeds_usd": "ProceedsFromIssuanceOfLongTermDebt",
    "debt_repayments_raw_usd": "RepaymentsOfLongTermDebt",
    "common_dividends_raw_usd": "PaymentsOfDividendsCommonStock",
    "cash_balance_usd": "CashAndCashEquivalentsAtCarryingValue",
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _number(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _fetch_or_load(company: str, cik: str, refresh: bool) -> tuple[dict | None, Path, str | None]:
    path = RAW_DIR / f"CIK{cik}_companyfacts.json"
    if path.is_file() and not refresh:
        try:
            wrapper = json.loads(path.read_text(encoding="utf-8"))
            response = wrapper.get("response", wrapper if "facts" in wrapper else None)
            return response, path, wrapper.get("retrieval_timestamp_utc")
        except (OSError, json.JSONDecodeError):
            pass
    url = API_ROOT.format(cik=cik)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        payload = {"status": "REQUEST_FAILED", "error": str(exc)}
    retrieved = utc_now()
    write_json(path, {"schema_version": "1.0", "provider": "U.S. Securities and Exchange Commission", "source_url": url, "retrieval_timestamp_utc": retrieved, "request_headers": {"User-Agent": USER_AGENT}, "response": payload})
    return payload, path, retrieved


def _annual_facts(facts: dict, tag: str) -> dict[int, tuple[float, str]]:
    """Select the latest filed 10-K annual duration/instant fact per fiscal year."""
    payload = facts.get("us-gaap", {}).get(tag, {})
    units = payload.get("units", {})
    records = units.get("USD", [])
    selected: dict[int, tuple[str, float]] = {}
    for record in records:
        form = record.get("form")
        if form not in {"10-K", "10-K/A"}:
            continue
        fy = record.get("fy")
        if fy is None:
            continue
        try:
            year = int(fy)
            value = float(record.get("val"))
        except (TypeError, ValueError):
            continue
        if year < START_YEAR or year > END_YEAR or not math.isfinite(value):
            continue
        start, end = record.get("start"), record.get("end")
        if start and end:
            # Cash-flow facts should represent roughly one fiscal year.
            try:
                duration = (date.fromisoformat(end) - date.fromisoformat(start)).days
            except ValueError:
                duration = 365
            if not 300 <= duration <= 400:
                continue
        filed = str(record.get("filed", ""))
        previous = selected.get(year)
        if previous is None or filed > previous[0]:
            selected[year] = (filed, value)
    return {year: value for year, (_filed, value) in selected.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Refresh SEC company-facts archives.")
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    company_records: list[dict[str, object]] = []
    source_records: list[dict[str, object]] = []
    for company, spec in FIRMS.items():
        response, path, retrieved = _fetch_or_load(company, spec["cik"], args.refresh)
        source_records.append({"source_id": f"sec_companyfacts_{company}", "source_url": API_ROOT.format(cik=spec["cik"]), "original_filename": path.name, "local_path": _relative(path), "retrieval_timestamp_utc": retrieved, "sha256": sha256(path), "units": "USD; annual 10-K facts", "benchmark_role": "public-firm accounting funding proxy; not payer ledger"})
        if not response or response.get("status") == "REQUEST_FAILED" or "facts" not in response:
            company_records.append({"company": company, "cik": spec["cik"], "sector": spec["sector"], "status": "BLOCKED", "reason": response.get("error") if response else "missing response"})
            continue
        facts = response["facts"]
        series = {field: _annual_facts(facts, tag) for field, tag in TAGS.items()}
        years = sorted(set().union(*(set(values) for values in series.values())))
        company_rows = 0
        for year in years:
            row: dict[str, object] = {"company": company, "cik": spec["cik"], "sector": spec["sector"], "fiscal_year": year}
            for field, values in series.items():
                row[field] = values.get(year)
            # Provider outflow signs are preserved; these are convenience scales, not shares.
            capex = _number(row.get("capex_raw_usd"))
            debt_repayments = _number(row.get("debt_repayments_raw_usd"))
            dividends = _number(row.get("common_dividends_raw_usd"))
            row["capex_outflow_scale_usd"] = abs(capex) if capex is not None else None
            row["debt_repayment_scale_usd"] = abs(debt_repayments) if debt_repayments is not None else None
            row["retained_profit_proxy_usd"] = (_number(row.get("net_income_usd")) or 0.0) + (dividends if dividends is not None else 0.0)
            rows.append(row)
            company_rows += 1
        company_records.append({"company": company, "cik": spec["cik"], "sector": spec["sector"], "status": "PASS_WITH_BOUNDARY" if company_rows else "WARN", "rows": company_rows, "years": [min(years), max(years)] if years else None, "available_tags": {field: len(values) for field, values in series.items()}})
        time.sleep(0.2)

    rows.sort(key=lambda row: (str(row["company"]), int(row["fiscal_year"])))
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    fields = ["company", "cik", "sector", "fiscal_year", *TAGS.keys(), "capex_outflow_scale_usd", "debt_repayment_scale_usd", "retained_profit_proxy_usd"]
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {"schema_version": "1.0", "provider": "U.S. Securities and Exchange Commission", "official_page": "https://www.sec.gov/edgar/sec-api-documentation", "retrieval_vintage": "2026-07-16", "terms": "SEC public data; follow SEC fair-access policy and preserve attribution.", "coverage": f"{len(FIRMS)} predeclared nonfinancial public firms; {START_YEAR}-{END_YEAR}", "sources": source_records, "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(rows)}, "status": "PASS_WITH_BOUNDARY" if rows and all(item.get("status") == "PASS_WITH_BOUNDARY" for item in company_records) else ("WARN" if rows else "BLOCKED")}
    write_json(MANIFEST, manifest)
    payload = {"schema_version": "1.0", "topic": "0.25_Strategy_Power_Economics", "status": manifest["status"], "controller_status": "SEC_PUBLIC_FIRM_PROXY_SOURCE_LOCKED" if manifest["status"] == "PASS_WITH_BOUNDARY" else "SEC_PUBLIC_FIRM_PROXY_GATE", "generated_at_utc": utc_now(), "source_manifest": {"path": _relative(MANIFEST), "sha256": sha256(MANIFEST), "status": manifest["status"]}, "companies": company_records, "coverage": {"rows": len(rows), "years": [START_YEAR, END_YEAR], "no_imputation": True}, "funding_share_identification": {"status": "NOT_IDENTIFIED", "reason": "Net income, debt proceeds, debt repayments, and capex are annual firm-accounting channels; they do not identify which dollar paid which invoice or prevent refinancing/working-capital overlap."}, "claim_boundary": "Public-firm accounting proxy only. It can compare observed profit/debt/cash/capex channels for the predeclared firms; it cannot establish economy-wide payer provenance, project-level payment identity, physical resource use, or causality.", "limitations": ["SEC company facts cover public registrants only and are not representative of all firms.", "Annual 10-K facts are current-vintage observations, not historical-as-of releases.", "Tag availability and fiscal-year definitions vary by issuer; missing facts remain missing."]}
    write_json(ARTIFACT, payload)
    print("SEC public-firm funding proxy:", payload["status"], "companies", len(FIRMS), "rows", len(rows))
    return 0 if payload["status"] in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
