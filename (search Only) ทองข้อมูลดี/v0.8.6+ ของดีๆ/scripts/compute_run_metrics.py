#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List, Tuple

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def _median(vals: List[float]) -> float:
    vs = [v for v in vals if not math.isnan(v)]
    if not vs:
        return float("nan")
    vs.sort()
    n=len(vs); m=n//2
    return vs[m] if n%2==1 else 0.5*(vs[m-1]+vs[m])

def read_timeseries(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        return [r for r in rdr]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="dt_ladder_ledger.csv")
    ap.add_argument("--out", default="", help="output csv (default: <ledger_parent>/run_metrics.csv)")
    ap.add_argument("--eps", type=float, default=1e-12, help="tightness epsilon for dOmega")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out = Path(args.out) if args.out else (ledger.parent/"run_metrics.csv")

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]

    if not rows:
        raise SystemExit("Empty ledger")

    out_rows = []
    for r in rows:
        run_dir = Path(str(r.get("run_dir","")).strip())
        summary_path = run_dir/"summary.json"
        ts_path = run_dir/"timeseries.csv"

        summary = {}
        if summary_path.exists():
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
            except Exception:
                summary = {}

        ts = read_timeseries(ts_path)
        # accepted steps
        accepted = [x for x in ts if str(x.get("accepted","1")) in ("1","True","true")]
        dO = [_f(str(x.get("dOmega","nan"))) for x in accepted]
        dt_series = [_f(str(x.get("dt","nan"))) for x in accepted]
        backtracks_series = [_f(str(x.get("backtracks","nan"))) for x in accepted]

        dOmega_max = max([v for v in dO if not math.isnan(v)], default=float("nan"))
        # tight fraction: dOmega close to 0 from below (or above due to numeric noise)
        tight = [1 for v in dO if (not math.isnan(v)) and v > -abs(args.eps)]
        tight_frac = (sum(tight)/len(dO)) if dO else float("nan")

        dt_nom = _f(str(r.get("dt","nan")))
        dt_min = _f(str(r.get("dt_min","nan")))
        dt_collapse_ratio = (dt_min/dt_nom) if (not math.isnan(dt_min) and not math.isnan(dt_nom) and dt_nom>0) else float("nan")

        bt_total = _f(str(r.get("dt_backtracks_total","nan")))
        steps_acc = _f(str(r.get("steps_accepted","nan")))
        backtracks_density = (bt_total/steps_acc) if (not math.isnan(bt_total) and not math.isnan(steps_acc) and steps_acc>0) else float("nan")

        dOmega_med = _median([v for v in dO if not math.isnan(v)]) if dO else float("nan")
        dt_med = _median([v for v in dt_series if not math.isnan(v)]) if dt_series else float("nan")
        bt_med = _median([v for v in backtracks_series if not math.isnan(v)]) if backtracks_series else float("nan")

        out_rows.append({
            "base_case_id": r.get("base_case_id",""),
            "band": r.get("band",""),
            "variant": r.get("variant",""),
            "origin_case_id": r.get("origin_case_id",""),
            "origin_fail_code": r.get("origin_fail_code",""),
            "case_id": r.get("case_id",""),
            "model": r.get("model",""),
            "integrator": r.get("integrator",""),
            "seed": r.get("seed",""),
            "dt": r.get("dt",""),
            "status": r.get("status",""),
            "fail_code": r.get("fail_code",""),
            "dt_min": r.get("dt_min",""),
            "dt_backtracks_total": r.get("dt_backtracks_total",""),
            "steps_accepted": r.get("steps_accepted",""),
            "dOmega_max": dOmega_max,
            "dOmega_median": dOmega_med,
            "tight_frac": tight_frac,
            "dt_collapse_ratio": dt_collapse_ratio,
            "backtracks_density": backtracks_density,
            "dt_median": dt_med,
            "backtracks_median": bt_med,
            "run_dir": str(run_dir),
        })

    out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out_rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for rr in out_rows:
            w.writerow(rr)
    print(f"Wrote {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
