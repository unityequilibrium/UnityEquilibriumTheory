#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary_csv", required=True, help="stress_summary.csv")
    ap.add_argument("--min_pass_rate", type=float, default=0.95)
    ap.add_argument("--min_ci_lo", type=float, default=0.90, help="require Wilson CI lower bound >= this")
    ap.add_argument("--out", default="", help="output report json (default: <summary_parent>/stress_gate_report.json)")
    ap.add_argument("--hint_top_k", type=int, default=10, help="include top failing groups by ci_lo deficit")
    args = ap.parse_args()

    summ = Path(args.summary_csv)
    out = Path(args.out) if args.out else (summ.parent/"stress_gate_report.json")

    with summ.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty summary")

    fails = []
    for r in rows:
        pr = float(r.get("pass_rate","nan"))
        lo = float(r.get("ci_lo","nan"))
        if not (pr >= args.min_pass_rate and lo >= args.min_ci_lo):
            fails.append(r)
    # hints: rank failing groups by how far below thresholds they are
    hints = []
    for r in fails:
        try:
            pr = float(r.get("pass_rate","nan"))
            lo = float(r.get("ci_lo","nan"))
        except Exception:
            pr = float("nan"); lo = float("nan")
        deficit = 0.0
        if not math.isnan(pr):
            deficit += max(0.0, args.min_pass_rate - pr)
        if not math.isnan(lo):
            deficit += 2.0*max(0.0, args.min_ci_lo - lo)
        rr = dict(r)
        rr["deficit_score"] = deficit
        hints.append(rr)
    hints.sort(key=lambda x: x.get("deficit_score", 0.0), reverse=True)
    hints = hints[:args.hint_top_k]


    report = {
        "min_pass_rate": args.min_pass_rate,
        "min_ci_lo": args.min_ci_lo,
        "n_groups": len(rows),
        "n_failed_groups": len(fails),
        "failed_groups": fails,
        "hints_top": hints,
        "status": "PASS" if len(fails)==0 else "FAIL",
    }
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
