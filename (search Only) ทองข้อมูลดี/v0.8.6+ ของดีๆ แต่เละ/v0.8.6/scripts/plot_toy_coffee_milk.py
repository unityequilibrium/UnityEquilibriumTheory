"""
Plot CoffeeMilk toy results from runs_toy_coffee_milk/{ledger.csv,validation_toy.csv}.

Usage:
  python scripts/plot_toy_coffee_milk.py --runs runs_toy_coffee_milk
"""
from __future__ import annotations
import argparse, re, math
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

S_RE = re.compile(r"_s([+-]\d+)_")
ASYM_RE = re.compile(r"bal_asym([0-9.]+)_")
KR_RE = re.compile(r"_kr([0-9.]+)_")
MR_RE = re.compile(r"_Mr([0-9.]+)_")

def parse_case_id(cid: str):
    s = None; asym=None; kr=None; mr=None
    m = S_RE.search(cid)
    if m: s = int(m.group(1))
    m = ASYM_RE.search(cid)
    if m: asym = float(m.group(1))
    m = KR_RE.search(cid)
    if m: kr = float(m.group(1))
    m = MR_RE.search(cid)
    if m: mr = float(m.group(1))
    family = "balanced"
    if "_kr" in cid: family = "k_ratio"
    if "_Mr" in cid: family = "M_ratio"
    return family, s, asym, kr, mr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="runs_toy_coffee_milk")
    args = ap.parse_args()

    runs = Path(args.runs)
    led = pd.read_csv(runs/"ledger.csv")
    valp = runs/"validation_toy.csv"
    if valp.exists():
        val = pd.read_csv(valp)
        df = led.merge(val[["run_id","case_id","grade"]], on=["run_id","case_id"], how="left")
    else:
        df = led.copy()
        df["grade"] = np.where(df["status"]=="PASS","PASS","FAIL")

    parsed = df["case_id"].apply(parse_case_id)
    df["family"] = parsed.apply(lambda x: x[0])
    df["s"] = parsed.apply(lambda x: x[1])
    df["asym"] = parsed.apply(lambda x: x[2])
    df["k_ratio"] = parsed.apply(lambda x: x[3])
    df["M_ratio"] = parsed.apply(lambda x: x[4])
    df["s_abs"] = df["s"].abs()

    # mixing hardness proxy: dt_min (smaller = harder)
    if "dt_min" in df.columns:
        df["hardness"] = -np.log10(np.clip(df["dt_min"].astype(float), 1e-18, None))
    else:
        df["hardness"] = np.nan

    # 1) OmegaT vs |s| by family
    for fam, sub in df.groupby("family"):
        agg = sub.groupby("s_abs")["OmegaT"].agg(["mean","std","count"]).reset_index()
        plt.figure()
        plt.plot(agg["s_abs"], agg["mean"], marker="o")
        plt.xlabel("|s| (tilt magnitude)")
        plt.ylabel("OmegaT (mean)")
        plt.title(f"CoffeeMilk toy: OmegaT vs |s| ({fam})")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # 2) Hardness vs |s| by family (if dt_min exists)
    if df["hardness"].notna().any():
        for fam, sub in df.groupby("family"):
            agg = sub.groupby("s_abs")["hardness"].agg(["mean","std","count"]).reset_index()
            plt.figure()
            plt.plot(agg["s_abs"], agg["mean"], marker="o")
            plt.xlabel("|s| (tilt magnitude)")
            plt.ylabel("Hardness = -log10(dt_min)")
            plt.title(f"CoffeeMilk toy: stiffness proxy vs |s| ({fam})")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

if __name__ == "__main__":
    main()
