#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def gen_stage1(seeds: list[int], grid: int, dt_C: float, dt_CI: float, T: float) -> pd.DataFrame:
    rows = []
    def add(case_id, model, params, dt):
        rows.append({
            "case_id": case_id,
            "tier": "atlas_stage1",
            "model": model,
            "dim": 2,
            "bc": "periodic",
            "integrator": "semiimplicit",
            "grid": grid,
            "dt": dt,
            "T": T,
            "seed": None,  # filled per-seed in loop below
            "refine_dt": 1,
            "refine_grid": 0,
            "params": params
        })

    # --- C-only axes ---
    a_list = [-1, 0, 1]
    delta_list = [1, 2]
    s_list = [0.0, 0.2]
    kappa_list = [0.2, 1.0]

    pid = 1
    for a in a_list:
        for delta in delta_list:
            for s in s_list:
                for kappa in kappa_list:
                    params = f"kappa={kappa},M=1, V=quartic(a={a},delta={delta},s={s}), init=random"
                    for seed in seeds:
                        cid = f"ATL_C_{pid:03d}_s{seed}"
                        rows.append({
                            "case_id": cid,
                            "tier": "atlas_stage1",
                            "model": "C_only",
                            "dim": 2,
                            "bc": "periodic",
                            "integrator": "semiimplicit",
                            "grid": grid,
                            "dt": dt_C,
                            "T": T,
                            "seed": seed,
                            "refine_dt": 1,
                            "refine_grid": 0,
                            "params": params
                        })
                    pid += 1

    # --- C+I axes ---
    beta_list = [0.5, 2.0]
    k_pairs = [(1.0, 1.0), (1.0, 0.2)]
    pot_sets = [
        ("aC=1,deltaC=1,sC=0", "aI=1,deltaI=1,sI=0"),
        ("aC=0,deltaC=4,sC=0", "aI=0,deltaI=4,sI=0"),
    ]

    pid2 = 1
    for beta in beta_list:
        for (kC, kI) in k_pairs:
            for (VC, VI) in pot_sets:
                params = f"kC={kC},kI={kI},MC=1,MI=1,beta={beta}, VC=quartic({VC}), VI=quartic({VI}), init=random_correlated"
                for seed in seeds:
                    cid = f"ATL_CI_{pid2:03d}_s{seed}"
                    rows.append({
                        "case_id": cid,
                        "tier": "atlas_stage1",
                        "model": "C_I",
                        "dim": 2,
                        "bc": "periodic",
                        "integrator": "semiimplicit",
                        "grid": grid,
                        "dt": dt_CI,
                        "T": T,
                        "seed": seed,
                        "refine_dt": 1,
                        "refine_grid": 0,
                        "params": params
                    })
                pid2 += 1

    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", choices=["stage1"], default="stage1")
    ap.add_argument("--out", required=True, help="output CSV path")
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--T", type=float, default=0.4)
    ap.add_argument("--dt_C", type=float, default=5e-4)
    ap.add_argument("--dt_CI", type=float, default=2e-4)
    ap.add_argument("--seeds", default="0,1,2", help="comma-separated seeds")
    args = ap.parse_args()

    seeds = [int(x) for x in args.seeds.split(",") if x.strip()!=""]
    if args.preset == "stage1":
        df = gen_stage1(seeds=seeds, grid=args.grid, dt_C=args.dt_C, dt_CI=args.dt_CI, T=args.T)
    else:
        raise SystemExit("Unknown preset")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {out} with {len(df)} rows")

if __name__ == "__main__":
    main()
