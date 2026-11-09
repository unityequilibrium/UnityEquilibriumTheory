"""Normalize the source-locked U.S. historical economics panel for Topic 0.25."""

from __future__ import annotations

import math
from pathlib import Path

from economic_hardening_common import (
    PANEL_PATH,
    PANEL_STATUS,
    ROOT,
    SOURCE_MANIFEST,
    SOURCE_READINESS,
    annualise_fred,
    as_float,
    load_json,
    log_change,
    read_csv,
    rebased_index,
    relative,
    sha256,
    source_path,
    utc_now,
    write_csv,
    write_json,
)


START_YEAR = 1959
END_YEAR = 2024


def verified_source_path(manifest: dict, source_id: str, blockers: list[str]) -> Path | None:
    for item in manifest.get("sources", []):
        if item.get("source_id") != source_id or not item.get("local_path"):
            continue
        candidate = ROOT / item["local_path"]
        if not candidate.exists():
            blockers.append(f"{source_id}: source file is absent from the manifest path.")
            return None
        expected = item.get("sha256")
        if expected and sha256(candidate) != expected:
            blockers.append(f"{source_id}: SHA-256 mismatch against source manifest.")
            return None
        return candidate
    blockers.append(f"{source_id}: source file is absent from the manifest.")
    return None


def annual_manual(path: Path, field_names: list[str]) -> dict[str, dict[int, float]]:
    output = {field: {} for field in field_names}
    for row in read_csv(path):
        year = as_float(row.get("Year"))
        if year is None or int(year) != year:
            continue
        for field in field_names:
            value = as_float(row.get(field))
            if value is not None:
                output[field][int(year)] = value
    return output


