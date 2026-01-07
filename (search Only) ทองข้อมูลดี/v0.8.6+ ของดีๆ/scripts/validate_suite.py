#!/usr/bin/env python
from __future__ import annotations

import argparse, json
from pathlib import Path
import pandas as pd

from uet_core.validation import (
    validate_artifacts,
    validate_additivity,
    validate_monotone,
    validate_dt_backtracks,
    validate_plateau,
    validate_conflict,
    validate_lambda_sweep,
    overall_grade,
)

def find_run_dirs(root: Path) -> list[Path]:
    # Any directory that contains config.json + timeseries.csv + summary.json is considered a run dir.
    run_dirs = []
    for p in root.rglob("config.json"):
        d = p.parent
        if (d/"timeseries.csv").exists() and (d/"summary.json").exists():
            run_dirs.append(d)
    # unique + stable order
    uniq = sorted({str(d): d for d in run_dirs}.values(), key=lambda x: str(x))
    return uniq

def main():
    ap = argparse.ArgumentParser(description="Validate one or many UET harness run folders (F0-F3 gates).")
    ap.add_argument("--runs", required=True, help="Path to a run dir, or a folder containing many run dirs.")
    ap.add_argument("--out_csv", default="", help="Optional: write a CSV report to this path.")
    ap.add_argument("--json", action="store_true", help="Also write a JSON report next to out_csv (or stdout if no out_csv).")
    args = ap.parse_args()

    root = Path(args.runs)

    # Optional: validate a lambda sweep table (F3) if present
    sweep_csv = None
    if root.is_file() and root.suffix.lower() == ".csv":
        sweep_csv = root
    elif root.is_dir() and (root/"lambda_sweep.csv").exists():
        sweep_csv = root/"lambda_sweep.csv"
    sweep_rows = []
    if sweep_csv is not None and sweep_csv.exists():
        issues = validate_lambda_sweep(sweep_csv)
        grade = overall_grade(issues)
        reasons = "; ".join([f"{i.level}:{i.code}" for i in issues if i.level in ("FAIL","WARN")]) or "OK"
        sweep_rows.append({
            "run_dir": str(sweep_csv),
            "grade": grade,
            "reasons": reasons,
            "n_fail": sum(1 for i in issues if i.level=="FAIL"),
            "n_warn": sum(1 for i in issues if i.level=="WARN"),
        })
        print(f"[{grade}] {sweep_csv}")
        for i in issues:
            if i.level in ("FAIL","WARN"):
                print(f"  - {i.level} {i.code}: {i.message}")
        print()
    run_dirs = []
    if root.is_dir():
        run_dirs = [root] if (root/"config.json").exists() else find_run_dirs(root)

    if not run_dirs and not sweep_rows:
        raise SystemExit(f"No run folders found under: {root}")

    rows = []
    for rd in run_dirs:
        cfg, df, summ, issues = validate_artifacts(rd)
        if cfg is not None and df is not None and summ is not None:
            issues += validate_additivity(df)
            issues += validate_monotone(df, cfg)
            issues += validate_dt_backtracks(summ, cfg)
            issues += validate_plateau(df)
            issues += validate_conflict(summ, df)

        grade = overall_grade(issues)
        # compact reason string
        reasons = "; ".join([f"{i.level}:{i.code}" for i in issues if i.level in ("FAIL","WARN")]) or "OK"
        rows.append({
            "run_dir": str(rd),
            "grade": grade,
            "reasons": reasons,
            "n_fail": sum(1 for i in issues if i.level=="FAIL"),
            "n_warn": sum(1 for i in issues if i.level=="WARN"),
        })

        print(f"[{grade}] {rd}")
        for i in issues:
            if i.level in ("FAIL","WARN"):
                print(f"  - {i.level} {i.code}: {i.message}")

    rows = sweep_rows + rows
    df_out = pd.DataFrame(rows)
    if args.out_csv:
        outp = Path(args.out_csv)
        outp.parent.mkdir(parents=True, exist_ok=True)
        df_out.to_csv(outp, index=False)
        if args.json:
            outp.with_suffix(".json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    else:
        print("\n=== Summary ===")
        print(df_out.to_string(index=False))

if __name__ == "__main__":
    main()