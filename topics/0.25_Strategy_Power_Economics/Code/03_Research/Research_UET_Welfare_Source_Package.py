"""Archive optional U.S. cost-of-living and household-welfare source files."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime

from economic_hardening_common import RAW_ROOT, download, relative, runtime_environment, sha256, utc_now, write_json, source_file_metadata


VINTAGE_DEFAULT = "2026-07-12"
MANIFEST = RAW_ROOT.parent.parent / "welfare" / "uet_us_welfare_source_manifest.json"

SERIES = {
    "fred_rent_primary": ("CUSR0000SEHA", "CPI rent of primary residence; index; monthly", "rent cost-of-living input"),
    "fred_oer": ("CUSR0000SEHC", "CPI owners' equivalent rent of residences; index; monthly", "housing cost input"),
    "fred_real_median_income": ("MEHOINUSA672N", "real median household income in 2024 dollars; annual", "real household welfare outcome"),
    "fred_house_price": ("USSTHPI", "FHFA all-transactions house price index; quarterly", "housing asset/burden robustness input"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Download the declared public FRED/FHFA series.")
    parser.add_argument("--vintage", default=VINTAGE_DEFAULT)
    args = parser.parse_args()
    records = []
    failures = []
    for source_id, (series_id, unit_system, role) in SERIES.items():
        path = RAW_ROOT / "fred" / args.vintage / f"{series_id}.csv"
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        if args.refresh:
            ok, reason = download(url, path)
            if not ok:
                failures.append(f"{series_id}: {reason}")
        record = {
            "source_id": source_id,
            "series_id": series_id,
            "source": "Federal Reserve Economic Data (FRED); FHFA series where identified by upstream provider",
            "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
            "download_url": url,
            "local_path": relative(path),
            "exists": path.exists(),
            "retrieval_vintage": args.vintage,
            "retrieval_timestamp_utc": utc_now() if path.exists() else None,
            "license_or_terms": "FRED terms and upstream agency terms apply; preserve attribution.",
            "unit_system": unit_system,
            "benchmark_role": role,
            "required_for_primary_macro_panel": False,
            "source_status": "READY_FOR_REVIEW" if path.exists() else "OPTIONAL_EXPORT_PENDING",
        }
        if path.exists():
            record.update(source_file_metadata(path))
        records.append(record)
    manifest = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "manifest_id": "EC25-WELFARE-SOURCE-V1",
        "generated_at_utc": utc_now(),
        "retrieval_vintage": args.vintage,
        "sources": records,
        "download_failures": failures,
        "coverage_policy": "Freeze observations through 2024; do not mix later revisions into the primary 1959-2024 panel.",
        "claim_boundary": "Source packaging supports household-welfare diagnostics only; it does not establish policy or causal effects.",
        "environment": runtime_environment(),
    }
    write_json(MANIFEST, manifest)
    print(f"UET welfare source package: {'PASS' if all(item['exists'] for item in records) else 'WARN'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
