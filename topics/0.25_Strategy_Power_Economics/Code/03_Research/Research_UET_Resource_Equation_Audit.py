"""Audit the operational R/N/K/I resource-engine hypothesis without causal claims."""

from __future__ import annotations

import math

from economic_hardening_common import (
    ARTIFACT_DIR,
    PANEL_PATH,
    PANEL_STATUS,
    PARAMETER_POLICY,
    as_float,
    load_json,
    median,
    moving_block_bootstrap_interval,
    ols,
    read_csv,
    rmse,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_uet_resource_equation_audit.json"


def load_panel() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for raw in read_csv(PANEL_PATH):
        row = {key: as_float(value) for key, value in raw.items()}
        if row.get("year") is not None:
            rows.append({key: value for key, value in row.items() if value is not None})
    return sorted(rows, key=lambda row: row["year"])


def source_rows(rows_by_year: dict[int, dict[str, float]], horizon: int, maximum_origin: int) -> list[dict[str, float]]:
    observations = []
    for year, row in rows_by_year.items():
        target = rows_by_year.get(year + horizon)
        if year > maximum_origin or target is None:
            continue
        required = ["cpi_energy_inflation_log", "unemployment_rate_percent", "knowledge_log_growth", "infrastructure_log_growth"]
        if any(name not in row for name in required) or "resource_capacity_log" not in target or "resource_capacity_log" not in row:
            continue
        observations.append(
            {
                "year": float(year),
                "energy_inflation": row["cpi_energy_inflation_log"],
                "unemployment": row["unemployment_rate_percent"],
                "knowledge_growth": row["knowledge_log_growth"],
                "infrastructure_growth": row["infrastructure_log_growth"],
                "target": target["resource_capacity_log"] - row["resource_capacity_log"],
            }
        )
    return sorted(observations, key=lambda row: row["year"])


def n_stats(observations: list[dict[str, float]]) -> tuple[float, float, float, float]:
    energy = [row["energy_inflation"] for row in observations]
    unemployment = [row["unemployment"] for row in observations]
    energy_mean = sum(energy) / len(energy)
    unemployment_mean = sum(unemployment) / len(unemployment)
    energy_std = math.sqrt(sum((value - energy_mean) ** 2 for value in energy) / max(1, len(energy) - 1))
    unemployment_std = math.sqrt(sum((value - unemployment_mean) ** 2 for value in unemployment) / max(1, len(unemployment) - 1))
    return energy_mean, energy_std, unemployment_mean, unemployment_std


def feature(row: dict[str, float], stats: tuple[float, float, float, float]) -> list[float]:
    energy_mean, energy_std, unemployment_mean, unemployment_std = stats
    energy_z = 0.0 if energy_std == 0 else (row["energy_inflation"] - energy_mean) / energy_std
    unemployment_z = 0.0 if unemployment_std == 0 else (row["unemployment"] - unemployment_mean) / unemployment_std
    return [1.0, (energy_z + unemployment_z) / 2.0, row["knowledge_growth"], row["infrastructure_growth"]]


def run_horizon(rows_by_year: dict[int, dict[str, float]], horizon: int, rolling_start: int) -> dict:
    all_observations = source_rows(rows_by_year, horizon, max(rows_by_year))
    if len(all_observations) < 12:
        return {"horizon_years": horizon, "status": "INSUFFICIENT_ROWS", "n": len(all_observations)}
    pre_holdout_observations = [row for row in all_observations if int(row["year"]) < rolling_start]
    if len(pre_holdout_observations) < 12:
        return {"horizon_years": horizon, "status": "INSUFFICIENT_PRE_HOLDOUT_ROWS", "n": len(pre_holdout_observations)}
    pre_holdout_stats = n_stats(pre_holdout_observations)
    pre_holdout_fit = ols(
        [feature(row, pre_holdout_stats) for row in pre_holdout_observations],
        [row["target"] for row in pre_holdout_observations],
    )
    origins: list[int] = []
    actual: list[float] = []
    uet_predictions: list[float] = []
    baseline_predictions = {"constant_growth": [], "zero_growth": []}
    for origin in range(rolling_start, max(rows_by_year) - horizon + 1):
        training = source_rows(rows_by_year, horizon, origin - horizon)
        candidate = next((row for row in source_rows(rows_by_year, horizon, origin) if int(row["year"]) == origin), None)
        if candidate is None or len(training) < 20:
            continue
        stats = n_stats(training)
        try:
            fit = ols([feature(row, stats) for row in training], [row["target"] for row in training])
        except ValueError:
            continue
        prediction = sum(coefficient * value for coefficient, value in zip(fit["coefficients"], feature(candidate, stats)))
        origins.append(origin)
        actual.append(candidate["target"])
        uet_predictions.append(prediction)
        baseline_predictions["constant_growth"].append(sum(row["target"] for row in training) / len(training))
        baseline_predictions["zero_growth"].append(0.0)

    uet_rmse = rmse(actual, uet_predictions)
    uet_median_absolute_error = median([abs(observed - predicted) for observed, predicted in zip(actual, uet_predictions)])
    baseline_metrics: dict[str, dict] = {}
    for name, predictions in baseline_predictions.items():
        baseline_rmse = rmse(actual, predictions)
        baseline_median_absolute_error = median([abs(observed - predicted) for observed, predicted in zip(actual, predictions)])
        deltas = [(uet - observed) ** 2 - (baseline - observed) ** 2 for observed, uet, baseline in zip(actual, uet_predictions, predictions)]
        baseline_metrics[name] = {
            "rolling_origin_rmse": baseline_rmse,
            "median_absolute_error": baseline_median_absolute_error,
            "rmse_improvement": None if uet_rmse is None or baseline_rmse in {None, 0} else 1.0 - uet_rmse / baseline_rmse,
            "median_absolute_error_improvement": None if uet_median_absolute_error is None or baseline_median_absolute_error in {None, 0} else 1.0 - uet_median_absolute_error / baseline_median_absolute_error,
            "squared_error_delta_bootstrap": moving_block_bootstrap_interval(deltas),
        }
    acceptance = all(
        item["rmse_improvement"] is not None
        and item["rmse_improvement"] >= 0.1
        and item["squared_error_delta_bootstrap"].get("upper") is not None
        and item["squared_error_delta_bootstrap"]["upper"] < 0
        for item in baseline_metrics.values()
    )
    beta_n, beta_k, beta_i = pre_holdout_fit["coefficients"][1:]
    candidate_signal = bool(acceptance and beta_k > 0 and beta_i > 0)
    constant = baseline_metrics["constant_growth"]
    return {
        "horizon_years": horizon,
        "status": "DIAGNOSTIC_COMPLETE",
        "pre_holdout_fit": {
            "coefficient_labels": ["intercept", "necessity_constraint_proxy", "knowledge_growth", "infrastructure_growth"],
            "coefficients": pre_holdout_fit["coefficients"],
            "r_squared": pre_holdout_fit["r_squared"],
            "residual_rmse": pre_holdout_fit["residual_rmse"],
            "n": pre_holdout_fit["n"],
            "fit_window": f"through_{rolling_start - 1}",
        },
        "rolling_origin": {
            "origins": origins,
            "uet_rmse": uet_rmse,
            "uet_median_absolute_error": uet_median_absolute_error,
            "constant_growth_baseline_rmse": constant["rolling_origin_rmse"],
            "constant_growth_baseline_median_absolute_error": constant["median_absolute_error"],
            "rmse_improvement": constant["rmse_improvement"],
            "median_absolute_error_improvement": constant["median_absolute_error_improvement"],
            "squared_error_delta_bootstrap": constant["squared_error_delta_bootstrap"],
            "baseline_metrics": baseline_metrics,
            "acceptance_rule": "Candidate requires at least 10 percent lower rolling-origin RMSE than every declared baseline and a 95 percent moving-block-bootstrap squared-error interval below zero.",
        },
        "candidate_signal": candidate_signal,
        "interpretation": "This legacy proxy sensitivity is retained as a bounded internal diagnostic. It is neither causal evidence nor a claim-class upgrade.",
    }


def main() -> int:
    panel_status = load_json(PANEL_STATUS)
    policy = load_json(PARAMETER_POLICY)
    if panel_status.get("status") != "PASS" or not PANEL_PATH.exists():
        artifact = {
            "schema_version": "2.0",
            "topic": "0.25_Strategy_Power_Economics",
            "status": "WARN",
            "generated_at_utc": utc_now(),
            "formula_ids": ["BOOK-HEURISTIC-001", "EC25-INNOVATION-CONSTRAINT"],
            "blockers": panel_status.get("blockers", ["Normalized U.S. panel is absent."]),
            "claim_boundary": "The R/N/K/I diagnostic did not run because the source-locked panel is incomplete.",
        }
        write_json(ARTIFACT, artifact)
        print("UET resource-equation audit: WARN (panel blocked)")
        return 0
    rows = load_panel()
    rows_by_year = {int(row["year"]): row for row in rows}
    horizons = [policy.get("horizons", {}).get("primary", 3)] + policy.get("horizons", {}).get("sensitivity", [1, 5])
    results = [run_horizon(rows_by_year, int(horizon), int(load_json(__import__("economic_hardening_common").HOLDOUT_POLICY).get("rolling_origin_start", 2000))) for horizon in horizons]
    primary = next((item for item in results if item["horizon_years"] == policy.get("horizons", {}).get("primary", 3)), results[0])
    artifact = {
        "schema_version": "2.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "DIAGNOSTIC_COMPLETE",
        "generated_at_utc": utc_now(),
        "formula_ids": ["BOOK-HEURISTIC-001", "EC25-INNOVATION-CONSTRAINT"],
        "parameter_policy": policy,
        "results": results,
        "controller_status": "CANDIDATE_SIGNAL_INTERNAL_ONLY" if primary.get("candidate_signal") else "NO_PREDECLARED_CANDIDATE_SIGNAL",
        "claim_boundary": "This legacy proxy sensitivity is retained as a negative internal diagnostic. BOOK-HEURISTIC-001 is retired as an identity; the result does not establish causality or an economic law.",
    }
    write_json(ARTIFACT, artifact)
    print(f"UET resource-equation audit: {artifact['controller_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
