"""Reconcile a bounded DOE award-obligation total with Treasury DOE outlays.

The comparison is deliberately descriptive. USAspending's grouped agency result
is an award-obligation measure, while Treasury MTS Table 5 is a government
program outlay measure. A difference is expected to be investigated, not treated
as missing cash, profit, debt attribution, or a one-to-one payment match.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, TREASURY_FUNDING_SOURCE_ARTIFACT, sha256, utc_now, write_json

ARTIFACT = ARTIFACT_DIR / "0_25_federal_award_outlay_reconciliation.json"
RAW_DIR = RAW_ROOT / "usaspending" / "2026-08-01"
RAW_PATH = RAW_DIR / "usaspending_doe_fy2024_awarding_agency_summary.json"
MANIFEST_PATH = RAW_DIR / "federal_award_outlay_reconciliation_manifest.json"
NORMALIZED = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "federal_award_outlay_reconciliation_2024.csv"
USA_URL = "https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/"
USA_DOCS = "https://api.usaspending.gov/docs/endpoints"
TREASURY_RAW = RAW_ROOT / "treasury_fiscal_data" / "2026-08-01" / "mts_table_5_2024-09-30.json"
START_DATE = "2023-10-01"
END_DATE = "2024-09-30"
AGENCY = "Department of Energy"
PAYLOAD = {
    "group": "awarding_agency",
    "filters": {
        "time_period": [{"start_date": START_DATE, "end_date": END_DATE}],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": AGENCY}],
        "award_type_codes": ["A", "B", "C", "D"],
    },
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _fetch(refresh: bool) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.is_file() and not refresh:
        try:
            cached = json.loads(RAW_PATH.read_text(encoding="utf-8"))
            if cached.get("request") == PAYLOAD:
                return {"path": RAW_PATH, "payload": cached, "cached": True}
        except (OSError, json.JSONDecodeError):
            pass
    error = None
    try:
        req = urllib.request.Request(USA_URL, data=json.dumps(PAYLOAD, separators=(",", ":")).encode("utf-8"), method="POST", headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "UET-Economics-Research/1.0 (public research)"})
        with urllib.request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        body = {"results": [], "error": str(exc)}
        error = str(exc)
    wrapped = {"schema_version": "1.0", "provider": "USAspending.gov / U.S. Treasury", "source_url": USA_URL, "documentation_url": USA_DOCS, "retrieval_timestamp_utc": utc_now(), "retrieval_vintage": "2026-08-01", "request": PAYLOAD, "response": body, "error": error}
    write_json(RAW_PATH, wrapped)
    return {"path": RAW_PATH, "payload": wrapped, "cached": False}


def _treasury_outlay() -> tuple[float | None, dict | None]:
    if not TREASURY_RAW.is_file():
        return None, None
    payload = json.loads(TREASURY_RAW.read_text(encoding="utf-8"))
    for row in payload.get("response", {}).get("data", []):
        if row.get("classification_desc") == "Total--Department of Energy":
            value = row.get("current_fytd_net_outly_amt")
            return (float(value) if value not in (None, "", "null") else None), row
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="retrieve a new USAspending aggregate response")
    args = parser.parse_args()
    item = _fetch(args.refresh)
    if not item.get("cached"): time.sleep(0.15)
    response = item["payload"].get("response", {})
    results = response.get("results", []) if isinstance(response.get("results", []), list) else []
    award = next((row for row in results if row.get("name") == AGENCY), None)
    award_obligation = float(award["amount"]) if award and award.get("amount") is not None else None
    treasury_outlay, treasury_row = _treasury_outlay()
    failures = []
    if item["payload"].get("error") or response.get("error"): failures.append({"source": "usaspending", "error": item["payload"].get("error") or response.get("error")})
    if not TREASURY_RAW.is_file(): failures.append({"source": "treasury", "error": "required frozen MTS Table 5 archive missing"})
    if award_obligation is None: failures.append({"source": "usaspending", "error": "DOE grouped award obligation not returned"})
    if treasury_outlay is None: failures.append({"source": "treasury", "error": "Total--Department of Energy net outlay not returned"})
    difference = award_obligation - treasury_outlay if award_obligation is not None and treasury_outlay is not None else None
    ratio = award_obligation / treasury_outlay if award_obligation is not None and treasury_outlay not in (None, 0) else None
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    with NORMALIZED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fiscal_year", "agency", "award_obligations_usd", "treasury_net_outlays_usd", "obligation_minus_outlay_usd", "obligation_to_outlay_ratio"])
        writer.writeheader(); writer.writerow({"fiscal_year": 2024, "agency": AGENCY, "award_obligations_usd": award_obligation, "treasury_net_outlays_usd": treasury_outlay, "obligation_minus_outlay_usd": difference, "obligation_to_outlay_ratio": ratio})
    manifest = {"schema_version": "1.0", "provider_pair": ["USAspending.gov / U.S. Treasury", "U.S. Department of the Treasury, Fiscal Service"], "retrieval_vintage": "2026-08-01", "coverage": "DOE, FY2024, 2023-10-01 through 2024-09-30", "no_imputation": True, "sources": [{"source_id": "usaspending_doe_awarding_agency_summary", "source_url": USA_URL, "documentation_url": USA_DOCS, "local_path": _relative(RAW_PATH), "sha256": sha256(RAW_PATH), "units": "current U.S. dollars; grouped prime-award obligations", "benchmark_role": "award-obligation side; not settlement"}, {"source_id": "treasury_doe_mts_table_5", "source_url": "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5?filter=record_date:eq:2024-09-30", "documentation_url": "https://fiscaldata.treasury.gov/api-documentation/", "local_path": _relative(TREASURY_RAW), "sha256": sha256(TREASURY_RAW) if TREASURY_RAW.is_file() else None, "units": "current U.S. dollars; FYTD net outlays", "benchmark_role": "Treasury program-outlay side; not award settlement"}], "normalized_panel": {"local_path": _relative(NORMALIZED), "sha256": sha256(NORMALIZED), "rows": 1}, "status": "PASS_WITH_BOUNDARY" if not failures else ("WARN" if award_obligation is not None or treasury_outlay is not None else "BLOCKED")}
    write_json(MANIFEST_PATH, manifest)
    artifact = {"schema_version": "1.0", "topic": "0.25_Strategy_Power_Economics", "status": manifest["status"], "controller_status": "AWARD_OUTLAY_RECONCILIATION_BOUNDARY" if manifest["status"] == "PASS_WITH_BOUNDARY" else "AWARD_OUTLAY_RECONCILIATION_GATE", "generated_at_utc": utc_now(), "source_manifest": {"path": _relative(MANIFEST_PATH), "sha256": sha256(MANIFEST_PATH), "status": manifest["status"]}, "coverage": {"fiscal_year": 2024, "agency": AGENCY, "award_type_codes": ["A", "B", "C", "D"], "start_date": START_DATE, "end_date": END_DATE, "no_imputation": True}, "observations": {"usaspending_grouped_award_obligations_usd": award_obligation, "treasury_mts_total_department_of_energy_net_outlays_usd": treasury_outlay, "treasury_row": treasury_row, "obligation_minus_outlay_usd": difference, "obligation_to_outlay_ratio": ratio}, "reconciliation": {"status": "NOT_ONE_TO_ONE" if not failures else "INCOMPLETE", "interpretation": "The two measures are comparable only as bounded scale diagnostics. USAspending reports award obligations, while Treasury MTS reports government program outlays; timing, accounting scope, unlinked awards, intergovernmental flows, and non-award government costs prevent a payment-level reconciliation.", "not_a_cash_settlement_match": True}, "request_failures": failures, "claim_boundary": "This artifact does not identify which tax, borrowing, cash-balance, or other financing source funded a specific award, nor does it prove that an obligation was paid to a supplier or transformed into a measured physical resource.", "limitations": ["USAspending grouped result is a prime-award obligation total, not a bank settlement total.", "Treasury MTS Department of Energy outlays cover agency programs and may include outlays not tied to the sampled award universe.", "The comparison is one fiscal-year aggregate and cannot establish causal or transaction-level provenance."]}
    write_json(ARTIFACT, artifact)
    print("Federal award/outlay reconciliation:", manifest["status"], "obligation", award_obligation, "outlay", treasury_outlay, "failures", len(failures))
    return 0 if manifest["status"] in {"PASS_WITH_BOUNDARY", "WARN"} else 1

if __name__ == "__main__": raise SystemExit(main())
