"""Diagnostic tests for the Book 1 monetary-resource and pegged-stone hypotheses."""

from __future__ import annotations

import math

from economic_hardening_common import (
    ARTIFACT_DIR,
    PANEL_PATH,
    PANEL_STATUS,
    PARAMETER_POLICY,
    SOURCE_MANIFEST,
    as_float,
    load_json,
    median,
    moving_block_bootstrap_interval,
    ols,
    read_csv,
    rmse,
    source_path,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_stone_balloon_audit.json"


def panel_rows() -> dict[int, dict[str, float]]:
    output: dict[int, dict[str, float]] = {}
    for raw in read_csv(PANEL_PATH):
        row = {key: as_float(value) for key, value in raw.items()}
        if row.get("year") is not None:
            output[int(row["year"])] = {key: value for key, value in row.items() if value is not None}
    return output


def inflation_observations(rows: dict[int, dict[str, float]], horizon: int, maximum_origin: int) -> list[dict[str, float]]:
    observations = []
    required = ["cpi_inflation_log", "m2_log_growth", "real_gdp_per_capita_log_growth", "monetary_resource_mismatch"]
    for year, row in rows.items():
        target = rows.get(year + horizon)
        if year > maximum_origin or target is None or any(name not in row for name in required) or "cpi_inflation_log" not in target:
            continue
        observations.append(
            {
                "year": float(year),
                "inflation_now": row["cpi_inflation_log"],
                "m2_growth": row["m2_log_growth"],
                "quantity_gap": row["m2_log_growth"] - row["real_gdp_per_capita_log_growth"],
                "uet_mismatch": row["monetary_resource_mismatch"],
                "target": target["cpi_inflation_log"],
            }
        )
    return sorted(observations, key=lambda row: row["year"])


def model_features(model: str, row: dict[str, float]) -> list[float]:
    if model == "inflation_autoregression":
        return [1.0, row["inflation_now"]]
    if model == "money_growth_only":
        return [1.0, row["m2_growth"]]
    if model == "quantity_style":
        return [1.0, row["quantity_gap"]]
    if model == "uet_monetary_resource_mismatch":
        return [1.0, row["uet_mismatch"]]
    raise ValueError(f"Unknown model: {model}")


def rolling_models(rows: dict[int, dict[str, float]], horizon: int, start: int = 2000) -> dict:
    names = ["inflation_autoregression", "money_growth_only", "quantity_style", "uet_monetary_resource_mismatch"]
    predictions = {name: [] for name in names}
    actual: list[float] = []
    origins: list[int] = []
    for origin in range(start, max(rows) - horizon + 1):
        training = inflation_observations(rows, horizon, origin - horizon)
        candidate = next((row for row in inflation_observations(rows, horizon, origin) if int(row["year"]) == origin), None)
        if candidate is None or len(training) < 20:
            continue
        pending: dict[str, float] = {}
        try:
            for name in names:
                fit = ols([model_features(name, row) for row in training], [row["target"] for row in training])
                pending[name] = sum(coefficient * value for coefficient, value in zip(fit["coefficients"], model_features(name, candidate)))
        except ValueError:
            continue
        origins.append(origin)
        actual.append(candidate["target"])
        for name in names:
            predictions[name].append(pending[name])
    metrics = {
        name: {
            "rolling_origin_rmse": rmse(actual, predicted),
            "median_absolute_error": median([abs(observed - forecast) for observed, forecast in zip(actual, predicted)]),
        }
        for name, predicted in predictions.items()
    }
    uet_rmse = metrics["uet_monetary_resource_mismatch"]["rolling_origin_rmse"]
    uet_median_absolute_error = metrics["uet_monetary_resource_mismatch"]["median_absolute_error"]
    comparisons = {}
    for name in names[:-1]:
        baseline_rmse = metrics[name]["rolling_origin_rmse"]
        baseline_median_absolute_error = metrics[name]["median_absolute_error"]
        deltas = [(uet - observed) ** 2 - (baseline - observed) ** 2 for observed, uet, baseline in zip(actual, predictions["uet_monetary_resource_mismatch"], predictions[name])]
        comparisons[name] = {
            "rmse_improvement": None if uet_rmse is None or baseline_rmse in {None, 0} else 1.0 - uet_rmse / baseline_rmse,
            "median_absolute_error_improvement": None if uet_median_absolute_error is None or baseline_median_absolute_error in {None, 0} else 1.0 - uet_median_absolute_error / baseline_median_absolute_error,
            "squared_error_delta_bootstrap": moving_block_bootstrap_interval(deltas),
        }
    candidate_signal = bool(comparisons) and all(
        item["rmse_improvement"] is not None
        and item["rmse_improvement"] >= 0.1
        and item["squared_error_delta_bootstrap"].get("upper") is not None
        and item["squared_error_delta_bootstrap"]["upper"] < 0
        for item in comparisons.values()
    )
    return {
        "horizon_years": horizon,
        "origins": origins,
        "actual_inflation": actual,
        "model_metrics": metrics,
        "uet_vs_baselines": comparisons,
        "acceptance_rule": "Candidate requires at least 10 percent lower rolling-origin RMSE than every named baseline and a 95 percent block-bootstrap squared-error interval below zero.",
        "candidate_signal": candidate_signal,
    }


def correlation(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3 or len(x) != len(y):
        return None
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - x_mean) ** 2 for a in x) * sum((b - y_mean) ** 2 for b in y))
    return None if denominator == 0 else numerator / denominator


