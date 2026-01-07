#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

P_POINTS=[("P1",-1.0,1.0,0.0),("P2",0.5,1.0,0.0),("P3",-1.0,4.0,0.0)]
KAPPA=[0.25,0.5,1.0,2.0,4.0,8.0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--grid", type=int, default=64)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--T", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--M", type=float, default=1.0)
    ap.add_argument("--model", default="C_only", choices=["C_only","C_I"])
    args=ap.parse_args()

    rows=[]
    for tag,a,d,s in P_POINTS:
        for k in KAPPA:
            if args.model=="C_only":
                params=f"kappa={k},M={args.M},V=quartic(a={a},delta={d},s={s})"
            else:
                params=f"kC={k},kI={k},MC={args.M},MI={args.M},beta=0.5,VC=quartic(a={a},delta={d},s={s}),VI=quartic(a={a},delta={d},s={s})"
            rows.append(dict(case_id=f"atlasB_{tag}_k{k}_a{a}_d{d}_g{args.grid}_seed{args.seed}",
                             model=args.model, grid=args.grid, dt=args.dt, T=args.T, seed=args.seed,
                             params=params, notes=f"ATLAS-B | kappa sweep | {tag}"))
    out=Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} cases -> {out}")

if __name__=="__main__": main()
