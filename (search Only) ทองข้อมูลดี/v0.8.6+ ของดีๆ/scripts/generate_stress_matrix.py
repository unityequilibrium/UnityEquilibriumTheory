#!/usr/bin/env python
from __future__ import annotations
import argparse, json, csv, math, hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

def _f(x) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")

def _hash_short(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:10]

def _sample_value(rng: np.random.Generator, spec: Dict[str, Any], base: float) -> float:
    dist = str(spec.get("dist","uniform")).lower()
    if dist == "fixed":
        return float(spec.get("value", base))
    lo = float(spec.get("min", base))
    hi = float(spec.get("max", base))
    if dist == "uniform":
        return float(rng.uniform(lo, hi))
    if dist == "loguniform":
        lo = max(lo, 1e-300)
        hi = max(hi, lo*(1+1e-12))
        return float(math.exp(rng.uniform(math.log(lo), math.log(hi))))
    if dist == "normal":
        mu = float(spec.get("mu", base))
        sigma = float(spec.get("sigma", 0.1*abs(mu) if mu!=0 else 0.1))
        return float(rng.normal(mu, sigma))
    # fallback uniform
    return float(rng.uniform(lo, hi))

def _parse_kv(params: str) -> Dict[str, float]:
    """
    Very small parser for top-level "k=v" in our params string (outside quartic(...) blocks).
    Returns float values when possible.
    """
    out: Dict[str, float] = {}
    # split by commas but keep quartic blocks intact
    parts = []
    buf = ""
    depth = 0
    for ch in params:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth-1)
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())

    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = k.strip()
        v = v.strip()
        # ignore init=..., V=quartic(...), VC/VI=quartic(...)
        if k.lower() in ("init","v","vc","vi"):
            continue
        try:
            out[k] = float(v)
        except Exception:
            pass
    return out

def _replace_top_level(params: str, key: str, val: float) -> str:
    # replace first occurrence of "key=<number>" at top-level
    pattern = rf"(?<![A-Za-z0-9_]){re_escape(key)}\s*=\s*([-+0-9.eE]+)"
    import re
    m = re.search(pattern, params)
    if not m:
        # append before init if present, else at end
        if ",init=" in params:
            return params.replace(",init=", f",{key}={val:.12g},init=")
        return params + f",{key}={val:.12g}"
    return params[:m.start()] + f"{key}={val:.12g}" + params[m.end():]

def re_escape(s: str) -> str:
    import re
    return re.escape(s)

def _replace_quartic(params: str, block_key: str, coeff_key: str, val: float) -> str:
    """
    Replace coefficient inside quartic(...) block for V/VC/VI.
    Example: V=quartic(a=1,delta=1,s=0)
             VC=quartic(aC=1,deltaC=1,sC=0)
    """
    import re
    # find block like "block_key=quartic(...)" 
    pat = rf"({re_escape(block_key)}\s*=\s*quartic\()([^)]*)(\))"
    m = re.search(pat, params)
    if not m:
        return params
    inner = m.group(2)

    # replace coeff_key=number inside inner
    pat2 = rf"(?<![A-Za-z0-9_]){re_escape(coeff_key)}\s*=\s*([-+0-9.eE]+)"
    if re.search(pat2, inner):
        inner2 = re.sub(pat2, f"{coeff_key}={val:.12g}", inner, count=1)
    else:
        # append inside
        inner2 = inner + ("," if inner.strip() else "") + f"{coeff_key}={val:.12g}"
    return params[:m.start(2)] + inner2 + params[m.end(2):]

