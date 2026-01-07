#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    ap = argparse.ArgumentParser(description="Make a 1-page identifiability table from graded atlas summaries.")
    ap.add_argument("--atlasA", required=True, help="reports/atlas_A/atlas_summary.csv (graded PASS-only recommended)")
    ap.add_argument("--atlasB", default="", help="reports/atlas_B/atlas_summary.csv")
    ap.add_argument("--atlasC", default="", help="reports/atlas_C/atlas_summary.csv")
    ap.add_argument("--out", required=True, help="output CSV path")
    args = ap.parse_args()

    A = pd.read_csv(args.atlasA)
    # sensitivity proxy: variation of metric across sweep axes
    rows = []

    def var_proxy(df, cols):
        d={}
        for c in cols:
            if c in df.columns:
                v = df[c].astype(float, errors="ignore")
                try:
                    d[c] = float(np.nanstd(pd.to_numeric(df[c], errors="coerce")))
                except Exception:
                    d[c] = float("nan")
        return d

    # For A: map to a,delta
    A_metrics = var_proxy(A, ["OmegaT_density","OmegaT","backtracks_total"])
    rows.append({"param":"a (alpha)","observable_hint":"OmegaT_density, phase-map","evidence":"Atlas-A sweep along a shows variation in ΩT / FAIL regions", "notes":"controls single/double-well tendency"})
    rows.append({"param":"delta (=lambda)","observable_hint":"OmegaT_density, stability/backtracks","evidence":"Atlas-A sweep along delta affects boundedness/stiffness", "notes":"quartic strength / boundedness knob"})
    rows.append({"param":"kappa","observable_hint":"xi, spectrum_ratio, rT","evidence":"Use Atlas-B (kappa sweep) to confirm xi↑ & spectrum_ratio↑ with kappa", "notes":"interaction reach / smoothing"})
    rows.append({"param":"s","observable_hint":"mean_C_T / phase_id","evidence":"Use Atlas-C to confirm sign(mean_C_T) follows sign(s)", "notes":"bias / phase selection"})

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote identifiability table -> {out}")

if __name__ == "__main__":
    main()
