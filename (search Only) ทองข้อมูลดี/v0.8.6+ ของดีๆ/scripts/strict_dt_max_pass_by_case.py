#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math, json
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
    ap.add_argument("--out", default="", help="output csv (default: <ledger_parent>/dt_max_strict_by_case.csv)")
    ap.add_argument("--seed_pass_mode", choices=["all","any"], default="all",
                    help="If repeats exist per seed+dt: all requires all repeats PASS; any requires at least one PASS.")
    ap.add_argument("--require_seed_coverage", action="store_true",
                    help="If enabled, dt is invalid unless all seeds observed for that case+integrator have an entry at dt.")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out = Path(args.out) if args.out else (ledger.parent/"dt_max_strict_by_case.csv")

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    # determine seed set per (base_case_id, integrator)
    seeds_by_case_integ: Dict[Tuple[str,str], Set[str]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip()
        seed = str(r.get("seed","")).strip()
        seeds_by_case_integ.setdefault((base, integ), set()).add(seed)

    # group by (base, integ, dt, seed)
    grp: Dict[Tuple[str,str,float,str], List[Dict[str,Any]]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(str(r.get("dt","nan")))
        seed = str(r.get("seed","")).strip()
        grp.setdefault((base, integ, dt, seed), []).append(r)

    # compute seed_pass at dt
    seed_pass: Dict[Tuple[str,str,float,str], bool] = {}
    for k, rs in grp.items():
        statuses = [str(x.get("status","")).upper() for x in rs]
        if args.seed_pass_mode == "any":
            seed_pass[k] = any(s=="PASS" for s in statuses)
        else:
            seed_pass[k] = all(s=="PASS" for s in statuses)

    # evaluate strict pass per (base, integ, dt)
    dt_stats: Dict[Tuple[str,str,float], Dict[str,Any]] = {}
    for (base, integ), seeds in seeds_by_case_integ.items():
        # collect all dt values seen for this pair
        dts = sorted(set(dt for (b,i,dt,s) in grp.keys() if b==base and i==integ and not math.isnan(dt)))
        for dt in dts:
            ok = True
            covered = 0
            for seed in seeds:
                k = (base, integ, dt, seed)
                if k not in seed_pass:
                    if args.require_seed_coverage:
                        ok = False
                        break
                    else:
                        continue
                covered += 1
                if not seed_pass[k]:
                    ok = False
                    break
            dt_stats[(base, integ, dt)] = {"strict_pass": ok, "seeds_total": len(seeds), "seeds_covered": covered}

    # dt_max_strict
    out_rows = []
    for (base, integ), seeds in sorted(seeds_by_case_integ.items()):
        dts = sorted([dt for (b,i,dt) in dt_stats.keys() if b==base and i==integ], reverse=True)
        dt_max = float("nan")
        cov = 0
        for dt in dts:
            st = dt_stats[(base, integ, dt)]
            if st["strict_pass"]:
                dt_max = dt
                cov = st["seeds_covered"]
                break
        out_rows.append({
            "base_case_id": base,
            "integrator": integ,
            "dt_max_strict_pass": dt_max,
            "seeds_total": len(seeds),
            "seeds_covered_at_dtmax": cov,
            "require_seed_coverage": int(args.require_seed_coverage),
            "seed_pass_mode": args.seed_pass_mode,
        })

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"Wrote {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
