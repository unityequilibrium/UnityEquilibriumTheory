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

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float,float]:
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    denom = 1 + (z*z)/n
    center = (phat + (z*z)/(2*n)) / denom
    half = (z*math.sqrt((phat*(1-phat) + (z*z)/(4*n)) / n)) / denom
    return (max(0.0, center-half), min(1.0, center+half))

def parse_variant(v: str) -> Tuple[str, float]:
    """
    variant like: ADAPT_codeDT_COLLAPSE_dt0p5 or ADAPT_codeX_dt0.5
    returns (code, dt_scale)
    """
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

def gkey(band: str, model: str, integ: str, code: str) -> str:
    return f"{band}|{model}|{integ}|{code}"

def geometric_mid(a: float, b: float) -> float:
    a = max(a, 1e-12)
    b = max(b, 1e-12)
    return math.sqrt(a*b)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant_summary_csv", required=True, help="summary grouped by band_model_integrator_variant")
    ap.add_argument("--out_plan", default="zoom_scale_plan.json")
    ap.add_argument("--min_pass_rate", type=float, default=0.95)
    ap.add_argument("--min_ci_lo", type=float, default=0.90)
    ap.add_argument("--min_scale", type=float, default=0.1)
    ap.add_argument("--max_scale", type=float, default=1.0)
    ap.add_argument("--eps_ratio", type=float, default=1.15, help="stop if pass/fail bracket ratio <= eps_ratio")
    ap.add_argument("--max_new_scales_per_group", type=int, default=1)
    ap.add_argument("--band_policy_json", default="", help="optional band zoom policy json")
    ap.add_argument("--use_smoothed", action="store_true", help="use smoothed_pass_rate/smoothed_ci_lo if present")
    ap.add_argument("--z", type=float, default=1.96, help="z for Wilson CI; recompute if needed")
    args = ap.parse_args()

    rows=[]
    with Path(args.variant_summary_csv).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    if not rows:
        raise SystemExit("Empty variant summary")


    band_policy = {}
    if args.band_policy_json:
        band_policy = json.loads(Path(args.band_policy_json).read_text(encoding="utf-8"))

    def get_pol(band: str) -> Dict[str, Any]:
        # global defaults
        d = band_policy.get("default", {}) if isinstance(band_policy, dict) else {}
        b = band_policy.get(band, {}) if isinstance(band_policy, dict) else {}
        out = dict(d)
        out.update(b)
        return out

    # group by (band, model, integrator, code)
    groups: Dict[str, List[Dict[str,Any]]] = {}
    for r in rows:
        band = (r.get("band","") or "UNLABELED").strip() or "UNLABELED"
        model = (r.get("model","") or "").strip()
        integ = (r.get("integrator","") or "").strip()
        variant = (r.get("variant","") or "BASE").strip() or "BASE"
        code, sc = parse_variant(variant)
        if math.isnan(sc) or sc <= 0:
            continue
        r2 = dict(r)
        r2["_code"] = code
        r2["_scale"] = sc
        groups.setdefault(gkey(band, model, integ, code), []).append(r2)

    plan = {}
    details = []
    n_new_total = 0

    for k, rs in sorted(groups.items()):
        # scale -> pass bool
        scale_map = {}
        for r in rs:
            sc = float(r["_scale"])
            if args.use_smoothed:
                pr = _f(str(r.get("smoothed_pass_rate", r.get("pass_rate","nan"))))
                lo = _f(str(r.get("smoothed_ci_lo", r.get("ci_lo","nan"))))
            else:
                pr = _f(str(r.get("pass_rate","nan")))
                lo = _f(str(r.get("ci_lo","nan")))
            # If ci_lo missing, recompute from pass/n
            if math.isnan(lo):
                try:
                    kk = int(float(str(r.get("pass","0"))))
                    nn = int(float(str(r.get("n","0"))))
                    lo, _ = wilson_ci(kk, nn, args.z)
                except Exception:
                    lo = float("nan")
            ok = (not math.isnan(pr)) and (not math.isnan(lo)) and (pr >= args.min_pass_rate) and (lo >= args.min_ci_lo)
            scale_map[sc] = ok

        scales = sorted(scale_map.keys())
        passes = [s for s in scales if scale_map[s]]
        fails = [s for s in scales if not scale_map[s]]

        rec = {"group_key": k, "tested_scales": scales, "pass_scales": passes, "fail_scales": fails}

        new_scales: List[float] = []

        if passes and fails:
            s_hi_pass = min(passes)  # smallest passing scale (most conservative among passes? actually smallest dt scale)
            # nearest fail below s_hi_pass if exists
            below = [s for s in fails if s < s_hi_pass]
            s_lo_fail = max(below) if below else max(fails)
            rec["bracket"] = {"s_lo_fail": s_lo_fail, "s_hi_pass": s_hi_pass, "ratio": (s_hi_pass / s_lo_fail) if s_lo_fail>0 else float("inf")}
            # stop if tight enough
            pol = get_pol(band)
            eps_ratio = float(pol.get('eps_ratio', args.eps_ratio))
            min_scale = float(pol.get('min_scale', args.min_scale))
            if s_lo_fail>0 and (s_hi_pass / s_lo_fail) <= eps_ratio:
                rec["status"] = "BRACKET_CONVERGED"
            else:
                # propose weighted geometric mid (band-aware)
                wmid = float(pol.get('mid_weight', 0.5))  # 0->toward fail (smaller), 1->toward pass (larger)
                wmid = max(0.0, min(1.0, wmid))
                a = max(s_lo_fail, 1e-12)
                b = max(s_hi_pass, 1e-12)
                cand = math.exp(math.log(a) + wmid*(math.log(b)-math.log(a)))
                # snap within bounds
                cand = max(min_scale, min(args.max_scale, cand))
                # avoid duplicates
                if all(abs(cand - s) > 1e-12 for s in scales):
                    new_scales.append(cand)
                else:
                    # fallback: linear mid
                    cand2 = 0.5*(s_lo_fail + s_hi_pass)
                    cand2 = max(min_scale, min(args.max_scale, cand2))
                    if all(abs(cand2 - s) > 1e-12 for s in scales):
                        new_scales.append(cand2)
                rec["status"] = "PROPOSE_ZOOM"
        elif fails and not passes:
            # always failing -> decrease scale (band-aware)
            pol = get_pol(band)
            min_scale = float(pol.get('min_scale', args.min_scale))
            step_down = float(pol.get('all_fail_step_down', 0.5))
            step_down = max(0.05, min(0.95, step_down))
            s_min = min(scales)
            cand = max(min_scale, s_min * step_down)
            if cand < args.min_scale + 1e-12 and abs(cand - s_min) < 1e-12:
                rec["status"] = "AT_MIN_SCALE_STILL_FAIL"
            else:
                if all(abs(cand - s) > 1e-12 for s in scales):
                    new_scales.append(cand)
                rec["status"] = "NEED_SMALLER_SCALE"
            rec["bracket"] = {"s_lo_fail": min(scales), "s_hi_pass": float("nan"), "ratio": float("inf")}
        elif passes and not fails:
            # all passing -> optionally try larger, but capped by max_scale
            rec["status"] = "ALL_PASS"
            rec["bracket"] = {"s_lo_fail": float("nan"), "s_hi_pass": min(passes), "ratio": float("nan")}
        else:
            rec["status"] = "NO_DATA"
            rec["bracket"] = {}

        # cap number new scales
        pol = get_pol(band)
        max_new = int(pol.get('max_new_scales_per_group', args.max_new_scales_per_group))
        new_scales = sorted(new_scales)[:max(0, max_new)]
        if new_scales:
            plan[k] = new_scales
            n_new_total += len(new_scales)
        rec["new_scales"] = new_scales
        details.append(rec)

    out = Path(args.out_plan)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "min_pass_rate": args.min_pass_rate,
            "min_ci_lo": args.min_ci_lo,
            "min_scale": args.min_scale,
            "max_scale": args.max_scale,
            "eps_ratio": args.eps_ratio,
            "max_new_scales_per_group": args.max_new_scales_per_group,
            "n_groups": len(groups),
            "n_groups_with_new_scales": len(plan),
            "n_new_scales_total": n_new_total,
        },
        "dt_scales_plan": plan,
        "details": details
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out} (groups_with_new_scales={len(plan)}, new_scales_total={n_new_total})")

if __name__ == "__main__":
    main()
