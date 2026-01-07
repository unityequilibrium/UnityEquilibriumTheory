#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

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

def _band_from_dt(dt: float, demo_dt: float, mid_dt: float, hard_dt: float) -> str:
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
    ap.add_argument("--ledger", required=True, help="dt_ladder_ledger.csv")
    ap.add_argument("--out", default="band_map.csv", help="output band_map csv")
    ap.add_argument("--policy", choices=["max_over_integrators","min_over_integrators","semiimplicit_only","stabilized_only"],
                    default="max_over_integrators",
                    help="How to collapse dt_max_pass over integrators to a single robustness dt per base_case_id")
    ap.add_argument("--demo_dt", type=float, default=0.05, help="dt threshold for DEMO band")
    ap.add_argument("--mid_dt", type=float, default=0.02, help="dt threshold for MID band")
    ap.add_argument("--hard_dt", type=float, default=0.01, help="dt threshold for BOUNDARY vs HARD")
    ap.add_argument("--demo_backtracks_max", type=float, default=1.0, help="max median backtracks at robust dt to keep DEMO")
    ap.add_argument("--strict_all_seeds", action="store_true", help="require PASS for all seeds at dt")
    ap.add_argument("--require_seed_coverage", action="store_true", help="require all seeds covered at dt")
    ap.add_argument("--use_model", default="", help="optional filter: only rows with this model")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    rows: List[Dict[str, Any]] = []
    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            if args.use_model and str(r.get("model","")).strip() != args.use_model:
                continue
            rows.append(r)
    if not rows:
        raise SystemExit("No rows after filtering")

    # Collect per base_case_id, per integrator: list of (dt, status, backtracks, dt_min)
    by_case: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip() or "unknown"
        if not base:
            continue
        by_case.setdefault(base, {}).setdefault(integ, []).append(r)

    out_rows = []
    for base, by_integ in sorted(by_case.items()):
        dt_max = {}
        back_at = {}
        dtmin_at = {}
        pass_rate = {}
        for integ, rs in by_integ.items():
            # compute dt_max_pass for this integrator
            # group by dt (in case repeated runs)
            dt_vals = sorted(set(_f(str(x.get("dt","nan"))) for x in rs if not math.isnan(_f(str(x.get("dt","nan"))))))
            if not dt_vals:
                dt_max[integ] = float("nan")
                continue
            # determine pass per dt (any PASS among repeats counts as pass; conservative option could be all-pass)
            pass_by_dt = {}
            back_by_dt = {}
            dtmin_by_dt = {}
            for dt in dt_vals:
                sub = [x for x in rs if abs(_f(str(x.get("dt","nan")))-dt) < 1e-15]
                pf = [1 if str(x.get("status","")).upper()=="PASS" else 0 for x in sub]
                pass_by_dt[dt] = 1 if any(pf) else 0  # seed-local; strict_all_seeds handled later
                back_by_dt[dt] = _median([_f(str(x.get("dt_backtracks_total","nan"))) for x in sub])
                dtmin_by_dt[dt] = _median([_f(str(x.get("dt_min","nan"))) for x in sub])
            pass_rate[integ] = sum(pass_by_dt.values()) / len(pass_by_dt) if pass_by_dt else float("nan")
            ok = [dt for dt, p in pass_by_dt.items() if p == 1]
            if not ok:
                dt_max[integ] = float("nan")
                continue
            dt_star = max(ok)
            # strict_all_seeds: ensure dt_star passes for all seeds (and coverage if required)
            if args.strict_all_seeds:
                # recompute strict over seeds for this base/integ at dt_star
                seeds = set(str(x.get('seed','')).strip() for x in rs)
                # build per-seed pass flags
                strict_ok = True
                for sd in seeds:
                    sub2 = [x for x in rs if str(x.get('seed','')).strip()==sd and abs(float(x.get('dt','nan'))-dt_star) < 1e-15]
                    if not sub2:
                        if args.require_seed_coverage:
                            strict_ok = False
                            break
                        else:
                            continue
                    if not all(str(x.get('status','')).upper()=='PASS' for x in sub2):
                        strict_ok = False
                        break
                if not strict_ok:
                    # if dt_star fails strict, try smaller dt
                    ok2 = sorted(ok, reverse=True)
                    dt_star2 = float('nan')
                    for cand in ok2:
                        strict_ok = True
                        for sd in seeds:
                            sub2 = [x for x in rs if str(x.get('seed','')).strip()==sd and abs(float(x.get('dt','nan'))-cand) < 1e-15]
                            if not sub2:
                                if args.require_seed_coverage:
                                    strict_ok = False
                                    break
                                else:
                                    continue
                            if not all(str(x.get('status','')).upper()=='PASS' for x in sub2):
                                strict_ok = False
                                break
                        if strict_ok:
                            dt_star2 = cand
                            break
                    dt_star = dt_star2

            dt_max[integ] = dt_star
            back_at[integ] = back_by_dt.get(dt_star, float("nan"))
            dtmin_at[integ] = dtmin_by_dt.get(dt_star, float("nan"))

        # collapse dt_max by policy
        semi = dt_max.get("semiimplicit", float("nan"))
        stab = dt_max.get("stabilized", float("nan"))
        if args.policy == "semiimplicit_only":
            robust_dt = semi
            chosen_integ = "semiimplicit"
        elif args.policy == "stabilized_only":
            robust_dt = stab
            chosen_integ = "stabilized"
        elif args.policy == "min_over_integrators":
            cands = [x for x in [semi, stab] if not math.isnan(x)]
            robust_dt = min(cands) if cands else float("nan")
            chosen_integ = "min(semi,stab)"
        else:  # max_over_integrators
            cands = [("semiimplicit", semi), ("stabilized", stab)]
            cands = [(k,v) for k,v in cands if not math.isnan(v)]
            if not cands:
                robust_dt = float("nan")
                chosen_integ = "none"
            else:
                chosen_integ, robust_dt = max(cands, key=lambda kv: kv[1])

        band = _band_from_dt(robust_dt, args.demo_dt, args.mid_dt, args.hard_dt)

        # degrade DEMO if backtracks too high at robust dt
        back = back_at.get(chosen_integ, float("nan")) if chosen_integ in back_at else float("nan")
        if band == "DEMO" and (not math.isnan(back)) and back > args.demo_backtracks_max:
            band = "MID"

        notes = (
            f"policy={args.policy}; robust_dt={robust_dt}; chosen_integ={chosen_integ}; "
            f"dt_max_semi={semi}; dt_max_stab={stab}; "
            f"med_back@robust={back}; med_dtmin@robust={dtmin_at.get(chosen_integ, float('nan'))}; "
            f"pass_rate_semi={pass_rate.get('semiimplicit', float('nan'))}; pass_rate_stab={pass_rate.get('stabilized', float('nan'))}"
        )

        out_rows.append({
            "base_case_id": base,
            "band": band,
            "notes": notes,
            "robust_dt": robust_dt,
            "dt_max_semi": semi,
            "dt_max_stab": stab,
            "chosen_integrator": chosen_integ,
            "median_backtracks_at_robust_dt": back,
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out_rows[0].keys()) if out_rows else ["base_case_id","band","notes"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"Wrote auto band_map: {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
