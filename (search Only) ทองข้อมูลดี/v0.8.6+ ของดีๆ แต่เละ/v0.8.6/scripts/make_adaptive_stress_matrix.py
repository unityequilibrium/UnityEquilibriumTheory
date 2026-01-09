#!/usr/bin/env python
from __future__ import annotations
import argparse, csv, json, math, hashlib, re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
import numpy as np

def _f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def _parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def _hash10(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]

def split_top_level(params: str) -> List[str]:
    parts=[]
    buf=""
    depth=0
    for ch in params:
        if ch=="(":
            depth+=1
        elif ch==")":
            depth=max(0, depth-1)
        if ch=="," and depth==0:
            parts.append(buf.strip()); buf=""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts

def parse_numeric_params(params: str) -> Tuple[Dict[str,float], Dict[str,Dict[str,float]]]:
    """
    Returns (top_level_numeric, quartic_blocks)
    quartic_blocks: {block_key: {coeff_key: val}}
    """
    top={}
    quartic={}
    for p in split_top_level(params):
        if "=" not in p:
            continue
        k,v = p.split("=",1)
        k=k.strip()
        v=v.strip()
        if k.lower() in ("init","pattern","noise"):
            continue
        # quartic blocks
        if v.startswith("quartic(") and v.endswith(")"):
            inner = v[len("quartic("):-1]
            coeffs={}
            for item in inner.split(","):
                item=item.strip()
                if "=" not in item: 
                    continue
                ck,cv = item.split("=",1)
                ck=ck.strip(); cv=cv.strip()
                try:
                    coeffs[ck]=float(cv)
                except Exception:
                    pass
            quartic[k]=coeffs
            continue
        # normal numeric
        try:
            top[k]=float(v)
        except Exception:
            pass
    return top, quartic

def rebuild_params(params: str, top_updates: Dict[str,float], quartic_updates: Dict[str,Dict[str,float]]) -> str:
    parts=[]
    for p in split_top_level(params):
        if "=" not in p:
            parts.append(p); continue
        k,v = p.split("=",1)
        k0=k.strip(); v0=v.strip()
        if k0 in top_updates:
            parts.append(f"{k0}={top_updates[k0]:.12g}")
            continue
        if v0.startswith("quartic(") and v0.endswith(")") and k0 in quartic_updates:
            inner = v0[len("quartic("):-1]
            coeffs={}
            for item in inner.split(","):
                item=item.strip()
                if "=" not in item:
                    continue
                ck,cv = item.split("=",1)
                ck=ck.strip(); cv=cv.strip()
                coeffs[ck]=cv
            # apply updates
            for ck,val in quartic_updates[k0].items():
                coeffs[ck]=f"{val:.12g}"
            inner2=",".join([f"{ck}={cv}" for ck,cv in coeffs.items()])
            parts.append(f"{k0}=quartic({inner2})")
            continue
        parts.append(p)
    return ",".join(parts)

