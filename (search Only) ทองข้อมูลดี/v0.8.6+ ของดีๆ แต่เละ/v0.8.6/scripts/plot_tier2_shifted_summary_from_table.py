#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser(description="Create Tier2 shifted summary plot from tier2_shifted_table.csv (no need to re-extract scale from config/meta).")
    ap.add_argument("--table", default=r"reports\tier2_shifted\tier2_shifted_table.csv", help="Path to tier2_shifted_table.csv")
    ap.add_argument("--out_dir", default=r"reports\tier2_shifted", help="Output directory")
    args = ap.parse_args()

    table_path = Path(args.table)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not table_path.exists():
        raise FileNotFoundError(f"Table not found: {table_path}. Run your shifted-table generator first.")

    df = pd.read_csv(table_path)
    if "scale" not in df.columns:
        raise RuntimeError("Column 'scale' not found in table. Your generator should include it (e.g. parsed from case_id).")

    # Ensure numeric scale
    df["scale"] = pd.to_numeric(df["scale"], errors="coerce")
    df = df.dropna(subset=["scale"])
    df["scale"] = df["scale"].astype(int)

    # Basic sanity
    needed = ["V0", "VT", "Omega0", "OmegaT", "Omega_star", "status"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing columns in table: {missing}")

    # Aggregate
    agg = df.groupby("scale").agg(
        n=("status", "size"),
        pass_rate=("status", lambda s: float((s == "PASS").mean())),
        Omega0_mean=("Omega0", "mean"),
        Omega0_std=("Omega0", "std"),
        OmegaT_mean=("OmegaT", "mean"),
        OmegaT_std=("OmegaT", "std"),
        V0_mean=("V0", "mean"),
        V0_std=("V0", "std"),
        VT_mean=("VT", "mean"),
        VT_std=("VT", "std"),
    ).reset_index().sort_values("scale")

    out_csv = out_dir / "tier2_shifted_summary.csv"
    agg.to_csv(out_csv, index=False)

    # Plot (2 panels)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    x = agg["scale"].values

    ax[0].errorbar(x, agg["V0_mean"].values, yerr=agg["V0_std"].values, marker="o", capsize=4)
    ax[0].set_title("V0 mean ± std by scale (shifted)")
    ax[0].set_xlabel("scale (s)")
    ax[0].set_ylabel("V0 = Omega0 - Omega*")
    ax[0].grid(True)

    ax[1].errorbar(x, agg["VT_mean"].values, yerr=agg["VT_std"].values, marker="o", capsize=4)
    ax[1].set_title("VT mean ± std by scale (shifted)")
    ax[1].set_xlabel("scale (s)")
    ax[1].set_ylabel("VT = OmegaT - Omega*")
    ax[1].grid(True)

    fig.tight_layout()
    out_png = out_dir / "tier2_shifted_summary.png"
    fig.savefig(out_png, dpi=180)
    plt.close(fig)

    print("Wrote:", out_csv)
    print("Saved:", out_png)
    print("Tip: VT≈0 across s means Omega(t) monotonically decreased to its minimum (good Lyapunov behavior).")

if __name__ == "__main__":
    main()
