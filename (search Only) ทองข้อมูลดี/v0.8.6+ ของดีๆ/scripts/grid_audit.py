#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import pandas as pd

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dt", type=float, default=1e-3)
    ap.add_argument("--T", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--L", type=float, default=1.0)
    args=ap.parse_args()

    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    grids=[32,64,128]
    pts=[("P1",-1.0,1.0,1.0,0.0),("P2",0.5,1.0,1.0,0.0)]
    rows=[]
    for tag,a,d,k,s in pts:
        for g in grids:
            rows.append(dict(case_id=f"audit_{tag}_g{g}_seed{args.seed}",
                             model="C_only", grid=g, dt=args.dt, T=args.T, seed=args.seed,
                             params=f"kappa={k},M=1,V=quartic(a={a},delta={d},s={s})", notes="GRID_AUDIT"))
    matrix=out/"grid_audit_matrix.csv"
    pd.DataFrame(rows).to_csv(matrix, index=False)
    runs=out/"runs"
    cmd=["python", str(Path("scripts")/"run_suite.py"), "--matrix", str(matrix), "--out", str(runs), "--L", str(args.L)]
    subprocess.check_call(cmd)
    led=pd.read_csv(runs/"ledger.csv")
    led["OmegaT_density"]=led["OmegaT"]/(args.L**2)
    led.to_csv(out/"grid_audit_ledger.csv", index=False)
    led[["case_id","OmegaT","OmegaT_density","backtracks_total","status"]].to_csv(out/"grid_audit_summary.csv", index=False)
    print("Wrote ->", out/"grid_audit_summary.csv")

if __name__=="__main__": main()
