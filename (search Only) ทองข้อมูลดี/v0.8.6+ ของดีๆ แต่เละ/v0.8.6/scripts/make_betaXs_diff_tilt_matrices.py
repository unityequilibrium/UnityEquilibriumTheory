#!/usr/bin/env python3
"""
Generate differential tilt matrices for beta × s_tilt cross-sweep.

Two modes:
- tiltCOnly: potC.s = s_tilt, potI.s = 0
- tiltOpp_half: potC.s = +s_tilt/2, potI.s = -s_tilt/2

Usage:
  python scripts/make_betaXs_diff_tilt_matrices.py
"""

import pandas as pd
from pathlib import Path

BETAS = [0, 0.1, 0.3, 1.0, 3.0]
S_TILTS = [-2, -1, 0, 1, 2]
NSEED = 10

BASE = dict(
    tier="cross_CI_diff_tilt",
    model="C_I",
    dim=2,
    bc="periodic",
    integrator="semiimplicit",
    grid=64,
    dt=0.001,
    T=0.6,
    max_steps=300000,
)


def btag(b: float) -> str:
    s = str(b).replace(".", "p")
    return s


def make_rows(mode: str):
    rows = []
    for beta in BETAS:
        for st in S_TILTS:
            for seed in range(NSEED):
                cid = f"betaXs_{mode}_b{btag(beta)}_sT{st}_seed{seed}"

                # core params
                kC = 1
                kI = 1
                MC = 1
                MI = 1

                if mode == "tiltCOnly":
                    sC = float(st)
                    sI = 0.0
                    note = "differential tilt: potC.s=s_tilt, potI.s=0"
                elif mode == "tiltOpp_half":
                    sC = float(st) / 2.0
                    sI = -float(st) / 2.0
                    note = "differential tilt: potC.s=+s_tilt/2, potI.s=-s_tilt/2 (so s_tilt=sC-sI)"
                else:
                    raise ValueError("unknown mode")

                params = (
                    f"kC={kC},kI={kI},MC={MC},MI={MI},beta={beta},"
                    f"VC=quartic(a=1,delta=1,s={sC}),"
                    f"VI=quartic(a=1,delta=1,s={sI})"
                )

                row = dict(case_id=cid, **BASE, seed=seed, params=params, notes=note)
                rows.append(row)
    return rows


def main():
    outdir = Path("matrices")
    outdir.mkdir(exist_ok=True)

    for mode in ["tiltCOnly", "tiltOpp_half"]:
        df = pd.DataFrame(make_rows(mode))
        out = outdir / f"UET_Cross_CI_beta_s_{mode}_seed10.csv"
        df.to_csv(out, index=False)
        print("Wrote:", out, "rows=", len(df))


if __name__ == "__main__":
    main()