def regime_summary(rows: dict[int, dict[str, float]], start: int, end: int) -> dict:
    selected = [row for year, row in rows.items() if start <= year <= end and "monetary_resource_mismatch" in row and "cpi_inflation_log" in row]
    mismatch = [row["monetary_resource_mismatch"] for row in selected]
    inflation = [row["cpi_inflation_log"] for row in selected]
    return {
        "years": [start, end],
        "n": len(selected),
        "mean_monetary_resource_mismatch": sum(mismatch) / len(mismatch) if mismatch else None,
        "mean_cpi_inflation_log": sum(inflation) / len(inflation) if inflation else None,
        "same_year_correlation": correlation(mismatch, inflation),
        "interpretation": "Descriptive regime summary only; 1971-1973 are excluded and no intervention effect is identified.",
    }


def manual_annual(path, column: str) -> dict[int, float]:
    output = {}
    if path is None:
        return output
    for row in read_csv(path):
        year = as_float(row.get("Year"))
        value = as_float(row.get(column))
        if year is not None and value is not None:
            output[int(year)] = value
    return output


def asset_lane(rows: dict[int, dict[str, float]], manifest: dict) -> dict:
    gold = manual_annual(source_path(manifest, "lbma_gold"), "gold_usd_per_troy_ounce")
    sp500 = manual_annual(source_path(manifest, "sp500_total_return"), "sp500_total_return_index")
    blockers = []
    if not gold:
        blockers.append("LBMA annual gold export is absent.")
    if not sp500:
        blockers.append("Licensed S&P 500 total-return annual export is absent; Yahoo price-only data are forbidden here.")
    if blockers:
        return {"status": "BLOCKED", "blockers": blockers, "claim_boundary": "No asset may be called a pegged stone without exact source-locked asset series."}
    assets = {"gold": gold, "sp500_total_return": sp500}
    summaries = {}
    for name, series in assets.items():
        years = sorted(set(series).intersection(rows))
        if len(years) < 15:
            summaries[name] = {"status": "INSUFFICIENT_COMMON_ROWS", "n": len(years)}
            continue
        base_year = years[0]
        base_real = series[base_year] / rows[base_year]["cpi_u"]
        residuals = []
        cash_residuals = []
        rolling_asset_errors = []
        rolling_cash_errors = []
        for year in years:
            real_index = 100.0 * (series[year] / rows[year]["cpi_u"]) / base_real
            resource = rows[year]["resource_capacity_index"]
            cash_index = 100.0 * rows[base_year]["cpi_u"] / rows[year]["cpi_u"]
            residuals.append(math.log(real_index) - math.log(resource))
            cash_residuals.append(math.log(cash_index) - math.log(resource))
        for index in range(9, len(years)):
            rolling_asset_errors.append(math.sqrt(sum(value * value for value in residuals[index - 9 : index + 1]) / 10))
            rolling_cash_errors.append(math.sqrt(sum(value * value for value in cash_residuals[index - 9 : index + 1]) / 10))
        summaries[name] = {
            "status": "DIAGNOSTIC_COMPLETE",
            "base_year": base_year,
            "n": len(years),
            "resource_tracking_rmse": math.sqrt(sum(value * value for value in residuals) / len(residuals)),
            "cash_tracking_rmse": math.sqrt(sum(value * value for value in cash_residuals) / len(cash_residuals)),
            "median_10_year_tracking_rmse": sorted(rolling_asset_errors)[len(rolling_asset_errors) // 2] if rolling_asset_errors else None,
            "median_10_year_cash_tracking_rmse": sorted(rolling_cash_errors)[len(rolling_cash_errors) // 2] if rolling_cash_errors else None,
            "residual_mean_reversion_proxy": correlation(residuals[:-1], [residuals[index + 1] - residuals[index] for index in range(len(residuals) - 1)]),
            "candidate_peg_signal": False,
            "claim_boundary": "Tracking diagnostics alone do not establish a currency peg, intrinsic value, or asset superiority.",
        }
    return {"status": "DIAGNOSTIC_COMPLETE", "assets": summaries}


def main() -> int:
    panel_status = load_json(PANEL_STATUS)
    if panel_status.get("status") != "PASS" or not PANEL_PATH.exists():
        artifact = {"schema_version": "2.0", "topic": "0.25_Strategy_Power_Economics", "status": "WARN", "generated_at_utc": utc_now(), "formula_ids": ["EC25-MONEY-IDENTITY", "EC25-RESOURCE-COVERAGE-DIAGNOSTIC"], "blockers": panel_status.get("blockers", ["Normalized panel is absent."]), "claim_boundary": "Stone-in-the-Balloon diagnostics did not run."}
        write_json(ARTIFACT, artifact)
        print("Stone-in-the-Balloon audit: WARN (panel blocked)")
        return 0
    rows = panel_rows()
    policy = load_json(PARAMETER_POLICY)
    horizons = [policy.get("horizons", {}).get("primary", 3)] + policy.get("horizons", {}).get("sensitivity", [1, 5])
    inflation_results = [rolling_models(rows, int(horizon)) for horizon in horizons]
    manifest = load_json(SOURCE_MANIFEST)
    artifact = {
        "schema_version": "2.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "DIAGNOSTIC_COMPLETE",
        "generated_at_utc": utc_now(),
        "formula_ids": ["EC25-MONEY-IDENTITY", "EC25-RESOURCE-COVERAGE-DIAGNOSTIC"],
        "inflation_baseline_comparison": inflation_results,
        "pre_1971_summary": regime_summary(rows, 1959, 1970),
        "post_1973_summary": regime_summary(rows, 1974, 2024),
        "asset_lane": asset_lane(rows, manifest),
        "claim_boundary": "This is a U.S. resource-coverage diagnostic, not observed money value. It does not identify a fiat-currency intervention effect or establish asset superiority.",
    }
    write_json(ARTIFACT, artifact)
    print("Stone-in-the-Balloon audit: DIAGNOSTIC_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
