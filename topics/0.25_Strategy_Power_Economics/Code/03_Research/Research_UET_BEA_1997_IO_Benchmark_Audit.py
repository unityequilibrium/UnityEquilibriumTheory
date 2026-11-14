"""Validate the archived BEA 1997 benchmark input-output structures.

This is a source-locked, one-year benchmark lane.  It checks that the public
BEA archives contain the stated make/use, direct-requirements, and total-
requirements tables and that their codes, table references, units, and values
are internally well formed.  It deliberately does not turn a benchmark into a
time series or identify a payer, a project, or a causal resource transformation.
"""

from __future__ import annotations

import csv
import io
import json
import math
import zipfile
from pathlib import Path

from economic_hardening_common import ARTIFACT_DIR, ROOT, sha256, utc_now, write_json


ARTIFACT = ARTIFACT_DIR / "0_25_bea_1997_io_benchmark_audit.json"
BENCHMARK_ROOT = ROOT / "docs" / "data" / "external" / "economics" / "us_historical" / "bea_io" / "1997-benchmark"
MANIFEST = BENCHMARK_ROOT / "source_manifest.json"

ARCHIVES = {
    "make_use": {
        "path": BENCHMARK_ROOT / "ndn0307.zip",
        "url": "https://apps.bea.gov/industry/zip/ndn0307.zip",
        "members": {"IOMakeDetail.txt", "IOUseDetail.txt", "IO-CodeDetail.txt", "ReadMe.txt"},
        "units": "make/use values are millions of dollars at producers' prices",
    },
    "direct_requirements": {
        "path": BENCHMARK_ROOT / "ndn0307.zip",
        "url": "https://apps.bea.gov/industry/zip/ndn0307.zip",
        "members": {"IODirectRequireDetail.txt", "IO-CodeDetail.txt", "ReadMe.txt"},
        "units": "direct requirements are coefficients per dollar of industry output",
    },
    "total_requirements": {
        "path": BENCHMARK_ROOT / "ndn0310.zip",
        "url": "https://apps.bea.gov/industry/zip/ndn0310.zip",
        "members": {"IndbyIndTRDetail.txt", "IO-CodeDetail.txt", "ReadMe.txt"},
        "units": "industry-by-industry total requirements are coefficients",
    },
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read_csv(archive: zipfile.ZipFile, member: str) -> list[list[str]]:
    raw = archive.read(member).decode("latin-1", errors="strict")
    return list(csv.reader(io.StringIO(raw)))


def _float(value: str) -> float | None:
    try:
        number = float(value.strip())
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _code_rows(rows: list[list[str]]) -> dict[str, str]:
    codes: dict[str, str] = {}
    for row in rows:
        if len(row) < 2:
            continue
        code, label = row[0].strip(), row[1].strip()
        if code and label:
            codes[code] = label
    return codes


def _matrix_check(rows: list[list[str]], codes: set[str], *, table_ref: str, value_col: int,
                  table_ref_col: int = 2,
                  year_col: int | None = None, expected_year: int | None = None,
                  nonnegative: bool = True) -> dict:
    data_rows = 0
    parse_failures: list[dict[str, object]] = []
    unknown_codes = 0
    nonnegative_failures = 0
    years: set[int] = set()
    row_codes: set[str] = set()
    col_codes: set[str] = set()
    positive_values = 0
    finite_values = 0
    values: list[float] = []
    for line_number, row in enumerate(rows, start=1):
        if not row or not any(cell.strip() for cell in row):
            continue
        data_rows += 1
        if len(row) <= value_col or len(row) < 3:
            parse_failures.append({"line": line_number, "reason": "short_row", "row": row[:6]})
            continue
        left, right = row[0].strip(), row[1].strip()
        row_codes.add(left)
        col_codes.add(right)
        if left not in codes or right not in codes:
            unknown_codes += 1
        if len(row) <= table_ref_col or row[table_ref_col].strip() != table_ref:
            parse_failures.append({"line": line_number, "reason": "table_reference", "observed": row[table_ref_col].strip() if len(row) > table_ref_col else None, "expected": table_ref})
        if year_col is not None:
            try:
                year = int(row[year_col].strip())
                years.add(year)
                if expected_year is not None and year != expected_year:
                    parse_failures.append({"line": line_number, "reason": "year", "observed": year, "expected": expected_year})
            except (ValueError, TypeError):
                parse_failures.append({"line": line_number, "reason": "year_parse", "observed": row[year_col] if len(row) > year_col else None})
        value = _float(row[value_col])
        if value is None:
            parse_failures.append({"line": line_number, "reason": "nonfinite_value", "observed": row[value_col]})
            continue
        finite_values += 1
        values.append(value)
        if value > 0:
            positive_values += 1
        if nonnegative and value < 0:
            nonnegative_failures += 1
    return {
        "rows": data_rows,
        "row_code_count": len(row_codes),
        "column_code_count": len(col_codes),
        "known_code_count": len(codes),
        "unknown_code_rows": unknown_codes,
        "finite_value_rows": finite_values,
        "positive_value_rows": positive_values,
        "nonnegative_failures": nonnegative_failures,
        "years": sorted(years),
        "value_min": min(values) if values else None,
        "value_max": max(values) if values else None,
        "parse_failure_count": len(parse_failures),
        "parse_failure_examples": parse_failures[:5],
    }



def _manifest_check() -> dict:
    result = {"path": _relative(MANIFEST) if MANIFEST.exists() else None, "exists": MANIFEST.is_file(), "records": [], "status": "MISSING"}
    if not MANIFEST.is_file():
        return result
    try:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        records = payload.get("sources", [])
        for record in records:
            local = ROOT / record.get("local_path", "")
            observed = sha256(local) if local.is_file() else None
            result["records"].append({
                "source_id": record.get("source_id"),
                "path": _relative(local) if local.is_file() else record.get("local_path"),
                "expected_sha256": record.get("sha256"),
                "observed_sha256": observed,
                "hash_matches": bool(observed and observed == record.get("sha256")),
            })
        complete = bool(records) and all(item["hash_matches"] for item in result["records"]) and payload.get("not_time_series") is True
        result["status"] = "PASS_WITH_BOUNDARY" if complete else "WARN"
    except (OSError, json.JSONDecodeError, TypeError):
        result["status"] = "WARN"
    return result

def _archive_check(spec: dict) -> dict:
    path = spec["path"]
    result: dict[str, object] = {
        "path": _relative(path) if path.exists() else None,
        "url": spec["url"],
        "exists": path.is_file(),
        "sha256": sha256(path) if path.is_file() else None,
        "required_members": sorted(spec["members"]),
        "missing_members": [],
        "member_checks": {},
        "units": spec["units"],
    }
    if not path.is_file():
        result["status"] = "MISSING"
        return result
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            result["missing_members"] = sorted(spec["members"] - names)
            result["member_count"] = len(names)
            if not result["missing_members"]:
                code_rows = _read_csv(archive, "IO-CodeDetail.txt")
                codes = _code_rows(code_rows)
                result["code_dictionary"] = {"rows": len(code_rows), "codes": len(codes), "sample": dict(list(codes.items())[:3])}
                if "IOMakeDetail.txt" in names:
                    result["member_checks"]["IOMakeDetail.txt"] = _matrix_check(_read_csv(archive, "IOMakeDetail.txt"), set(codes), table_ref="3", value_col=3)
                if "IOUseDetail.txt" in names:
                    result["member_checks"]["IOUseDetail.txt"] = _matrix_check(_read_csv(archive, "IOUseDetail.txt"), set(codes), table_ref="4", table_ref_col=3, value_col=4, year_col=2, expected_year=1997, nonnegative=False)
                if "IODirectRequireDetail.txt" in names:
                    result["member_checks"]["IODirectRequireDetail.txt"] = _matrix_check(_read_csv(archive, "IODirectRequireDetail.txt"), set(codes), table_ref="5", value_col=3, nonnegative=False)
                if "IndbyIndTRDetail.txt" in names:
                    result["member_checks"]["IndbyIndTRDetail.txt"] = _matrix_check(_read_csv(archive, "IndbyIndTRDetail.txt"), set(codes), table_ref="8", value_col=3, nonnegative=True)
            checks = list(result["member_checks"].values())
            structurally_clean = bool(not result["missing_members"] and checks and all(
                item["parse_failure_count"] == 0 and item["unknown_code_rows"] == 0 and item["nonnegative_failures"] == 0
                for item in checks
            ))
            result["status"] = "PASS_WITH_BOUNDARY" if structurally_clean else "WARN"
    except (OSError, zipfile.BadZipFile, KeyError, UnicodeError) as exc:
        result["status"] = "WARN"
        result["error"] = str(exc)
    return result


def main() -> int:
    manifest = _manifest_check()
    archives = {name: _archive_check(spec) for name, spec in ARCHIVES.items()}
    blocking = [name for name, item in archives.items() if item.get("status") in {"MISSING", "WARN"}]
    if manifest.get("status") not in {"PASS_WITH_BOUNDARY", "PASS"}:
        blocking.append("source_manifest")
    payload = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "formula_id": "EC25-PAYER-RESOURCE-JOIN",
        "status": "WARN" if blocking else "PASS_WITH_BOUNDARY",
        "controller_status": "BEA_1997_BENCHMARK_ONLY",
        "generated_at_utc": utc_now(),
        "source": {
            "provider": "U.S. Bureau of Economic Analysis (BEA)",
            "official_page": "https://www.bea.gov/industry/historical-benchmark-input-output-tables",
            "benchmark_year": 1997,
            "coverage": "NAICS benchmark make/use, direct requirements, and industry-by-industry total requirements",
            "not_time_series": True,
            "retrieval_vintage": "2026-07-16",
            "source_manifest": manifest,
            "archives": archives,
        },
        "validation": {
            "no_imputation": True,
            "code_dictionary_crosswalk_checked": True,
            "table_reference_and_unit_checks": True,
            "interpretation": "The tables establish a reproducible 1997 industry/commodity flow structure. They do not identify who paid, whether funding was profit or debt, labor hours by payment, or physical extraction quantities.",
        },
        "blocking_components": blocking,
        "claim_boundary": "Benchmark-descriptive only. Do not infer annual flow dynamics, payer provenance, resource causality, innovation causality, or fiat-money causality from this artifact.",
        "limitations": [
            "BEA explicitly cautions that benchmark input-output tables are not suitable as a time series.",
            "Make/use dollar cells are producers-prices millions of dollars; requirements tables are dimensionless coefficients.",
            "Aggregate sectoral funding remains separate from industry purchases and cannot be joined to a specific payer or project.",
        ],
    }
    write_json(ARTIFACT, payload)
    print("BEA 1997 benchmark audit:", payload["status"], "blocking archives", len(blocking))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
