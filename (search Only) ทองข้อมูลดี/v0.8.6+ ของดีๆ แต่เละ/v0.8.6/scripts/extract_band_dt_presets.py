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
    n = len(vs)
    m = n // 2
    return vs[m] if n % 2 == 1 else 0.5*(vs[m-1] + vs[m])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="dt_ladder_ledger.csv")
    ap.add_argument("--band_map", required=True, help="CSV mapping base_case_id->band (columns: base_case_id,band)")
    ap.add_argument("--out", default="", help="output folder (default: <ledger_parent>/band_dt_presets)")
    ap.add_argument("--pass_threshold", type=float, default=1.0)
    ap.add_argument("--prefer", choices=["largest_dt","smallest_backtracks"], default="largest_dt")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out) if args.out else (ledger.parent/"band_dt_presets")
    out_dir.mkdir(parents=True, exist_ok=True)

    # read band map
    band_of: Dict[str, str] = {}
    with Path(args.band_map).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames or "base_case_id" not in rdr.fieldnames or "band" not in rdr.fieldnames:
            raise SystemExit("band_map must have columns: base_case_id, band")
        for r in rdr:
            base = str(r.get("base_case_id","")).strip()
            band = str(r.get("band","")).strip()
            if base:
                band_of[base] = band or "UNLABELED"

    if not band_of:
        raise SystemExit("band_map is empty")

    rows: List[Dict[str, Any]] = []
    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty ledger")

    # group by (band, model, integrator, dt)
    grp: Dict[Tuple[str,str,str,float], List[Dict[str,Any]]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        band = band_of.get(base, "UNMAPPED")
        model = str(r.get("model","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        grp.setdefault((band, model, integ, dt), []).append(r)

    stats = []
    for (band, model, integ, dt), rs in grp.items():
        n = len(rs)
        pass_rate = sum(1 for x in rs if str(x.get("status","")).upper()=="PASS") / n if n else float("nan")
        med_back = _median([_f(str(x.get("dt_backtracks_total","nan"))) for x in rs])
        med_dtmin = _median([_f(str(x.get("dt_min","nan"))) for x in rs])
        stats.append({
            "band": band, "model": model, "integrator": integ, "dt": dt,
            "n": n, "pass_rate": pass_rate,
            "median_backtracks": med_back, "median_dt_min": med_dtmin
        })

    # choose dt per (band, model, integrator)
    by_key: Dict[Tuple[str,str,str], List[Dict[str,Any]]] = {}
    for s in stats:
        key = (s["band"], s["model"], s["integrator"])
        by_key.setdefault(key, []).append(s)

    selected = []
    for (band, model, integ), items in by_key.items():
        ok = [x for x in items if (not math.isnan(x["dt"])) and x["pass_rate"] >= args.pass_threshold]
        if not ok:
            selected.append({
                "band": band, "model": model, "integrator": integ,
                "dt_selected": float("nan"), "pass_threshold": args.pass_threshold,
                "reason": "no_dt_meets_threshold"
            })
            continue
        if args.prefer == "largest_dt":
            ok.sort(key=lambda x: (-x["dt"], x["median_backtracks"] if not math.isnan(x["median_backtracks"]) else 1e99))
        else:
            ok.sort(key=lambda x: (x["median_backtracks"] if not math.isnan(x["median_backtracks"]) else 1e99, -x["dt"]))
        best = ok[0]
        selected.append({
            "band": band, "model": model, "integrator": integ,
            "dt_selected": best["dt"], "pass_threshold": args.pass_threshold,
            "reason": "selected_from_ledger",
            "pass_rate": best["pass_rate"],
            "median_backtracks": best["median_backtracks"],
            "median_dt_min": best["median_dt_min"]
        })

    # write stats csv
    stats_csv = out_dir/"band_dt_presets_stats.csv"
    with stats_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
        w.writeheader()
        for r in sorted(stats, key=lambda x:(x["band"], x["model"], x["integrator"], -x["dt"])):
            w.writerow(r)

    sel_csv = out_dir/"band_dt_presets_selected.csv"
    with sel_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0].keys()))
        w.writeheader()
        for r in sorted(selected, key=lambda x:(x["band"], x["model"], x["integrator"])):
            w.writerow(r)

    # json mapping: presets[band][model][integrator]=dt
    presets: Dict[str, Dict[str, Dict[str, float]]] = {}
    for r in selected:
        b = r["band"]; m = r["model"]; i = r["integrator"]
        presets.setdefault(b, {}).setdefault(m, {})[i] = r.get("dt_selected", float("nan"))

    (out_dir/"band_dt_presets.json").write_text(json.dumps(presets, indent=2), encoding="utf-8")

    (out_dir/"README.md").write_text(
        "Band-aware dt presets extracted from dt ladder ledger.\n\n"
        "Files:\n- band_dt_presets_stats.csv\n- band_dt_presets_selected.csv\n- band_dt_presets.json\n",
        encoding="utf-8"
    )

    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
