#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
from typing import Dict, Any, Tuple, List

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
    ap.add_argument("--summaries", required=True, help="semicolon-separated summary csv paths")
    ap.add_argument("--out", default="merged_variant_summary.csv")
    ap.add_argument("--z", type=float, default=1.96)
    args = ap.parse_args()

    paths = [x.strip() for x in args.summaries.split(";") if x.strip()]
    if len(paths) < 1:
        raise SystemExit("No summaries provided")

    # aggregate by full key present in file: we assume columns include band, model, integrator, variant
    agg: Dict[Tuple[str,str,str,str], Dict[str,Any]] = {}
    for p in paths:
        pp = Path(p)
        if not pp.exists():
            raise SystemExit(f"Missing: {pp}")
        with pp.open("r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
                model = (r.get("model","") or "").strip()
                integ = (r.get("integrator","") or "").strip()
                variant = (r.get("variant","") or "BASE").strip() or "BASE"
                key = (band, model, integ, variant)
                n = int(float(r.get("n","0") or 0))
                kpass = int(float(r.get("pass","0") or 0))

                fc = {}
                try:
                    fc = json.loads(r.get("fail_codes_json","{}") or "{}")
                except Exception:
                    fc = {}

                rec = agg.get(key, {"band": band, "model": model, "integrator": integ, "variant": variant, "n": 0, "pass": 0, "fail_codes": {}})
                rec["n"] += n
                rec["pass"] += kpass
                # merge fail codes
                for code, cnt in fc.items():
                    rec["fail_codes"][code] = rec["fail_codes"].get(code, 0) + int(cnt)
                agg[key] = rec

    out_rows = []
    for key, rec in sorted(agg.items()):
        n = rec["n"]; kpass = rec["pass"]
        pr = (kpass/n) if n else float("nan")
        lo, hi = wilson_ci(kpass, n, args.z)
        out_rows.append({
            "band": rec["band"],
            "model": rec["model"],
            "integrator": rec["integrator"],
            "variant": rec["variant"],
            "n": n,
            "pass": kpass,
            "pass_rate": pr,
            "ci_lo": lo,
            "ci_hi": hi,
            "fail_codes_json": json.dumps(rec["fail_codes"], sort_keys=True),
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"Wrote {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
