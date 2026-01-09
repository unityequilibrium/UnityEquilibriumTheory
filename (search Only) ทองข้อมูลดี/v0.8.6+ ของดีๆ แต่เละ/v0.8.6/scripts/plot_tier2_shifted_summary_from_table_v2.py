#!/usr/bin/env python
import argparse
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def extract_scale_from_case_id(case_id: str):
    # expects patterns like "...s-2..." or "...s0..."
    m = re.search(r"s(-?\d+)", str(case_id))
    if m:
        return int(m.group(1))
    return np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="Path to tier2_shifted_table.csv")
    ap.add_argument("--out_dir", required=True, help="Output directory (e.g., reports/tier2_shifted)")
    args = ap.parse_args()

    table_path = Path(args.table)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(table_path)

    # Ensure numeric cols
    for c in ["Omega0","OmegaT","Omega_star","V0","VT"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Scale handling:
    if "scale" not in df.columns:
        df["scale"] = np.nan
    df["scale"] = pd.to_numeric(df["scale"], errors="coerce")

    # If scale missing/NaN, derive from case_id
    if df["scale"].isna().all():
        if "case_id" not in df.columns:
            raise RuntimeError("No 'scale' column and no 'case_id' column to derive it from.")
        df["scale"] = df["case_id"].apply(extract_scale_from_case_id)
        df["scale"] = pd.to_numeric(df["scale"], errors="coerce")

    # Drop rows without scale or V0/VT
    keep = df.dropna(subset=["scale","V0","VT"])
    if keep.empty:
        raise RuntimeError(
            "No rows left after dropping NaNs in scale/V0/VT. "
            "Check that tier2_shifted_table.csv has V0/VT computed and scale derivable."
        )

    # Aggregate by scale
    agg = keep.groupby("scale").agg(
        n=("VT","size"),
        V0_mean=("V0","mean"),
        V0_std=("V0","std"),
        VT_mean=("VT","mean"),
        VT_std=("VT","std"),
        Omega0_mean=("Omega0","mean"),
        OmegaT_mean=("OmegaT","mean"),
        Omega_star_mean=("Omega_star","mean"),
    ).reset_index().sort_values("scale")

    # std=NaN when n==1; set to 0 to plot cleanly
    for c in ["V0_std","VT_std"]:
        agg[c] = agg[c].fillna(0.0)

    # Save summary CSV
    out_csv = out_dir / "tier2_shifted_summary.csv"
    agg.to_csv(out_csv, index=False)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.errorbar(agg["scale"], agg["V0_mean"], yerr=agg["V0_std"], marker="o", capsize=4)
    ax1.set_title("V0 mean ± std by scale (shifted)")
    ax1.set_xlabel("scale (s)")
    ax1.set_ylabel("V0 = Omega0 - Omega*")
    ax1.grid(True)

    ax2.errorbar(agg["scale"], agg["VT_mean"], yerr=agg["VT_std"], marker="o", capsize=4)
    ax2.set_title("VT mean ± std by scale (shifted)")
    ax2.set_xlabel("scale (s)")
    ax2.set_ylabel("VT = OmegaT - Omega*")
    ax2.grid(True)

    fig.tight_layout()
    out_png = out_dir / "tier2_shifted_summary.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    # Quick sanity note
    # VT should be >= 0 by construction if Omega* is min_t Omega(t).
    if (agg["VT_mean"] < -1e-12).any():
        print("WARNING: Some VT_mean < 0 detected. That violates the 'Omega* = min' definition; check computations.")

    print(f"Wrote: {out_csv}")
    print(f"Saved: {out_png}")

if __name__ == "__main__":
    main()
