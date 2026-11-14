"""Audit cost-of-living and household-welfare indicators without GDP substitution."""

from __future__ import annotations

import math

from economic_hardening_common import ARTIFACT_DIR, RAW_ROOT, ROOT, annualise_fred, load_json, relative, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_uet_welfare_audit.json"
MANIFEST = RAW_ROOT.parent.parent / "welfare" / "uet_us_welfare_source_manifest.json"


def source_path(manifest: dict, source_id: str):
    for item in manifest.get("sources", []):
        if item.get("source_id") == source_id and item.get("exists") and item.get("local_path"):
            path = ROOT / item["local_path"]
            if path.exists():
                return path
    return None


def log_change(current: float, previous: float) -> float | None:
    if current <= 0 or previous <= 0:
        return None
    return math.log(current / previous)


def z(value: float, values: list[float]) -> float:
    center = sum(values) / len(values)
    deviation = math.sqrt(sum((item - center) ** 2 for item in values) / max(1, len(values) - 1))
    return 0.0 if deviation == 0 else (value - center) / deviation


def main() -> int:
    manifest = load_json(MANIFEST)
    series = {}
    missing = []
    for source_id, method in {
        "fred_rent_primary": "mean",
        "fred_oer": "mean",
        "fred_real_median_income": "mean",
        "fred_house_price": "mean",
    }.items():
        path = source_path(manifest, source_id)
        if path is None:
            missing.append(source_id)
            continue
        series[source_id] = annualise_fred(path, method=method)
    years = sorted(set.intersection(*(set(values) for values in series.values()))) if series else []
    years = [year for year in years if 1984 <= year <= 2024]
    observations = []
    for year in years:
        previous = year - 1
        if not all(previous in values for values in series.values()):
            continue
        rent_growth = log_change(series["fred_rent_primary"][year], series["fred_rent_primary"][previous])
        oer_growth = log_change(series["fred_oer"][year], series["fred_oer"][previous])
        income_growth = log_change(series["fred_real_median_income"][year], series["fred_real_median_income"][previous])
        house_growth = log_change(series["fred_house_price"][year], series["fred_house_price"][previous])
        if None in {rent_growth, oer_growth, income_growth, house_growth}:
            continue
        observations.append({"year": year, "rent_inflation": rent_growth, "oer_inflation": oer_growth, "real_median_income_growth": income_growth, "house_price_growth": house_growth})
    status = "PASS" if not missing and len(observations) >= 30 else "WARN"
    if observations:
        rent_values = [row["rent_inflation"] for row in observations]
        oer_values = [row["oer_inflation"] for row in observations]
        income_values = [row["real_median_income_growth"] for row in observations]
        for row in observations:
            row["housing_cost_pressure_index"] = (z(row["rent_inflation"], rent_values) + z(row["oer_inflation"], oer_values) - z(row["real_median_income_growth"], income_values)) / 3.0
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "generated_at_utc": utc_now(),
        "source_manifest": {"path": relative(MANIFEST), "retrieval_vintage": manifest.get("retrieval_vintage"), "sources": manifest.get("sources", [])},
        "coverage": {"requested": [1984, 2024], "actual": [observations[0]["year"], observations[-1]["year"]] if observations else None, "rows": len(observations)},
        "outcomes": ["rent_inflation", "oer_inflation", "real_median_income_growth", "house_price_growth", "housing_cost_pressure_index"],
        "observations": observations,
        "missing_sources": missing,
        "unit_policy": "Rent/OER/house prices are source indexes; real median income is provider real 2024-dollar annual income. The pressure index is dimensionless after explicit standardization.",
        "no_imputation": True,
        "claim_boundary": "This is a descriptive household-welfare and cost-of-living lane separate from GDP. It does not establish policy success, fiat causality, or household welfare causality.",
    }
    write_json(ARTIFACT, artifact)
    print(f"UET welfare audit: {status} ({len(observations)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
