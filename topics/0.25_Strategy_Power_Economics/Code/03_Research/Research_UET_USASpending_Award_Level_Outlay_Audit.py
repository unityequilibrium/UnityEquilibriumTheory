"""Audit account-level outlay and obligation fields for a fixed USAspending sample.

USAspending award detail records expose account-level totals that are closer to
award accounting than a grouped agency total. They remain an accounting view,
not a bank settlement or supplier invoice ledger. The sample is deliberately
predeclared as the first ten unique generated award IDs in the frozen DOE FY2024
transaction archive, sorted lexicographically.
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

ARTIFACT = ARTIFACT_DIR / "0_25_usaspending_award_level_outlay_audit.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
MANIFEST_PATH = RAW_DIR / "award_level_outlay_manifest.json"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "usaspending_award_level_outlay_2024.csv"
BASE = "https://api.usaspending.gov/api/v2/awards/"
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
CSV_FIELDS = ["generated_award_id", "piid", "recipient_name", "award_type", "total_obligation_usd", "total_account_obligation_usd", "total_account_outlay_usd", "outlay_minus_obligation_usd", "outlay_to_obligation_ratio", "subaward_count", "total_subaward_amount_usd", "date_signed"]


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _fetch(award_id: str, refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    token = award_id.replace("/", "_")
    path = RAW_DIR / f"award_detail_{token}.json"
    url = BASE + award_id + "/"
    if path.is_file() and not refresh:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("source_url") == url:
                return {"path": path, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "UET-Economics-Research/1.0 (public research)"})
        with urllib.request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        body = {"error": str(exc)}; error = str(exc)
    wrapped = {"schema_version": "1.0", "provider": "USAspending.gov / U.S. Treasury", "source_url": url, "documentation_url": DOCS, "retrieval_timestamp_utc": utc_now(), "retrieval_vintage": "2026-08-01", "generated_award_id": award_id, "response": body, "error": error}
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
        payload = item["payload"]; body = payload.get("response", {})
        if payload.get("error") or body.get("error") or not body.get("generated_unique_award_id"):
            failures.append({"path": _relative(item["path"]), "error": payload.get("error") or body.get("error") or "award detail response missing generated_unique_award_id"})
            continue
        total_obligation = _number(body.get("total_obligation")); account_obligation = _number(body.get("total_account_obligation")); account_outlay = _number(body.get("total_account_outlay"))
        difference = account_outlay - account_obligation if account_outlay is not None and account_obligation is not None else None
        ratio = account_outlay / account_obligation if account_outlay is not None and account_obligation not in (None, 0) else None
        rows.append({"generated_award_id": body.get("generated_unique_award_id"), "piid": body.get("piid"), "recipient_name": body.get("recipient_name"), "award_type": body.get("type_description"), "total_obligation_usd": total_obligation, "total_account_obligation_usd": account_obligation, "total_account_outlay_usd": account_outlay, "outlay_minus_obligation_usd": difference, "outlay_to_obligation_ratio": ratio, "subaward_count": body.get("subaward_count"), "total_subaward_amount_usd": _number(body.get("total_subaward_amount")), "date_signed": body.get("date_signed")})
        if not item.get("cached"): time.sleep(0.15)
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS); writer.writeheader(); writer.writerows(rows)
    sources = [{"source_id": item["payload"].get("generated_award_id"), "source_url": item["payload"].get("source_url"), "documentation_url": DOCS, "original_filename": item["path"].name, "local_path": _relative(item["path"]), "retrieval_timestamp_utc": item["payload"].get("retrieval_timestamp_utc"), "sha256": sha256(item["path"]), "units": "current U.S. dollars; USAspending account-level obligation/outlay fields", "benchmark_role": "award-level accounting diagnostic; not bank settlement"} for item in items]
    status = "PASS_WITH_BOUNDARY" if len(rows) == len(AWARD_IDS) and not failures else ("WARN" if rows else "BLOCKED")
    manifest = {"schema_version": "1.0", "provider": "USAspending.gov / U.S. Treasury", "official_page": "https://api.usaspending.gov/", "documentation_url": DOCS, "retrieval_vintage": "2026-08-01", "coverage": "DOE FY2024 fixed award-detail sample; first 10 unique generated award IDs sorted lexicographically from frozen five-page transaction archive", "sample_policy": {"selection": "first ten unique generated_internal_id values sorted lexicographically", "sample_size": 10, "representative": False, "source_archive": "docs/data/external/economics/us_historical/usaspending/2026-08-01/usaspending_doe_fy2024_page_01.json through page_05.json"}, "no_imputation": True, "sources": sources, "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": len(rows)}, "status": status}
    write_json(MANIFEST_PATH, manifest)
    ratios = [row["outlay_to_obligation_ratio"] for row in rows if row["outlay_to_obligation_ratio"] is not None]
    artifact = {"schema_version": "1.0", "topic": "0.25_Strategy_Power_Economics", "status": status, "controller_status": "AWARD_LEVEL_ACCOUNT_OUTLAY_BOUNDARY" if status == "PASS_WITH_BOUNDARY" else "AWARD_LEVEL_OUTLAY_GATE", "generated_at_utc": utc_now(), "source_manifest": {"path": _relative(MANIFEST_PATH), "sha256": sha256(MANIFEST_PATH), "status": status}, "coverage": {"fiscal_year": 2024, "sample_size_requested": len(AWARD_IDS), "rows_returned": len(rows), "complete_account_obligation_rows": sum(row["total_account_obligation_usd"] is not None for row in rows), "complete_account_outlay_rows": sum(row["total_account_outlay_usd"] is not None for row in rows), "no_imputation": True}, "summary": {"account_obligation_total_usd": sum(row["total_account_obligation_usd"] or 0 for row in rows), "account_outlay_total_usd": sum(row["total_account_outlay_usd"] or 0 for row in rows), "outlay_minus_obligation_total_usd": sum(row["outlay_minus_obligation_usd"] or 0 for row in rows), "median_outlay_to_obligation_ratio": sorted(ratios)[len(ratios)//2] if ratios else None}, "request_failures": failures, "interpretation": "Award-level account outlay and obligation fields are observable for the fixed sample, but they are accounting totals, not evidence of bank settlement, supplier invoice payment, or financing-source provenance.", "claim_boundary": "This artifact does not establish that an award was paid to a supplier, identify whether payment came from profit/debt/taxes/money creation, or connect the award to a physical resource transformation.", "limitations": ["The ten-award sample is deterministic but nonrepresentative and must not be generalized to all DOE awards.", "Account outlay is not a bank settlement ledger or invoice-level payment record.", "Awards may have multiple transactions, modifications, de-obligations, and account-level adjustments."]}
    write_json(ARTIFACT, artifact)
    print("USAspending award-level outlay audit:", status, "rows", len(rows), "failures", len(failures), "ratios", len(ratios))
    return 0 if status in {"PASS_WITH_BOUNDARY", "WARN"} else 1

if __name__ == "__main__": raise SystemExit(main())
