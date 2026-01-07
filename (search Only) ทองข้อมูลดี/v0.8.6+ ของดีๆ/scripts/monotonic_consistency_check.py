#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math, re
from pathlib import Path
from typing import Dict, Any, List, Tuple

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

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float,float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    phat = k / n
    denom = 1 + (z*z)/n
    center = (phat + (z*z)/(2*n)) / denom
    half = (z*math.sqrt((phat*(1-phat) + (z*z)/(4*n)) / n)) / denom
    return (max(0.0, center-half), min(1.0, center+half))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant_summary_csv", required=True, help="summary grouped by band_model_integrator_variant (can be merged)")
    ap.add_argument("--out", default="", help="default: <parent>/monotonic_report.json")
    ap.add_argument("--z", type=float, default=1.96)
    ap.add_argument("--min_n", type=int, default=50, help="only check adjacent pairs where both n >= min_n")
    ap.add_argument("--delta", type=float, default=0.05, help="raw pass_rate drop threshold to flag")
    ap.add_argument("--use_smoothed_if_present", action="store_true",
                    help="if smoothed_pass_rate/smoothed_ci_lo exist, also compute smoothed checks")
    args = ap.parse_args()

    p = Path(args.variant_summary_csv)
    out = Path(args.out) if args.out else (p.parent/"monotonic_report.json")

    rows=[]
    with p.open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty variant summary")

    # group by (band,model,integrator,code)
    groups: Dict[Tuple[str,str,str,str], List[Dict[str,Any]]] = {}
    for r in rows:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        variant = (r.get("variant","") or "BASE").strip() or "BASE"
        code, sc = parse_variant(variant)
        if math.isnan(sc) or sc <= 0:
            continue
        r2 = dict(r)
        r2["_scale"] = float(sc)
        r2["_code"] = code
        groups.setdefault((band,model,integ,code), []).append(r2)

    violations=[]
    warnings=[]
    blocklist=[]  # band|model|integrator
    for (band,model,integ,code), rs in sorted(groups.items()):
        # sort by scale descending (bigger dt first), and expect pass_rate non-decreasing as scale decreases
        rs_sorted = sorted(rs, key=lambda r: -float(r["_scale"]))
        # Build arrays
        scales=[float(r["_scale"]) for r in rs_sorted]
        n=[int(float(r.get("n","0") or 0)) for r in rs_sorted]
        kpass=[int(float(r.get("pass","0") or 0)) for r in rs_sorted]
        pr=[_f(str(r.get("pass_rate","nan"))) for r in rs_sorted]
        lo=[_f(str(r.get("ci_lo","nan"))) for r in rs_sorted]
        hi=[_f(str(r.get("ci_hi","nan"))) for r in rs_sorted]
        # Fill ci if missing
        for i in range(len(rs_sorted)):
            if math.isnan(lo[i]) or math.isnan(hi[i]):
                lo[i], hi[i] = wilson_ci(kpass[i], n[i], args.z)

        # optional smoothed
        pr_s=None; lo_s=None; hi_s=None
        if args.use_smoothed_if_present and any("smoothed_pass_rate" in r for r in rs_sorted):
            pr_s=[_f(str(r.get("smoothed_pass_rate", r.get("pass_rate","nan")))) for r in rs_sorted]
        if args.use_smoothed_if_present and any("smoothed_ci_lo" in r for r in rs_sorted):
            lo_s=[_f(str(r.get("smoothed_ci_lo", r.get("ci_lo","nan")))) for r in rs_sorted]
            # we don't have smoothed ci_hi; approximate by keeping original width
            hi_s=[]
            for i in range(len(rs_sorted)):
                width = (hi[i]-lo[i]) if (not math.isnan(hi[i]) and not math.isnan(lo[i])) else 0.0
                hi_s.append(min(1.0, max(0.0, lo_s[i] + max(0.0, width))))

        # check adjacent pairs: i (higher scale) vs j=i+1 (lower scale)
        for i in range(len(rs_sorted)-1):
            j=i+1
            if n[i] < args.min_n or n[j] < args.min_n:
                continue
            # If smaller scale looks worse than larger by delta
            if (not math.isnan(pr[i]) and not math.isnan(pr[j])) and (pr[j] + args.delta < pr[i]):
                # significance check via CI separation: upper(smaller) < lower(larger)
                sig = (not math.isnan(hi[j]) and not math.isnan(lo[i]) and (hi[j] < lo[i]))
                rec = {
                    "band": band, "model": model, "integrator": integ, "code": code,
                    "scale_hi": scales[i], "scale_lo": scales[j],
                    "pass_rate_hi": pr[i], "pass_rate_lo": pr[j],
                    "ci_lo_hi": lo[i], "ci_hi_hi": hi[i],
                    "ci_lo_lo": lo[j], "ci_hi_lo": hi[j],
                    "n_hi": n[i], "n_lo": n[j],
                    "delta": args.delta,
                    "significant": bool(sig),
                    "group_band_model_integrator": f"{band}|{model}|{integ}",
                }
                violations.append(rec)
                if sig:
                    blocklist.append(rec["group_band_model_integrator"])
            # also check smoothed if present (as warning)
            if pr_s is not None and (not math.isnan(pr_s[i]) and not math.isnan(pr_s[j])) and (pr_s[j] + args.delta < pr_s[i]):
                warnings.append({
                    "band": band, "model": model, "integrator": integ, "code": code,
                    "scale_hi": scales[i], "scale_lo": scales[j],
                    "smoothed_pass_rate_hi": pr_s[i], "smoothed_pass_rate_lo": pr_s[j],
                    "type": "smoothed_drop",
                    "group_band_model_integrator": f"{band}|{model}|{integ}",
                })

    # unique blocklist
    blocklist = sorted(set(blocklist))

    report = {
        "meta": {
            "z": args.z, "min_n": args.min_n, "delta": args.delta,
            "use_smoothed_if_present": bool(args.use_smoothed_if_present),
            "n_groups_checked": len(groups),
            "n_violations": len(violations),
            "n_significant_blocklist": len(blocklist),
        },
        "blocklist_band_model_integrator": blocklist,
        "violations": violations[:2000],
        "warnings": warnings[:2000],
        "status": "OK" if len(blocklist)==0 else "BLOCK",
    }
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["meta"], indent=2))
    print("Wrote", out)

if __name__ == "__main__":
    main()
