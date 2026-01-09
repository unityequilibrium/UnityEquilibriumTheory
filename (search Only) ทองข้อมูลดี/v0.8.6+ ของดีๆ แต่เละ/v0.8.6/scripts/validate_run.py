#!/usr/bin/env python
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="path to a single run folder")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)

    cfg = json.loads((run_dir/"config.json").read_text(encoding="utf-8"))
    ts = (run_dir/"timeseries.csv").read_text(encoding="utf-8").splitlines()
    summ = json.loads((run_dir/"summary.json").read_text(encoding="utf-8"))

    # Minimal invariant check: monotonicity under configured tolerances
    import pandas as pd
    import numpy as np
    df = pd.read_csv(run_dir/"timeseries.csv")
    tol_abs = float(cfg["time"].get("tol_abs", 1e-10))
    tol_rel = float(cfg["time"].get("tol_rel", 1e-10))
    Omega = df["Omega"].to_numpy()
    dOmega = df["dOmega"].to_numpy()
    thr = tol_abs + tol_rel*np.maximum(1.0, np.abs(Omega))
    viol = np.where(dOmega > thr)[0]
    ok = (len(viol) == 0)

    print("monotone_ok:", ok)
    if not ok:
        first = int(viol[0])
        print("first_violation_step:", first, "dOmega:", float(dOmega[first]), "thr:", float(thr[first]))
    print("reported_status:", summ.get("status"))

if __name__ == "__main__":
    main()
