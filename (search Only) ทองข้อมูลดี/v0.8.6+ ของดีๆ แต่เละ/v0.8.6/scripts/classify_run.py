#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import json

def classify_from_timeseries(df: pd.DataFrame, eps_range: float = 1e-3) -> str:
    # Divergent if any NaN
    if not np.isfinite(df["Omega"].to_numpy()).all():
        return "DIVERGENT"
    # Use final range proxy from min/max columns if present
    cols = df.columns
    def _range(prefix: str) -> float | None:
        minc = f"min_{prefix}"
        maxc = f"max_{prefix}"
        if minc in cols and maxc in cols:
            return float(df[maxc].iloc[-1] - df[minc].iloc[-1])
        return None
    rC = _range("C")
    rI = _range("I")
    r = 0.0
    if rC is not None:
        r = max(r, abs(rC))
    if rI is not None:
        r = max(r, abs(rI))
    if r < eps_range:
        return "STEADY"
    return "PATTERNED"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--eps_range", type=float, default=1e-3)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    df = pd.read_csv(run_dir/"timeseries.csv")
    cls = classify_from_timeseries(df, eps_range=args.eps_range)
    summ = json.loads((run_dir/"summary.json").read_text(encoding="utf-8"))
    print("case_id:", summ.get("case_id"))
    print("status:", summ.get("status"))
    print("classification:", cls)

if __name__ == "__main__":
    main()
