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
    ap.add_argument("--out_dir", default="", help="default: <ledger_parent>/dt_presets_strict")
    ap.add_argument("--strict_all_seeds", action="store_true", help="require PASS for all seeds")
    ap.add_argument("--require_seed_coverage", action="store_true")
    ap.add_argument("--metrics", default="", help="optional run_metrics.csv")
    ap.add_argument("--thresholds_json", default="", help="optional metric_thresholds.json")
    ap.add_argument("--prefer", choices=["largest_dt","smallest_backtracks"], default="largest_dt")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out_dir) if args.out_dir else (ledger.parent/"dt_presets_strict")
    out_dir.mkdir(parents=True, exist_ok=True)

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

    # seeds per model+integrator+base
    seeds_by_base = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        seed = str(r.get("seed","")).strip()
        seeds_by_base.setdefault((model, integ, base), set()).add(seed)

    # group by (model, integ, dt) -> list of rows
    grp = {}
    for r in rows:
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        grp.setdefault((model, integ, dt), []).append(r)

    # strict pass check for dt across all bases (and seeds)
    selected = []
    presets = {}

    # collect all model/integ combos
    combos = sorted(set((m,i) for (m,i,dt) in grp.keys()))
    for model, integ in combos:
        # candidate dt values
        dts = sorted([dt for (m,i,dt) in grp.keys() if m==model and i==integ and not math.isnan(dt)], reverse=True)
        best = float("nan")
        best_stats = {}
        for dt in dts:
            rs = [r for r in grp[(model, integ, dt)]]
            ok = True
            # per base, per seed constraints
            bases = sorted(set(str(r.get("base_case_id","")).strip() for r in rs))
            worst_bt = -1.0
            worst_tight = -1.0
            worst_collapse = 1e99
            worst_btden = -1.0
            for base in bases:
                seeds = set()
                # union of seeds expected for this base
                for k, sset in seeds_by_base.items():
                    if k[0]==model and k[1]==integ and k[2]==base:
                        seeds |= sset
                # rows at this dt, base
                rbs = [r for r in rs if str(r.get("base_case_id","")).strip()==base]
                if not rbs:
                    continue
                # group by seed
                by_seed = {}
                for r in rbs:
                    by_seed.setdefault(str(r.get("seed","")).strip(), []).append(r)
                # check each seed
                for seed in seeds:
                    if seed not in by_seed:
                        if args.require_seed_coverage:
                            ok = False
                            break
                        else:
                            continue
                    statuses = [str(x.get("status","")).upper() for x in by_seed[seed]]
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

                # metric gating (optional) across all runs at this base+dt (worst-case)
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
                # apply thresholds if available (skip if NaN)
                if (worst_tight >= 0 and worst_tight > tight_max) or (worst_collapse < collapse_min) or (worst_btden >= 0 and worst_btden > btden_max):
                    # too tight; try smaller dt
                    continue

                best = dt
                best_stats = {"worst_backtracks_total": worst_bt, "worst_tight_frac": worst_tight, "worst_dt_collapse_ratio": worst_collapse, "worst_backtracks_density": worst_btden}
                break

        presets.setdefault(model, {})[integ] = best
        selected.append({"model": model, "integrator": integ, "dt_selected": best, **best_stats,
                         "strict_all_seeds": int(args.strict_all_seeds), "require_seed_coverage": int(args.require_seed_coverage)})

    (out_dir/"dt_presets_strict.json").write_text(json.dumps(presets, indent=2), encoding="utf-8")
    with (out_dir/"dt_presets_strict_selected.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0].keys()))
        w.writeheader()
        for r in selected:
            w.writerow(r)
    (out_dir/"README.md").write_text("Strict dt presets extracted from ledger (and optional metrics thresholds).\n", encoding="utf-8")
    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