def main() -> int:
    manifest = load_json(SOURCE_MANIFEST)
    readiness = load_json(SOURCE_READINESS)
    blockers: list[str] = []
    if not manifest:
        blockers.append("Source manifest is missing; run Research_UET_Economics_Source_Package.py first.")
    if readiness.get("status") != "PASS":
        blockers.extend(readiness.get("blockers", []))

    fred_methods = {
        "fred_m2sl": "end",
        "fred_gdpc1": "mean",
        "fred_pop": "mean",
        "fred_unrate": "mean",
        "fred_cpiengsl": "mean",
        "fred_cpiaucsl": "mean",
        "fred_gdpdef": "mean",
        "fred_tb3ms": "mean",
        "fred_ophnfb": "mean",
        "fred_comprnfb": "mean",
        "fred_payems": "mean",
        "fred_cmdebt": "end",
    }
    fred: dict[str, dict[int, float]] = {}
    for source_id, method in fred_methods.items():
        path = verified_source_path(manifest, source_id, blockers)
        if path is None:
            blockers.append(f"{source_id}: source file is absent from the manifest.")
            continue
        try:
            fred[source_id] = annualise_fred(path, method)
        except Exception as error:  # noqa: BLE001
            blockers.append(f"{source_id}: annualization failed ({type(error).__name__}: {error}).")

    bea_path = verified_source_path(manifest, "bea_fixed_assets", blockers)
    eia_path = verified_source_path(manifest, "eia_primary_energy", blockers)
    bea: dict[str, dict[int, float]] = {}
    energy: dict[str, dict[int, float]] = {}
    if bea_path is None:
        blockers.append("bea_fixed_assets: required normalized annual export is absent.")
    else:
        bea = annual_manual(
            bea_path,
            ["ip_product_quantity_index_2017_100", "private_tangible_fixed_assets_quantity_index_2017_100", "government_fixed_assets_quantity_index_2017_100"],
        )
    if eia_path is None:
        blockers.append("eia_primary_energy: required normalized annual export is absent.")
    else:
        energy = annual_manual(eia_path, ["primary_energy_quadrillion_btu"])

    required_series = list(fred_methods)
    if any(source_id not in fred for source_id in required_series) or not bea or not energy:
        blockers.append("Primary panel cannot be constructed until every declared primary source is present and parseable.")

    rows: list[dict[str, object]] = []
    missing_years: dict[str, list[int]] = {}
    if not blockers:
        for year in range(START_YEAR, END_YEAR + 1):
            values = {
                "m2_usd_billions": fred["fred_m2sl"].get(year),
                "real_gdp": fred["fred_gdpc1"].get(year),
                "population_thousands": fred["fred_pop"].get(year),
                "unemployment_rate_percent": fred["fred_unrate"].get(year),
                "cpi_energy": fred["fred_cpiengsl"].get(year),
                "cpi_u": fred["fred_cpiaucsl"].get(year),
                "gdp_deflator": fred["fred_gdpdef"].get(year),
                "tbill_3m_percent": fred["fred_tb3ms"].get(year),
                "productivity_output_per_hour": fred["fred_ophnfb"].get(year),
                "real_hourly_compensation": fred["fred_comprnfb"].get(year),
                "employees_thousands": fred["fred_payems"].get(year),
                "domestic_nonfinancial_debt_usd_billions": fred["fred_cmdebt"].get(year),
                "primary_energy_quadrillion_btu": energy["primary_energy_quadrillion_btu"].get(year),
                "ip_product_quantity_index_2017_100": bea["ip_product_quantity_index_2017_100"].get(year),
                "private_tangible_fixed_assets_quantity_index_2017_100": bea["private_tangible_fixed_assets_quantity_index_2017_100"].get(year),
                "government_fixed_assets_quantity_index_2017_100": bea["government_fixed_assets_quantity_index_2017_100"].get(year),
            }
            absent = [name for name, value in values.items() if value is None or value <= 0]
            if absent:
                for name in absent:
                    missing_years.setdefault(name, []).append(year)
                continue
            rows.append({"year": year, **values})
    if missing_years:
        blockers.append("The required common annual coverage is incomplete; missing values were not imputed.")

    if blockers:
        status = {
            "schema_version": "1.0",
            "topic": "0.25_Strategy_Power_Economics",
            "status": "WARN",
            "generated_at_utc": utc_now(),
            "panel_path": relative(PANEL_PATH),
            "controller_reason": "Source-lock and complete annual coverage are required before a UET historical panel can exist.",
            "blockers": sorted(set(blockers)),
            "missing_years": missing_years,
            "claim_boundary": "No model result was generated; absent values were not inferred or imputed.",
        }
        write_json(PANEL_STATUS, status)
        print("UET 0.25 economics panel: WARN")
        for blocker in status["blockers"]:
            print(f"  blocker: {blocker}")
        return 0

    by_year = {int(row["year"]): row for row in rows}
    base = by_year[START_YEAR]
    for row in rows:
        row["real_gdp_per_capita"] = float(row["real_gdp"]) / float(row["population_thousands"])
        row["primary_energy_per_capita"] = float(row["primary_energy_quadrillion_btu"]) / float(row["population_thousands"])
        row["knowledge_per_employee"] = float(row["ip_product_quantity_index_2017_100"]) / float(row["employees_thousands"])
        private_tangible = float(row["private_tangible_fixed_assets_quantity_index_2017_100"]) / float(row["employees_thousands"])
        government_assets = float(row["government_fixed_assets_quantity_index_2017_100"]) / float(row["employees_thousands"])
        row["infrastructure_per_employee"] = math.sqrt(private_tangible * government_assets)
    base_gdp_pc = float(base["real_gdp"]) / float(base["population_thousands"])
    base_energy_pc = float(base["primary_energy_quadrillion_btu"]) / float(base["population_thousands"])
    base_productivity = float(base["productivity_output_per_hour"])
    for row in rows:
        gdp_component = rebased_index(float(row["real_gdp_per_capita"]), base_gdp_pc)
        productivity_component = rebased_index(float(row["productivity_output_per_hour"]), base_productivity)
        energy_component = rebased_index(float(row["primary_energy_per_capita"]), base_energy_pc)
        row["resource_capacity_index"] = (gdp_component * productivity_component * energy_component) ** (1.0 / 3.0)
        row["resource_capacity_log"] = math.log(float(row["resource_capacity_index"]))
    previous: dict[str, object] | None = None
    for row in rows:
        if previous is None:
            for column in ["m2_log_growth", "resource_log_growth", "real_gdp_per_capita_log_growth", "knowledge_log_growth", "infrastructure_log_growth", "cpi_inflation_log", "cpi_energy_inflation_log", "gdp_deflator_inflation_log", "monetary_resource_mismatch"]:
                row[column] = None
        else:
            row["m2_log_growth"] = log_change(float(row["m2_usd_billions"]), float(previous["m2_usd_billions"]))
            row["resource_log_growth"] = log_change(float(row["resource_capacity_index"]), float(previous["resource_capacity_index"]))
            row["real_gdp_per_capita_log_growth"] = log_change(float(row["real_gdp_per_capita"]), float(previous["real_gdp_per_capita"]))
            row["knowledge_log_growth"] = log_change(float(row["knowledge_per_employee"]), float(previous["knowledge_per_employee"]))
            row["infrastructure_log_growth"] = log_change(float(row["infrastructure_per_employee"]), float(previous["infrastructure_per_employee"]))
            row["cpi_inflation_log"] = log_change(float(row["cpi_u"]), float(previous["cpi_u"]))
            row["cpi_energy_inflation_log"] = log_change(float(row["cpi_energy"]), float(previous["cpi_energy"]))
            row["gdp_deflator_inflation_log"] = log_change(float(row["gdp_deflator"]), float(previous["gdp_deflator"]))
            row["monetary_resource_mismatch"] = float(row["m2_log_growth"]) - float(row["resource_log_growth"])
        previous = row
    fields = list(rows[0].keys())
    write_csv(PANEL_PATH, rows, fields)
    input_paths = [verified_source_path(manifest, source_id, []) for source_id in list(fred_methods) + ["bea_fixed_assets", "eia_primary_energy"]]
    status = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PASS",
        "generated_at_utc": utc_now(),
        "panel_path": relative(PANEL_PATH),
        "panel_sha256": sha256(PANEL_PATH),
        "coverage": {"start_year": START_YEAR, "end_year": END_YEAR, "rows": len(rows)},
        "input_hashes": [{"path": relative(path), "sha256": sha256(path)} for path in input_paths if path is not None],
        "formula_boundary": "R/N/K/I are dimensionless proxy constructs after the stated transformations; they are not a dimensional identity.",
        "claim_boundary": "The normalized panel enables internal descriptive diagnostics only.",
    }
    write_json(PANEL_STATUS, status)
    print("UET 0.25 economics panel: PASS")
    print(f"  rows: {len(rows)}, coverage: {START_YEAR}-{END_YEAR}")
    print(f"  panel: {PANEL_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