def jitter_value(rng: np.random.Generator, val: float, log_span: float, abs_span: float) -> float:
    if val == 0.0 or math.isnan(val):
        return float(rng.uniform(-abs_span, abs_span))
    # multiplicative jitter in log space
    factor = math.exp(rng.uniform(-log_span, log_span))
    return float(val * factor)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stress_matrix_in", required=True, help="original stress_matrix.csv used for runs")
    ap.add_argument("--stress_ledger", required=True, help="stress_runs/dt_ladder_ledger.csv")
    ap.add_argument("--out", default="adaptive_stress_matrix.csv")
    ap.add_argument("--top_groups", type=int, default=5, help="top failing (band,model,integrator,fail_code) groups")
    ap.add_argument("--cases_per_group", type=int, default=5, help="unique failed base_case_id to focus per group")
    ap.add_argument("--jitters_per_case", type=int, default=3, help="new samples per failed case")
    ap.add_argument("--log_span", type=float, default=0.35, help="log multiplicative jitter span (exp(unif(-s,s)))")
    ap.add_argument("--abs_span_zero", type=float, default=0.2, help="absolute jitter span when base value is 0")
    ap.add_argument("--dt_scales", default="1.0;0.5", help="semicolon separated dt scales for A/B test")
    ap.add_argument("--dt_scales_plan", default="", help="json with dt_scales_plan mapping group_key->list(scales) from suggest_zoom_scales.py")
    ap.add_argument("--seeds", default="", help="override seeds list (semicolon). If empty, reuse from failing rows.")
    ap.add_argument("--max_rows", type=int, default=20000)
    ap.add_argument("--only_fail_codes", default="", help="optional filter fail codes (semicolon)")
    ap.add_argument("--skip_params_regex", default="", help="regex to exclude top-level keys from jitter (e.g. '^(beta|M)$')")
    ap.add_argument("--keep_quartic", action="store_true", help="if set, do not jitter quartic coefficients")
    ap.add_argument("--variant_prefix", default="ADAPT")
    args = ap.parse_args()

    # load matrix map
    matrix_rows=[]
    with Path(args.stress_matrix_in).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            matrix_rows.append(r)
    if not matrix_rows:
        raise SystemExit("Empty stress_matrix_in")

    by_base = {}
    for r in matrix_rows:
        by_base[str(r.get("base_case_id","")).strip()] = r

    # load ledger
    ledger_rows=[]
    with Path(args.stress_ledger).open("r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            ledger_rows.append(r)
    if not ledger_rows:
        raise SystemExit("Empty stress_ledger")

    fail_codes_filter = set(_parse_list(args.only_fail_codes))
    if args.only_fail_codes and not fail_codes_filter:
        raise SystemExit("only_fail_codes given but parsed empty")

    fails=[]
    for r in ledger_rows:
        if str(r.get("status","")).upper()=="PASS":
            continue
        code = (str(r.get("fail_code","")).strip() or "UNKNOWN")
        if fail_codes_filter and code not in fail_codes_filter:
            continue
        base = str(r.get("base_case_id","")).strip()
        if base not in by_base:
            continue
        fails.append(r)

    if not fails:
        raise SystemExit("No failing rows found (after filters)")

    # rank fail groups
    grp={}
    for r in fails:
        key=( (r.get("band","") or "UNLABELED").strip() or "UNLABELED",
              (r.get("model","") or "").strip(),
              (r.get("integrator","") or "").strip(),
              (str(r.get("fail_code","")).strip() or "UNKNOWN") )
        grp[key]=grp.get(key,0)+1

    top = sorted(grp.items(), key=lambda kv: kv[1], reverse=True)[:args.top_groups]

    # build failed cases per group (prefer those failing on many seeds)
    # compute seed-fail counts per base_case_id within group
    rng = np.random.default_rng(0)

    dt_scales = [float(x) for x in _parse_list(args.dt_scales)]
    plan = {}
    if args.dt_scales_plan:
        plan = json.loads(Path(args.dt_scales_plan).read_text(encoding="utf-8")).get("dt_scales_plan", {})

    if not dt_scales:
        dt_scales = [1.0]

    skip_re = re.compile(args.skip_params_regex) if args.skip_params_regex else None

    out_rows=[]
    used=0
    for (band, model, integ, code), count in top:
        # collect rows in this group
        rows_g=[r for r in fails if ( (r.get("band","") or "UNLABELED").strip() or "UNLABELED")==band
                and (r.get("model","") or "").strip()==model
                and (r.get("integrator","") or "").strip()==integ
                and (str(r.get("fail_code","")).strip() or "UNKNOWN")==code]
        # score by unique seeds failing
        seed_fail={}
        for r in rows_g:
            base=str(r.get("base_case_id","")).strip()
            seed=str(r.get("seed","")).strip()
            seed_fail.setdefault(base,set()).add(seed)
        bases_sorted=sorted(seed_fail.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        focus_bases=[b for b,_ in bases_sorted[:args.cases_per_group]]

        for base in focus_bases:
            src = by_base[base]
            params0 = src.get("params","").strip()
            N = src.get("N","128"); L=src.get("L","1.0"); T=src.get("T","5.0")
            # determine base dt from any ledger row in this group with this base
            rows_base=[r for r in rows_g if str(r.get("base_case_id","")).strip()==base]
            if not rows_base:
                continue
            dt0 = _f(str(rows_base[0].get("dt","nan")))
            # decide seeds set
            if args.seeds:
                seeds = [int(x) for x in _parse_list(args.seeds)]
            else:
                seeds = sorted({int(float(str(r.get("seed","0")))) for r in rows_base})

            # parse params and create jitters
            top_num, quartic = parse_numeric_params(params0)

            for j in range(args.jitters_per_case):
                top_up={}
                for k,v in top_num.items():
                    if skip_re and skip_re.search(k):
                        top_up[k]=v
                    else:
                        top_up[k]=jitter_value(rng, v, args.log_span, args.abs_span_zero)
                quartic_up={}
                if not args.keep_quartic:
                    for bk, coeffs in quartic.items():
                        quartic_up[bk]={}
                        for ck, cv in coeffs.items():
                            quartic_up[bk][ck]=jitter_value(rng, cv, args.log_span, args.abs_span_zero)

                params = rebuild_params(params0, top_up, quartic_up)
                h = _hash10(params)
                new_base = f"{base}__{args.variant_prefix}__J{j:02d}__h{h}"

                scales_here = dt_scales
                gk = f"{band}|{model}|{integ}|{code}"
                if plan and gk in plan:
                    try:
                        scales_here = [float(x) for x in plan[gk]]
                    except Exception:
                        scales_here = dt_scales
                for scale in scales_here:
                    dt = dt0*scale if (not math.isnan(dt0)) else float("nan")
                    if not (dt>0):
                        continue
                    variant = f"{args.variant_prefix}_code{code}_dt{scale:.3g}".replace(".","p")
                    for seed in seeds:
                        row = {
                            "base_case_id": new_base,
                            "band": band,
                            "variant": variant,
                            "origin_case_id": base,
                            "origin_fail_code": code,
                            "model": model,
                            "params": params,
                            "N": N, "L": L, "T": T,
                            "seed": str(seed),
                            "dt_list": f"{dt:.12g}",
                            "integrators": integ,
                            # inherit stab controls if present else defaults
                            "stab_scale": src.get("stab_scale","0.5"),
                            "stab_margin": src.get("stab_margin","0.0"),
                            "stab_min": src.get("stab_min","0.0"),
                            "stab_max": src.get("stab_max","1e9"),
                        }
                        out_rows.append(row)
                        used += 1
                        if used >= args.max_rows:
                            break
                    if used >= args.max_rows:
                        break
                if used >= args.max_rows:
                    break
            if used >= args.max_rows:
                break
        if used >= args.max_rows:
            break

    if not out_rows:
        raise SystemExit("No adaptive rows generated")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out_rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"Wrote {out} (rows={len(out_rows)})")
    print("Top fail groups used:", top)

if __name__ == "__main__":
    main()
