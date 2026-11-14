"""Map the Fed Z.1 annual nonfinancial-corporate flow table to funding roles.

This is a source-locked accounting bridge, not a transaction-level payment ledger.
It makes explicit which aggregate flows can be observed (wages, taxes, interest,
dividends, saving, capital formation, debt and equity transactions) and which
counterparty/resource links are still absent.
"""

from __future__ import annotations

import csv
import io
import json
import math
import statistics
import zipfile
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, ROOT, sha256, utc_now, write_json


ZIP_PATH = ROOT / "docs" / "data" / "external" / "economics" / "us_historical" / "fed_z1" / "2026-07-16" / "z1_csv_files.zip"
ARTIFACT = ARTIFACT_DIR / "0_25_fed_z1_funding_mapping_probe.json"
TABLE = "csv/S11_1_i_a.csv"
START_YEAR = 1959
END_YEAR = 2024


SERIES = {
    "gross_value_added": ("FU106902501.A", "output", "gross value added"),
    "compensation_paid": ("FU106025005.A", "labor_payment", "compensation of employees paid"),
    "wages_salaries_paid": ("FU106020001.A", "labor_payment", "wages and salaries paid"),
    "operating_surplus_net": ("FU106402101.A", "profit", "operating surplus, net"),
    "taxes_paid": ("FU106220001.A", "public_payment", "current taxes on income, wealth, etc. paid"),
    "interest_paid": ("FU106130001.A", "debt_service", "interest paid"),
    "dividends_paid": ("FU106121001.A", "equity_payment", "dividends paid"),
    "other_current_transfers_paid": ("FU106403001.A", "transfer", "other current transfers paid"),
    "net_saving": ("FU106012095.A", "internal_funding_proxy", "disposable income, net; net saving"),
    "net_capital_transfers_paid": ("FU105440005.A", "transfer", "net capital transfers paid"),
    "net_capital_formation": ("FU105050985.A", "real_use", "capital formation, net"),
    "net_lending_capital_account": ("FU105000905.A", "accounting_bridge", "net lending (+) or borrowing (-), capital account"),
    "net_lending_financial_account": ("FU105000005.A", "accounting_bridge", "net lending (+) or borrowing (-), financial account"),
    "debt_securities_liability": ("FU104122005.A", "debt_funding", "debt securities liability"),
    "corporate_bonds_liability": ("FU103163005.A", "debt_funding", "corporate bonds liability"),
    "loans_liability": ("FU104135005.A", "debt_funding", "total loans liability"),
    "equity_fund_shares_liability": ("FU103181005.A", "equity_funding", "equity and investment fund shares liability"),
    "corporate_equities_liability": ("FU103164105.A", "equity_funding", "corporate equities liability"),
}


def _number(value: str) -> float | None:
    value = value.strip()
    if not value or value in {"ND", "NA", "NM"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_annual_table() -> tuple[dict[str, list[float | None]], list[str], dict[str, list[int]]]:
    with zipfile.ZipFile(ZIP_PATH) as archive:
        raw = archive.read(TABLE).decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(raw)))
    header = rows[0]
    positions: dict[str, list[int]] = {}
    for index, code in enumerate(header):
        positions.setdefault(code, []).append(index)
    years: list[str] = []
    values = {name: [] for name in SERIES}
    for row in rows[1:]:
        try:
            year = int(row[0])
        except (ValueError, IndexError):
            continue
        if not START_YEAR <= year <= END_YEAR:
            continue
        years.append(str(year))
        for name, (code, _role, _label) in SERIES.items():
            index = positions.get(code, [None])[0]
            values[name].append(_number(row[index]) if index is not None and index < len(row) else None)
    return values, years, positions


def _complete_rows(values: dict[str, list[float | None]]) -> list[int]:
    required = list(SERIES)
    return [
        index
        for index in range(len(next(iter(values.values()))))
        if all(values[name][index] is not None for name in required)
    ]


def _summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "max_abs": None}
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "max_abs": max(abs(value) for value in values),
    }


