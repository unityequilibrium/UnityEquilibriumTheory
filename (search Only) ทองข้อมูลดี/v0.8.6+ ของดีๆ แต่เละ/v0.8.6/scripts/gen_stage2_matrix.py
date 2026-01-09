#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def _pick_representative(atlas: pd.DataFrame, model: str, param_id: str) -> dict:
    g = atlas[(atlas["model"]==model) & (atlas["param_id"]==param_id)].copy()
    if len(g)==0:
        raise ValueError(f"No rows for model={model} param_id={param_id}")
    # Prefer PASS base if present
    if "variant" in g.columns:
        g = g[g["variant"]=="base"] if (g["variant"]=="base").any() else g
    g_pass = g[g["status"]=="PASS"]
    row = (g_pass.iloc[0] if len(g_pass)>0 else g.iloc[0]).to_dict()
    return row

def _ensure_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return float(default)

def _case_id(prefix: str, idx: int, seed: int) -> str:
    return f"{prefix}_{idx:03d}_s{seed}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atlas_csv", required=True, help="atlas_outputs/atlas.csv")
    ap.add_argument("--candidates_csv", required=True, help="boundary_candidates.csv from boundary_select.py")
    ap.add_argument("--out", required=True, help="output Stage-2 matrix CSV")
    ap.add_argument("--grid", type=int, default=128)
    ap.add_argument("--T", type=float, default=0.6)
    ap.add_argument("--seeds", default="0,1,2,3,4", help="comma-separated seeds for stage2")
    ap.add_argument("--refine_dt", type=int, default=1)
    ap.add_argument("--refine_grid", type=int, default=1)
    args = ap.parse_args()

    atlas = pd.read_csv(args.atlas_csv)
    cand = pd.read_csv(args.candidates_csv)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()!=""]

    rows = []
    def add_row(case_id, model, params, dt):
        rows.append({
            "case_id": case_id,
            "tier": "atlas_stage2",
            "model": model,
            "dim": 2,
            "bc": "periodic",
            "integrator": "semiimplicit",
            "grid": args.grid,
            "dt": dt,
            "T": args.T,
            "seed": None,
            "refine_dt": args.refine_dt,
            "refine_grid": args.refine_grid,
            "params": params
        })

    idx = 1
    for _, cr in cand.iterrows():
        model = str(cr["model"])
        pid = str(cr["param_id"])
        rep = _pick_representative(atlas, model, pid)
        # Use atlas dt as a starting point but be conservative for stage2
        dt_base = _ensure_float(rep.get("dt", 2e-4), 2e-4)
        dt_stage2 = dt_base/2.0

        if model == "C_only":
            a = _ensure_float(rep.get("a", 0.0))
            delta = _ensure_float(rep.get("delta", 1.0), 1.0)
            s = _ensure_float(rep.get("s", 0.0))
            kappa = _ensure_float(rep.get("kappa", 1.0), 1.0)
            M = _ensure_float(rep.get("M", 1.0), 1.0)

            # Local perturbations around boundary: vary one axis at a time
            a_list = [a-0.5, a, a+0.5]
            s_list = [s-0.1, s, s+0.1]
            k_list = [max(0.05, kappa/2.0), kappa, kappa*2.0]

            for a2 in a_list:
                params = f"kappa={kappa},M={M}, V=quartic(a={a2},delta={delta},s={s}), init=random"
                for sd in seeds:
                    rows.append({
                        "case_id": _case_id("BND_Ca", idx, sd),
                        "tier": "atlas_stage2",
                        "model": "C_only",
                        "dim": 2, "bc": "periodic", "integrator": "semiimplicit",
                        "grid": args.grid, "dt": dt_stage2, "T": args.T,
                        "seed": sd, "refine_dt": args.refine_dt, "refine_grid": args.refine_grid,
                        "params": params
                    })
                idx += 1

            for s2 in s_list:
                params = f"kappa={kappa},M={M}, V=quartic(a={a},delta={delta},s={s2}), init=random"
                for sd in seeds:
                    rows.append({
                        "case_id": _case_id("BND_Cs", idx, sd),
                        "tier": "atlas_stage2",
                        "model": "C_only",
                        "dim": 2, "bc": "periodic", "integrator": "semiimplicit",
                        "grid": args.grid, "dt": dt_stage2, "T": args.T,
                        "seed": sd, "refine_dt": args.refine_dt, "refine_grid": args.refine_grid,
                        "params": params
                    })
                idx += 1

            for k2 in k_list:
                params = f"kappa={k2},M={M}, V=quartic(a={a},delta={delta},s={s}), init=random"
                for sd in seeds:
                    rows.append({
                        "case_id": _case_id("BND_Ck", idx, sd),
                        "tier": "atlas_stage2",
                        "model": "C_only",
                        "dim": 2, "bc": "periodic", "integrator": "semiimplicit",
                        "grid": args.grid, "dt": dt_stage2, "T": args.T,
                        "seed": sd, "refine_dt": args.refine_dt, "refine_grid": args.refine_grid,
                        "params": params
                    })
                idx += 1

        elif model == "C_I":
            beta = _ensure_float(rep.get("beta", 0.5), 0.5)
            kC = _ensure_float(rep.get("kC", 1.0), 1.0)
            kI = _ensure_float(rep.get("kI", 1.0), 1.0)
            MC = _ensure_float(rep.get("MC", 1.0), 1.0)
            MI = _ensure_float(rep.get("MI", 1.0), 1.0)

            aC = _ensure_float(rep.get("aC", 0.0))
            dC = _ensure_float(rep.get("deltaC", 1.0), 1.0)
            sC = _ensure_float(rep.get("sC", 0.0))
            aI = _ensure_float(rep.get("aI", 0.0))
            dI = _ensure_float(rep.get("deltaI", 1.0), 1.0)
            sI = _ensure_float(rep.get("sI", 0.0))

            beta_list = [max(0.0, beta-0.75), beta, beta+0.75]
            kI_list = [max(0.05, kI/2.0), kI, kI*2.0]

            for b2 in beta_list:
                params = f"kC={kC},kI={kI},MC={MC},MI={MI},beta={b2}, VC=quartic(aC={aC},deltaC={dC},sC={sC}), VI=quartic(aI={aI},deltaI={dI},sI={sI}), init=random_correlated"
                for sd in seeds:
                    rows.append({
                        "case_id": _case_id("BND_CIbeta", idx, sd),
                        "tier": "atlas_stage2",
                        "model": "C_I",
                        "dim": 2, "bc": "periodic", "integrator": "semiimplicit",
                        "grid": args.grid, "dt": dt_stage2, "T": args.T,
                        "seed": sd, "refine_dt": args.refine_dt, "refine_grid": args.refine_grid,
                        "params": params
                    })
                idx += 1

            for kI2 in kI_list:
                params = f"kC={kC},kI={kI2},MC={MC},MI={MI},beta={beta}, VC=quartic(aC={aC},deltaC={dC},sC={sC}), VI=quartic(aI={aI},deltaI={dI},sI={sI}), init=random_correlated"
                for sd in seeds:
                    rows.append({
                        "case_id": _case_id("BND_CIkI", idx, sd),
                        "tier": "atlas_stage2",
                        "model": "C_I",
                        "dim": 2, "bc": "periodic", "integrator": "semiimplicit",
                        "grid": args.grid, "dt": dt_stage2, "T": args.T,
                        "seed": sd, "refine_dt": args.refine_dt, "refine_grid": args.refine_grid,
                        "params": params
                    })
                idx += 1

        else:
            continue

    out = pd.DataFrame(rows)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(out)} rows")

if __name__ == "__main__":
    main()
