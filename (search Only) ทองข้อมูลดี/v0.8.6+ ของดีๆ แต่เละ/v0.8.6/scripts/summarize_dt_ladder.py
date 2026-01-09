#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math
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
    mid = n // 2
    if n % 2 == 1:
        return vs[mid]
    return 0.5*(vs[mid-1] + vs[mid])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--pass_threshold", type=float, default=1.0)
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out) if args.out else (ledger.parent / "dt_ladder_summary")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    if not rows:
        (out_dir/"README.md").write_text("No rows in ledger.\n", encoding="utf-8")
        print("No rows.")
        return

    # group by (integrator, dt)
    grp: Dict[Tuple[str,float], List[Dict[str, Any]]] = {}
    for r in rows:
        integ = str(r.get("integrator","")).strip()
        dt = _f(r.get("dt","nan"))
        grp.setdefault((integ, dt), []).append(r)

    # build summary rows
    summ_rows = []
    for (integ, dt), rs in grp.items():
        n = len(rs)
        pass_flags = [1 if str(x.get("status","")).upper()=="PASS" else 0 for x in rs]
        pass_rate = sum(pass_flags)/n if n else float("nan")
        med_back = _median([_f(x.get("dt_backtracks_total","nan")) for x in rs])
        med_dtmin = _median([_f(x.get("dt_min","nan")) for x in rs])
        med_dO = _median([_f(x.get("DeltaOmega","nan")) for x in rs])
        summ_rows.append({
            "integrator": integ,
            "dt": dt,
            "n": n,
            "pass_rate": pass_rate,
            "median_backtracks": med_back,
            "median_dt_min": med_dtmin,
            "median_DeltaOmega": med_dO,
        })

    # sort by integrator, dt desc
    summ_rows.sort(key=lambda r: (r["integrator"], -(r["dt"] if not math.isnan(r["dt"]) else -1e99)))

    summ_csv = out_dir/"dt_ladder_summary.csv"
    with summ_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summ_rows[0].keys()))
        w.writeheader()
        for r in summ_rows:
            w.writerow(r)

    # dt_max_pass per integrator
    best_rows = []
    integrators = sorted(set(r["integrator"] for r in summ_rows))
    for integ in integrators:
        sub = [r for r in summ_rows if r["integrator"]==integ and not math.isnan(r["dt"])]
        sub.sort(key=lambda r: -r["dt"])
        ok = [r for r in sub if r["pass_rate"] >= args.pass_threshold]
        best_rows.append({
            "integrator": integ,
            "dt_max_pass": ok[0]["dt"] if ok else float("nan"),
            "pass_threshold": args.pass_threshold,
        })
    best_csv = out_dir/"dt_ladder_best_dt.csv"
    with best_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(best_rows[0].keys()))
        w.writeheader()
        for r in best_rows:
            w.writerow(r)

    # per-case breakdown
    bycase: Dict[Tuple[str,str,float], List[Dict[str, Any]]] = {}
    for r in rows:
        base = str(r.get("base_case_id","")).strip()
        integ = str(r.get("integrator","")).strip()
        dt = _f(r.get("dt","nan"))
        bycase.setdefault((base, integ, dt), []).append(r)

    bycase_rows = []
    for (base, integ, dt), rs in bycase.items():
        n = len(rs)
        pass_rate = sum(1 if str(x.get("status","")).upper()=="PASS" else 0 for x in rs)/n
        bycase_rows.append({
            "base_case_id": base,
            "integrator": integ,
            "dt": dt,
            "n": n,
            "pass_rate": pass_rate,
            "median_backtracks": _median([_f(x.get("dt_backtracks_total","nan")) for x in rs]),
            "median_dt_min": _median([_f(x.get("dt_min","nan")) for x in rs]),
        })
    bycase_rows.sort(key=lambda r: (r["base_case_id"], r["integrator"], -(r["dt"] if not math.isnan(r["dt"]) else -1e99)))
    bycase_csv = out_dir/"dt_ladder_by_case.csv"
    with bycase_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(bycase_rows[0].keys()))
        w.writeheader()
        for r in bycase_rows:
            w.writerow(r)

    (out_dir/"README.md").write_text(
        "# dt ladder summary\n\nOutputs:\n- dt_ladder_summary.csv\n- dt_ladder_best_dt.csv\n- dt_ladder_by_case.csv\n",
        encoding="utf-8"
    )
    print("Wrote summary to", out_dir)

if __name__ == "__main__":
    main()
