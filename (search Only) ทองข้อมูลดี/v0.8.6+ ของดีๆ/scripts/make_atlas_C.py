#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

S_SWEEP=[-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--T", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--kappa", type=float, default=1.0)
    ap.add_argument("--M", type=float, default=1.0)
    ap.add_argument("--a", type=float, default=-1.0)
    ap.add_argument("--delta", type=float, default=1.0)
    ap.add_argument("--model", default="C_only", choices=["C_only","C_I"])
    args=ap.parse_args()

    rows=[]
    for s in S_SWEEP:
        if args.model=="C_only":
            params=f"kappa={args.kappa},M={args.M},V=quartic(a={args.a},delta={args.delta},s={s})"
        else:
            params=f"kC={args.kappa},kI={args.kappa},MC={args.M},MI={args.M},beta=0.5,VC=quartic(a={args.a},delta={args.delta},s={s}),VI=quartic(a={args.a},delta={args.delta},s={s})"
        rows.append(dict(case_id=f"atlasC_s{s}_a{args.a}_d{args.delta}_g{args.grid}_seed{args.seed}",
                         model=args.model, grid=args.grid, dt=args.dt, T=args.T, seed=args.seed,
                         params=params, notes="ATLAS-C | s sweep"))
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} cases -> {out}")

if __name__=="__main__": main()
