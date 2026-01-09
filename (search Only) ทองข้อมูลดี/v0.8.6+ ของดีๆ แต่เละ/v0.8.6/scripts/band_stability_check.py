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

def band_from_dt(dt: float, demo_dt: float, mid_dt: float, hard_dt: float) -> str:
    if math.isnan(dt):
        return "FAIL"
    if dt >= demo_dt:
        return "DEMO"
    if dt >= mid_dt:
        return "MID"
    if dt >= hard_dt:
        return "BOUNDARY"
    return "HARD"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out_dir", default="", help="default: <ledger_parent>/band_stability")
    ap.add_argument("--policy", choices=["max_over_integrators","min_over_integrators","semiimplicit_only","stabilized_only"],
                    default="max_over_integrators")
    ap.add_argument("--demo_dt", type=float, default=0.05)
    ap.add_argument("--mid_dt", type=float, default=0.02)
    ap.add_argument("--hard_dt", type=float, default=0.01)
    ap.add_argument("--write_band_map", action="store_true", help="write band_map_mode.csv")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out_dir) if args.out_dir else (ledger.parent/"band_stability")
    out_dir.mkdir(parents=True, exist_ok=True)

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    # base_case_id and seed -> dt_max_pass per integrator
    # group by (base, seed, integ, dt)
    by_key: Dict[Tuple[str,str,str,float], List[Dict[str,Any]]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        seed = str(r.get("seed","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        by_key.setdefault((base, seed, integ, dt), []).append(r)

    dt_max: Dict[Tuple[str,str,str], float] = {}
    for (base, seed, integ, dt), rs in by_key.items():
        # if any PASS at this dt, count as pass
        is_pass = any(str(x.get("status","")).upper()=="PASS" for x in rs)
        if not is_pass:
            continue
        k = (base, seed, integ)
        prev = dt_max.get(k, float("nan"))
        if math.isnan(prev) or dt > prev:
            dt_max[k] = dt

    # collapse to robust_dt per (base, seed)
    band_rows = []
    by_case_seed: Dict[Tuple[str,str], Dict[str,float]] = {}
    for (base, seed, integ), dt in dt_max.items():
        by_case_seed.setdefault((base, seed), {})[integ] = dt

    for (base, seed), dts in sorted(by_case_seed.items()):
        semi = dts.get("semiimplicit", float("nan"))
        stab = dts.get("stabilized", float("nan"))

        if args.policy == "semiimplicit_only":
            robust = semi
        elif args.policy == "stabilized_only":
            robust = stab
        elif args.policy == "min_over_integrators":
            cands = [x for x in [semi, stab] if not math.isnan(x)]
            robust = min(cands) if cands else float("nan")
        else:
            cands = [x for x in [semi, stab] if not math.isnan(x)]
            robust = max(cands) if cands else float("nan")

        band = band_from_dt(robust, args.demo_dt, args.mid_dt, args.hard_dt)
        band_rows.append({
            "base_case_id": base,
            "seed": seed,
            "dt_max_semi": semi,
            "dt_max_stab": stab,
            "robust_dt": robust,
            "band": band,
        })

    # compute stability per base_case_id
    by_base: Dict[str, List[str]] = {}
    for r in band_rows:
        by_base.setdefault(r["base_case_id"], []).append(r["band"])

    stability_rows = []
    for base, bands in sorted(by_base.items()):
        # mode + agreement
        counts = {}
        for b in bands:
            counts[b] = counts.get(b, 0) + 1
        mode = max(counts.items(), key=lambda kv: kv[1])[0]
        agree = counts[mode] / len(bands)
        stability_rows.append({
            "base_case_id": base,
            "n_seeds": len(bands),
            "band_mode": mode,
            "agreement": agree,
            "band_counts_json": json.dumps(counts, sort_keys=True),
        })

    # write outputs
    by_seed_csv = out_dir/"band_by_seed.csv"
    with by_seed_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(band_rows[0].keys()) if band_rows else ["base_case_id","seed","band"])
        w.writeheader()
        for r in band_rows:
            w.writerow(r)

    stab_csv = out_dir/"band_stability_by_case.csv"
    with stab_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stability_rows[0].keys()) if stability_rows else ["base_case_id","agreement"])
        w.writeheader()
        for r in stability_rows:
            w.writerow(r)

    overview = {
        "policy": args.policy,
        "thresholds": {"DEMO": args.demo_dt, "MID": args.mid_dt, "BOUNDARY": args.hard_dt},
        "n_cases": len(stability_rows),
        "n_rows_by_seed": len(band_rows),
    }
    (out_dir/"band_stability_overview.json").write_text(json.dumps(overview, indent=2), encoding="utf-8")

    if args.write_band_map:
        bm = out_dir/"band_map_mode.csv"
        with bm.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["base_case_id","band","notes"])
            w.writeheader()
            for r in stability_rows:
                w.writerow({"base_case_id": r["base_case_id"], "band": r["band_mode"], "notes": f"agreement={r['agreement']}; {r['band_counts_json']}"})

    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
