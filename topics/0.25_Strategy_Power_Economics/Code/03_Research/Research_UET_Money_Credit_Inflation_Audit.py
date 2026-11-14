"""Descriptive money, credit, velocity, and inflation diagnostics for Wave 4."""

from __future__ import annotations

import math

from economic_hardening_common import ARTIFACT_DIR, PANEL_PATH, PANEL_STATUS, as_float, load_json, read_csv, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_money_credit_inflation_audit.json"


def load_rows() -> list[dict[str, float]]:
    rows = []
    for raw in read_csv(PANEL_PATH):
        row = {key: as_float(value) for key, value in raw.items()}
        if row.get("year") is not None:
            rows.append({key: value for key, value in row.items() if value is not None})
    return sorted(rows, key=lambda row: row["year"])


def log_change(current: float, previous: float) -> float | None:
    if current <= 0 or previous <= 0:
        return None
    return math.log(current / previous)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    lm, rm = mean(left), mean(right)
    ldev, rdev = [x - lm for x in left], [x - rm for x in right]
    denominator = math.sqrt(sum(x * x for x in ldev) * sum(x * x for x in rdev))
    return None if denominator == 0 else sum(a * b for a, b in zip(ldev, rdev)) / denominator


def regression(features: list[list[float]], targets: list[float]) -> list[float]:
    width = len(features[0])
    xtx = [[0.0] * width for _ in range(width)]
    xty = [0.0] * width
    for row, target in zip(features, targets):
        for i in range(width):
            xty[i] += row[i] * target
            for j in range(width):
                xtx[i][j] += row[i] * row[j]
    augmented = [xtx[i][:] + [xty[i]] for i in range(width)]
    for col in range(width):
        pivot = max(range(col, width), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("singular monetary-credit design")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [x / scale for x in augmented[col]]
        for row in range(width):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[col])]
    return [augmented[i][-1] for i in range(width)]


def main() -> int:
    panel_status = load_json(PANEL_STATUS)
    required = ["year", "m2_usd_billions", "real_gdp", "gdp_deflator", "cpi_inflation_log", "domestic_nonfinancial_debt_usd_billions", "resource_capacity_log"]
    if panel_status.get("status") != "PASS" or not PANEL_PATH.exists():
        write_json(ARTIFACT, {"schema_version": "1.0", "topic": "0.25_Strategy_Power_Economics", "status": "WARN", "generated_at_utc": utc_now(), "blockers": ["panel_not_pass"]})
        return 0
    rows = load_rows()
    missing = [field for field in required if not any(field in row for row in rows)]
    observations = []
    by_year = {int(row["year"]): row for row in rows}
    for year in sorted(by_year):
        row = by_year[year]
        previous = by_year.get(year - 1)
        if previous is None or any(field not in row or field not in previous for field in required if field != "year"):
            continue
        m2_growth = log_change(row["m2_usd_billions"], previous["m2_usd_billions"])
        debt_growth = log_change(row["domestic_nonfinancial_debt_usd_billions"], previous["domestic_nonfinancial_debt_usd_billions"])
        nominal_gdp = row["real_gdp"] * row["gdp_deflator"]
        previous_nominal_gdp = previous["real_gdp"] * previous["gdp_deflator"]
        nominal_gdp_growth = log_change(nominal_gdp, previous_nominal_gdp)
        velocity = nominal_gdp / row["m2_usd_billions"] if row["m2_usd_billions"] > 0 else None
        previous_velocity = previous_nominal_gdp / previous["m2_usd_billions"] if previous["m2_usd_billions"] > 0 else None
        velocity_growth = log_change(velocity, previous_velocity) if velocity and previous_velocity else None
        credit_to_gdp = row["domestic_nonfinancial_debt_usd_billions"] / nominal_gdp if nominal_gdp > 0 else None
        if None in {m2_growth, debt_growth, nominal_gdp_growth, velocity_growth, credit_to_gdp}:
            continue
        observations.append({"year": year, "inflation": row["cpi_inflation_log"], "m2_growth": m2_growth, "debt_growth": debt_growth, "nominal_gdp_growth": nominal_gdp_growth, "velocity_growth": velocity_growth, "credit_to_gdp": credit_to_gdp, "mismatch": row.get("monetary_resource_mismatch")})
    for index, row in enumerate(observations):
        trailing = [item["credit_to_gdp"] for item in observations[max(0, index - 5): index + 1]]
        row["credit_to_gdp_gap_5y"] = row["credit_to_gdp"] - mean(trailing)
        row["regime"] = "pre_1971" if row["year"] <= 1970 else ("transition_excluded" if row["year"] <= 1973 else "post_1973")
    usable = [row for row in observations if row["mismatch"] is not None]
    correlations = {}
    for field in ["mismatch", "m2_growth", "debt_growth", "velocity_growth", "credit_to_gdp_gap_5y"]:
        correlations[field] = correlation([row[field] for row in usable], [row["inflation"] for row in usable])
    models = {}
    if len(usable) > 8:
        target = [row["inflation"] for row in usable]
        designs = {
            "mismatch_only": [[1.0, row["mismatch"]] for row in usable],
            "money_credit": [[1.0, row["m2_growth"], row["debt_growth"], row["credit_to_gdp_gap_5y"]] for row in usable],
            "money_credit_velocity": [[1.0, row["m2_growth"], row["debt_growth"], row["credit_to_gdp_gap_5y"], row["velocity_growth"]] for row in usable],
        }
        for name, design in designs.items():
            try:
                coefficients = regression(design, target)
                models[name] = {"coefficients": coefficients, "n": len(target), "interpretation": "descriptive association only"}
            except ValueError as error:
                models[name] = {"status": "WARN", "error": str(error)}
    regime_summary = {}
    for regime in ["pre_1971", "post_1973"]:
        subset = [row for row in observations if row["regime"] == regime]
        regime_summary[regime] = {"n": len(subset), "mean_inflation": mean([row["inflation"] for row in subset]) if subset else None, "mean_mismatch": mean([row["mismatch"] for row in subset]) if subset else None, "mean_credit_to_gdp": mean([row["credit_to_gdp"] for row in subset]) if subset else None}
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PASS" if not missing and len(observations) >= 50 else "WARN",
        "generated_at_utc": utc_now(),
        "panel": {"path": str(PANEL_PATH), "coverage": [1959, 2024], "rows": len(observations), "no_imputation": True},
        "definitions": {"nominal_gdp_proxy": "real_gdp multiplied by GDP deflator", "velocity": "nominal GDP proxy divided by M2", "credit_to_gdp_gap_5y": "current debt/nominal-GDP ratio minus trailing five-year mean", "transition_policy": "1971-1973 described separately and excluded from pre/post summaries"},
        "correlations_with_inflation": correlations,
        "descriptive_models": models,
        "regime_summary": regime_summary,
        "observations": observations,
        "blockers": missing,
        "claim_boundary": "Money, credit, velocity, and inflation results are descriptive diagnostics. They do not identify fiat-currency, monetary-policy, or fiscal causal effects.",
    }
    write_json(ARTIFACT, artifact)
    print(f"UET money-credit-inflation audit: {artifact['status']} ({len(observations)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
