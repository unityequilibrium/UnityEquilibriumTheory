#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import List, Dict, Any

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def quantile(vals: List[float], q: float) -> float:
    vs = [v for v in vals if not math.isnan(v)]
    if not vs:
        return float("nan")
    vs.sort()
    if q <= 0: return vs[0]
    if q >= 1: return vs[-1]
    pos = q*(len(vs)-1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vs[lo]
    return vs[lo]*(hi-pos) + vs[hi]*(pos-lo)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_metrics", required=True, help="run_metrics.csv")
    ap.add_argument("--out", default="", help="output json (default: <run_metrics_parent>/metric_thresholds.json)")
    ap.add_argument("--use_only_pass", action="store_true", help="filter status==PASS")
    ap.add_argument("--q_tight", type=float, default=0.9, help="quantile for tight_frac_max")
    ap.add_argument("--q_btden", type=float, default=0.9, help="quantile for backtracks_density_max")
    ap.add_argument("--q_collapse", type=float, default=0.1, help="quantile for dt_collapse_ratio_min (lower tail)")
    args = ap.parse_args()

    rm = Path(args.run_metrics)
    out = Path(args.out) if args.out else (rm.parent/"metric_thresholds.json")

    rows=[]
    with rm.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if args.use_only_pass and str(r.get("status","")).upper() != "PASS":
                continue
            rows.append(r)
    if not rows:
        raise SystemExit("No rows after filtering")

    tight = [_f(str(r.get("tight_frac","nan"))) for r in rows]
    btden = [_f(str(r.get("backtracks_density","nan"))) for r in rows]
    collapse = [_f(str(r.get("dt_collapse_ratio","nan"))) for r in rows]

    thresholds = {
        "tight_frac_max": float(quantile(tight, args.q_tight)),
        "backtracks_density_max": float(quantile(btden, args.q_btden)),
        "dt_collapse_ratio_min": float(quantile(collapse, args.q_collapse)),
        "source": {"q_tight": args.q_tight, "q_btden": args.q_btden, "q_collapse": args.q_collapse, "use_only_pass": int(args.use_only_pass)},
    }
    out.write_text(json.dumps(thresholds, indent=2), encoding="utf-8")
    print("Wrote", out)

if __name__ == "__main__":
    main()
