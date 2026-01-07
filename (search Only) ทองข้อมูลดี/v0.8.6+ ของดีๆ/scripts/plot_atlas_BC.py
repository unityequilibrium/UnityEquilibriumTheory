#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from _plot_common import load_config_for_run, extract_quartic_params, add_density_columns

def group_from_case(case_id: str)->str:
    for tag in ["P1","P2","P3"]:
        if case_id.startswith(f"atlasB_{tag}_") or f"_{tag}_" in case_id:
            return tag
    return "all"

def lineplot(df: pd.DataFrame, x: str, y: str, out_path: Path):
    fig=plt.figure(); ax=plt.gca()
    for g,sub in df.groupby("group"):
        sub=sub.sort_values(x)
        ax.plot(sub[x].values, sub[y].values, marker="o", label=str(g))
    ax.set_xlabel(x); ax.set_ylabel(y); ax.legend()
    fig.tight_layout(); out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160); plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pass_only", action="store_true")
    args=ap.parse_args()

    runs=Path(args.runs); out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ledger=pd.read_csv(runs/"ledger.csv")
    meta=[]
    for rid, cid in zip(ledger["run_id"].astype(str), ledger["case_id"].astype(str)):
        cfg=load_config_for_run(runs, rid)
        p=extract_quartic_params(cfg); p["run_id"]=rid; p["group"]=group_from_case(cid)
        meta.append(p)
    df=ledger.merge(pd.DataFrame(meta), on="run_id", how="left")
    df=add_density_columns(df)
    if args.pass_only: df=df[df["status"]=="PASS"].copy()
    df.to_csv(out/"atlas_joined.csv", index=False)

    sweep=None
    if "kappa" in df.columns and df["kappa"].nunique(dropna=True)>1: sweep="kappa"
    if "s" in df.columns and df["s"].nunique(dropna=True)>1:
        if sweep is None or df["s"].nunique(dropna=True)>=df["kappa"].nunique(dropna=True): sweep="s"
    if sweep is None:
        print("No sweep var"); return

    for metric in ["OmegaT","OmegaT_density","backtracks_total"]:
        if metric not in df.columns: continue
        lineplot(df.dropna(subset=[sweep,metric]), sweep, metric, out/f"line_{metric}_vs_{sweep}.png")
    df.to_csv(out/"atlas_summary.csv", index=False)
    print(f"Wrote -> {out}")

if __name__=="__main__": main()
