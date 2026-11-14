"""Run predeclared proxy-family sensitivity for the R/N/K/I resource engine.

This is a measurement diagnostic, not a latent-variable proof or causal estimate.  Missing
families remain explicit blockers; the script never substitutes a convenience series.
"""

from __future__ import annotations

import math
from itertools import product

from economic_hardening_common import (
    ARTIFACT_DIR,
    PANEL_PATH,
    PANEL_STATUS,
    as_float,
    load_json,
    ols,
    read_csv,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_uet_measurement_validity_audit.json"


def load_rows() -> list[dict[str, float]]:
    rows = []
    for raw in read_csv(PANEL_PATH):
        row = {key: as_float(value) for key, value in raw.items()}
        if row.get("year") is not None:
            rows.append({key: value for key, value in row.items() if value is not None})
    return sorted(rows, key=lambda row: row["year"])


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def stdev(values: list[float]) -> float:
    center = mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / max(1, len(values) - 1))


def z(value: float, values: list[float]) -> float:
    deviation = stdev(values)
    return 0.0 if deviation == 0 else (value - mean(values)) / deviation


def log_change(current: float, previous: float) -> float | None:
    if current <= 0 or previous <= 0:
        return None
    return math.log(current / previous)


def geometric(values: list[float]) -> float:
    return math.exp(mean([math.log(value) for value in values if value > 0]))


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    left_mean, right_mean = mean(left), mean(right)
    left_dev = [value - left_mean for value in left]
    right_dev = [value - right_mean for value in right]
    denominator = math.sqrt(sum(value * value for value in left_dev) * sum(value * value for value in right_dev))
    return None if denominator == 0 else sum(a * b for a, b in zip(left_dev, right_dev)) / denominator


def sign(value: float | None) -> str:
    if value is None:
        return "NA"
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "0"


def build_families(rows: list[dict[str, float]]) -> tuple[dict, dict, dict, list[str]]:
    blockers: list[str] = []
    required = {
        "real_gdp_per_capita": "real_gdp_per_capita",
        "productivity_output_per_hour": "productivity_output_per_hour",
        "primary_energy_per_capita": "primary_energy_per_capita",
        "cpi_energy_inflation_log": "cpi_energy_inflation_log",
        "cpi_inflation_log": "cpi_inflation_log",
        "unemployment_rate_percent": "unemployment_rate_percent",
        "knowledge_per_employee": "knowledge_per_employee",
        "ip_product_quantity_index_2017_100": "ip_product_quantity_index_2017_100",
        "infrastructure_per_employee": "infrastructure_per_employee",
        "private_tangible_fixed_assets_quantity_index_2017_100": "private_tangible_fixed_assets_quantity_index_2017_100",
        "government_fixed_assets_quantity_index_2017_100": "government_fixed_assets_quantity_index_2017_100",
    }
    for name, column in required.items():
        if not any(column in row for row in rows):
            blockers.append(f"missing_column:{column}")
    if not rows:
        return {}, {}, {}, blockers
    component_values = {
        column: [row[column] for row in rows if column in row and row[column] > 0]
        for column in ["real_gdp_per_capita", "productivity_output_per_hour", "primary_energy_per_capita"]
    }
    r_families = {
        "R_core_geometric": [row.get("resource_capacity_index") for row in rows],
        "R_no_energy_geometric": [
            geometric([row["real_gdp_per_capita"], row["productivity_output_per_hour"]])
            if "real_gdp_per_capita" in row and "productivity_output_per_hour" in row else None
            for row in rows
        ],
        "R_standardized_additive": [
            100.0
            + 10.0
            * mean(
                [
                    z(row[column], component_values[column])
                    for column in component_values
                    if column in row and row[column] > 0
                ]
            )
            if all(column in row and row[column] > 0 for column in component_values)
            else None
            for row in rows
        ],
    }
    n_families = {
        "N_energy_unemployment": [
            mean(
                [
                    z(row["cpi_energy_inflation_log"], [item["cpi_energy_inflation_log"] for item in rows if "cpi_energy_inflation_log" in item]),
                    z(row["unemployment_rate_percent"], [item["unemployment_rate_percent"] for item in rows if "unemployment_rate_percent" in item]),
                ]
            )
            if "cpi_energy_inflation_log" in row and "unemployment_rate_percent" in row
            else None
            for row in rows
        ],
        "N_cpi_unemployment": [
            mean(
                [
                    z(row["cpi_inflation_log"], [item["cpi_inflation_log"] for item in rows if "cpi_inflation_log" in item]),
                    z(row["unemployment_rate_percent"], [item["unemployment_rate_percent"] for item in rows if "unemployment_rate_percent" in item]),
                ]
            )
            if "cpi_inflation_log" in row and "unemployment_rate_percent" in row
            else None
            for row in rows
        ],
        "N_unemployment_only": [
            z(row["unemployment_rate_percent"], [item["unemployment_rate_percent"] for item in rows if "unemployment_rate_percent" in item])
            if "unemployment_rate_percent" in row else None
            for row in rows
        ],
    }
    k_families = {
        "K_ip_per_employee": [row.get("knowledge_per_employee") for row in rows],
        "K_ip_quantity_index": [row.get("ip_product_quantity_index_2017_100") for row in rows],
        "K_patents_per_capita": [None for _ in rows],
    }
    i_families = {
        "I_combined_per_employee": [row.get("infrastructure_per_employee") for row in rows],
        "I_private_quantity_index": [row.get("private_tangible_fixed_assets_quantity_index_2017_100") for row in rows],
        "I_government_quantity_index": [row.get("government_fixed_assets_quantity_index_2017_100") for row in rows],
    }
    blockers.append("K_patents_per_capita:USPTO/PatsView export not present in frozen panel")
    return r_families, n_families, {**k_families, **i_families}, blockers


