#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import csv

DEFAULT_DTS = ["0.1","0.05","0.02","0.01","0.005"]
DEFAULT_INTEG = ["semiimplicit","stabilized"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dt_ladder_matrix.csv")
    ap.add_argument("--dts", default=";".join(DEFAULT_DTS))
    ap.add_argument("--integrators", default=";".join(DEFAULT_INTEG))
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--L", type=float, default=1.0)
    ap.add_argument("--T", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "base_case_id":"ladder_C_only",
            "model":"C_only",
            "params":'kappa=1,M=1,V=quartic(a=1,delta=1,s=0),init=random',
            "N":str(args.N),
            "L":str(args.L),
            "T":str(args.T),
            "seed":str(args.seed),
            "dt_list":args.dts,
            "integrators":args.integrators,
            "stab_scale":"0.5",
            "stab_margin":"0.0",
            "stab_min":"0.0",
            "stab_max":"1e9",
        },
        {
            "base_case_id":"ladder_CI",
            "model":"C_I",
            "params":'kC=1,kI=1,MC=1,MI=1,beta=1.5,VC=quartic(aC=1,deltaC=1,sC=0),VI=quartic(aI=1,deltaI=1,sI=0),init=random_correlated',
            "N":str(args.N),
            "L":str(args.L),
            "T":str(args.T),
            "seed":str(args.seed),
            "dt_list":args.dts,
            "integrators":args.integrators,
            "stab_scale":"0.5",
            "stab_margin":"0.0",
            "stab_min":"0.0",
            "stab_max":"1e9",
        }
    ]

    cols = ["base_case_id","model","params","N","L","T","seed","dt_list","integrators",
            "stab_scale","stab_margin","stab_min","stab_max"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote starter dt ladder matrix: {out}")

if __name__ == "__main__":
    main()