def pick_dt(band: str, model: str, integrator: str, band_presets: Dict[str,Any], global_presets: Dict[str,Any], default_dt: float) -> float:
    dt = float("nan")
    # band-aware
    try:
        dt = float(band_presets.get(band, {}).get(model, {}).get(integrator, float("nan")))
    except Exception:
        dt = float("nan")
    if not (dt > 0):
        try:
            dt = float(global_presets.get(model, {}).get(integrator, float("nan")))
        except Exception:
            dt = float("nan")
    if not (dt > 0):
        dt = float(default_dt)
    return dt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="stress_spec.json")
    ap.add_argument("--out", default="stress_matrix.csv")
    ap.add_argument("--band_dt_presets", default="", help="band_dt_presets*.json mapping band->model->integrator->dt")
    ap.add_argument("--dt_presets", default="", help="dt_presets*.json mapping model->integrator->dt")
    ap.add_argument("--default_dt", type=float, default=float("nan"))
    ap.add_argument("--n_per_case", type=int, default=-1, help="override spec.n_per_case if >0")
    ap.add_argument("--seeds", default="", help="override spec.seeds like 0;1;2 (optional)")
    ap.add_argument("--integrators", default="", help="override spec.integrators like semiimplicit;stabilized (optional)")
    ap.add_argument("--stab_scale", type=float, default=0.5)
    ap.add_argument("--stab_margin", type=float, default=0.0)
    ap.add_argument("--stab_min", type=float, default=0.0)
    ap.add_argument("--stab_max", type=float, default=1e9)
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    cases = spec.get("cases", [])
    meta = spec.get("meta", {})

    N = int(meta.get("N", 128))
    L = float(meta.get("L", 1.0))
    T = float(meta.get("T", 5.0))

    n_per = int(meta.get("n_per_case", 20))
    if args.n_per_case and args.n_per_case > 0:
        n_per = args.n_per_case

    seeds = str(meta.get("seeds", "0")).strip()
    if args.seeds:
        seeds = args.seeds
    seed_list = [int(x) for x in seeds.split(";") if x.strip()]

    integrators = str(meta.get("integrators", "semiimplicit;stabilized")).strip()
    if args.integrators:
        integrators = args.integrators
    integ_list = [x.strip() for x in integrators.split(";") if x.strip()]

    band_presets = {}
    global_presets = {}
    if args.band_dt_presets:
        band_presets = json.loads(Path(args.band_dt_presets).read_text(encoding="utf-8"))
    if args.dt_presets:
        global_presets = json.loads(Path(args.dt_presets).read_text(encoding="utf-8"))

    rng = np.random.default_rng(int(meta.get("rng_seed", 0)))

    out_rows: List[Dict[str, Any]] = []
    missing_rows: List[Dict[str, Any]] = []

    for c in cases:
        base_id = str(c.get("base_case_id","stress_case")).strip()
        band = str(c.get("band","UNLABELED")).strip()
        model = str(c.get("model","")).strip()
        params0 = str(c.get("params","")).strip()
        pert = c.get("perturb", {}) or {}

        # parse base numerical values we can reference in perturb specs
        top = _parse_kv(params0)

        for j in range(n_per):
            params = params0
            # sample top-level
            for key, ps in (pert.get("top_level", {}) or {}).items():
                base_val = top.get(key, float(ps.get("base", 1.0)))
                val = _sample_value(rng, ps, base_val)
                params = _replace_top_level(params, key, val)
            # sample quartic blocks
            for block_key, block_spec in (pert.get("quartic", {}) or {}).items():
                for coeff_key, ps in (block_spec or {}).items():
                    base_val = float(ps.get("base", 1.0))
                    val = _sample_value(rng, ps, base_val)
                    params = _replace_quartic(params, block_key, coeff_key, val)

            sample_tag = f"{base_id}__S{j:04d}__h{_hash_short(params)}"
            for seed in seed_list:
                for integ in integ_list:
                    dt = pick_dt(band, model, integ, band_presets, global_presets, args.default_dt)
                    if not (dt > 0):
                        missing_rows.append({
                            "base_case_id": sample_tag,
                            "band": band,
                            "model": model,
                            "integrator": integ,
                            "seed": seed,
                            "reason": "missing_dt_preset",
                        })
                        continue

                    out_rows.append({
                        "base_case_id": sample_tag,
                        "band": band,
                        "model": model,
                        "params": params,
                        "N": N,
                        "L": L,
                        "T": T,
                        "seed": seed,
                        "dt_list": f"{dt:.12g}",
                        "integrators": integ,
                        "stab_scale": f"{args.stab_scale:.12g}",
                        "stab_margin": f"{args.stab_margin:.12g}",
                        "stab_min": f"{args.stab_min:.12g}",
                        "stab_max": f"{args.stab_max:.12g}",
                    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out_rows:
        raise SystemExit("No rows generated (maybe missing dt presets).")

    cols = list(out_rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    if missing_rows:
        miss = out.parent/"stress_missing_presets.csv"
        with miss.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(missing_rows[0].keys()))
            w.writeheader()
            for r in missing_rows:
                w.writerow(r)
        print("WARNING: missing dt presets for some rows; wrote", miss)

    print(f"Wrote stress matrix: {out} (rows={len(out_rows)})")

if __name__ == "__main__":
    main()
