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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="dt_ladder_ledger.csv")
    ap.add_argument("--out", default="", help="output folder (default: <ledger_parent>/dt_presets)")
    ap.add_argument("--pass_threshold", type=float, default=1.0, help="required pass rate to accept dt")
    ap.add_argument("--prefer", choices=["largest_dt","smallest_backtracks"], default="largest_dt",
                    help="tie-breaker when multiple dt pass threshold")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out) if args.out else (ledger.parent/"dt_presets")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    if not rows:
        raise SystemExit("Empty ledger")

    # group by (model, integrator, dt)
    grp: Dict[Tuple[str,str,float], List[Dict[str,Any]]] = {}
    for r in rows:
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(r.get("dt","nan"))
        grp.setdefault((model, integ, dt), []).append(r)

    # compute pass rate and median backtracks per group
    def median(vals):
        vs = [v for v in vals if not math.isnan(v)]
        if not vs:
            return float("nan")
        vs.sort()
        n=len(vs)
        mid=n//2
        return vs[mid] if n%2==1 else 0.5*(vs[mid-1]+vs[mid])

    stats = []
    for (model, integ, dt), rs in grp.items():
        n=len(rs)
        pass_flags=[1 if str(x.get("status","")).upper()=="PASS" else 0 for x in rs]
        pass_rate=sum(pass_flags)/n if n else float("nan")
        backtracks=median([_f(x.get("dt_backtracks_total","nan")) for x in rs])
        dtmin=median([_f(x.get("dt_min","nan")) for x in rs])
        stats.append({
            "model": model,
            "integrator": integ,
            "dt": dt,
            "n": n,
            "pass_rate": pass_rate,
            "median_backtracks": backtracks,
            "median_dt_min": dtmin,
        })

    # choose dt per (model, integrator)
    choices = {}
    for s in stats:
        key=(s["model"], s["integrator"])
        choices.setdefault(key, []).append(s)

    selected = []
    for (model, integ), items in choices.items():
        items_ok = [x for x in items if not math.isnan(x["dt"]) and x["pass_rate"] >= args.pass_threshold]
        if not items_ok:
            selected.append({"model": model, "integrator": integ, "dt_selected": float("nan"),
                             "pass_threshold": args.pass_threshold, "reason":"no_dt_meets_threshold"})
            continue
        # primary: largest dt
        if args.prefer == "largest_dt":
            items_ok.sort(key=lambda x: (-x["dt"], x["median_backtracks"] if not math.isnan(x["median_backtracks"]) else 1e99))
        else:
            # smallest backtracks among those meeting threshold, tie-breaker largest dt
            items_ok.sort(key=lambda x: (x["median_backtracks"] if not math.isnan(x["median_backtracks"]) else 1e99, -x["dt"]))
        best = items_ok[0]
        selected.append({"model": model, "integrator": integ, "dt_selected": best["dt"],
                         "pass_threshold": args.pass_threshold, "reason":"selected_from_ledger",
                         "pass_rate": best["pass_rate"], "median_backtracks": best["median_backtracks"], "median_dt_min": best["median_dt_min"]})

    # write outputs
    stats_csv = out_dir/"dt_presets_stats.csv"
    with stats_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
        w.writeheader()
        for r in sorted(stats, key=lambda x:(x["model"], x["integrator"], -x["dt"])):
            w.writerow(r)

    sel_csv = out_dir/"dt_presets_selected.csv"
    with sel_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0].keys()))
        w.writeheader()
        for r in sorted(selected, key=lambda x:(x["model"], x["integrator"])):
            w.writerow(r)

    # json mapping: presets[model][integrator] = dt
    presets = {}
    for r in selected:
        m = r["model"]; integ = r["integrator"]; dt = r["dt_selected"]
        presets.setdefault(m, {})[integ] = dt

    (out_dir/"dt_presets.json").write_text(json.dumps(presets, indent=2), encoding="utf-8")

    (out_dir/"README.md").write_text(
        "dt presets extracted from dt ladder ledger.\n\n"
        "Files:\n- dt_presets_stats.csv\n- dt_presets_selected.csv\n- dt_presets.json\n",
        encoding="utf-8"
    )

    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
