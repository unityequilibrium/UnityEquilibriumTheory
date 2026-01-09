#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True, help="UET_final_summary.csv")
    ap.add_argument("--out", default="phase_beta_s.png")
    args = ap.parse_args()

    df = pd.read_csv(args.summary)
    df = df.dropna(subset=["beta","s_tilt","grade_bias"])

    # map grade to number for heat-ish plot
    mapv = {"BIAS_C": 1, "SYM": 0, "BIAS_I": -1}
    df["g"] = df["grade_bias"].map(mapv)

    piv = df.groupby(["beta","s_tilt"])["g"].mean().unstack()

    plt.figure()
    plt.imshow(piv.values, aspect="auto")
    plt.yticks(range(len(piv.index)), piv.index)
    plt.xticks(range(len(piv.columns)), piv.columns)
    plt.xlabel("s_tilt")
    plt.ylabel("beta")
    plt.title("Phase (mean grade): BIAS_I=-1, SYM=0, BIAS_C=+1")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(args.out, dpi=200)

if __name__ == "__main__":
    main()
