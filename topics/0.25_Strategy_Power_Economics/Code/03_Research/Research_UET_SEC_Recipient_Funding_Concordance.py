"""Concordance fixed-award recipients with exact SEC public-firm identities.

The concordance is deliberately exact-name only.  It combines the frozen prime
award and downstream subaward recipient names, archives the SEC company-ticker
registry, and retrieves company-facts JSON for every unique exact match.  The
result can compare firm-level profit, operating cash flow, capex, debt, and cash
channels around FY2024, but it cannot assign any one award dollar to a firm's
invoice or prove that an award was financed by profit rather than borrowing.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_sec_recipient_funding_concordance_audit.json"
RAW_DIR = RAW_ROOT / "sec_xbrl" / "2026-08-01"
TICKER_PATH = RAW_DIR / "company_tickers.json"
SUBAWARD_CSV = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_subaward_downstream_recipients_2024.csv"
PRIME_CSV = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_doe_fy2024_transactions.csv"
CONCORDANCE_CSV = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "sec_recipient_firm_concordance_2024.csv"
FACTS_CSV = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "sec_recipient_funding_channels_2010_2024.csv"
TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
API_ROOT = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SEC_DOCS = "https://www.sec.gov/edgar/sec-api-documentation"
SEC_TICKER_DOCS = "https://www.sec.gov/file/company-tickers"
USER_AGENT = "UET-Economics-Audit/1.0 (public research)"
START_YEAR = 2010
END_YEAR = 2024
PRIMARY_YEAR = 2024

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


def _norm_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", value.upper().replace("&", "AND"))


def _number(value):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _fy(action_date: str | None) -> int | None:
    if not action_date:
        return None
    try:
        parsed = date.fromisoformat(str(action_date)[:10])
    except ValueError:
        return None
    return parsed.year + 1 if parsed.month >= 10 else parsed.year


def _fetch_json(url: str, path: Path, refresh: bool, body: dict | None = None) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("request", {}).get("url") == url:
                return cached
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8") if body is not None else None,
            method="POST" if body is not None else "GET",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        response_body = {"status": "REQUEST_FAILED", "error": str(exc)}
        error = str(exc)
    wrapper = {
        "schema_version": "1.0",
        "provider": "U.S. Securities and Exchange Commission",
        "source_url": url,
        "documentation_url": SEC_DOCS,
        "retrieval_timestamp_utc": utc_now(),
        "retrieval_vintage": "2026-08-01",
        "request": {"url": url, "method": "POST" if body is not None else "GET", "body": body},
        "response": response_body,
        "error": error,
    }
    write_json(path, wrapper)
    return wrapper


def _annual_facts(facts: dict, tag: str) -> dict[int, float]:
    tag_payload = facts.get("us-gaap", {}).get(tag, {})
    records = tag_payload.get("units", {}).get("USD", [])
    selected: dict[int, tuple[str, float]] = {}
    for record in records:
        if record.get("form") not in {"10-K", "10-K/A"}:
            continue
        try:
            fiscal_year = int(record.get("fy"))
            value = float(record.get("val"))
        except (TypeError, ValueError):
            continue
        if not START_YEAR <= fiscal_year <= END_YEAR or not math.isfinite(value):
            continue
        start, end = record.get("start"), record.get("end")
        if start and end:
            try:
                duration = (date.fromisoformat(end) - date.fromisoformat(start)).days
            except ValueError:
                duration = 365
            if not 300 <= duration <= 400:
                continue
        filed = str(record.get("filed", ""))
        previous = selected.get(fiscal_year)
        if previous is None or filed > previous[0]:
            selected[fiscal_year] = (filed, value)
    return {year: value for year, (_filed, value) in selected.items()}


def _source_record(path: Path, url: str, role: str, preprocessing: str) -> dict:
    return {
        "source_url": url,
        "documentation_url": SEC_DOCS,
        "terms": "SEC public data; automated access follows SEC fair-access policy and preserves attribution",
        "original_filename": path.name,
        "local_path": _relative(path),
        "retrieval_timestamp_utc": json.loads(path.read_text(encoding="utf-8")).get("retrieval_timestamp_utc"),
        "retrieval_vintage": "2026-08-01",
        "preprocessing": preprocessing,
        "units": "USD; annual 10-K XBRL facts; identifiers categorical",
        "coverage": "exact SEC title/recipient match from fixed prime and downstream award panels",
        "sha256": sha256(path),
        "benchmark_role": role,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new SEC source vintage")
    args = parser.parse_args()
    for required in (SUBAWARD_CSV, PRIME_CSV):
        if not required.is_file():
            print("SEC recipient concordance: BLOCKED (missing input)", _relative(required))
            return 1

    subaward_rows = list(csv.DictReader(SUBAWARD_CSV.open(encoding="utf-8")))
    prime_rows = list(csv.DictReader(PRIME_CSV.open(encoding="utf-8")))
    aggregate: dict[str, dict] = {}

    def add_name(name: str, role: str, amount: float | None, fiscal_year: int | None) -> None:
        record = aggregate.setdefault(name, {"recipient_name": name, "roles": set(), "subaward_rows": 0, "subaward_amount_all_year_usd": 0.0, "subaward_rows_primary_year": 0, "subaward_amount_primary_year_usd": 0.0, "prime_transaction_rows": 0, "prime_transaction_amount_all_year_usd": 0.0, "prime_transaction_rows_primary_year": 0, "prime_transaction_amount_primary_year_usd": 0.0})
        record["roles"].add(role)
        if role == "downstream_subaward":
            record["subaward_rows"] += 1
            if amount is not None:
                record["subaward_amount_all_year_usd"] += amount
                if fiscal_year == PRIMARY_YEAR:
                    record["subaward_amount_primary_year_usd"] += amount
            if fiscal_year == PRIMARY_YEAR:
                record["subaward_rows_primary_year"] += 1
        else:
            record["prime_transaction_rows"] += 1
            if amount is not None:
                record["prime_transaction_amount_all_year_usd"] += amount
                if fiscal_year == PRIMARY_YEAR:
                    record["prime_transaction_amount_primary_year_usd"] += amount
            if fiscal_year == PRIMARY_YEAR:
                record["prime_transaction_rows_primary_year"] += 1

    for row in subaward_rows:
        name = str(row.get("recipient_name", "")).strip()
        if name:
            add_name(name, "downstream_subaward", _number(row.get("amount_usd")), int(row["action_fiscal_year_derived"]) if row.get("action_fiscal_year_derived", "").isdigit() else None)
    for row in prime_rows:
        name = str(row.get("recipient_name", "")).strip()
        if name:
            add_name(name, "prime_award", _number(row.get("transaction_amount_usd")), _fy(row.get("action_date")))

    ticker_wrapper = _fetch_json(TICKER_URL, TICKER_PATH, args.refresh)
    ticker_response = ticker_wrapper.get("response", {})
    ticker_entries = list(ticker_response.values()) if isinstance(ticker_response, dict) else []
    by_norm: dict[str, list[dict]] = {}
    for entry in ticker_entries:
        title = entry.get("title")
        if title:
            by_norm.setdefault(_norm_name(title), []).append(entry)

    concordance_rows: list[dict] = []
    matched_ciks: dict[str, dict] = {}
    for name in sorted(aggregate):
        normalized = _norm_name(name)
        matches = by_norm.get(normalized, [])
        if len(matches) == 1:
            match_status = "EXACT_UNIQUE"
            entry = matches[0]
            cik = f"{int(entry['cik_str']):010d}"
            matched_ciks[cik] = entry
        elif matches:
            match_status = "EXACT_AMBIGUOUS"
            entry = {}
            cik = None
        else:
            match_status = "NO_EXACT_MATCH"
            entry = {}
            cik = None
        record = aggregate[name]
        concordance_rows.append({
            "recipient_name": name,
            "normalized_recipient_name": normalized,
            "recipient_role": "+".join(sorted(record["roles"])),
            "match_status": match_status,
            "sec_cik": cik,
            "sec_ticker": entry.get("ticker"),
            "sec_title": entry.get("title"),
            "subaward_rows_all_year": record["subaward_rows"],
            "subaward_amount_all_year_usd": round(record["subaward_amount_all_year_usd"], 2),
            "subaward_rows_primary_year": record["subaward_rows_primary_year"],
            "subaward_amount_primary_year_usd": round(record["subaward_amount_primary_year_usd"], 2),
            "prime_transaction_rows_all_year": record["prime_transaction_rows"],
            "prime_transaction_amount_all_year_usd": round(record["prime_transaction_amount_all_year_usd"], 2),
            "prime_transaction_rows_primary_year": record["prime_transaction_rows_primary_year"],
            "prime_transaction_amount_primary_year_usd": round(record["prime_transaction_amount_primary_year_usd"], 2),
        })

    CONCORDANCE_CSV.parent.mkdir(parents=True, exist_ok=True)
    concordance_fields = list(concordance_rows[0]) if concordance_rows else ["recipient_name", "match_status"]
    with CONCORDANCE_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=concordance_fields)
        writer.writeheader()
        writer.writerows(concordance_rows)

    fact_rows: list[dict] = []
    company_records: list[dict] = []
    source_records = [_source_record(TICKER_PATH, TICKER_URL, "exact recipient-to-SEC registry concordance", "Cache official company_tickers.json; normalize names; exact unique matches only; preserve no-match and ambiguous statuses; no fuzzy matching")]
    for cik, entry in sorted(matched_ciks.items()):
        facts_path = RAW_DIR / f"CIK{cik}_recipient_companyfacts.json"
        url = API_ROOT.format(cik=cik)
        wrapper = _fetch_json(url, facts_path, args.refresh)
        source_records.append(_source_record(facts_path, url, "matched recipient public-firm accounting channels", "Cache companyfacts JSON; select latest filed 10-K/10-K-A annual facts by SEC fiscal year; preserve missing tags; no imputation"))
        response = wrapper.get("response", {})
        if not isinstance(response, dict) or "facts" not in response:
            company_records.append({"cik": cik, "ticker": entry.get("ticker"), "title": entry.get("title"), "status": "BLOCKED", "reason": wrapper.get("error") or response.get("error")})
            continue
        facts = response["facts"]
        series = {field: _annual_facts(facts, tag) for field, tag in TAGS.items()}
        years = sorted(set().union(*(set(values) for values in series.values())))
        matched_names = [row for row in concordance_rows if row.get("sec_cik") == cik]
        for recipient in matched_names:
            for fiscal_year in years:
                row = {
                    "recipient_name": recipient["recipient_name"],
                    "recipient_role": recipient["recipient_role"],
                    "sec_cik": cik,
                    "sec_ticker": entry.get("ticker"),
                    "sec_title": entry.get("title"),
                    "fiscal_year": fiscal_year,
                    "subaward_rows_primary_year": recipient["subaward_rows_primary_year"],
                    "subaward_amount_primary_year_usd": recipient["subaward_amount_primary_year_usd"],
                    "prime_transaction_rows_primary_year": recipient["prime_transaction_rows_primary_year"],
                    "prime_transaction_amount_primary_year_usd": recipient["prime_transaction_amount_primary_year_usd"],
                }
                for field, values in series.items():
                    row[field] = values.get(fiscal_year)
                capex = _number(row.get("capex_raw_usd"))
                repayment = _number(row.get("debt_repayments_raw_usd"))
                proceeds = _number(row.get("debt_proceeds_usd"))
                row["capex_outflow_scale_usd"] = abs(capex) if capex is not None else None
                row["debt_repayment_scale_usd"] = abs(repayment) if repayment is not None else None
                row["debt_net_issuance_scale_usd"] = (proceeds - abs(repayment)) if proceeds is not None and repayment is not None else None
                fact_rows.append(row)
        company_records.append({"cik": cik, "ticker": entry.get("ticker"), "title": entry.get("title"), "status": "PASS_WITH_BOUNDARY" if years else "WARN", "rows": len(years), "years": [min(years), max(years)] if years else None, "matched_recipient_names": len(matched_names), "available_tags": {field: len(values) for field, values in series.items()}})
        if not wrapper.get("request", {}).get("body"):
            time.sleep(0.2)

    fact_rows.sort(key=lambda row: (str(row["recipient_name"]), int(row["fiscal_year"])))
    fact_fields = ["recipient_name", "recipient_role", "sec_cik", "sec_ticker", "sec_title", "fiscal_year", "subaward_rows_primary_year", "subaward_amount_primary_year_usd", "prime_transaction_rows_primary_year", "prime_transaction_amount_primary_year_usd", *TAGS.keys(), "capex_outflow_scale_usd", "debt_repayment_scale_usd", "debt_net_issuance_scale_usd"]
    with FACTS_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fact_fields)
        writer.writeheader()
        writer.writerows(fact_rows)

    exact_unique = [row for row in concordance_rows if row["match_status"] == "EXACT_UNIQUE"]
    ambiguous = [row for row in concordance_rows if row["match_status"] == "EXACT_AMBIGUOUS"]
    no_match = [row for row in concordance_rows if row["match_status"] == "NO_EXACT_MATCH"]
    status = "PASS_WITH_BOUNDARY" if exact_unique and fact_rows and all(record.get("status") == "PASS_WITH_BOUNDARY" for record in company_records) else ("WARN" if concordance_rows else "BLOCKED")
    manifest_path = RAW_DIR / "sec_recipient_funding_concordance_manifest.json"
    manifest = {
        "schema_version": "1.0",
        "provider": "U.S. Securities and Exchange Commission plus source-locked USAspending recipient panels",
        "official_page": SEC_DOCS,
        "ticker_registry_page": SEC_TICKER_DOCS,
        "retrieval_vintage": "2026-08-01",
        "coverage": "all unique recipient names from fixed prime-award and downstream-subaward panels; exact SEC title matching; 2010-2024 annual company facts",
        "selection_policy": "no fuzzy matching and no post-hoc recipient selection; every exact-unique match is included, every ambiguous/no-match name remains in the concordance",
        "no_imputation": True,
        "inputs": {"subaward_csv": _relative(SUBAWARD_CSV), "prime_csv": _relative(PRIME_CSV)},
        "sources": source_records,
        "normalized_panels": {
            "concordance": {"local_path": _relative(CONCORDANCE_CSV), "sha256": sha256(CONCORDANCE_CSV), "rows": len(concordance_rows)},
            "funding_channels": {"local_path": _relative(FACTS_CSV), "sha256": sha256(FACTS_CSV), "rows": len(fact_rows)},
        },
        "status": status,
    }
    write_json(manifest_path, manifest)
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "controller_status": "SEC_RECIPIENT_FUNDING_CONCORDANCE_BOUNDARY" if status == "PASS_WITH_BOUNDARY" else "SEC_RECIPIENT_FUNDING_CONCORDANCE_GATE",
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": _relative(manifest_path), "sha256": sha256(manifest_path), "status": status},
        "coverage": {
            "unique_recipient_names": len(concordance_rows),
            "exact_unique_matches": len(exact_unique),
            "ambiguous_matches": len(ambiguous),
            "no_exact_matches": len(no_match),
            "unique_sec_ciks": len(matched_ciks),
            "facts_rows": len(fact_rows),
            "years": [START_YEAR, END_YEAR],
            "no_imputation": True,
        },
        "matched_companies": company_records,
        "funding_share_identification": {
            "status": "NOT_IDENTIFIED",
            "reason": "SEC net income, operating cash flow, capex, debt, dividends, and cash are annual firm-accounting channels; exact recipient identity does not map any award dollar to a specific invoice or prove profit-versus-borrowing finance.",
        },
        "request_failures": [record for record in company_records if record.get("status") == "BLOCKED"],
        "claim_boundary": "This artifact supports a bounded exact-name recipient-to-public-firm accounting comparison only. It does not establish payment settlement, invoice funding, financing causality, profit funding, debt funding, or physical-resource transformation.",
        "limitations": [
            "Exact-name matching excludes alternate legal names, subsidiaries, private firms, and non-reporting entities; no fuzzy match is used.",
            "The fixed award panels are nonrepresentative and dominated by one downstream award.",
            "SEC company-facts values are current-vintage annual 10-K observations; fiscal years and tag availability vary by issuer.",
            "A firm-level accounting channel is not an earmarked source for a particular government award or subaward payment.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("SEC recipient funding concordance:", status, "names", len(concordance_rows), "exact", len(exact_unique), "CIKs", len(matched_ciks), "fact rows", len(fact_rows))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
