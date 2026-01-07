# scripts/plot_phase_maps.py
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


GRADE_MAP = {
    "BIAS_I": -1.0,
    "SYM": 0.0,
    "BIAS_C": 1.0,
}


def _pick_bias_col(df: pd.DataFrame) -> str:
    for c in ["grade_bias", "grade_bias_v2", "bias_grade", "gradeBias"]:
        if c in df.columns:
            return c
    # fallback: sometimes stored as "grade" in bias file merges (rare)
    if "grade" in df.columns:
        return "grade"
    raise ValueError("No bias grade column found (expected grade_bias).")


def _heatmap(mat: np.ndarray, xvals, yvals, title: str, cbar_label: str, out: Path,
             vmin=None, vmax=None, fmt="{:.2f}"):
    fig = plt.figure()
    ax = plt.gca()

    # If the matrix is 1x1 or 1xN or Nx1, 'auto' is usually fine, but 
    # if it's truly empty, we can't plot.
    if mat.size == 0:
        print(f"Skipping empty heatmap: {title}")
        plt.close(fig)
        return

    # Handle singular dimensions to avoid warnings
    aspect = "auto"
    if len(xvals) == 1 or len(yvals) == 1:
        aspect = "equal"    

    im = ax.imshow(mat, aspect=aspect, origin="lower", vmin=vmin, vmax=vmax)

    ax.set_xticks(np.arange(len(xvals)))
    ax.set_xticklabels([str(x) for x in xvals])
    ax.set_yticks(np.arange(len(yvals)))
    ax.set_yticklabels([str(y) for y in yvals])

    ax.set_xlabel("s_tilt")
    ax.set_ylabel("beta")
    ax.set_title(title)

    # annotate
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            if np.isnan(val):
                txt = "NA"
            else:
                txt = fmt.format(val)
            ax.text(j, i, txt, ha="center", va="center")

    cbar = plt.colorbar(im)
    cbar.set_label(cbar_label)

    out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close(fig)
    print(f"Wrote: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="reports/UET_final_summary.csv")
    ap.add_argument("--outdir", default="reports")
    ap.add_argument("--model", default=None, help="Optional filter, e.g. C_I")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    bias_col = _pick_bias_col(df)

    # keep only rows that have beta/s_tilt and bias grade
    df["beta"] = pd.to_numeric(df.get("beta", np.nan), errors="coerce")
    df["s_tilt"] = pd.to_numeric(df.get("s_tilt", np.nan), errors="coerce")
    df = df[df["beta"].notna() & df["s_tilt"].notna() & df[bias_col].notna()].copy()

    if args.model and "model" in df.columns:
        df = df[df["model"].astype(str) == args.model].copy()

    df["grade_num"] = df[bias_col].astype(str).map(GRADE_MAP)

    betas = sorted(df["beta"].unique())
    svals = sorted(df["s_tilt"].unique())

    # mean grade map
    mean_mat = np.full((len(betas), len(svals)), np.nan, dtype=float)
    strength_mat = np.full((len(betas), len(svals)), np.nan, dtype=float)

    for bi, beta in enumerate(betas):
        for sj, s in enumerate(svals):
            sub = df[(df["beta"] == beta) & (df["s_tilt"] == s)]
            if sub.empty:
                continue

            # mean numeric grade
            mean_mat[bi, sj] = float(sub["grade_num"].mean())

            # strength
            n = len(sub)
            pC = float((sub[bias_col].astype(str) == "BIAS_C").sum()) / n
            pI = float((sub[bias_col].astype(str) == "BIAS_I").sum()) / n
            strength_mat[bi, sj] = pC - pI

    outdir = Path(args.outdir)
    _heatmap(
        mean_mat, svals, betas,
        title="Phase: mean grade (BIAS_I=-1, SYM=0, BIAS_C=+1)",
        cbar_label="Value",
        out=outdir / "phase_mean_grade.png",
        vmin=-1, vmax=1, fmt="{:.2f}",
    )
    _heatmap(
        strength_mat, svals, betas,
        title="Phase: Strength = P(BIAS_C) - P(BIAS_I)",
        cbar_label="Value",
        out=outdir / "phase_strength.png",
        vmin=-1, vmax=1, fmt="{:.2f}",
    )


if __name__ == "__main__":
    main()
