#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_bias.py

Bias validator for UET runs.

2 โหมด:
1) --input_csv bias_summary.csv
2) --runs_dir <runs_folder> : scan หา */timeseries.csv แล้วดึง "แถวสุดท้าย"

ให้เกรด:
- SYM     : |bias_CI| <= bias_eps
- BIAS_C  : bias_CI >  bias_eps
- BIAS_I  : bias_CI < -bias_eps
- FAIL    : ไม่มี timeseries หรือไม่มี bias

เขียนออก:
- out_csv (default: validation_bias.csv)
- out_json (optional) หรือใช้ --json ให้มันเขียน <out_csv>.json
- (optional) group summary: --group_by "s_tilt,beta" -> <out_csv>_bygroup.csv
"""

from __future__ import annotations
import argparse, json, math, os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


@dataclass
class Thresholds:
    bias_eps: float = 1e-3
    accept_only: bool = False


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, str) and x.strip() == "":
            return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def _load_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _iter_timeseries_files(runs_dir: Path) -> Iterable[Path]:
    for root, _dirs, files in os.walk(runs_dir):
        if "timeseries.csv" in files:
            yield Path(root) / "timeseries.csv"


def _extract_last_row(ts_path: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    try:
        df = pd.read_csv(ts_path)
    except Exception:
        return None, ["NO_TIMESERIES_READ"]
    if df.shape[0] == 0:
        return None, ["EMPTY_TIMESERIES"]

    last = df.iloc[-1].to_dict()

    mean_c = _safe_float(last.get("mean_C"))
    mean_i = _safe_float(last.get("mean_I"))
    bias = _safe_float(last.get("bias_CI"))

    if bias is None and mean_c is not None and mean_i is not None:
        bias = mean_c - mean_i
        last["bias_CI"] = bias

    last["__mean_C"] = mean_c
    last["__mean_I"] = mean_i
    last["__bias_CI"] = bias

    reasons = []
    if mean_c is None: reasons.append("NO_MEAN_C")
    if mean_i is None: reasons.append("NO_MEAN_I")
    if bias is None:   reasons.append("NO_BIAS_CI")
    return last, reasons


def _grade(row: Dict[str, Any], th: Thresholds) -> Tuple[str, List[str]]:
    if th.accept_only:
        acc = _safe_float(row.get("accepted"))
        if acc is None or int(acc) != 1:
            return "FAIL", ["NOT_ACCEPTED"]

    bias = _safe_float(row.get("__bias_CI"))
    if bias is None:
        return "FAIL", ["NO_BIAS_CI"]

    if abs(bias) <= th.bias_eps:
        return "SYM", ["OK"]
    if bias > th.bias_eps:
        return "BIAS_C", ["OK"]
    return "BIAS_I", ["OK"]


def _validate_df(df: pd.DataFrame, th: Thresholds) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.copy()

    # normalize column names (optional)
    ren = {}
    for c in df.columns:
        lc = c.lower()
        if lc == "meanc": ren[c] = "mean_C"
        if lc == "meani": ren[c] = "mean_I"
        if lc == "bias":  ren[c] = "bias_CI"
    if ren:
        df = df.rename(columns=ren)

    df["__mean_C"] = df["mean_C"].apply(_safe_float) if "mean_C" in df.columns else None
    df["__mean_I"] = df["mean_I"].apply(_safe_float) if "mean_I" in df.columns else None
    if "bias_CI" in df.columns:
        df["__bias_CI"] = df["bias_CI"].apply(_safe_float)
    else:
        df["__bias_CI"] = (df["__mean_C"] - df["__mean_I"]).apply(_safe_float)

    out_rows = []
    issues = []

    for i, r in df.iterrows():
        row = r.to_dict()
        miss = []
        if row.get("__mean_C") is None: miss.append("NO_MEAN_C")
        if row.get("__mean_I") is None: miss.append("NO_MEAN_I")
        if row.get("__bias_CI") is None: miss.append("NO_BIAS_CI")

        g, gr = _grade(row, th)
        reasons = (miss if miss else []) + (gr if gr != ["OK"] else ([] if miss else ["OK"]))

        out_rows.append({
            **{k: row.get(k) for k in df.columns if not k.startswith("__")},
            "grade_bias": g,
            "reasons_bias": ",".join(reasons),
            "mean_C": row.get("__mean_C"),
            "mean_I": row.get("__mean_I"),
            "bias_CI": row.get("__bias_CI"),
            "bias_abs": abs(row.get("__bias_CI")) if row.get("__bias_CI") is not None else None,
        })

        if g == "FAIL":
            issues.append({"row_index": int(i), "reasons": reasons})

    out = pd.DataFrame(out_rows)
    summary = {
        "thresholds": asdict(th),
        "grade_counts": out["grade_bias"].value_counts(dropna=False).to_dict(),
        "issues": issues[:50],
    }
    return out, summary


def _scan_runs(runs_dir: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    rows = []
    scan_issues = []
    ts_list = list(_iter_timeseries_files(runs_dir))

    for ts in ts_list:
        run_dir = ts.parent
        last, rs = _extract_last_row(ts)
        if last is None:
            rows.append({"run_dir": str(run_dir), "timeseries": str(ts), "mean_C": None, "mean_I": None, "bias_CI": None})
            scan_issues.append({"run_dir": str(run_dir), "reasons": rs})
            continue

        cfg = _load_json(run_dir / "config.json")
        meta = _load_json(run_dir / "meta.json")
        summ = _load_json(run_dir / "summary.json")
        params = cfg.get("params", {}) if isinstance(cfg.get("params"), dict) else {}

        row = {
            "run_dir": str(run_dir),
            "timeseries": str(ts),
            "t": _safe_float(last.get("t")),
            "Omega": _safe_float(last.get("Omega")),
            "accepted": _safe_float(last.get("accepted")),
            "backtracks": _safe_float(last.get("backtracks")),
            "mean_C": last.get("__mean_C"),
            "mean_I": last.get("__mean_I"),
            "bias_CI": last.get("__bias_CI"),
            "case_id": meta.get("case_id") or summ.get("case_id") or cfg.get("case_id"),
            "model": cfg.get("model") or meta.get("model") or summ.get("model"),
        }
        for k in ["beta", "MC", "MI", "kC", "kI", "s_tilt", "s", "delta", "asym"]:
            if k in params:
                row[k] = params.get(k)

        rows.append(row)

    df = pd.DataFrame(rows)
    scan_summary = {
        "mode": "runs_dir",
        "runs_dir": str(runs_dir),
        "n_timeseries_found": int(len(ts_list)),
        "scan_issues": scan_issues[:50],
    }
    return df, scan_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_csv", default="", help="bias_summary.csv (optional)")
    ap.add_argument("--runs_dir", default="", help="scan runs directory (optional)")
    ap.add_argument("--out_csv", default="validation_bias.csv")
    ap.add_argument("--out_json", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--bias_eps", type=float, default=1e-3)
    ap.add_argument("--accept_only", action="store_true")
    ap.add_argument("--group_by", default="", help='comma cols e.g. "s_tilt,beta"')
    args = ap.parse_args()

    th = Thresholds(bias_eps=float(args.bias_eps), accept_only=bool(args.accept_only))

    if not args.input_csv and not args.runs_dir:
        raise SystemExit("Provide --input_csv or --runs_dir")

    if args.input_csv:
        df = pd.read_csv(args.input_csv)
        scan_summary = {"mode": "input_csv", "input_csv": args.input_csv}
    else:
        df, scan_summary = _scan_runs(Path(args.runs_dir))

    out, summary = _validate_df(df, th)
    summary.update(scan_summary)

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    group_csv = None
    if args.group_by.strip():
        cols = [c.strip() for c in args.group_by.split(",") if c.strip()]
        miss = [c for c in cols if c not in out.columns]
        if miss:
            summary["group_by_error"] = {"missing_columns": miss}
        else:
            g = out.groupby(cols)["grade_bias"].value_counts().unstack(fill_value=0).reset_index()
            group_csv = out_path.with_name(out_path.stem + "_bygroup.csv")
            g.to_csv(group_csv, index=False)
            summary["group_by_csv"] = str(group_csv)

    if args.out_json:
        jpath = Path(args.out_json)
    elif args.json:
        jpath = out_path.with_suffix(".json")
    else:
        jpath = None

    if jpath is not None:
        jpath.parent.mkdir(parents=True, exist_ok=True)
        jpath.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Grades:", out["grade_bias"].value_counts().to_dict())
    print("Wrote:", str(out_path))
    if group_csv is not None:
        print("Wrote:", str(group_csv))
    if jpath is not None:
        print("Wrote:", str(jpath))


if __name__ == "__main__":
    main()
