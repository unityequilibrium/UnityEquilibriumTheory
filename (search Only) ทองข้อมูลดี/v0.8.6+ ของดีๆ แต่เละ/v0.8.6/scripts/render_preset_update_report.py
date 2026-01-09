#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
from typing import List, Dict, Any

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--updates_csv", required=True)
    ap.add_argument("--out_md", default="preset_update_report.md")
    ap.add_argument("--only_changes", action="store_true", help="show only rows where recommended_scale != 1")
    args = ap.parse_args()

    rows=[]
    with Path(args.updates_csv).open("r", encoding="utf-8") as f:
        rdr=csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty updates_csv")

    def fmt(x):
        try:
            v=float(x)
            if math.isnan(v): return "NaN"
            return f"{v:.6g}"
        except Exception:
            return str(x)

    lines=[]
    lines.append("# Preset Update Report (Auto) v0.1\n")
    lines.append("This report is generated from adaptive stress variant summary.\n")
    lines.append("Columns: band, model, integrator, recommended_scale, recommended_dt, gate_pass.\n\n")

    # sort by band then model
    def key(r):
        return (r.get("band",""), r.get("model",""), r.get("integrator",""))
    rows_sorted=sorted(rows, key=key)

    # table header
    lines.append("| band | model | integrator | scale | base_dt | rec_dt | gate_pass | evidence_variant | pass_rate | ci_lo | n | reason |\n")
    lines.append("|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|\n")

    for r in rows_sorted:
        sc = _f(str(r.get("recommended_scale","nan")))
        if args.only_changes and (not math.isnan(sc)) and abs(sc-1.0) < 1e-12:
            continue
        lines.append(
            f"| {r.get('band','')} | {r.get('model','')} | {r.get('integrator','')} | {fmt(r.get('recommended_scale',''))} | "
            f"{fmt(r.get('base_dt_from_presets',''))} | {fmt(r.get('recommended_dt',''))} | "
            f"{r.get('gate_pass_at_recommended_scale','')} | {r.get('evidence_variant','')} | "
            f"{fmt(r.get('evidence_pass_rate',''))} | {fmt(r.get('evidence_ci_lo',''))} | {r.get('evidence_n','')} | {r.get('reason','')} |\n"
        )

    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text("".join(lines), encoding="utf-8")
    print("Wrote", args.out_md)

if __name__ == "__main__":
    main()