def aligned_changes(values: list[float | None], years: list[float], horizon: int) -> list[dict[str, float]]:
    by_year = {int(year): value for year, value in zip(years, values) if value is not None and value > 0}
    output = []
    for year in sorted(by_year):
        target = by_year.get(year + horizon)
        previous = by_year.get(year - 1)
        if target is None or previous is None:
            continue
        change = log_change(by_year[year], previous)
        target_change = log_change(target, by_year[year])
        if change is not None and target_change is not None:
            output.append({"year": float(year), "growth": change, "target": target_change})
    return output


def run_combinations(rows: list[dict[str, float]], r_families: dict, n_families: dict, ki_families: dict) -> list[dict]:
    years = [row["year"] for row in rows]
    results = []
    for r_name, n_name, k_name, i_name in product(r_families, n_families, [name for name in ki_families if name.startswith("K_")], [name for name in ki_families if name.startswith("I_")]):
        if "patents" in k_name:
            continue
        r_values, n_values = r_families[r_name], n_families[n_name]
        k_values, i_values = ki_families[k_name], ki_families[i_name]
        by_year = {int(row["year"]): row for row in rows}
        observations = []
        for year in sorted(by_year):
            target_row = by_year.get(year + 3)
            if target_row is None:
                continue
            index = year - int(rows[0]["year"])
            target_index = int(target_row["year"]) - int(rows[0]["year"])
            if any(index >= len(values) or target_index >= len(values) for values in [r_values, n_values, k_values, i_values]):
                continue
            if any(values[index] is None or values[target_index] is None for values in [r_values, k_values, i_values]) or n_values[index] is None:
                continue
            r_growth = log_change(r_values[target_index], r_values[index])
            k_growth = log_change(k_values[index], k_values[index - 1]) if index > 0 and k_values[index - 1] else None
            i_growth = log_change(i_values[index], i_values[index - 1]) if index > 0 and i_values[index - 1] else None
            if r_growth is None or k_growth is None or i_growth is None:
                continue
            observations.append({"year": float(year), "n": n_values[index], "k": k_growth, "i": i_growth, "target": r_growth})
        if len(observations) < 12:
            results.append({"r_family": r_name, "n_family": n_name, "k_family": k_name, "i_family": i_name, "status": "INSUFFICIENT_ROWS", "n": len(observations)})
            continue
        fit = ols([[1.0, row["n"], row["k"], row["i"]] for row in observations], [row["target"] for row in observations])
        results.append({
            "r_family": r_name,
            "n_family": n_name,
            "k_family": k_name,
            "i_family": i_name,
            "status": "DIAGNOSTIC_COMPLETE",
            "n": len(observations),
            "coefficients": fit["coefficients"],
            "coefficient_signs": [sign(value) for value in fit["coefficients"][1:]],
            "r_squared": fit["r_squared"],
            "residual_rmse": fit["residual_rmse"],
        })
    return results


