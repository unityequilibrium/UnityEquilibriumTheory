#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary_csv", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    summ = Path(args.summary_csv)
    out_dir = Path(args.out) if args.out else (summ.parent / "plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(summ)
    if len(df) == 0:
        print("Empty summary.")
        return

    plt.figure()
    for integ, sub in df.groupby("integrator"):
        sub2 = sub.sort_values("dt")
        plt.plot(sub2["dt"], sub2["pass_rate"], marker="o", label=str(integ))
    plt.xscale("log")
    plt.ylim(-0.05, 1.05)
    plt.xlabel("dt")
    plt.ylabel("pass_rate")
    plt.title("Pass rate vs dt (dt ladder)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir/"pass_rate_vs_dt.png", dpi=160)
    plt.close()

    plt.figure()
    for integ, sub in df.groupby("integrator"):
        sub2 = sub.sort_values("dt")
        plt.plot(sub2["dt"], sub2["median_backtracks"], marker="o", label=str(integ))
    plt.xscale("log")
    plt.xlabel("dt")
    plt.ylabel("median_backtracks")
    plt.title("Median backtracks vs dt (dt ladder)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir/"median_backtracks_vs_dt.png", dpi=160)
    plt.close()

    print("Wrote plots to", out_dir)

if __name__ == "__main__":
    main()
