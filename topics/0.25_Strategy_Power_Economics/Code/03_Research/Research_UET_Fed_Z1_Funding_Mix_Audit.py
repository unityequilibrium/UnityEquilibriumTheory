"""Descriptive Fed Z.1 funding-flow associations; never interpret them as earmarked shares."""

from __future__ import annotations

import math
import statistics

from economic_hardening_common import ARTIFACT_DIR, write_json, utc_now
from Research_UET_Fed_Z1_Funding_Mapping_Probe import (
    END_YEAR,
    START_YEAR,
    SERIES,
    _complete_rows,
    load_annual_table,
)


ARTIFACT = ARTIFACT_DIR / "0_25_fed_z1_funding_mix_audit.json"
FUNDING_FLOWS = {
    "internal_saving": "net_saving",
    "debt_securities": "debt_securities_liability",
    "loans": "loans_liability",
    "equity_fund_shares": "equity_fund_shares_liability",
    "corporate_equities": "corporate_equities_liability",
}
PAYMENT_FLOWS = {
    "compensation": "compensation_paid",
    "taxes": "taxes_paid",
    "interest": "interest_paid",
    "dividends": "dividends_paid",
    "capital_formation": "net_capital_formation",
}


def corr(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    mean_left = statistics.fmean(left)
    mean_right = statistics.fmean(right)
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denom_left = math.sqrt(sum((a - mean_left) ** 2 for a in left))
    denom_right = math.sqrt(sum((b - mean_right) ** 2 for b in right))
    return numerator / (denom_left * denom_right) if denom_left and denom_right else None


def main() -> int:
    values, years, _positions = load_annual_table()
    complete = _complete_rows(values)
    cap = values["net_capital_formation"]
    associations = {}
    for label, name in FUNDING_FLOWS.items():
        lag_rows = {}
        for lag in (0, 1, 2):
            pairs = [
                (values[name][i], cap[i + lag])
                for i in complete
                if i + lag < len(cap) and cap[i + lag] is not None
            ]
            lag_rows[f"lead_{lag}_years"] = {
                "correlation": corr([a for a, _b in pairs], [b for _a, b in pairs]),
                "rows": len(pairs),
                "interpretation": "descriptive lead association only; not funding direction or causality",
            }
        associations[label] = {"series": name, "lags": lag_rows}

    payment_ratios = {}
    for label, name in PAYMENT_FLOWS.items():
        ratios = [
            values[name][i] / values["gross_value_added"][i]
            for i in complete
            if values["gross_value_added"][i] and values["gross_value_added"][i] > 0
        ]
        payment_ratios[label] = {
            "series": name,
            "ratio_to_gross_value_added": {
                "rows": len(ratios),
                "mean": statistics.fmean(ratios) if ratios else None,
                "median": statistics.median(ratios) if ratios else None,
            },
            "interpretation": "sector-level flow scale, not a payer identity or earmarked use",
        }

    periods = [("1959-1970", 1959, 1970), ("1974-1990", 1974, 1990), ("1991-2007", 1991, 2007), ("2008-2019", 2008, 2019), ("2020-2024", 2020, 2024)]
    period_summary = {}
    for label, start, end in periods:
        indexes = [i for i in complete if start <= int(years[i]) <= end]
        period_summary[label] = {
            "rows": len(indexes),
            "median_flow_to_capital_formation": {
                name: statistics.median(
                    values[name][i] / values["net_capital_formation"][i]
                    for i in indexes
                    if values["net_capital_formation"][i] and values["net_capital_formation"][i] > 0
                )
                if any(values["net_capital_formation"][i] and values["net_capital_formation"][i] > 0 for i in indexes)
                else None
                for name in FUNDING_FLOWS.values()
            },
            "interpretation": "signed net-flow ratios; they must not be summed as funding shares",
        }

    payload = {
        "schema_version": "1.0",
        "status": "WARN",
        "controller_status": "FUNDING_MIX_ASSOCIATION_DESCRIPTIVE_ONLY",
        "generated_at_utc": utc_now(),
        "source_role": "Fed Z.1 S11.1.i.a annual nonfinancial corporate business flows",
        "coverage": {"requested": [START_YEAR, END_YEAR], "observed": [int(years[0]), int(years[-1])], "rows": len(years), "complete_rows": len(complete), "no_imputation": True},
        "funding_flow_associations": associations,
        "payment_flow_scale": payment_ratios,
        "period_net_flow_ratios": period_summary,
        "funding_share_identification": {
            "status": "NOT_IDENTIFIED",
            "reason": "Z.1 reports net sectoral transactions. A debt issuance, retained saving, or equity transaction is not earmarked to a specific capital-formation project, and liability flows can include refinancing, redemptions, or repurchases.",
            "required_evidence": ["firm/project cash-flow or payment ledger", "counterparty concordance", "industry/commodity use table", "labor-hours and physical resource quantities"],
        },
        "claim_boundary": "The audit reports signed sector-level co-movements and payment-flow scale. It cannot answer which source paid for a particular purchase, nor connect money to labor and natural-resource transformation at project level.",
        "blockers": [
            "No gross earmarked funding shares are identified.",
            "Same-year and lead correlations are descriptive and non-causal.",
            "BLS input-output archive and physical resource concordance remain unavailable or quality-blocked.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("Fed Z.1 funding mix audit:", payload["status"], "rows", len(years), "complete", len(complete))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
