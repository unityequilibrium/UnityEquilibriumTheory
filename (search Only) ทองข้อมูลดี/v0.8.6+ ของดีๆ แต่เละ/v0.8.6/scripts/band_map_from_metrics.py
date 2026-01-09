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
    ap.add_argument("--run_metrics", required=True, help="run_metrics.csv from compute_run_metrics.py")
    ap.add_argument("--out", default="band_map_metrics.csv")
    ap.add_argument("--policy", choices=["max_over_integrators","min_over_integrators","semiimplicit_only","stabilized_only"],
                    default="max_over_integrators")
    ap.add_argument("--strict_all_seeds", action="store_true", help="use strict dt_max (PASS for all seeds)")
    ap.add_argument("--require_seed_coverage", action="store_true")
    ap.add_argument("--demo_dt", type=float, default=0.05)
    ap.add_argument("--mid_dt", type=float, default=0.02)
    ap.add_argument("--hard_dt", type=float, default=0.01)
    # metric thresholds (degrade if violated)
    ap.add_argument("--tight_frac_max", type=float, default=0.2)
    ap.add_argument("--dt_collapse_ratio_min", type=float, default=0.5)
    ap.add_argument("--backtracks_density_max", type=float, default=0.5)
    args = ap.parse_args()

    # load run_metrics keyed by (case_id) - unique per run
    metrics = {}
    with Path(args.run_metrics).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            metrics[str(r.get("case_id","")).strip()] = r

    # load ledger
    with Path(args.ledger).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    # collect seeds per base+integrator
    seeds_by = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip()
        seed = str(r.get("seed","")).strip()
        seeds_by.setdefault((base, integ), set()).add(seed)

    # group by base, integrator, dt, seed
    grp = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        seed = str(r.get("seed","")).strip()
        grp.setdefault((base, integ, dt, seed), []).append(r)

    def seed_pass(rs: List[Dict[str,Any]]) -> bool:
        # strict per run: require PASS
        return all(str(x.get("status","")).upper()=="PASS" for x in rs)

    # compute dt_max per base+integrator, optionally strict over seeds
    dt_max = {}
    for (base, integ), seeds in seeds_by.items():
        dts = sorted(set(dt for (b,i,dt,s) in grp.keys() if b==base and i==integ and not math.isnan(dt)), reverse=True)
        best = float("nan")
        for dt in dts:
            ok = True
            covered = 0
            for seed in seeds:
                k = (base, integ, dt, seed)
                if k not in grp:
                    if args.require_seed_coverage:
                        ok = False
                        break
                    else:
                        continue
                covered += 1
                if args.strict_all_seeds:
                    if not seed_pass(grp[k]):
                        ok = False
                        break
                else:
                    # non-strict: any PASS among repeats
                    if not any(str(x.get("status","")).upper()=="PASS" for x in grp[k]):
                        ok = False
                        break
            if ok:
                best = dt
                break
        dt_max[(base, integ)] = best

    # choose robust_dt per base by policy
    bases = sorted(set(str(r.get("base_case_id","")).strip() for r in rows))
    out_rows = []
    for base in bases:
        semi = dt_max.get((base, "semiimplicit"), float("nan"))
        stab = dt_max.get((base, "stabilized"), float("nan"))
        if args.policy == "semiimplicit_only":
            robust_dt = semi
            chosen = "semiimplicit"
        elif args.policy == "stabilized_only":
            robust_dt = stab
            chosen = "stabilized"
        elif args.policy == "min_over_integrators":
            c = [("semiimplicit", semi), ("stabilized", stab)]
            c = [(k,v) for k,v in c if not math.isnan(v)]
            if not c:
                robust_dt = float("nan"); chosen="none"
            else:
                chosen, robust_dt = min(c, key=lambda kv: kv[1])
        else:
            c = [("semiimplicit", semi), ("stabilized", stab)]
            c = [(k,v) for k,v in c if not math.isnan(v)]
            if not c:
                robust_dt = float("nan"); chosen="none"
            else:
                chosen, robust_dt = max(c, key=lambda kv: kv[1])

        band = band_from_dt(robust_dt, args.demo_dt, args.mid_dt, args.hard_dt)

        # data-driven degradation: evaluate worst metrics among runs at dt=robust_dt for chosen integrator
        # pick all matching runs
        worst_tight = -1.0
        worst_collapse = 1e99
        worst_btden = -1.0

        if chosen != "none" and (not math.isnan(robust_dt)):
            for r in rows:
                if str(r.get("base_case_id","")).strip()!=base: 
                    continue
                if str(r.get("integrator","")).strip()!=chosen:
                    continue
                if abs(_f(str(r.get("dt","nan")))-robust_dt) > 1e-15:
                    continue
                mid = metrics.get(str(r.get("case_id","")).strip(), {})
                tf = _f(str(mid.get("tight_frac","nan")))
                cr = _f(str(mid.get("dt_collapse_ratio","nan")))
                bd = _f(str(mid.get("backtracks_density","nan")))
                if not math.isnan(tf): worst_tight = max(worst_tight, tf)
                if not math.isnan(cr): worst_collapse = min(worst_collapse, cr)
                if not math.isnan(bd): worst_btden = max(worst_btden, bd)

            # degrade if metrics violate
            if (worst_tight >= 0 and worst_tight > args.tight_frac_max) or (worst_collapse < args.dt_collapse_ratio_min) or (worst_btden >= 0 and worst_btden > args.backtracks_density_max):
                # DEMO->MID, MID->BOUNDARY, BOUNDARY->HARD
                band = {"DEMO":"MID","MID":"BOUNDARY","BOUNDARY":"HARD","HARD":"HARD","FAIL":"FAIL"}[band]

        out_rows.append({
            "base_case_id": base,
            "band": band,
            "notes": f"policy={args.policy}; strict_all_seeds={int(args.strict_all_seeds)}; chosen={chosen}; robust_dt={robust_dt}; dt_max_semi={semi}; dt_max_stab={stab}; worst_tight={worst_tight}; worst_collapse={worst_collapse}; worst_btden={worst_btden}",
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print("Wrote", out)

if __name__ == "__main__":
    main()
