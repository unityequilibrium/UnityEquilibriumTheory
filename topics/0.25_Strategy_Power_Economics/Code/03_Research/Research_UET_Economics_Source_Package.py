"""Package the auditable U.S. economics inputs for Topic 0.25.

Run with --refresh only when external downloads are intended. Public FRED files
and source-specific normalized subsets are checked against the declared vintage;
the official BEA/EIA/EPI transformation pass must run before this manifest pass.
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
from pathlib import Path

from economic_hardening_common import (
    CLAIM_GATE,
    FORMULA_GATE,
    HOLDOUT_POLICY,
    PARAMETER_POLICY,
    RAW_ROOT,
    RESEARCH_DATA,
    ROOT,
    SOURCE_MANIFEST,
    SOURCE_READINESS,
    download,
    relative,
    runtime_environment,
    sha256,
    utc_now,
    write_json,
)


def file_coverage(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            date_field = next((field for field in fields if field.lower() in {"observation_date", "date", "year"}), None)
            if date_field is None:
                return None
            values = [str(row.get(date_field, "")).strip() for row in reader if str(row.get(date_field, "")).strip()]
        if not values:
            return None
        return {"start": min(values), "end": max(values), "observations": len(values), "field": date_field}
    except (OSError, UnicodeError, csv.Error):
        return None


FRED_SERIES = {
    "fred_m2sl": ("M2SL", "M2 money stock; billions of USD, seasonally adjusted; monthly"),
    "fred_gdpc1": ("GDPC1", "real GDP; chained dollars; quarterly"),
    "fred_pop": ("POP", "civilian noninstitutional population; thousands of persons; monthly"),
    "fred_unrate": ("UNRATE", "unemployment rate; percent; monthly"),
    "fred_cpiengsl": ("CPIENGSL", "CPI energy index; index; monthly"),
    "fred_cpiaucsl": ("CPIAUCSL", "CPI-U all items; index; monthly"),
    "fred_gdpdef": ("GDPDEF", "GDP implicit price deflator; index; quarterly"),
    "fred_tb3ms": ("TB3MS", "three-month Treasury bill secondary-market rate; percent; monthly"),
    "fred_ophnfb": ("OPHNFB", "BLS nonfarm-business output per hour; index; quarterly"),
    "fred_comprnfb": ("COMPRNFB", "BLS nonfarm-business real hourly compensation; index; quarterly"),
    "fred_payems": ("PAYEMS", "all employees, total nonfarm; thousands of persons; monthly"),
    "fred_cmdebt": ("CMDEBT", "domestic nonfinancial sectors debt; billions of USD; quarterly"),
}


def record(path: Path, **fields: object) -> dict:
    payload = dict(fields)
    payload["local_path"] = relative(path)
    payload["exists"] = path.exists()
    payload["coverage"] = file_coverage(path)
    payload["retrieval_timestamp_utc"] = utc_now() if path.exists() else None
    if path.exists():
        payload["sha256"] = sha256(path)
        payload["bytes"] = path.stat().st_size
    return payload


def manual_target(provider: str, vintage: str, filename: str, source_id: str, source_url: str, terms: str, schema: list[str], role: str, required: bool, unit_system: str) -> dict:
    path = RAW_ROOT / provider / vintage / filename
    return record(
        path,
        source_id=source_id,
        source=provider,
        source_url=source_url,
        retrieval_date=vintage if path.exists() else None,
        original_filename=filename,
        license_or_terms=terms,
        preprocessing="Normalized research subset produced from a provider raw export. See Data/03_Research/uet_us_economics_transform_manifest.json for raw identity, table/series selection, and transformations.",
        transformation_manifest="docs/topics/0.25_Strategy_Power_Economics/Data/03_Research/uet_us_economics_transform_manifest.json",
        unit_system=unit_system,
        benchmark_role=role,
        required_for_primary_panel=required,
        expected_columns=schema,
        source_status=(
            "READY_FOR_REVIEW"
            if path.exists()
            else ("MISSING_REQUIRED_EXPORT" if required else "OPTIONAL_EXPORT_PENDING")
        ),
    )


def write_contracts() -> None:
    write_json(
        FORMULA_GATE,
        {
            "schema_version": "1.0",
            "topic": "0.25_Strategy_Power_Economics",
            "claim_boundary": "Formula entries are diagnostic operationalizations of Book 1 hypotheses; none is a derived economic law.",
            "formulae": [
                {
                    "formula_id": "EC25-UET-RESOURCE-ENGINE",
                    "relation": "R = N + K + I (Book 1 conceptual expression); operational diagnostic uses delta ln(R[t+3]) = alpha + beta_N*N_t + beta_K*delta ln(K_t) + beta_I*delta ln(I_t) + epsilon_t.",
                    "variables": {"R": "dimensionless resource-capacity index", "N": "dimensionless constraint proxy", "K": "BEA chain-type IP-product quantity index (2017=100) divided by employees; indexed proxy", "I": "geometric mean of BEA chain-type fixed-asset quantity indexes (2017=100) divided by employees; indexed proxy"},
                    "unit_closure_status": "Proxy",
                    "conversion_steps": ["source units to annual observations", "per-capita/per-employee normalization", "1959=100 rebasing", "log changes", "training-window standardization for N"],
                    "constant_origin": "heuristic_bridge",
                    "proof_status": "heuristic bridge",
                    "verification_role": "diagnostic-only temporal association",
                    "failure_mode": "A fitted proxy composite could be mistaken for a dimensional identity or causal mechanism.",
                    "next_hardening_step": "Add a source-locked patent robustness series and externally replicated panel before any stronger interpretation.",
                },
                {
                    "formula_id": "EC25-UET-MONETARY-RESOURCE-MISMATCH",
                    "relation": "D_t = delta ln(M2_t) - delta ln(R_t)",
                    "variables": {"D": "dimensionless mismatch", "M2": "money stock", "R": "resource-capacity proxy"},
                    "unit_closure_status": "Closed after log transformation",
                    "constant_origin": "topic_derived_relation",
                    "proof_status": "heuristic bridge",
                    "verification_role": "inflation diagnostic comparator",
                    "failure_mode": "Endogeneity and omitted supply/demand factors make causal interpretation invalid.",
                    "next_hardening_step": "Report baseline comparison and uncertainty; retain the non-causal claim boundary.",
                },
                {
                    "formula_id": "EC25-UET-WAGE-PRODUCTIVITY-GAP",
                    "relation": "gap_t = ln(productivity_t) - ln(compensation_t)",
                    "variables": {"productivity": "source-specific output-per-hour or EPI net-productivity measure", "compensation": "source-specific real compensation measure"},
                    "unit_closure_status": "Closed after log transformation",
                    "constant_origin": "source_locked_benchmark_input when the source export is present",
                    "proof_status": "diagnostic",
                    "verification_role": "construction-specific replication and comparator",
                    "failure_mode": "BLS and EPI series have different universes and deflators; they must not be silently interchanged.",
                    "next_hardening_step": "Archive a versioned EPI export and report both constructions separately.",
                },
            ],
        },
    )
    write_json(
        PARAMETER_POLICY,
        {
            "schema_version": "1.0",
            "topic": "0.25_Strategy_Power_Economics",
            "policy": "Predeclared before the first model run; do not tune against holdout results.",
            "sample": {"country": "United States", "frequency": "annual", "start_year": 1959, "end_year": 2024},
            "resource_index": {"components": ["real_gdp_per_capita", "nonfarm_business_output_per_hour", "primary_energy_per_capita"], "aggregation": "equal-weight geometric mean", "base_year": 1959},
            "necessity_proxy": {"components": ["annual_cpi_energy_inflation", "annual_unemployment_rate"], "aggregation": "equal-weight standardized mean", "standardization": "fit on each training window only"},
            "knowledge_proxy": {"primary": "ip_product_quantity_index_2017_100_per_employee", "robustness": "utility_patents_per_capita", "unit_note": "BEA chain-type quantity index, not a dollar-valued investment series"},
            "infrastructure_proxy": {"components": ["private_tangible_fixed_assets_quantity_index_2017_100_per_employee", "government_fixed_assets_quantity_index_2017_100_per_employee"], "aggregation": "equal-weight geometric mean", "unit_note": "BEA chain-type quantity indexes, not a dollar-valued stock series"},
            "horizons": {"primary": 3, "sensitivity": [1, 5]},
            "candidate_signal_threshold": {"declared_primary_baselines": ["constant_growth", "zero_growth"], "median_rmse_improvement_vs_each_primary_baseline": 0.1, "bootstrap_interval_requirement": "95 percent interval for squared-error difference lies below zero", "claim_impact": "none; Claim Class C remains controlling"},
        },
    )
    write_json(
        HOLDOUT_POLICY,
        {
            "schema_version": "1.0",
            "topic": "0.25_Strategy_Power_Economics",
            "training_start": 1959,
            "rolling_origin_start": 2000,
            "rolling_origin_end": 2024,
            "transition_years_excluded_from_pre_post_summary": [1971, 1972, 1973],
            "rules": ["Fit transformations and coefficients with data available at each origin only.", "Do not select source proxies, lags, or coefficients after inspecting holdout results.", "Report missing-source or insufficient-row conditions as WARN/FAIL, never by imputation."],
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Download the public FRED source files.")
    parser.add_argument("--vintage", default=datetime.now(UTC).date().isoformat(), help="Retrieval-vintage directory label.")
    args = parser.parse_args()
    vintage = args.vintage
    sources: list[dict] = []
    download_failures: list[str] = []

    for source_id, (series_id, units) in FRED_SERIES.items():
        path = RAW_ROOT / "fred" / vintage / f"{series_id}.csv"
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        if args.refresh:
            ok, reason = download(url, path)
            if not ok:
                download_failures.append(f"{series_id}: {reason}")
        sources.append(
            record(
                path,
                source_id=source_id,
                source="Federal Reserve Economic Data (FRED); upstream agency varies by series",
                source_url=f"https://fred.stlouisfed.org/series/{series_id}",
                download_url=url,
                retrieval_date=vintage if path.exists() else None,
                original_filename=f"{series_id}.csv",
                license_or_terms="FRED terms and the upstream agency terms apply; preserve attribution in downstream artifacts.",
                preprocessing="Raw FRED CSV. Annualization is performed transparently by Research_UET_Economics_Panel.py.",
                unit_system=units,
                benchmark_role="primary U.S. macroeconomic panel input",
                required_for_primary_panel=True,
                source_status="READY_FOR_REVIEW" if path.exists() else "DOWNLOAD_FAILED_OR_NOT_RUN",
            )
        )

    sources.extend(
        [
            manual_target("bea", vintage, "bea_fixed_assets_annual.csv", "bea_fixed_assets", "https://www.bea.gov/itable/fixed-assets", "BEA public-data terms; record exact table and release vintage.", ["Year", "ip_product_quantity_index_2017_100", "private_tangible_fixed_assets_quantity_index_2017_100", "government_fixed_assets_quantity_index_2017_100"], "primary knowledge and infrastructure input", True, "BEA chain-type quantity indexes, 2017=100; runtime divides by employees for indexed proxies; no dollar conversion"),
            manual_target("eia", vintage, "eia_primary_energy_annual.csv", "eia_primary_energy", "https://www.eia.gov/totalenergy/data/browser/csv.php?tbl=T01.03&freq=A", "EIA public-data terms; preserve table release vintage.", ["Year", "primary_energy_quadrillion_btu"], "primary resource-capacity energy input", True, "quadrillion Btu per year; runtime divides by population thousands before rebasing"),
            manual_target("eia", vintage, "eia_energy_history_1776_1945.csv", "eia_energy_history", "https://www.eia.gov/todayinenergy/detail.php?id=67824", "EIA public-data terms; preserve estimation notes and source columns.", ["Year", "wood_quadrillion_btu", "coal_quadrillion_btu", "petroleum_quadrillion_btu"], "historical descriptive energy-transition input", False, "source-declared quadrillion Btu; literal heat-content comparability remains blocked"),
            manual_target("epi", vintage, "epi_productivity_pay.csv", "epi_productivity_pay", "https://www.epi.org/productivity-pay-gap/", "EPI data-library terms; archive the downloaded chart data and chart date.", ["Year", "net_productivity_index", "epi_compensation_index"], "exact construction-specific wage-productivity replication", True, "dimensionless indexes rebased to 1979=100 from provider chart values"),
            manual_target("lbma", vintage, "lbma_gold_annual.csv", "lbma_gold", "https://www.lbma.org.uk/prices-and-data/precious-metal-prices", "LBMA data terms apply; archive licensed/export metadata.", ["Year", "gold_usd_per_troy_ounce"], "gold real-asset diagnostic", False, "USD per troy ounce; real normalization uses CPI-U"),
            manual_target("sp_dji", vintage, "sp500_total_return_annual.csv", "sp500_total_return", "https://www.spglobal.com/spdji/", "Requires a user-licensed S&P Dow Jones total-return export; do not use a Yahoo price-only substitute.", ["Year", "sp500_total_return_index"], "S&P wealth-preservation diagnostic", False, "dimensionless total-return index; real normalization uses CPI-U"),
        ]
    )

    required = [item for item in sources if item.get("required_for_primary_panel")]
    blockers = [f"{item['source_id']}: {item['source_status']}" for item in required if item.get("source_status") != "READY_FOR_REVIEW"]
    manifest = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "generated_at_utc": utc_now(),
        "retrieval_vintage": vintage,
        "data_class": "source-lock manifest for the Book 1 U.S. historical diagnostic lane",
        "claim_boundary": "A present file is an auditable input candidate, not an endorsement of UET or a policy claim.",
        "sources": sources,
        "download_failures": download_failures,
        "raw_root": relative(RAW_ROOT),
        "environment": runtime_environment(),
    }
    readiness = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "gate": "uet_us_historical_source_readiness",
        "status": "PASS" if not blockers else "WARN",
        "controller_reason": "All required primary-panel sources are source-packaged." if not blockers else "The U.S. historical primary panel is incomplete; model results must remain blocked.",
        "required_sources": len(required),
        "required_sources_ready": len(required) - len(blockers),
        "blockers": blockers,
        "asset_lane_status": "BLOCKED_PENDING_LBMA_AND_LICENSED_SP500_TOTAL_RETURN" if any(item["source_id"] in {"lbma_gold", "sp500_total_return"} and not item["exists"] for item in sources) else "READY_FOR_REVIEW",
        "energy_density_literal_status": "BLOCKED_PENDING_SOURCE_LOCKED_HEAT_CONTENT_BASIS",
        "claim_boundary": "This readiness gate cannot promote Topic 0.25 beyond internal diagnostic evidence.",
    }
    write_json(SOURCE_MANIFEST, manifest)
    write_json(SOURCE_READINESS, readiness)
    write_contracts()
    print("UET 0.25 economics source package")
    print(f"  readiness: {readiness['status']}")
    print(f"  required sources ready: {readiness['required_sources_ready']}/{readiness['required_sources']}")
    for blocker in blockers:
        print(f"  blocker: {blocker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
