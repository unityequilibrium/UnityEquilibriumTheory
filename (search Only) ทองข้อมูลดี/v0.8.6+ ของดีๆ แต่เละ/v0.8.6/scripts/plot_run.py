#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _save_plot(x, y, xlabel, ylabel, title, out_path: Path):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="path to a run folder containing timeseries.csv")
    ap.add_argument("--out_dir", default="", help="where to save plots (default: <run_dir>/plots)")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    ts_path = run_dir / "timeseries.csv"
    if not ts_path.exists():
        raise SystemExit(f"Missing timeseries.csv in {run_dir}")

    df = pd.read_csv(ts_path)
    out_dir = Path(args.out_dir) if args.out_dir else (run_dir / "plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    t = df["t"].to_numpy()
    Omega = df["Omega"].to_numpy()
    dOmega = df["dOmega"].to_numpy()

    _save_plot(t, Omega, "t", "Omega", "Omega(t)", out_dir / "omega_t.png")
    _save_plot(t, dOmega, "t", "dOmega", "dOmega(t) = Omega_{n+1}-Omega_n", out_dir / "domega_t.png")

    # Range proxy
    if "min_C" in df.columns and "max_C" in df.columns:
        rC = (df["max_C"] - df["min_C"]).to_numpy()
        _save_plot(t, rC, "t", "range_C", "range_C(t) = max_C - min_C", out_dir / "range_C_t.png")

    if "min_I" in df.columns and "max_I" in df.columns:
        # may contain blanks for C-only; guard with numeric conversion
        try:
            maxI = pd.to_numeric(df["max_I"], errors="coerce")
            minI = pd.to_numeric(df["min_I"], errors="coerce")
            if np.isfinite(maxI).any() and np.isfinite(minI).any():
                rI = (maxI - minI).to_numpy()
                _save_plot(t, rI, "t", "range_I", "range_I(t) = max_I - min_I", out_dir / "range_I_t.png")
        except Exception:
            pass

    print(f"Wrote plots to {out_dir}")

if __name__ == "__main__":
    main()
