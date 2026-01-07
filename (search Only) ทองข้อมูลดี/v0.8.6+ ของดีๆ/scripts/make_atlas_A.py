#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--T", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--kappa", type=float, default=1.0)
    ap.add_argument("--M", type=float, default=1.0)
    ap.add_argument("--s", type=float, default=0.0)
    ap.add_argument("--model", default="C_only", choices=["C_only","C_I"])
    args=ap.parse_args()

    a_vals=[-2.0,-1.0,-0.5,0.5,1.0]
    d_vals=[0.25,0.5,1.0,2.0,4.0]
    rows=[]
    for a in a_vals:
        for d in d_vals:
            if args.model=="C_only":
                params=f"kappa={args.kappa},M={args.M},V=quartic(a={a},delta={d},s={args.s})"
            else:
                params=f"kC={args.kappa},kI={args.kappa},MC={args.M},MI={args.M},beta=0.5,VC=quartic(a={a},delta={d},s={args.s}),VI=quartic(a={a},delta={d},s={args.s})"
            rows.append(dict(case_id=f"atlasA_a{a}_d{d}_g{args.grid}_seed{args.seed}",
                             model=args.model, grid=args.grid, dt=args.dt, T=args.T, seed=args.seed,
                             params=params, notes="ATLAS-A | sweep a x delta"))
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} cases -> {out}")

if __name__=="__main__": main()
