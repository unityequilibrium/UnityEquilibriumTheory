"""Replicate the EPI wage-productivity construction without conflating it with BLS."""

from __future__ import annotations

from economic_hardening_common import (
    ARTIFACT_DIR,
    SOURCE_MANIFEST,
    annualise_fred,
    as_float,
    load_json,
    read_csv,
    source_path,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_wage_productivity_audit.json"
START_YEAR = 1979
END_YEAR = 2021


def cumulative_growth(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or start <= 0 or end <= 0:
        return None
    return 100.0 * (end / start - 1.0)


def epi_replication(path) -> dict:
    if path is None:
        return {"status": "BLOCKED", "blocker": "Versioned EPI chart-data export is absent."}
    values = {}
    for row in read_csv(path):
        year = as_float(row.get("Year"))
        productivity = as_float(row.get("net_productivity_index"))
        compensation = as_float(row.get("epi_compensation_index"))
        if compensation is None:
            compensation = as_float(row.get("typical_worker_compensation_index"))
        if year is not None and productivity is not None and compensation is not None:
            values[int(year)] = {"productivity": productivity, "compensation": compensation}
    start = values.get(START_YEAR)
    end = values.get(END_YEAR)
    if start is None or end is None:
        return {"status": "INSUFFICIENT_ROWS", "available_coverage": [min(values) if values else None, max(values) if values else None], "blocker": "EPI export lacks one or both required 1979/2021 rows."}
    productivity_growth = cumulative_growth(start["productivity"], end["productivity"])
    compensation_growth = cumulative_growth(start["compensation"], end["compensation"])
    return {
        "status": "REPLICATED_FROM_VERSIONED_EXPORT",
        "coverage": [START_YEAR, END_YEAR],
        "productivity_growth_percent": productivity_growth,
        "epi_published_compensation_growth_percent": compensation_growth,
        "gap_percentage_points": None if productivity_growth is None or compensation_growth is None else productivity_growth - compensation_growth,
        "quoted_book_figure": {"productivity_growth_percent": 64.6, "book_quoted_typical_worker_compensation_growth_percent": 17.3},
        "comparison_to_book": "Report any difference as a source-vintage or construction difference; do not select the closer result.",
    }


def bls_comparator(manifest: dict) -> dict:
    productivity_path = source_path(manifest, "fred_ophnfb")
    compensation_path = source_path(manifest, "fred_comprnfb")
    if productivity_path is None or compensation_path is None:
        return {"status": "BLOCKED", "blocker": "FRED/BLS productivity or real-compensation source is absent."}
    productivity = annualise_fred(productivity_path)
    compensation = annualise_fred(compensation_path)
    productivity_growth = cumulative_growth(productivity.get(START_YEAR), productivity.get(END_YEAR))
    compensation_growth = cumulative_growth(compensation.get(START_YEAR), compensation.get(END_YEAR))
    return {
        "status": "DIAGNOSTIC_COMPLETE" if productivity_growth is not None and compensation_growth is not None else "INSUFFICIENT_ROWS",
        "coverage": [START_YEAR, END_YEAR],
        "productivity_growth_percent": productivity_growth,
        "real_hourly_compensation_growth_percent": compensation_growth,
        "gap_percentage_points": None if productivity_growth is None or compensation_growth is None else productivity_growth - compensation_growth,
        "construction_note": "This BLS nonfarm-business all-worker measure differs from EPI's total-economy net-productivity and typical-worker compensation construction, so numerical agreement is not expected.",
    }


def main() -> int:
    manifest = load_json(SOURCE_MANIFEST)
    epi = epi_replication(source_path(manifest, "epi_productivity_pay"))
    bls = bls_comparator(manifest)
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "DIAGNOSTIC_COMPLETE" if epi.get("status") == "REPLICATED_FROM_VERSIONED_EXPORT" and bls.get("status") == "DIAGNOSTIC_COMPLETE" else "WARN",
        "generated_at_utc": utc_now(),
        "formula_ids": ["EC25-UET-WAGE-PRODUCTIVITY-GAP"],
        "epi_replication": epi,
        "bls_comparator": bls,
        "distribution_lane": {
            "status": "BLOCKED",
            "required_sources": ["CPS/CE real median wage", "BEA real median disposable income", "distributional national accounts", "industry and hours controls"],
            "blocker": "The frozen primary panel does not contain source-locked median, quantile, household-disposable-income, or industry-composition series; aggregate wage/productivity results cannot be presented as distributional evidence.",
        },
        "claim_boundary": "The result can describe source-specific wage/productivity divergence. It cannot identify fiat-money causality, transfer mechanisms, distributional welfare, or a policy prescription.",
    }
    write_json(ARTIFACT, artifact)
    print(f"Wage-productivity audit: {artifact['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
