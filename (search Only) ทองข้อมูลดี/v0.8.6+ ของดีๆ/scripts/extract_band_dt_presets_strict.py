#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--band_map", required=True, help="base_case_id->band mapping (columns: base_case_id, band)")
    ap.add_argument("--out_dir", default="", help="default: <ledger_parent>/band_dt_presets_strict")
    ap.add_argument("--strict_all_seeds", action="store_true")
    ap.add_argument("--require_seed_coverage", action="store_true")
    ap.add_argument("--metrics", default="", help="optional run_metrics.csv")
    ap.add_argument("--thresholds_json", default="", help="optional metric_thresholds.json")
    ap.add_argument("--prefer", choices=["largest_dt","smallest_backtracks"], default="largest_dt")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out_dir) if args.out_dir else (ledger.parent/"band_dt_presets_strict")
    out_dir.mkdir(parents=True, exist_ok=True)

    # band map
    band_of = {}
    with Path(args.band_map).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            base = str(r.get("base_case_id","")).strip()
            band = str(r.get("band","")).strip() or "UNLABELED"
            if base:
                band_of[base] = band

    # optional metrics
    metrics = {}
    if args.metrics:
        with Path(args.metrics).open("r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                metrics[str(r.get("case_id","")).strip()] = r

    thresholds = {}
    if args.thresholds_json:
        thresholds = json.loads(Path(args.thresholds_json).read_text(encoding="utf-8"))
    tight_max = float(thresholds.get("tight_frac_max", 1e9))
    collapse_min = float(thresholds.get("dt_collapse_ratio_min", -1e9))
    btden_max = float(thresholds.get("backtracks_density_max", 1e9))

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    # tag each row with band
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        r["_band"] = band_of.get(base, "UNMAPPED")

    # seeds per (band, model, integ, base)
    seeds_by_base = {}
    for r in rows:
        band = r["_band"]
        base = str(r.get("base_case_id","")).strip()
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        seed = str(r.get("seed","")).strip()
        seeds_by_base.setdefault((band, model, integ, base), set()).add(seed)

    # group by (band, model, integ, dt)
    grp = {}
    for r in rows:
        band = r["_band"]
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        grp.setdefault((band, model, integ, dt), []).append(r)

    bands = sorted(set(b for (b,m,i,dt) in grp.keys()))
    selected_rows = []
    presets = {}

    for band in bands:
        combos = sorted(set((m,i) for (b,m,i,dt) in grp.keys() if b==band))
        for model, integ in combos:
            dts = sorted([dt for (b,m,i,dt) in grp.keys() if b==band and m==model and i==integ and not math.isnan(dt)], reverse=True)
            best = float("nan")
            best_stats = {}
            for dt in dts:
                rs = grp[(band, model, integ, dt)]
                ok = True
                bases = sorted(set(str(r.get("base_case_id","")).strip() for r in rs))
                worst_bt = -1.0
                worst_tight = -1.0
                worst_collapse = 1e99
                worst_btden = -1.0

                for base in bases:
                    seeds = set()
                    for k, sset in seeds_by_base.items():
                        if k[0]==band and k[1]==model and k[2]==integ and k[3]==base:
                            seeds |= sset
                    rbs = [r for r in rs if str(r.get("base_case_id","")).strip()==base]
                    by_seed={}
                    for r in rbs:
                        by_seed.setdefault(str(r.get("seed","")).strip(), []).append(r)
                    for seed in seeds:
                        if seed not in by_seed:
                            if args.require_seed_coverage:
                                ok = False
                                break
                            else:
                                continue
                        statuses=[str(x.get("status","")).upper() for x in by_seed[seed]]
                        if args.strict_all_seeds:
                            if not all(s=="PASS" for s in statuses):
                                ok = False
                                break
                        else:
                            if not any(s=="PASS" for s in statuses):
                                ok = False
                                break
                    if not ok:
                        break

                    for r in rbs:
                        cid = str(r.get("case_id","")).strip()
                        mid = metrics.get(cid, {})
                        tf = _f(str(mid.get("tight_frac","nan")))
                        cr = _f(str(mid.get("dt_collapse_ratio","nan")))
                        bd = _f(str(mid.get("backtracks_density","nan")))
                        bt = _f(str(r.get("dt_backtracks_total","nan")))
                        if not math.isnan(bt): worst_bt = max(worst_bt, bt)
                        if not math.isnan(tf): worst_tight = max(worst_tight, tf)
                        if not math.isnan(cr): worst_collapse = min(worst_collapse, cr)
                        if not math.isnan(bd): worst_btden = max(worst_btden, bd)

                if ok:
                    if (worst_tight >= 0 and worst_tight > tight_max) or (worst_collapse < collapse_min) or (worst_btden >= 0 and worst_btden > btden_max):
                        continue
                    best = dt
                    best_stats = {"worst_backtracks_total": worst_bt, "worst_tight_frac": worst_tight, "worst_dt_collapse_ratio": worst_collapse, "worst_backtracks_density": worst_btden}
                    break

            presets.setdefault(band, {}).setdefault(model, {})[integ] = best
            selected_rows.append({"band": band, "model": model, "integrator": integ, "dt_selected": best, **best_stats,
                                  "strict_all_seeds": int(args.strict_all_seeds), "require_seed_coverage": int(args.require_seed_coverage)})

    (out_dir/"band_dt_presets_strict.json").write_text(json.dumps(presets, indent=2), encoding="utf-8")
    with (out_dir/"band_dt_presets_strict_selected.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(selected_rows[0].keys()))
        w.writeheader()
        for r in selected_rows:
            w.writerow(r)
    (out_dir/"README.md").write_text("Strict band-aware dt presets extracted from ledger (and optional metrics thresholds).\n", encoding="utf-8")
    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