def main() -> int:
    if not ZIP_PATH.exists():
        payload = {
            "schema_version": "1.0",
            "status": "BLOCKED",
            "controller_status": "FUNDING_FLOW_MAPPING_BLOCKED",
            "zip_path": str(ZIP_PATH).replace("\\", "/"),
            "blockers": ["Fed Z.1 archive is absent; no funding mapping can be claimed."],
        }
        write_json(ARTIFACT, payload)
        print("Fed Z.1 funding mapping probe: BLOCKED")
        return 0

    values, years, positions = load_annual_table()
    complete = _complete_rows(values)
    bridge_residuals = []
    financial_gap = []
    for index in complete:
        # Z.1's capital-account identity: net lending = saving - capital formation
        # - net capital transfers paid.  This is an accounting check, not causal proof.
        expected = (
            values["net_saving"][index]
            - values["net_capital_formation"][index]
            - values["net_capital_transfers_paid"][index]
        )
        bridge_residuals.append(values["net_lending_capital_account"][index] - expected)
        financial_gap.append(
            values["net_lending_financial_account"][index]
            - values["net_lending_capital_account"][index]
        )

    mapping = {
        name: {
            "series_code": code,
            "table": TABLE,
            "role": role,
            "label": label,
            "unit": "millions of dollars; annual transactions, not seasonally adjusted",
            "coverage": [START_YEAR, END_YEAR],
            "source_vintage": "Fed Z.1 current release 2026:Q1; observations frozen through 2024",
        }
        for name, (code, role, label) in SERIES.items()
    }
    payload = {
        "schema_version": "1.0",
        "status": "WARN",
        "controller_status": "FUNDING_FLOW_MAPPING_DESCRIPTIVE_ONLY",
        "generated_at_utc": utc_now(),
        "source": {
            "provider": "Federal Reserve Financial Accounts (Z.1)",
            "release_vintage": "2026:Q1 current release",
            "archive_path": str(ZIP_PATH).replace("\\", "/"),
            "archive_sha256": sha256(ZIP_PATH),
            "table": TABLE,
            "table_role": "annual nonfinancial corporate business integrated macro accounts",
        },
        "coverage": {
            "requested": [START_YEAR, END_YEAR],
            "observed": [int(years[0]), int(years[-1])] if years else None,
            "rows": len(years),
            "complete_rows": len(complete),
            "missing_required_rows": len(years) - len(complete),
            "no_imputation": True,
        },
        "series_mapping": mapping,
        "accounting_bridge": {
            "identity": "net_lending_capital = net_saving - net_capital_formation - net_capital_transfers_paid",
            "identity_status": ("PASS" if bridge_residuals and max(abs(x) for x in bridge_residuals) == 0 else ("PASS_WITH_ROUNDING" if bridge_residuals and max(abs(x) for x in bridge_residuals) <= 1.0 else "WARN")),
            "residual_summary_millions": _summary(bridge_residuals),
            "financial_vs_capital_gap_summary_millions": _summary(financial_gap),
            "interpretation": "Exact within the published rounded table for the mapped rows; the financial-account gap is a reconciliation/statistical item, not a payer trace.",
        },
        "payer_and_source_visibility": {
            "observable_aggregate_flows": [
                "nonfinancial corporate business pays compensation/wages, taxes, interest, dividends, and transfers",
                "net saving is an internal-funding proxy after current-account flows",
                "debt and equity liability transactions are observable funding channels",
                "capital formation is an observed real-use destination",
            ],
            "not_observable_from_this_table": [
                "individual payer-payee identity or invoice-level exchange",
                "whether a particular investment dollar came from profit, a new loan, equity issuance, or a transfer",
                "labor hours and physical natural-resource extraction linked to each payment",
                "innovation/output transformation at project or firm level",
            ],
            "required_join_sources": [
                "BEA Supply-Use/Input-Output accounts for industry-to-industry purchases and compensation",
                "BLS hours/occupations and productivity for labor input",
                "EIA, USGS, and FAOSTAT source-level extraction/energy/material quantities",
                "Census business/transaction microdata or administrative payment data for payer-payee provenance",
            ],
        },
        "claim_boundary": "The mapping establishes a reproducible sectoral accounting bridge and identifies observable funding channels. It does not establish payment-level provenance, resource causality, or fiat-money causality.",
        "blockers": [
            "Z.1 current-release vintage is revised; historical-as-of vintages are still needed for real-time tests.",
            "Counterparty and project-level payer provenance is not identified by the aggregate S11.1.i.a table.",
            "Natural-resource extraction and labor-use links require a separate physical/industry panel and explicit concordance.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("Fed Z.1 funding mapping probe:", payload["status"], "rows", len(years), "complete", len(complete))
    print("  capital-account residual max abs:", payload["accounting_bridge"]["residual_summary_millions"]["max_abs"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