def main() -> int:
    panel_status = load_json(PANEL_STATUS)
    if panel_status.get("status") != "PASS" or not PANEL_PATH.exists():
        write_json(ARTIFACT, {"schema_version": "2.0", "topic": "0.25_Strategy_Power_Economics", "status": "WARN", "generated_at_utc": utc_now(), "blockers": ["panel_not_pass"]})
        return 0
    rows = load_rows()
    r_families, n_families, ki_families, blockers = build_families(rows)
    available_r = {name: [value for value in values if value is not None and value > 0] for name, values in r_families.items()}
    correlations = {}
    for left, right in product(r_families, r_families):
        if left >= right:
            continue
        aligned = [(a, b) for a, b in zip(r_families[left], r_families[right]) if a is not None and b is not None]
        correlations[f"{left}__{right}"] = pearson([item[0] for item in aligned], [item[1] for item in aligned])
    combinations = run_combinations(rows, r_families, n_families, ki_families)
    stable_r = all(value is not None and value >= 0.8 for value in correlations.values())
    usable = [item for item in combinations if item.get("status") == "DIAGNOSTIC_COMPLETE"]
    sign_patterns = {tuple(item["coefficient_signs"]) for item in usable}
    directional_stability = len(sign_patterns) <= 1 and bool(usable)
    operationalization_counts = {
        "R": len(r_families),
        "N": len(n_families),
        "K": sum(name.startswith("K_") for name in ki_families),
        "I": sum(name.startswith("I_") for name in ki_families),
    }
    at_least_three_available = all(count >= 3 for count in operationalization_counts.values())
    independent_provenance_families = {
        "R": ["shared_BEA_BLS_EIA_component_set"],
        "N": ["shared_BLS_macro_constraint_set"],
        "K": ["BEA_IP_quantity_family"],
        "I": ["BEA_fixed_asset_quantity_family"],
    }
    at_least_three_independent = all(len(groups) >= 3 for groups in independent_provenance_families.values())
    status = "PASS" if stable_r and directional_stability and at_least_three_available and at_least_three_independent and not blockers else "WARN"
    artifact = {
        "schema_version": "2.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "generated_at_utc": utc_now(),
        "panel": {"path": str(PANEL_PATH), "sha256": panel_status.get("panel_sha256"), "coverage": [1959, 2024], "n": len(rows)},
        "constructs": {"R": list(r_families), "N": list(n_families), "K": list(name for name in ki_families if name.startswith("K_")), "I": list(name for name in ki_families if name.startswith("I_"))},
        "proxy_family_correlations": correlations,
        "three_year_diagnostic_combinations": combinations,
        "measurement_gates": {
            "operationalization_counts": operationalization_counts,
            "at_least_three_available_operationalizations_per_construct": at_least_three_available,
            "independent_provenance_families": independent_provenance_families,
            "at_least_three_independent_measurement_families": at_least_three_independent,
            "pairwise_R_correlation_threshold": 0.8,
            "R_family_stability": stable_r,
            "directional_coefficient_stability": directional_stability,
            "no_silent_imputation": True,
        },
        "blockers": sorted(set(blockers)),
        "claim_boundary": "This legacy R/N/K/I artifact tests proxy sensitivity only. The operationalizations do not yet constitute three independent measurement families, and BOOK-HEURISTIC-001 is retired as an identity.",
    }
    write_json(ARTIFACT, artifact)
    print(f"UET measurement-validity audit: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
