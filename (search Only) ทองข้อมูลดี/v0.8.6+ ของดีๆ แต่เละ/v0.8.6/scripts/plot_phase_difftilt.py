#!/usr/bin/env python3
"""Plot phase maps for differential tilt results."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to UET_final_summary.csv")
    parser.add_argument("--out", default=".", help="Output directory for plots")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    
    grade_map = {"BIAS_I": -1, "SYM": 0, "BIAS_C": 1}
    df["grade_num"] = df["grade_bias"].map(grade_map)

    g = df.groupby(["beta", "s_tilt"])
    mean_grade = g["grade_num"].mean().unstack("s_tilt").sort_index(ascending=False)
    pC = g.apply(lambda x: (x["grade_bias"] == "BIAS_C").mean()).unstack("s_tilt").sort_index(ascending=False)
    pI = g.apply(lambda x: (x["grade_bias"] == "BIAS_I").mean()).unstack("s_tilt").sort_index(ascending=False)
    strength = (pC - pI)

    def save_heat(mat, title, out, cmap="RdBu_r"):
        plt.figure(figsize=(9, 6))
        plt.imshow(mat.values, aspect="auto", cmap=cmap, vmin=-1, vmax=1)
        plt.xticks(range(mat.shape[1]), mat.columns)
        plt.yticks(range(mat.shape[0]), mat.index)
        plt.colorbar(label="Value")
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                v = mat.values[i, j]
                if np.isfinite(v):
                    plt.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=10)
        plt.title(title)
        plt.xlabel("s_tilt")
        plt.ylabel("beta")
        plt.tight_layout()
        plt.savefig(out, dpi=200)
        plt.close()
        print(f"Saved: {out}")

    import os
    save_heat(mean_grade, "Phase: mean grade (BIAS_I=-1, SYM=0, BIAS_C=+1)", 
              os.path.join(args.out, "phase_mean_grade.png"))
    save_heat(strength, "Phase: Strength = P(BIAS_C) - P(BIAS_I)", 
              os.path.join(args.out, "phase_strength.png"))

if __name__ == "__main__":
    main()
