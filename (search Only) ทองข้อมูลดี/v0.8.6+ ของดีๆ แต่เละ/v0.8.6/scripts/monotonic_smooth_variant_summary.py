#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, math, re, json
from pathlib import Path
from typing import List, Dict, Any, Tuple

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def parse_variant(v: str) -> Tuple[str, float]:
    v = (v or "").strip()
    code = "UNKNOWN"
    m = re.search(r"_code([A-Za-z0-9_]+)", v)
    if m:
        code = m.group(1)
    sc = float("nan")
    m2 = re.search(r"_dt([0-9]+(?:[p\.][0-9]+)?)", v)
    if m2:
        s = m2.group(1).replace("p",".")
        try:
            sc = float(s)
        except Exception:
            sc = float("nan")
    return code, sc

def gkey(band: str, model: str, integ: str, code: str) -> Tuple[str,str,str,str]:
    return (band, model, integ, code)

def pava_non_decreasing(x: List[float], y: List[float], w: List[float]) -> List[float]:
    """
    Pool Adjacent Violators Algorithm for non-decreasing y with respect to x (assumed x sorted ascending).
    Returns fitted yhat.
    """
    n = len(y)
    # blocks: (start, end, weight_sum, ybar)
    blocks = []
    for i in range(n):
        blocks.append([i, i, w[i], y[i]])
        # merge while violation: previous ybar > current ybar
        while len(blocks) >= 2 and blocks[-2][3] > blocks[-1][3]:
            b2 = blocks.pop()
            b1 = blocks.pop()
            wsum = b1[2] + b2[2]
            ybar = (b1[2]*b1[3] + b2[2]*b2[3]) / max(wsum, 1e-12)
            blocks.append([b1[0], b2[1], wsum, ybar])

    yhat = [0.0]*n
    for b in blocks:
        for i in range(b[0], b[1]+1):
            yhat[i] = b[3]
    return yhat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant_summary_csv", required=True, help="merged variant summary (band,model,integrator,variant,pass_rate,ci_lo,n,pass)")
    ap.add_argument("--out", default="variant_summary_smoothed.csv")
    ap.add_argument("--target", choices=["pass_rate","ci_lo","both"], default="both",
                    help="which signals to smooth monotonic in scale")
    ap.add_argument("--min_scale", type=float, default=1e-6)
    ap.add_argument("--max_scale", type=float, default=1.0)
    ap.add_argument("--weight", choices=["n","sqrt_n","none"], default="n")
    args = ap.parse_args()

    rows=[]
    with Path(args.variant_summary_csv).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty variant summary")

    # group rows
    groups: Dict[Tuple[str,str,str,str], List[Dict[str,Any]]] = {}
    for r in rows:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        variant = (r.get("variant","") or "BASE").strip() or "BASE"
        code, sc = parse_variant(variant)
        if math.isnan(sc) or sc <= 0:
            # keep but no smoothing
            r["_code"] = code
            r["_scale"] = float("nan")
            continue
        sc = max(args.min_scale, min(args.max_scale, sc))
        r["_code"] = code
        r["_scale"] = sc
        groups.setdefault(gkey(band, model, integ, code), []).append(r)

    # apply smoothing within each group
    for key, rs in groups.items():
        # sort by x = -log(scale) ascending => scale descending (largest dt) first
        rs_sorted = sorted(rs, key=lambda r: -math.log(max(float(r["_scale"]), 1e-12)))
        x = [-math.log(max(float(r["_scale"]), 1e-12)) for r in rs_sorted]  # larger scale => smaller x? actually -log: scale=1 -> 0, scale=0.5 -> 0.693. so x increases as scale decreases. Good.
        # ensure x sorted ascending
        order = sorted(range(len(x)), key=lambda i: x[i])
        rs_sorted = [rs_sorted[i] for i in order]
        x = [x[i] for i in order]

        n_list = [int(float(r.get("n","0") or 0)) for r in rs_sorted]
        if args.weight == "n":
            w = [max(1.0, float(n)) for n in n_list]
        elif args.weight == "sqrt_n":
            w = [max(1.0, math.sqrt(float(n))) for n in n_list]
        else:
            w = [1.0 for _ in n_list]

        if args.target in ("pass_rate","both"):
            y = [_f(str(r.get("pass_rate","nan"))) for r in rs_sorted]
            # replace NaNs with 0.0 for smoothing; mark later
            y2 = [0.0 if math.isnan(v) else max(0.0, min(1.0, v)) for v in y]
            yhat = pava_non_decreasing(x, y2, w)
            for r, yh, yraw in zip(rs_sorted, yhat, y):
                r["smoothed_pass_rate"] = yh
                r["smoothed_pass_rate_raw_missing"] = 1 if math.isnan(yraw) else 0

        if args.target in ("ci_lo","both"):
            y = [_f(str(r.get("ci_lo","nan"))) for r in rs_sorted]
            y2 = [0.0 if math.isnan(v) else max(0.0, min(1.0, v)) for v in y]
            yhat = pava_non_decreasing(x, y2, w)
            for r, yh, yraw in zip(rs_sorted, yhat, y):
                r["smoothed_ci_lo"] = yh
                r["smoothed_ci_lo_raw_missing"] = 1 if math.isnan(yraw) else 0

    # write output
    # ensure consistent columns: keep original plus smoothing columns if present
    extra_cols = []
    for c in ["smoothed_pass_rate","smoothed_ci_lo","smoothed_pass_rate_raw_missing","smoothed_ci_lo_raw_missing"]:
        if any(c in r for r in rows):
            extra_cols.append(c)

    # Preserve original columns order
    base_cols = list(rows[0].keys())
    # Remove internal keys if present
    base_cols = [c for c in base_cols if not c.startswith("_")]
    cols = base_cols + [c for c in extra_cols if c not in base_cols]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=cols)
        wtr.writeheader()
        for r in rows:
            rr = {k: r.get(k,"") for k in cols}
            wtr.writerow(rr)

    print("Wrote", out)

if __name__ == "__main__":
    main()
