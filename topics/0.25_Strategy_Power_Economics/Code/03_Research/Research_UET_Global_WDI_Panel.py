"""Build the strict complete-case WDI panel and invalidate legacy global results on failure."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from economic_hardening_common import ROOT, TOPIC, load_json, relative, sha256, utc_now, write_json

RAW = ROOT / "docs/data/external/economics/global/wdi/2026-07-16"
OUT = TOPIC / "Data/03_Research/uet_global_wdi_panel.csv"
ART = TOPIC / "Result/artifacts/0_25_global_wdi_panel.json"
INTEGRITY = TOPIC / "Result/artifacts/0_25_global_panel_integrity_gate.json"
REQUIRED = {
    "NY.GDP.PCAP.KD": "real_gdp_per_capita_usd_2015",
    "NY.GDP.PCAP.PP.KD": "real_gdp_per_capita_ppp_constant_2021_intl_dollar",
    "SP.POP.TOTL": "population",
    "EG.USE.PCAP.KG.OE": "energy_use_kg_oil_equivalent_per_capita",
}
DOWNSTREAM = [
    "0_25_global_wdi_leave_one_out.json",
    "0_25_global_wdi_leave_one_region_out.json",
    "0_25_global_wdi_ppp_comparison.json",
    "0_25_global_wdi_strata_audit.json",
    "0_25_global_wdi_income_classification.json",
    "0_25_global_imf_wdi_normalization.json",
]


def maximum_consecutive_years(years: set[int]) -> int:
    longest = current = 0
    previous = None
    for year in sorted(years):
        current = current + 1 if previous is not None and year == previous + 1 else 1
        longest = max(longest, current)
        previous = year
    return longest


def country_metadata() -> tuple[set[str], dict[str, dict]]:
    path = RAW / "country_metadata.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    metadata = {row.get("id"): row for row in rows if row.get("id")}
    countries = {
        code
        for code, row in metadata.items()
        if row.get("region", {}).get("value") not in {None, "", "Aggregates"}
        and row.get("incomeLevel", {}).get("id") not in {None, "", "NA"}
    }
    return countries, metadata


def invalidate_downstream(reason: str) -> list[dict]:
    records = []
    for name in DOWNSTREAM:
        path = ART.parent / name
        previous = load_json(path)
        previous_hash = sha256(path) if path.exists() else None
        payload = {
            "schema_version": "2.0",
            "topic": "0.25_Strategy_Power_Economics",
            "status": "INVALID_SUPERSEDED",
            "generated_at_utc": utc_now(),
            "superseded_by": relative(INTEGRITY),
            "reason": reason,
            "previous_artifact": {
                "path": relative(path),
                "sha256": previous_hash,
                "status": previous.get("status") if previous else None,
                "rows": previous.get("rows") if previous else None,
            },
            "claim_boundary": "No global replication result may be exported from this superseded artifact.",
        }
        write_json(path, payload)
        records.append({"path": relative(path), "previous_sha256": previous_hash})
    return records


def main() -> int:
    valid_countries, metadata = country_metadata()
    source_manifest_path = RAW / "source_manifest.json"
    source_manifest = load_json(source_manifest_path)
    expected_hashes = {row["indicator"]: row.get("sha256") for row in source_manifest.get("records", [])}
    observations: dict[tuple[str, int], dict[str, float]] = {}
    non_null_counts = {indicator: 0 for indicator in REQUIRED}
    raw_checks = []
    for indicator, column in REQUIRED.items():
        path = RAW / f"{indicator}.json"
        actual_hash = sha256(path) if path.exists() else None
        raw_checks.append({"indicator": indicator, "path": relative(path), "sha256": actual_hash, "manifest_sha256": expected_hashes.get(indicator), "hash_matches": actual_hash == expected_hashes.get(indicator)})
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for record in records:
            code = record.get("country", {}).get("id")
            year = record.get("date")
            value = record.get("value")
            if code not in valid_countries or year is None or value is None:
                continue
            try:
                observations.setdefault((code, int(year)), {})[column] = float(value)
                non_null_counts[indicator] += 1
            except (TypeError, ValueError):
                continue
    required_columns = list(REQUIRED.values())
    rows = [
        {"country_code": code, "year": year, **values}
        for (code, year), values in sorted(observations.items())
        if all(column in values for column in required_columns)
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["country_code", "year", *required_columns])
        writer.writeheader()
        writer.writerows(rows)
    coverage: dict[str, set[int]] = {}
    for row in rows:
        coverage.setdefault(str(row["country_code"]), set()).add(int(row["year"]))
    consecutive = {code: maximum_consecutive_years(years) for code, years in coverage.items()}
    countries_20 = sum(value >= 20 for value in consecutive.values())
    complete_hashes = all(row["hash_matches"] for row in raw_checks)
    passed = bool(rows) and countries_20 >= 30 and complete_hashes
    reason = "GLOBAL_COMPLETE_CASE_PANEL_UNAVAILABLE" if not rows else "GLOBAL_COMMON_COVERAGE_BELOW_THRESHOLD"
    previous_hash = sha256(ART) if ART.exists() else None
    artifact = {
        "schema_version": "2.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PASS" if passed else "BLOCKED",
        "evidence_status": "CURRENT" if passed else "INVALID_SUPERSEDED",
        "generated_at_utc": utc_now(),
        "controller": None if passed else reason,
        "required_indicators": REQUIRED,
        "raw_non_null_counts": non_null_counts,
        "complete_case_rows": len(rows),
        "countries_in_complete_case_panel": len(coverage),
        "countries_with_20_plus_consecutive_common_years": countries_20,
        "consecutive_common_years_by_country": consecutive,
        "excluded_world_bank_aggregates": len(metadata) - len(valid_countries),
        "panel_path": relative(OUT),
        "panel_sha256": sha256(OUT),
        "source_manifest": {"path": relative(source_manifest_path), "sha256": sha256(source_manifest_path)},
        "raw_hash_checks": raw_checks,
        "previous_artifact_sha256": previous_hash,
        "missingness_policy": "Every required indicator must be non-null in an analysis row; no imputation.",
        "blockers": [] if passed else [reason, "Energy-use coverage does not overlap the other required indicators sufficiently in this frozen WDI vintage."],
        "claim_boundary": "A panel PASS is source/panel readiness only, not global replication or measurement invariance.",
    }
    write_json(ART, artifact)
    invalidated = [] if passed else invalidate_downstream(reason)
    integrity = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "PASS" if passed else "BLOCKED",
        "generated_at_utc": utc_now(),
        "controller": None if passed else reason,
        "panel_artifact": {"path": relative(ART), "sha256": sha256(ART)},
        "required_complete_case_columns": required_columns,
        "complete_case_rows": len(rows),
        "minimum_economies": 30,
        "minimum_consecutive_common_years": 20,
        "invalidated_downstream_artifacts": invalidated,
        "claim_effect": "Current global evidence is blocked and cannot contribute to Evidence Grade A." if not passed else "Panel readiness only; downstream replication gates still apply.",
    }
    write_json(INTEGRITY, integrity)
    print(f"Global WDI complete-case panel: {artifact['status']} rows={len(rows)} countries20={countries_20}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
