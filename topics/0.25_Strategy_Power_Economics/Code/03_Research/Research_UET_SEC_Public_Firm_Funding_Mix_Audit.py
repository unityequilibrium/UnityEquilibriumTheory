"""Descriptive funding-channel audit for the SEC public-firm panel.

The audit compares observed annual profit, operating cash flow, debt flows, and
capital expenditure scales.  Ratios are not interpreted as funding shares:
cash pooling, refinancing, working capital, acquisitions, and reporting-tag
differences prevent a payment-level allocation.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_sec_public_firm_funding_mix_audit.json"
PANEL = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics" / "Data" / "03_Research" / "sec_public_firm_funding_proxy_2010_2024.csv"
SOURCE_ARTIFACT = ARTIFACT_DIR / "0_25_sec_public_firm_funding_proxy.json"


def _number(value: str) -> float | None:
    if value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def main() -> int:
    rows = []
    if PANEL.is_file():
        with PANEL.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    usable: list[dict[str, object]] = []
    for row in rows:
        capex = _number(row.get("capex_outflow_scale_usd", ""))
        if capex is None or capex <= 0:
            continue
        profit = _number(row.get("net_income_usd", ""))
        op_cash = _number(row.get("operating_cash_flow_usd", ""))
        debt_proceeds = _number(row.get("debt_proceeds_usd", ""))
        debt_repayments = _number(row.get("debt_repayments_raw_usd", ""))
        dividends = _number(row.get("common_dividends_raw_usd", ""))
        net_debt = None if debt_proceeds is None and debt_repayments is None else (debt_proceeds or 0.0) + (debt_repayments or 0.0)
        retained_profit = None if profit is None and dividends is None else (profit or 0.0) + (dividends or 0.0)
        usable.append({
            "company": row.get("company"),
            "sector": row.get("sector"),
            "fiscal_year": int(row["fiscal_year"]),
            "capex_usd": capex,
            "profit_to_capex": None if retained_profit is None else retained_profit / capex,
            "operating_cash_to_capex": None if op_cash is None else op_cash / capex,
            "net_debt_to_capex": None if net_debt is None else net_debt / capex,
            "profit_observed": retained_profit is not None,
            "debt_observed": net_debt is not None,
        })
    by_sector: dict[str, list[dict[str, object]]] = {}
    for row in usable:
        by_sector.setdefault(str(row["sector"]), []).append(row)
    summaries = {}
    for sector, sector_rows in sorted(by_sector.items()):
        summaries[sector] = {
            "rows": len(sector_rows),
            "median_profit_to_capex": _median([float(x["profit_to_capex"]) for x in sector_rows if x["profit_to_capex"] is not None]),
            "median_operating_cash_to_capex": _median([float(x["operating_cash_to_capex"]) for x in sector_rows if x["operating_cash_to_capex"] is not None]),
            "median_net_debt_to_capex": _median([float(x["net_debt_to_capex"]) for x in sector_rows if x["net_debt_to_capex"] is not None]),
            "profit_observed_rows": sum(1 for x in sector_rows if x["profit_observed"]),
            "debt_observed_rows": sum(1 for x in sector_rows if x["debt_observed"]),
        }
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PASS_WITH_BOUNDARY" if usable else "BLOCKED",
        "controller_status": "SEC_PUBLIC_FIRM_FUNDING_MIX_DESCRIPTIVE_ONLY",
        "generated_at_utc": utc_now(),
        "source_artifact": {"path": str(SOURCE_ARTIFACT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(SOURCE_ARTIFACT) if SOURCE_ARTIFACT.exists() else None},
        "panel": {"path": str(PANEL.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PANEL) if PANEL.exists() else None, "rows": len(rows), "usable_capex_rows": len(usable)},
        "sector_summaries": summaries,
        "funding_share_identification": {"status": "NOT_IDENTIFIED", "reason": "Profit, operating cash, and net debt are annual firm-accounting channels; their ratios to capex are scale diagnostics, not source-of-payment shares."},
        "claim_boundary": "Descriptive public-firm accounting comparison only. No economy-wide, payer-level, project-level, physical-resource, or causal funding claim is supported.",
        "limitations": [
            "The panel covers only ten predeclared public firms and current-vintage 10-K facts.",
            "Net debt flows can include refinancing, redemptions, and timing differences; cash pooling is unobserved.",
            "Capex tags do not identify which supplier or physical resource was paid.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("SEC public-firm funding mix audit:", payload["status"], "usable rows", len(usable))
    return 0 if payload["status"] in {"PASS_WITH_BOUNDARY", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
