import argparse, math, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--outdir", default="plots_sweep")
    ap.add_argument("--param", default="k_ratio", help="k_ratio or Mr_effective or abs_s or s")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)

    # derived params
    if "kC" in df.columns and "kI" in df.columns:
        df["k_ratio"] = df["kC"] / df["kI"].replace(0, np.nan)
    if "MC" in df.columns and "MI" in df.columns:
        df["Mr_effective"] = df["MI"] / df["MC"].replace(0, np.nan)
    if "s" in df.columns:
        df["abs_s"] = df["s"].abs()

    p = args.param
    if p not in df.columns:
        raise ValueError(f"param '{p}' not found. available: {list(df.columns)}")

    metrics = [m for m in ["OmegaT","t_relax","AUC_E_norm","AUC_Omega_norm","slope_init"] if m in df.columns]

    # group mean/std
    g = df.groupby(p)[metrics].agg(["mean","std","count"]).reset_index()
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    g.to_csv(outdir / f"summary_by_{p}.csv", index=False)
    print("Wrote:", outdir / f"summary_by_{p}.csv")

    # plots
    for m in metrics:
        plt.figure()
        x = g[p].to_numpy()
        y = g[(m,"mean")].to_numpy()
        yerr = g[(m,"std")].to_numpy()
        plt.errorbar(x, y, yerr=yerr, marker="o", linestyle="-", capsize=3)
        plt.xlabel(p); plt.ylabel(m); plt.title(f"{m} vs {p}")
        # log x for ratios if all positive and wide
        if (x > 0).all() and (x.max() / x.min() > 30):
            plt.xscale("log")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(outdir / f"{m}_vs_{p}.png", dpi=160)
        plt.close()

if __name__ == "__main__":
    main()
