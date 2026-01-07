#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math, json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float,float]:
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    denom = 1 + (z*z)/n
    center = (phat + (z*z)/(2*n)) / denom
    half = (z*math.sqrt((phat*(1-phat) + (z*z)/(4*n)) / n)) / denom
    return (max(0.0, center-half), min(1.0, center+half))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="stress run ledger (dt_ladder_ledger.csv)")
    ap.add_argument("--out_dir", default="", help="default: <ledger_parent>/stress_summary")
    ap.add_argument("--group", choices=["band","band_model","band_model_integrator","band_model_integrator_variant","variant"], default="band_model_integrator")
    ap.add_argument("--z", type=float, default=1.96, help="z-score for Wilson CI")
    args = ap.parse_args()

    ledger = Path(args.ledger)
    out_dir = Path(args.out_dir) if args.out_dir else (ledger.parent/"stress_summary")
    out_dir.mkdir(parents=True, exist_ok=True)

    with ledger.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        rows = [r for r in rdr]
    if not rows:
        raise SystemExit("Empty ledger")

    def key(r):
        band = (r.get("band","") or "").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        variant = (r.get("variant","") or "").strip() or "BASE"
        if args.group == "variant":
            return (variant,)
        if args.group == "band":
            return (band,)
        if args.group == "band_model":
            return (band, model)
        if args.group == "band_model_integrator_variant":
            return (band, model, integ, variant)
        return (band, model, integ)

    grp: Dict[Tuple[str,...], List[Dict[str,Any]]] = {}
    for r in rows:
        grp.setdefault(key(r), []).append(r)

    out_rows = []
    for k, rs in sorted(grp.items()):
        n = len(rs)
        kpass = sum(1 for r in rs if str(r.get("status","")).upper()=="PASS")
        ci_lo, ci_hi = wilson_ci(kpass, n, args.z)
        fail_codes = {}
        for r in rs:
            if str(r.get("status","")).upper() != "PASS":
                code = str(r.get("fail_code","")).strip() or "UNKNOWN"
                fail_codes[code] = fail_codes.get(code, 0) + 1

        row = {"n": n, "pass": kpass, "pass_rate": kpass/n if n else float("nan"),
               "ci_lo": ci_lo, "ci_hi": ci_hi,
               "fail_codes_json": json.dumps(fail_codes, sort_keys=True)}
        if args.group == "variant":
            row["variant"] = k[0]
        elif args.group == "band":
            row["band"] = k[0]
        elif args.group == "band_model":
            row["band"], row["model"] = k
        elif args.group == "band_model_integrator_variant":
            row["band"], row["model"], row["integrator"], row["variant"] = k
        else:
            row["band"], row["model"], row["integrator"] = k
        out_rows.append(row)

    out_csv = out_dir/"stress_summary.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    (out_dir/"README.md").write_text(
        "Stress test summary.\n\n- stress_summary.csv: pass rates with Wilson CI.\n",
        encoding="utf-8"
    )
    print("Wrote", out_dir)

if __name__ == "__main__":
    main()
