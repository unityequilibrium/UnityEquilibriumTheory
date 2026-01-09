#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from _plot_common import load_config_for_run, extract_quartic_params, add_density_columns

def heatmap(piv: pd.DataFrame, title: str, out_path: Path):
    fig=plt.figure()
    ax=plt.gca()
    im=ax.imshow(piv.values, aspect="auto", origin="lower")
    ax.set_title(title)
    ax.set_xlabel(piv.columns.name or "a")
    ax.set_ylabel(piv.index.name or "delta")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([str(c) for c in piv.columns], rotation=45, ha="right")
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([str(i) for i in piv.index])
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pass_only", action="store_true")
    args=ap.parse_args()

    runs=Path(args.runs); out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ledger=pd.read_csv(runs/"ledger.csv")
    meta=[]
    for rid in ledger["run_id"].astype(str):
        cfg=load_config_for_run(runs, rid)
        p=extract_quartic_params(cfg); p["run_id"]=rid
        meta.append(p)
    df=ledger.merge(pd.DataFrame(meta), on="run_id", how="left")
    df=add_density_columns(df)
    if args.pass_only:
        df=df[df["status"]=="PASS"].copy()
    df=df.dropna(subset=["a","delta"])
    df.to_csv(out/"atlas_A_joined.csv", index=False)

    for metric in ["OmegaT","OmegaT_density","backtracks_total"]:
        if metric not in df.columns: continue
        piv=df.pivot_table(index="delta", columns="a", values=metric, aggfunc="mean")
        piv.index.name="delta"; piv.columns.name="a"
        heatmap(piv, f"Atlas-A {metric}", out/f"heatmap_{metric}.png")
    df.to_csv(out/"atlas_summary.csv", index=False)
    print(f"Wrote -> {out}")

if __name__=="__main__": main()
