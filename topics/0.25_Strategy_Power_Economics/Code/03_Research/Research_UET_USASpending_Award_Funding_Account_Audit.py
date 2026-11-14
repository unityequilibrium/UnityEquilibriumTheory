"""Link a fixed USAspending award sample to federal accounts and funding agencies.

The award-funding endpoint exposes public accounting linkages: federal account,
account title, funding agency, object class, transaction obligation, and gross
outlay. This is closer to payer/account provenance than a grouped obligation,
but it is not a bank settlement ledger and does not reveal whether an account
was funded by taxes, debt, cash balances, or money creation.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, sha256, utc_now, write_json

ARTIFACT = ARTIFACT_DIR / "0_25_usaspending_award_funding_account_audit.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
MANIFEST_PATH = RAW_DIR / "award_funding_account_manifest.json"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_award_funding_account_2024.csv"
BASE = "https://api.usaspending.gov/api/v2/awards/funding/"
DOCS = "https://api.usaspending.gov/docs/endpoints"
AWARD_IDS = [
    "CONT_AWD_89233018CNR000004_8900_-NONE-_-NONE-",
    "CONT_AWD_89233023FNR400103_8900_GS02F004HA_4732",
    "CONT_AWD_89233024FNR000025_8900_89303022AMA000041_8900",
    "CONT_AWD_89233024FNR000027_8900_89303022AMA000041_8900",
    "CONT_AWD_89233024PNR000112_8900_-NONE-_-NONE-",
    "CONT_AWD_89233118FNA000019_8900_DEMA0011379_8900",
    "CONT_AWD_89233118FNA400114_8900_GS00F0004T_4730",
    "CONT_AWD_89233119CNA000083_8900_-NONE-_-NONE-",
    "CONT_AWD_89233119FNA000060_8900_DEMA0011379_8900",
    "CONT_AWD_89233119FNA400174_8900_GS02F013CA_4732",
]
CSV_FIELDS = ["generated_award_id", "reporting_fiscal_year", "reporting_fiscal_quarter", "reporting_fiscal_month", "federal_account", "account_title", "funding_agency_name", "awarding_agency_name", "object_class", "object_class_name", "program_activity_code", "program_activity_name", "transaction_obligated_amount_usd", "gross_outlay_amount_usd"]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _fetch(award_id: str, refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    token = award_id.replace("/", "_")
    path = RAW_DIR / f"award_funding_{token}.json"
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("request", {}).get("award_id") == award_id:
                return {"path": path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        req = urllib.request.Request(BASE, data=json.dumps({"award_id": award_id}).encode("utf-8"), method="POST", headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "UET-Economics-Research/1.0 (public research)"})
        with urllib.request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        body = {"results": [], "error": str(exc)}; error = str(exc)
    wrapped = {"schema_version": "1.0", "provider": "USAspending.gov / U.S. Treasury", "source_url": BASE, "documentation_url": DOCS, "retrieval_timestamp_utc": utc_now(), "retrieval_vintage": "2026-08-01", "request": {"award_id": award_id}, "response": body, "error": error}
    write_json(path, wrapped)
    return {"path": path, "payload": wrapped, "cached": False}


def _number(value) -> float | None:
    if value in (None, "", "null"): return None
    try: return float(value)
    except (TypeError, ValueError): return None


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--refresh", action="store_true", help="retrieve a new provider vintage")
    args = parser.parse_args()
    items = [_fetch(award_id, args.refresh) for award_id in AWARD_IDS]
    rows = []; failures = []
    for item in items:
        payload = item["payload"]; body = payload.get("response", {}); results = body.get("results", []) if isinstance(body.get("results", []), list) else []
        if payload.get("error") or body.get("error") or not results:
            failures.append({"award_id": payload.get("request", {}).get("award_id"), "path": _relative(item["path"]), "error": payload.get("error") or body.get("error") or "empty award funding result"})
            continue
        for raw in results:
            if str(raw.get("reporting_fiscal_year")) != "2024": continue
            rows.append({"generated_award_id": item["payload"].get("request", {}).get("award_id"), "reporting_fiscal_year": raw.get("reporting_fiscal_year"), "reporting_fiscal_quarter": raw.get("reporting_fiscal_quarter"), "reporting_fiscal_month": raw.get("reporting_fiscal_month"), "federal_account": raw.get("federal_account"), "account_title": raw.get("account_title"), "funding_agency_name": raw.get("funding_agency_name"), "awarding_agency_name": raw.get("awarding_agency_name"), "object_class": raw.get("object_class"), "object_class_name": raw.get("object_class_name"), "program_activity_code": raw.get("program_activity_code"), "program_activity_name": raw.get("program_activity_name"), "transaction_obligated_amount_usd": _number(raw.get("transaction_obligated_amount")), "gross_outlay_amount_usd": _number(raw.get("gross_outlay_amount"))})
        if not item.get("cached"): time.sleep(0.15)
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda r: (r["generated_award_id"], str(r["reporting_fiscal_quarter"]), str(r["federal_account"])))
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=CSV_FIELDS);writer.writeheader();writer.writerows(rows)
    sources=[{"source_id": item["payload"].get("request",{}).get("award_id"),"source_url":BASE,"documentation_url":DOCS,"original_filename":item["path"].name,"local_path":_relative(item["path"]),"retrieval_timestamp_utc":item["payload"].get("retrieval_timestamp_utc"),"sha256":sha256(item["path"]),"terms":"U.S. government public API; no separate dataset license notice observed at retrieval","coverage":"fixed predeclared award ID; reporting fiscal year 2024 rows when returned","preprocessing":"POST JSON request; retain cached response; filter reporting_fiscal_year=2024; normalize numeric fields; preserve empty/missing award responses; no imputation","units":"current U.S. dollars; award funding-account obligation and gross-outlay fields","benchmark_role":"federal-account linkage; not bank settlement"} for item in items]
    status="PASS_WITH_BOUNDARY" if len(items)==len(AWARD_IDS) and not failures and rows else ("WARN" if rows else "BLOCKED")
    manifest={"schema_version":"1.0","provider":"USAspending.gov / U.S. Treasury","official_page":"https://api.usaspending.gov/","documentation_url":DOCS,"retrieval_vintage":"2026-08-01","coverage":"fixed ten-award DOE FY2024 sample; award funding endpoint filtered to reporting fiscal year 2024","sample_policy":{"award_ids":AWARD_IDS,"sample_size":10,"representative":False,"selection_inherited_from":"award_level_outlay_manifest.json"},"no_imputation":True,"sources":sources,"normalized_panel":{"local_path":_relative(NORMALIZED),"sha256":sha256(NORMALIZED),"rows":len(rows)},"status":status}
    returned_awards=sorted({r["generated_award_id"] for r in rows if r.get("generated_award_id")})
    missing_awards=sorted(set(AWARD_IDS)-set(returned_awards))
    bounded_ready=bool(rows and returned_awards)
    manifest["bounded_coverage"]={"ready":bounded_ready,"requested_awards":len(AWARD_IDS),"awards_with_fy2024_rows":len(returned_awards),"missing_awards":missing_awards,"no_imputation":True}
    write_json(MANIFEST_PATH,manifest)
    fy_obligation=sum(r["transaction_obligated_amount_usd"] or 0 for r in rows); fy_outlay=sum(r["gross_outlay_amount_usd"] or 0 for r in rows)
    accounts=sorted({r["federal_account"] for r in rows if r["federal_account"]}); agencies=sorted({r["funding_agency_name"] for r in rows if r["funding_agency_name"]}); objects=sorted({r["object_class_name"] for r in rows if r["object_class_name"]})
    artifact={"schema_version":"1.0","topic":"0.25_Strategy_Power_Economics","status":status,"controller_status":"AWARD_FEDERAL_ACCOUNT_LINKAGE_BOUNDARY" if status=="PASS_WITH_BOUNDARY" else "AWARD_FUNDING_ACCOUNT_GATE","generated_at_utc":utc_now(),"source_manifest":{"path":_relative(MANIFEST_PATH),"sha256":sha256(MANIFEST_PATH),"status":status},"coverage":{"fiscal_year":2024,"sample_awards":len(AWARD_IDS),"fy2024_rows":len(rows),"complete_federal_account_rows":sum(bool(r["federal_account"]) for r in rows),"complete_funding_agency_rows":sum(bool(r["funding_agency_name"]) for r in rows),"no_imputation":True},"bounded_coverage":{"ready":bounded_ready,"requested_awards":len(AWARD_IDS),"awards_with_fy2024_rows":len(returned_awards),"missing_awards":missing_awards,"no_imputation":True},"funding_linkage":{"unique_federal_accounts":accounts,"funding_agencies":agencies,"object_classes":objects,"fy2024_transaction_obligated_total_usd":fy_obligation,"fy2024_gross_outlay_total_usd":fy_outlay,"gross_outlay_minus_obligation_usd":fy_outlay-fy_obligation},"request_failures":failures,"interpretation":"The public award-funding endpoint links the fixed awards to federal accounts, account titles, funding agencies, object classes, and reported gross outlays for FY2024. It does not identify the Treasury financing instrument or a bank settlement counterparty.","claim_boundary":"This artifact supports bounded federal-account and program provenance only. It does not establish tax-versus-debt-versus-money-creation funding, supplier payment, profit funding, or physical-resource transformation.","limitations":["The ten-award sample is deterministic but nonrepresentative.","Gross outlay and transaction obligation are USAspending accounting fields, not bank settlement or invoice records.","A federal account identifies an appropriations/reporting channel, not the ultimate financing source of each dollar."]}
    write_json(ARTIFACT,artifact);print("USAspending award funding-account audit:",status,"rows",len(rows),"accounts",len(accounts),"failures",len(failures));return 0 if status in {"PASS_WITH_BOUNDARY","WARN"} else 1

if __name__ == "__main__": raise SystemExit(main())
